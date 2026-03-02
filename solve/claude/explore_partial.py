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
        rounds_info.append({'total': total, 'truncated': truncated, 'msg_count': len(msg_lens)})
        msg_lens.append(output_len)
    return rounds_info, system_len

def dp_segment_with_partial(tokens, system_len):
    n = len(tokens)
    if n == 0:
        return float('inf'), set()
    
    INF = float('inf')
    dp = [INF] * n
    dp_parent = [-2] * n
    dp_write_pos = [0] * n
    
    for w in range(n):
        cost = 0.0
        for i in range(w + 1):
            cost += system_len * CACHED_RATE + (tokens[i] - system_len) * INPUT_RATE
        cost += tokens[w] * WRITE_RATE
        dp[w] = cost
        dp_parent[w] = -1
        dp_write_pos[w] = w
    
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
    
    return best_cost, best_last

def dp_segment_partial_write(tokens, system_len):
    n = len(tokens)
    if n == 0:
        return float('inf'), set()
    
    INF = float('inf')
    best_cost_overall = INF
    best_writes = set()
    
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
            for write_level in [tokens[w2]]:
                cost = dp[w]
                for i in range(w + 1, w2 + 1):
                    cost += tokens[w] * CACHED_RATE + (tokens[i] - tokens[w]) * INPUT_RATE
                cost += write_level * WRITE_RATE
                
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
    
    return best_cost, best_last

rounds_info, system_len = precompute()

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i - 1))
        seg_start = i
segments.append((seg_start, len(rounds_info) - 1))

seg = segments[0]
tokens = [rounds_info[i]['total'] for i in range(seg[0], seg[1] + 1)]
print(f'Segment 0: {seg[0]}-{seg[1]}, len={len(tokens)}')
print(f'Tokens range: [{min(tokens)}, {max(tokens)}]')
print(f'System len: {system_len}')
print()

cost_normal, last_normal = dp_segment_with_partial(tokens, system_len)
print(f'Normal DP cost: {cost_normal:.2f}, last_write={last_normal}')

cost_partial, last_partial = dp_segment_partial_write(tokens, system_len)
print(f'Partial write DP cost: {cost_partial:.2f}, last_write={last_partial}')
