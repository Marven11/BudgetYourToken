import random

rng = random.Random(114514)

system_content = "Example System Prompt" * 500
history_contents = [system_content]

output_match = "Example output of cache match"
output_nomatch = "Example output of matching no cache"

rounds_data = []

for round_idx in range(3000):
    num_new = rng.randint(1, 3)
    new_msgs = []
    for _ in range(num_new):
        c = chr(rng.randint(32, 127))
        if rng.randint(1, 100) < 95:
            content = c * rng.randint(20, 100)
        else:
            content = c * rng.randint(500, 2000)
        new_msgs.append(content)
    
    for c in new_msgs:
        history_contents.append(c)
    
    total = sum(len(c) for c in history_contents)
    truncated = False
    if total > 128 * 1024:
        n = len(history_contents)
        cut = int(n * rng.randint(40, 60) / 100)
        history_contents = [history_contents[0]] + history_contents[cut:]
        truncated = True
        total = sum(len(c) for c in history_contents)
    
    rounds_data.append({
        'round': round_idx,
        'num_messages': len(history_contents),
        'total_tokens': total,
        'truncated': truncated,
    })
    
    history_contents.append(output_match)

truncations = [r for r in rounds_data if r['truncated']]
print(f"Total truncations: {len(truncations)}")
for t in truncations:
    print(f"  Round {t['round']}: {t['num_messages']} msgs, {t['total_tokens']} tokens")

print(f"\nTotal rounds: {len(rounds_data)}")
print(f"Final messages: {rounds_data[-1]['num_messages']}")
print(f"Final tokens: {rounds_data[-1]['total_tokens']}")

segments = []
prev = -1
for t in truncations:
    segments.append((prev+1, t['round']))
    prev = t['round']
segments.append((prev+1, 2999))

print(f"\nSegments between truncations:")
for s, e in segments:
    seg_rounds = [rounds_data[i] for i in range(s, e+1)]
    tok_at_start = seg_rounds[0]['total_tokens']
    tok_at_end = seg_rounds[-1]['total_tokens']
    print(f"  Rounds {s}-{e} ({e-s+1} rounds): tokens {tok_at_start} -> {tok_at_end}")
