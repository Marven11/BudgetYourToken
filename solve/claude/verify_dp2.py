import sys
sys.path.insert(0, '.')
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
        rounds_info.append({'total': total, 'truncated': truncated})
        msg_lens.append(output_len)
    return rounds_info, system_len

def exact_segment_cost(tokens, writes, system_len):
    n = len(tokens)
    writes_sorted = sorted(writes)
    cost = 0.0
    last_cache = -1
    last_cache_tokens = system_len
    
    for i in range(n):
        cost += last_cache_tokens * CACHED_RATE + (tokens[i] - last_cache_tokens) * INPUT_RATE
        if i in writes:
            cost += tokens[i] * WRITE_RATE
            last_cache = i
            last_cache_tokens = tokens[i]
    
    return cost

def dp_segment_optimal(tokens, system_len):
    n = len(tokens)
    if n == 0:
        return 0.0, set()
    
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
        return no_write_total, set()
    
    writes = set()
    cur = best_last
    while cur >= 0:
        writes.add(cur)
        cur = dp_parent[cur]
    
    verify_cost = exact_segment_cost(tokens, writes, system_len)
    if abs(verify_cost - best_cost) > 0.01:
        print(f'WARNING: DP cost {best_cost:.2f} != verify cost {verify_cost:.2f}')
    
    return best_cost, writes

rounds_info, system_len = precompute()

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i - 1))
        seg_start = i
segments.append((seg_start, len(rounds_info) - 1))

total_cost = 0.0
total_writes = 0
output_len = len("Example output of cache match")

for seg_idx, (seg_s, seg_e) in enumerate(segments):
    tokens = [rounds_info[i]['total'] for i in range(seg_s, seg_e + 1)]
    cost, writes = dp_segment_optimal(tokens, system_len)
    total_cost += cost
    total_writes += len(writes)
    
    if seg_idx < 5:
        print(f'Seg {seg_idx} [{seg_s}-{seg_e}] n={len(tokens)}: cost={cost/1e6:.4f}M, writes={len(writes)}, positions={sorted(writes)[:10]}...')

total_output_cost = 3000 * output_len * 4.8 / 1e6
total_cost_rmb = total_cost / 1e6 + total_output_cost
print(f'\nTotal input cost: {total_cost/1e6:.4f}')
print(f'Total output cost: {total_output_cost:.4f}')
print(f'Total: {total_cost_rmb:.2f}')
print(f'Percentage: {total_cost_rmb / 226.12 * 100:.2f}%')
print(f'Total writes: {total_writes}')
