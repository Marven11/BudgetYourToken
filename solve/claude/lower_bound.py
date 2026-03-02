import random

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
        rounds_info.append({'total_tokens': total, 'truncated': truncated, 'new_tokens': sum(msg_lens) - (sum(msg_lens) - total) if not truncated else total})
        msg_lens.append(output_len)
    return rounds_info

rounds_info = _precompute()
system_len = len("Example System Prompt" * 500)
output_len = len("Example output of cache match")

cost_every_round_write = 0.0
prev_tokens = system_len
for i, r in enumerate(rounds_info):
    t = r['total_tokens']
    if r['truncated']:
        cost_every_round_write += system_len * CACHED_RATE + (t - system_len) * INPUT_RATE + t * WRITE_RATE
        prev_tokens = t
    else:
        cost_every_round_write += prev_tokens * CACHED_RATE + (t - prev_tokens) * INPUT_RATE + t * WRITE_RATE
        prev_tokens = t

cost_every_round_write += output_len * 3000 * OUTPUT_RATE

all_cached = sum(r['total_tokens'] * CACHED_RATE for r in rounds_info) + output_len * 3000 * OUTPUT_RATE

uncached_baseline = sum(r['total_tokens'] * INPUT_RATE for r in rounds_info) + output_len * 3000 * OUTPUT_RATE

print(f'Uncached baseline: {uncached_baseline/1e6:.4f}')
print(f'All cached (no write cost): {all_cached/1e6:.4f}')
print(f'Write every round: {cost_every_round_write/1e6:.4f}')
print(f'Write every round %: {cost_every_round_write/uncached_baseline*100:.2f}%')

total_write_cost = sum(r['total_tokens'] * WRITE_RATE for r in rounds_info)
print(f'Total write cost if write every round: {total_write_cost/1e6:.4f}')

cost_write_2 = 0.0
prev_tokens = system_len
for i, r in enumerate(rounds_info):
    t = r['total_tokens']
    if r['truncated']:
        cost_write_2 += system_len * CACHED_RATE + (t - system_len) * INPUT_RATE + t * WRITE_RATE
        prev_tokens = t
    else:
        cost_write_2 += prev_tokens * CACHED_RATE + (t - prev_tokens) * INPUT_RATE
        if i % 2 == 0:
            cost_write_2 += t * WRITE_RATE
            prev_tokens = t
cost_write_2 += output_len * 3000 * OUTPUT_RATE
print(f'Write every 2: {cost_write_2/1e6:.4f} ({cost_write_2/uncached_baseline*100:.2f}%)')

for gap in [1, 2, 3, 5, 10, 15, 20, 25, 30, 50]:
    cost = 0.0
    prev_t = system_len
    count_in_seg = 0
    for i, r in enumerate(rounds_info):
        t = r['total_tokens']
        if r['truncated']:
            cost += system_len * CACHED_RATE + (t - system_len) * INPUT_RATE + t * WRITE_RATE
            prev_t = t
            count_in_seg = 1
        else:
            cost += prev_t * CACHED_RATE + (t - prev_t) * INPUT_RATE
            count_in_seg += 1
            if count_in_seg % gap == 0:
                cost += t * WRITE_RATE
                prev_t = t
    cost += output_len * 3000 * OUTPUT_RATE
    print(f'gap={gap:3d}: {cost/1e6:.4f} ({cost/uncached_baseline*100:.2f}%)')
