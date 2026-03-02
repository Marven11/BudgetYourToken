import random

def precompute():
    rng = random.Random(114514)
    system_len = len("Example System Prompt" * 500)
    output_len = len("Example output of cache match")
    msg_lens = [system_len]
    rounds_info = []
    for _ in range(3000):
        num_new = rng.randint(1, 3)
        new_lens = []
        for _ in range(num_new):
            c = chr(rng.randint(32, 127))
            if rng.randint(1, 100) < 95:
                l = rng.randint(20, 100)
            else:
                l = rng.randint(500, 2000)
            new_lens.append(l)
            msg_lens.append(l)
        total = sum(msg_lens)
        truncated = False
        if total > 128 * 1024:
            n = len(msg_lens)
            cut = int(n * rng.randint(40, 60) / 100)
            msg_lens = [msg_lens[0]] + msg_lens[cut:]
            truncated = True
            total = sum(msg_lens)
        rounds_info.append({
            'total_tokens': total,
            'truncated': truncated,
            'num_msgs': len(msg_lens),
            'new_lens': new_lens,
        })
        msg_lens.append(output_len)
    return rounds_info

rounds_info = precompute()
system_len = len("Example System Prompt" * 500)
output_len = len("Example output of cache match")

for i in range(min(20, len(rounds_info))):
    r = rounds_info[i]
    print(f"Round {i}: total={r['total_tokens']}, msgs={r['num_msgs']}, new_lens={r['new_lens']}, trunc={r['truncated']}")

print(f"\nSystem len: {system_len}")
print(f"Output len: {output_len}")

tokens_per_round = []
for i, r in enumerate(rounds_info):
    if i == 0:
        tokens_per_round.append(r['total_tokens'])
    elif r['truncated']:
        tokens_per_round.append(r['total_tokens'])
    else:
        added = r['total_tokens'] - rounds_info[i-1]['total_tokens'] - output_len
        tokens_per_round.append(added)

print(f"\nAvg new tokens per round: {sum(tokens_per_round)/len(tokens_per_round):.1f}")
print(f"Min: {min(tokens_per_round)}, Max: {max(tokens_per_round)}")

segments = []
seg_start = 0
for i, r in enumerate(rounds_info):
    if r['truncated']:
        segments.append((seg_start, i-1))
        seg_start = i
segments.append((seg_start, len(rounds_info)-1))

print(f"\nSegments: {len(segments)}")
for s, e in segments:
    print(f"  [{s}, {e}]: {e-s+1} rounds, start_tokens={rounds_info[s]['total_tokens']}, end_tokens={rounds_info[e]['total_tokens']}")

print("\n--- Multi-savepoint analysis ---")
print("If we write at round i with N messages, we could potentially")
print("set savepoints at intermediate positions within one call.")
print("Each intermediate savepoint at position j < n-1 writes history[:j+1]")
print("and can be hit by a future call with matching prefix.")

print("\n--- Prefix token counts for round 0 ---")
r = rounds_info[0]
print(f"Total: {r['total_tokens']}, msgs: {r['num_msgs']}")
