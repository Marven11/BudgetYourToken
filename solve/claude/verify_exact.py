import sys
sys.path.insert(0, '.')
from challenge import Message, Billing, LlmApplication
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

print(f"Total segments: {len(segments)}")
for idx, (s, e) in enumerate(segments):
    tokens = [rounds_info[i]['total_tokens'] for i in range(s, e + 1)]
    print(f"Seg {idx}: rounds {s}-{e}, len={e-s+1}, tokens[0]={tokens[0]}, tokens[-1]={tokens[-1]}")

total_cached_possible = sum(r['total_tokens'] for r in rounds_info)
print(f"\nTotal tokens across all rounds: {total_cached_possible}")
print(f"If all cached: {total_cached_possible * CACHED_RATE / 1e6:.2f} yuan")

output_tokens = 3000 * len("Example output of cache match")
first_no_cache = sum(r['total_tokens'] for r in rounds_info if r == rounds_info[0])
print(f"Output cost: {output_tokens * 4.8 / 1e6:.2f} yuan")
