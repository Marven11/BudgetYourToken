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

total_write_every = 0
total_cached_every = 0
total_uncached_every = 0

for s, e in segments:
    tokens = [rounds_info[i]['total_tokens'] for i in range(s, e + 1)]
    n = len(tokens)
    for i in range(n):
        total_write_every += tokens[i] * 1.0
        if i == 0:
            total_cached_every += system_len * 0.08
            total_uncached_every += (tokens[i] - system_len) * 0.8
        else:
            total_cached_every += tokens[i-1] * 0.08
            total_uncached_every += (tokens[i] - tokens[i-1]) * 0.8

print(f"Every round write:")
print(f"  write cost: {total_write_every/1e6:.4f}")
print(f"  cached cost: {total_cached_every/1e6:.4f}")
print(f"  uncached cost: {total_uncached_every/1e6:.4f}")
print(f"  total: {(total_write_every + total_cached_every + total_uncached_every)/1e6:.4f}")
print(f"  + output: {87006*4.8/1e6:.4f}")
print(f"  = total: {(total_write_every + total_cached_every + total_uncached_every + 87006*4.8)/1e6:.4f}")

total_no_write = 0
for s, e in segments:
    tokens = [rounds_info[i]['total_tokens'] for i in range(s, e + 1)]
    for t in tokens:
        total_no_write += system_len * 0.08 + (t - system_len) * 0.8

print(f"\nNo write at all:")
print(f"  total: {total_no_write/1e6:.4f}")
print(f"  + output: {87006*4.8/1e6:.4f}")
print(f"  = total: {(total_no_write + 87006*4.8)/1e6:.4f}")

all_cached = sum(r['total_tokens'] * 0.08 for r in rounds_info)
print(f"\nAll cached (theoretical min):")
print(f"  cached: {all_cached/1e6:.4f}")
print(f"  + output: {87006*4.8/1e6:.4f}")
print(f"  = total: {(all_cached + 87006*4.8)/1e6:.4f}")
