import random

CACHED_RATE = 0.08
INPUT_RATE = 0.8
WRITE_RATE = 1.0

def precompute():
    rng = random.Random(114514)
    system_len = len("Example System Prompt" * 500)
    output_len = len("Example output of cache match")
    msg_lens = [system_len]
    rounds_info = []
    cumulative_tokens = []
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

rounds_info = precompute()
system_len = 10000

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i - 1))
        seg_start = i
segments.append((seg_start, len(rounds_info) - 1))

def dp_full_write(tokens):
    n = len(tokens)
    if n == 0:
        return 0
    INF = float('inf')
    dp = [INF] * n
    for w in range(n):
        cost = 0.0
        for i in range(w + 1):
            cost += system_len * CACHED_RATE + (tokens[i] - system_len) * INPUT_RATE
        cost += tokens[w] * WRITE_RATE
        dp[w] = cost
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
    no_write_total = sum(system_len * CACHED_RATE + (t - system_len) * INPUT_RATE for t in tokens)
    best = no_write_total
    for w in range(n):
        remaining = sum(tokens[w] * CACHED_RATE + (tokens[i] - tokens[w]) * INPUT_RATE for i in range(w + 1, n))
        if dp[w] + remaining < best:
            best = dp[w] + remaining
    return best

def dp_partial_write(tokens):
    n = len(tokens)
    if n == 0:
        return 0
    INF = float('inf')
    dp = {}
    for w in range(n):
        for frac in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            cached_len = int(tokens[w] * frac)
            if cached_len < system_len:
                cached_len = system_len
            cost = 0.0
            for i in range(w + 1):
                cost += system_len * CACHED_RATE + (tokens[i] - system_len) * INPUT_RATE
            cost += cached_len * WRITE_RATE
            key = (w, cached_len)
            if key not in dp or cost < dp[key]:
                dp[key] = cost
    for (w, cl) in sorted(dp.keys()):
        if dp[(w, cl)] == INF:
            continue
        for w2 in range(w + 1, n):
            for frac2 in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                cached_len2 = int(tokens[w2] * frac2)
                if cached_len2 < cl:
                    cached_len2 = cl
                cost = dp[(w, cl)]
                for i in range(w + 1, w2 + 1):
                    cost += cl * CACHED_RATE + (tokens[i] - cl) * INPUT_RATE
                cost += cached_len2 * WRITE_RATE
                key2 = (w2, cached_len2)
                if key2 not in dp or cost < dp[key2]:
                    dp[key2] = cost
    no_write_total = sum(system_len * CACHED_RATE + (t - system_len) * INPUT_RATE for t in tokens)
    best = no_write_total
    for (w, cl) in dp:
        remaining = sum(cl * CACHED_RATE + (tokens[i] - cl) * INPUT_RATE for i in range(w + 1, n))
        if dp[(w, cl)] + remaining < best:
            best = dp[(w, cl)] + remaining
    return best

total_full = 0
total_partial = 0
for idx, (s, e) in enumerate(segments[:3]):
    if s > e:
        continue
    tokens = [rounds_info[i]['total_tokens'] for i in range(s, e + 1)]
    cost_full = dp_full_write(tokens)
    cost_partial = dp_partial_write(tokens)
    total_full += cost_full
    total_partial += cost_partial
    print(f"Seg {idx}: full={cost_full/1e6:.4f}, partial={cost_partial/1e6:.4f}, diff={((cost_full-cost_partial)/1e6):.4f}")

print(f"\nTotal (first 3 segs): full={total_full/1e6:.4f}, partial={total_partial/1e6:.4f}")
