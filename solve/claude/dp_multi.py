import random

CACHED_RATE = 0.08
INPUT_RATE = 0.8
WRITE_RATE = 1.0
OUTPUT_RATE = 4.8

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

rounds_info = _precompute_simulation()
system_len = len("Example System Prompt" * 500)

seg_start = 0
seg_end = 434
tokens = [rounds_info[i]['total_tokens'] for i in range(seg_start, seg_end + 1)]
n = len(tokens)

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
        cost_normal = dp[w]
        for i in range(w + 1, w2 + 1):
            cost_normal += tokens[w] * CACHED_RATE + (tokens[i] - tokens[w]) * INPUT_RATE
        cost_normal += tokens[w2] * WRITE_RATE
        
        if cost_normal < dp[w2]:
            dp[w2] = cost_normal
            dp_parent[w2] = w

no_write_total = sum(system_len * CACHED_RATE + (t - system_len) * INPUT_RATE for t in tokens)
best_cost = no_write_total
best_last = -1
for w in range(n):
    remaining = sum(tokens[w] * CACHED_RATE + (tokens[i] - tokens[w]) * INPUT_RATE for i in range(w + 1, n))
    total_cost = dp[w] + remaining
    if total_cost < best_cost:
        best_cost = total_cost
        best_last = w

writes = []
cur = best_last
while cur >= 0:
    writes.append(cur)
    cur = dp_parent[cur]
writes.reverse()

print(f'Segment n={n}, writes={len(writes)}, dp_cost={best_cost/1e6:.4f}')
print(f'Write positions: {writes}')
print(f'Write gaps: {[writes[i+1]-writes[i] for i in range(len(writes)-1)]}')
print(f'Tokens at writes: {[tokens[w] for w in writes]}')

detailed_cost = 0.0
cached_at = system_len
for i in range(n):
    input_cost = cached_at * CACHED_RATE + (tokens[i] - cached_at) * INPUT_RATE
    write_cost = 0.0
    if i in set(writes):
        write_cost = tokens[i] * WRITE_RATE
        cached_at = tokens[i]
    detailed_cost += input_cost + write_cost

print(f'Detailed cost: {detailed_cost/1e6:.4f}')
print(f'All-cached cost: {sum(t * CACHED_RATE for t in tokens)/1e6:.4f}')

for i, w in enumerate(writes[:5]):
    uncached_before = tokens[w] - (tokens[writes[i-1]] if i > 0 else system_len)
    write_c = tokens[w] * WRITE_RATE
    if i < len(writes) - 1:
        next_w = writes[i + 1]
        savings_per_round = (tokens[w] - (tokens[writes[i-1]] if i > 0 else system_len)) * (INPUT_RATE - CACHED_RATE)
        rounds_until_next = next_w - w
        total_savings = savings_per_round * rounds_until_next
        print(f'  write {i} at round {w}: tokens={tokens[w]} write_cost={write_c} savings_per_round={savings_per_round:.0f} x {rounds_until_next} rounds = {total_savings:.0f} vs write_cost={write_c:.0f}')
