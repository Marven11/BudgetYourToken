import random

def precompute():
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

CACHED_RATE = 0.08
INPUT_RATE = 0.8
WRITE_RATE = 1.0

def dp_segment(tokens, system_len):
    n = len(tokens)
    if n == 0:
        return set(), 0
    INF = float('inf')
    dp = [INF] * n
    dp_parent = [-2] * n
    for w in range(n):
        cost = 0.0
        for i in range(w + 1):
            cost += system_len * CACHED_RATE + (tokens[i] - system_len) * INPUT_RATE
        cost += tokens[w] * WRITE_RATE
        dp[w] = cost
        dp_parent[w] = -1
    for w in range(n):
        if dp[w] == INF:
            continue
        for w2 in range(w + 1, n):
            cost = dp[w]
            for i in range(w + 1, w2 + 1):
                cost += tokens[w] * CACHED_RATE + (tokens[i] - tokens[w]) * INPUT_RATE
            cost += tokens[w2] * WRITE_RATE
            if cost < dp[w2]:
                dp[w2] = cost
                dp_parent[w2] = w
    no_write_total = 0.0
    for i in range(n):
        no_write_total += system_len * CACHED_RATE + (tokens[i] - system_len) * INPUT_RATE
    best_cost = no_write_total
    best_last = -1
    for w in range(n):
        remaining = 0.0
        for i in range(w + 1, n):
            remaining += tokens[w] * CACHED_RATE + (tokens[i] - tokens[w]) * INPUT_RATE
        total_cost = dp[w] + remaining
        if total_cost < best_cost:
            best_cost = total_cost
            best_last = w
    if best_last == -1:
        return set(), best_cost
    writes = set()
    cur = best_last
    while cur >= 0:
        writes.add(cur)
        cur = dp_parent[cur]
    return writes, best_cost

rounds_info = precompute()
system_len = 10000

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i - 1))
        seg_start = i
segments.append((seg_start, len(rounds_info) - 1))

total_cost = 0
for idx, (s, e) in enumerate(segments):
    if s > e:
        continue
    tokens = [rounds_info[i]['total_tokens'] for i in range(s, e + 1)]
    writes, cost = dp_segment(tokens, system_len)
    total_cost += cost
    sorted_w = sorted(writes)
    if sorted_w:
        last_w = sorted_w[-1]
        n = len(tokens)
        print(f"Seg {idx}: {n} rounds, {len(sorted_w)} writes, last_write={last_w}/{n-1}, gap_to_end={n-1-last_w}, cost={cost/1e6:.4f}")
        print(f"  writes at: {sorted_w[:5]}...{sorted_w[-3:]}" if len(sorted_w) > 5 else f"  writes at: {sorted_w}")
    else:
        print(f"Seg {idx}: {n} rounds, 0 writes, cost={cost/1e6:.4f}")

print(f"\nTotal DP cost: {total_cost/1e6:.4f}")
print(f"+ output: {87006*4.8/1e6:.4f}")
print(f"= total: {(total_cost + 87006*4.8)/1e6:.4f}")
