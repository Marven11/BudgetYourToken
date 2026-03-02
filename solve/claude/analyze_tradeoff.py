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

for seg_idx, (seg_start, seg_end) in enumerate(segments[:3]):
    tokens = [rounds_info[i]['total_tokens'] for i in range(seg_start, seg_end + 1)]
    n = len(tokens)
    
    write_every_1 = 0.0
    cached_t = system_len
    for i in range(n):
        write_every_1 += cached_t * CACHED_RATE + (tokens[i] - cached_t) * INPUT_RATE + tokens[i] * WRITE_RATE
        cached_t = tokens[i]
    
    write_every_5 = 0.0
    cached_t = system_len
    for i in range(n):
        write_every_5 += cached_t * CACHED_RATE + (tokens[i] - cached_t) * INPUT_RATE
        if (i + 1) % 5 == 0 or i == n - 1:
            write_every_5 += tokens[i] * WRITE_RATE
            cached_t = tokens[i]
    
    no_write = 0.0
    for i in range(n):
        no_write += system_len * CACHED_RATE + (tokens[i] - system_len) * INPUT_RATE
    
    print(f'seg {seg_idx} [{seg_start}-{seg_end}] n={n}')
    print(f'  no_write={no_write/1e6:.4f} every_5={write_every_5/1e6:.4f} every_1={write_every_1/1e6:.4f}')
    
    for gap in [1, 2, 3, 5, 10, 20, 50]:
        cost = 0.0
        cached_t = system_len
        for i in range(n):
            cost += cached_t * CACHED_RATE + (tokens[i] - cached_t) * INPUT_RATE
            if (i + 1) % gap == 0:
                cost += tokens[i] * WRITE_RATE
                cached_t = tokens[i]
        print(f'  gap={gap:3d}: cost={cost/1e6:.6f}')
