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
        rounds_info.append({'total': total, 'truncated': truncated})
        msg_lens.append(output_len)
    return rounds_info

rounds = precompute()
system_len = 10500

segments = []
seg_start = 0
for i, r in enumerate(rounds):
    if r['truncated']:
        segments.append((seg_start, i-1))
        seg_start = i
segments.append((seg_start, len(rounds)-1))

total_dp_cost = 0
total_every_round_cost = 0
total_sys_only_cost = 0

for s, e in segments:
    tokens = [rounds[i]['total'] for i in range(s, e+1)]
    n = len(tokens)
    
    sys_only = sum(system_len * 0.08 + (t - system_len) * 0.8 for t in tokens)
    
    every_round = 0
    for i in range(n):
        if i == 0:
            every_round += system_len * 0.08 + (tokens[i] - system_len) * 0.8
        else:
            every_round += tokens[i-1] * 0.08 + (tokens[i] - tokens[i-1]) * 0.8
        every_round += tokens[i] * 1.0
    
    every_round_no_last = 0
    for i in range(n):
        if i == 0:
            every_round_no_last += system_len * 0.08 + (tokens[i] - system_len) * 0.8
            every_round_no_last += tokens[i] * 1.0
        elif i == n - 1:
            every_round_no_last += tokens[i-1] * 0.08 + (tokens[i] - tokens[i-1]) * 0.8
        else:
            every_round_no_last += tokens[i-1] * 0.08 + (tokens[i] - tokens[i-1]) * 0.8
            every_round_no_last += tokens[i] * 1.0
    
    total_sys_only_cost += sys_only
    total_every_round_cost += every_round_no_last

print(f"Sys only (no writes): {total_sys_only_cost/1e6:.2f} yuan")
print(f"Every round write (skip last): {total_every_round_cost/1e6:.2f} yuan")

print(f"\n--- Breakdown per segment for every-round-write ---")
for s, e in segments:
    tokens = [rounds[i]['total'] for i in range(s, e+1)]
    n = len(tokens)
    
    write_cost = sum(tokens[i] * 1.0 for i in range(n-1))
    cached_cost = sum(tokens[i] * 0.08 for i in range(n-1))
    uncached_cost = sum((tokens[i+1] - tokens[i]) * 0.8 for i in range(n-1))
    first_round_cost = system_len * 0.08 + (tokens[0] - system_len) * 0.8 + tokens[0] * 1.0
    
    total = first_round_cost + cached_cost + uncached_cost + write_cost - tokens[0] * 1.0
    
    sys_only = sum(system_len * 0.08 + (t - system_len) * 0.8 for t in tokens)
    
    actual_every = 0
    for i in range(n):
        if i == 0:
            actual_every += system_len * 0.08 + (tokens[i] - system_len) * 0.8 + tokens[i] * 1.0
        elif i < n - 1:
            actual_every += tokens[i-1] * 0.08 + (tokens[i] - tokens[i-1]) * 0.8 + tokens[i] * 1.0
        else:
            actual_every += tokens[i-1] * 0.08 + (tokens[i] - tokens[i-1]) * 0.8
    
    print(f"Seg [{s},{e}] {n}r: sys_only={sys_only/1e6:.4f} every={actual_every/1e6:.4f} diff={actual_every/1e6 - sys_only/1e6:.4f}")

print(f"\n--- What if we write every K rounds? ---")
for K in [1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50]:
    total = 0
    for s, e in segments:
        tokens = [rounds[i]['total'] for i in range(s, e+1)]
        n = len(tokens)
        last_write = -1
        last_write_token = system_len
        seg_cost = 0
        for i in range(n):
            seg_cost += last_write_token * 0.08 + (tokens[i] - last_write_token) * 0.8
            if i - last_write < K and last_write >= 0:
                pass
            elif i < n - 1:
                seg_cost += tokens[i] * 1.0
                last_write = i
                last_write_token = tokens[i]
        total += seg_cost
    print(f"  K={K:3d}: {total/1e6:.2f} yuan = {total/1e6/226.12*100:.2f}%")
