import random
import math

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

rounds_info = precompute()
system_len = 10000

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i - 1))
        seg_start = i
segments.append((seg_start, len(rounds_info) - 1))

for idx, (s, e) in enumerate(segments[:3]):
    tokens = [rounds_info[i]['total_tokens'] for i in range(s, e + 1)]
    n = len(tokens)
    deltas = [tokens[0] - system_len] + [tokens[i] - tokens[i-1] for i in range(1, n)]
    avg_delta = sum(deltas) / len(deltas)
    total_tokens_sum = sum(tokens)
    
    all_cached_cost = sum(t * 0.08 for t in tokens)
    
    min_uncached_per_write = 0
    
    print(f"Seg {idx}: {n} rounds")
    print(f"  avg delta per round: {avg_delta:.0f}")
    print(f"  all cached: {all_cached_cost/1e6:.4f}")
    
    for num_writes in [1, 5, 10, 20, 50, 100, n]:
        if num_writes > n:
            continue
        gap = n / num_writes
        write_cost = 0
        uncached_cost = 0
        cached_cost = 0
        last_write_tokens = system_len
        for i in range(n):
            write_idx = int(i / gap)
            if write_idx >= num_writes:
                write_idx = num_writes - 1
            next_write = int((write_idx + 1) * gap)
            if next_write > n:
                next_write = n
            
            is_write = (i > 0 and int((i-1)/gap) != int(i/gap)) or (i == 0 and num_writes > 0)
            if i == 0:
                cached_cost += system_len * 0.08
                uncached_cost += (tokens[i] - system_len) * 0.8
                if num_writes > 0:
                    write_cost += tokens[i] * 1.0
                    last_write_tokens = tokens[i]
            elif is_write:
                cached_cost += last_write_tokens * 0.08
                uncached_cost += (tokens[i] - last_write_tokens) * 0.8
                write_cost += tokens[i] * 1.0
                last_write_tokens = tokens[i]
            else:
                cached_cost += last_write_tokens * 0.08
                uncached_cost += (tokens[i] - last_write_tokens) * 0.8
        
        total = (write_cost + uncached_cost + cached_cost) / 1e6
        print(f"  {num_writes} writes: write={write_cost/1e6:.4f} uncached={uncached_cost/1e6:.4f} cached={cached_cost/1e6:.4f} total={total:.4f}")
