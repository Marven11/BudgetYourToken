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

for idx, (s, e) in enumerate(segments):
    tokens = [rounds_info[i]['total_tokens'] for i in range(s, e + 1)]
    n = len(tokens)
    total_all_cached = sum(t * 0.08 for t in tokens)
    total_no_cache = sum(system_len * 0.08 + (t - system_len) * 0.8 for t in tokens)
    print(f"Seg {idx}: rounds {s}-{e} ({n} rounds), tokens {tokens[0]}-{tokens[-1]}, all_cached={total_all_cached:.1f}, no_cache={total_no_cache:.1f}")

all_cached_total = sum(r['total_tokens'] * 0.08 for r in rounds_info)
print(f"\nAll cached total: {all_cached_total:.1f}")
print(f"Output cost: {87006 * 4.8:.1f}")
print(f"Theoretical min: {(all_cached_total + 87006 * 4.8) / 1_000_000:.2f}")
