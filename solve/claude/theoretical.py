import sys
sys.path.insert(0, '.')
import random

CACHED_RATE = 0.08
INPUT_RATE = 0.8
WRITE_RATE = 1.0
OUTPUT_RATE = 4.8

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
    return rounds_info, system_len, output_len

rounds_info, system_len, output_len = precompute()

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i - 1))
        seg_start = i
segments.append((seg_start, len(rounds_info) - 1))

for gap in [1, 2, 3, 5, 10, 20, 30]:
    total_write = 0
    total_cached = 0
    total_uncached = 0
    
    for seg_s, seg_e in segments:
        last_write_tokens = system_len
        for idx, i in enumerate(range(seg_s, seg_e + 1)):
            t = rounds_info[i]['total']
            total_cached += last_write_tokens
            total_uncached += t - last_write_tokens
            
            if idx % gap == 0:
                total_write += t
                last_write_tokens = t
    
    cost = (total_write * WRITE_RATE + total_cached * CACHED_RATE + total_uncached * INPUT_RATE + 3000 * output_len * OUTPUT_RATE) / 1e6
    print(f'gap={gap:3d}: write={total_write*WRITE_RATE/1e6:.2f} cached={total_cached*CACHED_RATE/1e6:.2f} uncached={total_uncached*INPUT_RATE/1e6:.2f} total={cost:.2f} ({cost/226.12*100:.2f}%)')

print(f'\nDP result: 40.02 (17.70%)')
print(f'All cached: {(sum(r["total"] for r in rounds_info) * CACHED_RATE + 3000 * output_len * OUTPUT_RATE) / 1e6:.2f}')

print('\n--- What if we could write just the delta? ---')
for gap in [1, 2, 3, 5]:
    total_write = 0
    total_cached = 0
    total_uncached = 0
    
    for seg_s, seg_e in segments:
        last_write_tokens = system_len
        for idx, i in enumerate(range(seg_s, seg_e + 1)):
            t = rounds_info[i]['total']
            total_cached += last_write_tokens
            total_uncached += t - last_write_tokens
            
            if idx % gap == 0:
                total_write += t - last_write_tokens
                last_write_tokens = t
    
    cost = (total_write * WRITE_RATE + total_cached * CACHED_RATE + total_uncached * INPUT_RATE + 3000 * output_len * OUTPUT_RATE) / 1e6
    print(f'gap={gap:3d} (delta write): write={total_write*WRITE_RATE/1e6:.2f} cached={total_cached*CACHED_RATE/1e6:.2f} uncached={total_uncached*INPUT_RATE/1e6:.2f} total={cost:.2f} ({cost/226.12*100:.2f}%)')
