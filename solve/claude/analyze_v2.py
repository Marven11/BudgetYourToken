from challenge import Message, Billing
import random

def _precompute_simulation():
    rng = random.Random(114514)
    system_len = len("Example System Prompt" * 500)
    output_len = len("Example output of cache match")

    msg_lens = [system_len]
    rounds_info = []

    for round_idx in range(3000):
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
        segments.append((seg_start, i))
        seg_start = i + 1
segments.append((seg_start, len(rounds_info) - 1))

for seg_start, seg_end in segments:
    seg_tokens = [rounds_info[i]['total_tokens'] for i in range(seg_start, seg_end + 1)]
    seg_len = seg_end - seg_start + 1
    total_all = sum(seg_tokens)
    uncached_if_system_hit = sum(t - system_len for t in seg_tokens)
    cached_if_system_hit = system_len * seg_len
    no_cache_cost = total_all * 0.8 / 1e6
    system_only_cost = (cached_if_system_hit * 0.08 + uncached_if_system_hit * 0.8) / 1e6
    print(f'seg [{seg_start}-{seg_end}] len={seg_len} no_cache={no_cache_cost:.4f} sys_only={system_only_cost:.4f} savings={no_cache_cost - system_only_cost:.4f}')

total_uncached_cost = sum(r['total_tokens'] for r in rounds_info) * 0.8 / 1e6
print(f'\ntotal uncached cost: {total_uncached_cost:.2f}')

total_sys_cached = system_len * len(rounds_info)
total_uncached_remainder = sum(r['total_tokens'] - system_len for r in rounds_info)
sys_only_cost = (total_sys_cached * 0.08 + total_uncached_remainder * 0.8) / 1e6
print(f'system-only cache cost: {sys_only_cost:.4f}')
print(f'system cache savings: {total_uncached_cost - sys_only_cost:.4f}')
