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

rounds_info, system_len = precompute()

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i - 1))
        seg_start = i
segments.append((seg_start, len(rounds_info) - 1))

total_all_cached_cost = 0.0
total_all_uncached_cost = 0.0

for seg_s, seg_e in segments:
    tokens = [rounds_info[i]['total'] for i in range(seg_s, seg_e + 1)]
    n = len(tokens)
    
    for t in tokens:
        total_all_cached_cost += t * CACHED_RATE
        total_all_uncached_cost += t * INPUT_RATE

print(f'If all cached: {total_all_cached_cost / 1e6:.2f}')
print(f'If all uncached: {total_all_uncached_cost / 1e6:.2f}')
print(f'Saving per token cached: {INPUT_RATE - CACHED_RATE} = {INPUT_RATE - CACHED_RATE}')
print(f'Write cost per token: {WRITE_RATE}')
print()

for seg_idx, (seg_s, seg_e) in enumerate(segments[:3]):
    tokens = [rounds_info[i]['total'] for i in range(seg_s, seg_e + 1)]
    n = len(tokens)
    
    print(f'\nSegment {seg_idx} [{seg_s}-{seg_e}] len={n}')
    
    for gap in [10, 20, 30, 40, 50]:
        write_cost = 0.0
        save_cost = 0.0
        for i in range(n):
            if i > 0 and i % gap == 0:
                last_write_idx = i
                write_cost += tokens[i] * WRITE_RATE
            else:
                last_write_idx_actual = (i // gap) * gap if i >= gap else -1
                if last_write_idx_actual >= 0 and last_write_idx_actual < n:
                    cached_tokens = tokens[last_write_idx_actual]
                    save_cost += (cached_tokens - system_len) * (INPUT_RATE - CACHED_RATE)
        
        print(f'  gap={gap}: write_cost={write_cost/1e6:.4f}, save_cost={save_cost/1e6:.4f}, net={(-write_cost+save_cost)/1e6:.4f}')

print('\n--- Analyzing write breakeven ---')
for seg_idx, (seg_s, seg_e) in enumerate(segments[:5]):
    tokens = [rounds_info[i]['total'] for i in range(seg_s, seg_e + 1)]
    n = len(tokens)
    
    total_tokens_sum = sum(tokens)
    avg_token = total_tokens_sum / n
    
    breakeven_rounds = avg_token * WRITE_RATE / (avg_token * (INPUT_RATE - CACHED_RATE))
    
    print(f'Seg {seg_idx}: n={n}, avg_token={avg_token:.0f}, breakeven_rounds={breakeven_rounds:.1f}')
    print(f'  Write cost of avg: {avg_token * WRITE_RATE:.0f}')
    print(f'  Per-round saving: {avg_token * (INPUT_RATE - CACHED_RATE):.0f}')
