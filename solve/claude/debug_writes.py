import random

CACHED_RATE = 0.08
INPUT_RATE = 0.8
WRITE_RATE = 1.0


def _precompute_simulation():
    rng = random.Random(114514)
    system_len = len("Example System Prompt" * 500)
    output_len = len("Example output of cache match")
    msg_lens = [system_len]
    rounds_info = []
    for _ in range(3000):
        num_new = rng.randint(1, 3)
        for _ in range(num_new):
            c = chr(rng.randint(32, 127))
            if rng.randint(1, 100) < 95:
                l = rng.randint(20, 100)
            else:
                l = rng.randint(500, 2000)
            msg_lens.append(l)
        total = sum(msg_lens)
        truncated = False
        if total > 128 * 1024:
            n = len(msg_lens)
            cut = int(n * rng.randint(40, 60) / 100)
            msg_lens = [msg_lens[0]] + msg_lens[cut:]
            truncated = True
            total = sum(msg_lens)
        rounds_info.append({'total_tokens': total, 'truncated': truncated})
        msg_lens.append(output_len)
    return rounds_info


def _cost_between(tokens, start, end, cached_tokens):
    c = 0.0
    for i in range(start, end):
        c += cached_tokens * CACHED_RATE + (tokens[i] - cached_tokens) * INPUT_RATE
    return c


def _dp_segment(tokens, system_len):
    n = len(tokens)
    if n == 0:
        return []
    INF = float('inf')
    dp = [INF] * n
    dp_parent = [-2] * n
    for w in range(n):
        cost = _cost_between(tokens, 0, w + 1, system_len) + tokens[w] * WRITE_RATE
        dp[w] = cost
        dp_parent[w] = -1
    for w in range(n):
        if dp[w] == INF:
            continue
        for w2 in range(w + 1, n):
            cost = dp[w] + _cost_between(tokens, w + 1, w2 + 1, tokens[w]) + tokens[w2] * WRITE_RATE
            if cost < dp[w2]:
                dp[w2] = cost
                dp_parent[w2] = w
    no_write_total = _cost_between(tokens, 0, n, system_len)
    best_cost = no_write_total
    best_last = -1
    for w in range(n):
        remaining = _cost_between(tokens, w + 1, n, tokens[w])
        total = dp[w] + remaining
        if total < best_cost:
            best_cost = total
            best_last = w
    if best_last == -1:
        return []
    writes = []
    cur = best_last
    while cur >= 0:
        writes.append(cur)
        cur = dp_parent[cur]
    writes.reverse()
    return writes


rounds_info = _precompute_simulation()
system_len = len("Example System Prompt" * 500)

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i))
        seg_start = i + 1
segments.append((seg_start, len(rounds_info) - 1))

total_write_cost = 0
total_uncached_cost = 0
total_cached_cost = 0

for seg_start, seg_end in segments:
    if seg_start > seg_end:
        continue
    tokens = [rounds_info[i]['total_tokens'] for i in range(seg_start, seg_end + 1)]
    writes = _dp_segment(tokens, system_len)
    n = len(tokens)

    print(f"Segment {seg_start}-{seg_end} ({n} rounds), tokens[0]={tokens[0]}, tokens[-1]={tokens[-1]}")
    print(f"  Writes at local indices: {writes}")
    print(f"  Write tokens: {[tokens[w] for w in writes]}")
    if writes:
        print(f"  First write at round {writes[0]} (offset from segment start)")
