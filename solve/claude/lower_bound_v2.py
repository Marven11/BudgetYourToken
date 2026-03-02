import sys
sys.path.insert(0, '.')
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

rounds_info = _precompute_simulation()
system_len = len("Example System Prompt" * 500)

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i - 1))
        seg_start = i
segments.append((seg_start, len(rounds_info) - 1))

total_dp_cost = 0.0
total_all_cached_cost = 0.0
total_no_write_cost = 0.0

for seg_idx, (s, e) in enumerate(segments):
    tokens = [rounds_info[i]['total_tokens'] for i in range(s, e + 1)]
    n = len(tokens)
    
    all_cached = sum(t * CACHED_RATE for t in tokens)
    total_all_cached_cost += all_cached
    
    no_write = sum(system_len * CACHED_RATE + (t - system_len) * INPUT_RATE for t in tokens)
    total_no_write_cost += no_write
    
    from solve.claude.solve import _dp_segment
    writes = _dp_segment(tokens, system_len)
    
    dp_cost = 0.0
    last_hit = system_len
    sorted_writes = sorted(writes)
    
    for i in range(n):
        if i in writes:
            dp_cost += last_hit * CACHED_RATE + (tokens[i] - last_hit) * INPUT_RATE + tokens[i] * WRITE_RATE
            last_hit = tokens[i]
        else:
            dp_cost += last_hit * CACHED_RATE + (tokens[i] - last_hit) * INPUT_RATE
    
    total_dp_cost += dp_cost
    
    write_cost_in_seg = sum(tokens[w] * WRITE_RATE for w in writes)
    uncached_in_seg = dp_cost - all_cached - write_cost_in_seg
    
    print(f"Seg {seg_idx} [{s}-{e}] n={n}: dp={dp_cost/1e6:.4f} all_cached={all_cached/1e6:.4f} no_write={no_write/1e6:.4f} writes={len(writes)} write_cost={write_cost_in_seg/1e6:.4f}")

output_cost = 3000 * len("Example output of cache match") * 4.8 / 1e6
print(f"\nTotal DP cost: {total_dp_cost/1e6:.4f} yuan + output {output_cost:.4f} = {total_dp_cost/1e6 + output_cost:.4f}")
print(f"Total all_cached: {total_all_cached_cost/1e6:.4f} yuan + output {output_cost:.4f} = {total_all_cached_cost/1e6 + output_cost:.4f}")
print(f"Total no_write: {total_no_write_cost/1e6:.4f} yuan + output {output_cost:.4f} = {total_no_write_cost/1e6 + output_cost:.4f}")
print(f"\nGap from theoretical: {(total_dp_cost - total_all_cached_cost)/1e6:.4f} yuan")
print(f"  = write_costs + extra_uncached")

total_write_cost = 0
total_uncached_gap = 0
for seg_idx, (s, e) in enumerate(segments):
    tokens = [rounds_info[i]['total_tokens'] for i in range(s, e + 1)]
    n = len(tokens)
    writes = _dp_segment(tokens, system_len)
    
    last_hit = system_len
    for i in range(n):
        if i in writes:
            total_uncached_gap += (tokens[i] - last_hit) * (INPUT_RATE - CACHED_RATE)
            total_write_cost += tokens[i] * WRITE_RATE
            last_hit = tokens[i]
        else:
            total_uncached_gap += (tokens[i] - last_hit) * (INPUT_RATE - CACHED_RATE)

print(f"  write_costs = {total_write_cost/1e6:.4f}")
print(f"  uncached_gap = {total_uncached_gap/1e6:.4f}")
print(f"  sum = {(total_write_cost + total_uncached_gap)/1e6:.4f}")
