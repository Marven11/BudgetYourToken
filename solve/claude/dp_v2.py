import random
import time

CACHED_RATE = 0.08
INPUT_RATE = 0.8
WRITE_RATE = 1.0
OUTPUT_RATE = 4.8

def _precompute():
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

rounds_info = _precompute()
system_len = len("Example System Prompt" * 500)

seg_start = 0
seg_end = 434
tokens = [rounds_info[i]['total_tokens'] for i in range(seg_start, seg_end + 1)]
n = len(tokens)

all_levels = sorted(set([system_len] + tokens))
level_idx = {v: i for i, v in enumerate(all_levels)}

INF = float('inf')

dp_old = {system_len: 0.0}

start = time.time()
write_decisions = [{} for _ in range(n)]

for i in range(n):
    t = tokens[i]
    dp_new = {}
    
    for cached_level, prev_cost in dp_old.items():
        round_input_cost = cached_level * CACHED_RATE + (t - cached_level) * INPUT_RATE
        
        no_write_cost = prev_cost + round_input_cost
        if cached_level not in dp_new or no_write_cost < dp_new[cached_level]:
            dp_new[cached_level] = no_write_cost
            write_decisions[i][cached_level] = (cached_level, False)
        
        write_at_end_cost = prev_cost + round_input_cost + t * WRITE_RATE
        if t not in dp_new or write_at_end_cost < dp_new[t]:
            dp_new[t] = write_at_end_cost
            write_decisions[i][t] = (cached_level, True)
    
    dp_old = dp_new
    
    if i % 100 == 0:
        elapsed = time.time() - start
        print(f'Round {i}/{n}: {len(dp_old)} states, elapsed={elapsed:.1f}s')

best_level = min(dp_old, key=dp_old.get)
best_cost = dp_old[best_level]

remaining = 0.0
for i in range(seg_end - seg_start + 1, n):
    remaining += best_level * CACHED_RATE + (tokens[i] - best_level) * INPUT_RATE

print(f'Best cost for segment: {best_cost/1e6:.4f}')
print(f'Best final cache level: {best_level}')
print(f'States explored: {len(dp_old)}')

old_dp_cost = 4.1229
print(f'Old DP cost: {old_dp_cost:.4f}')
print(f'Improvement: {(old_dp_cost - best_cost/1e6):.4f}')
