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
        rounds_info.append({'total': total, 'truncated': truncated})
        msg_lens.append(output_len)
    return rounds_info

rounds = precompute()
system_len = 10500

segments = []
seg_start = 0
for i, r in enumerate(rounds):
    if r['truncated']:
        segments.append((seg_start, i-1))
        seg_start = i
segments.append((seg_start, len(rounds)-1))

for s, e in segments:
    tokens = [rounds[i]['total'] for i in range(s, e+1)]
    n = len(tokens)
    
    no_cache_cost = sum(t * 0.8 for t in tokens)
    sys_cache_cost = sum(system_len * 0.08 + (t - system_len) * 0.8 for t in tokens)
    
    saving_per_round = system_len * (0.8 - 0.08)
    total_saving = saving_per_round * n
    
    print(f"Seg [{s},{e}] {n}r: no_cache={no_cache_cost/1e6:.4f} sys_cache={sys_cache_cost/1e6:.4f} save={total_saving/1e6:.4f}")

total_sys_saving = sum(
    system_len * (0.8 - 0.08) * (e - s + 1)
    for s, e in segments
) / 1e6
print(f"\nTotal system prompt cache saving: {total_sys_saving:.4f}M RMB = {total_sys_saving:.2f} yuan")
print(f"That's {total_sys_saving/226.12*100:.2f}% of baseline")

print(f"\n--- Current DP scheme already accounts for sys prompt cache ---")
print(f"The DP uses sys_len*CACHED_RATE for cached portion")
print(f"So system prompt cache saving is already included in the 17.68%")

print(f"\n--- What if we could cache MORE across truncations? ---")
print(f"After truncation: history = [sys_prompt] + history[cut:]")
print(f"The history[cut:] messages are a SUFFIX of the old history")
print(f"If we had cached [sys_prompt] + some_suffix before...")
print(f"But the suffix after truncation won't match any old prefix.")

print(f"\n--- What about caching intermediate prefixes? ---")
print(f"If we cache history[:k] for various k values,")
print(f"after truncation the new history won't match any of them")
print(f"(because truncation removes middle messages, not end).")
print(f"So cross-truncation caching only works for system prompt.")

print(f"\n--- Real question: can we do better WITHIN a segment? ---")
print(f"Within a segment, messages grow monotonically.")
print(f"DP already finds optimal write points.")
print(f"The only room is if multi-savepoint gives some advantage.")

print(f"\n--- Multi-savepoint test ---")
print(f"In one call with savepoints at positions A < B:")
print(f"  Scan from end: B not cached -> write B (cost=token[:B+1])")
print(f"  Continue: A cached -> hit A (cached=token[:A+1], uncached=token[A+1:])")
print(f"  Total: write=token[:B+1], cached=token[:A+1], uncached=token[A+1:]")
print(f"")
print(f"vs single savepoint at A only:")
print(f"  cached=token[:A+1], uncached=token[A+1:]")
print(f"  Total: cached=token[:A+1], uncached=token[A+1:]")
print(f"")
print(f"Difference: extra write=token[:B+1] for multi-savepoint")
print(f"Benefit: B is now cached for next round")
print(f"So multi-savepoint = writing for free while still hitting old cache!")
print(f"Wait... it's NOT free, we pay cache_write_tokens for B")
print(f"But we DON'T lose the cache hit on A!")
print(f"")
print(f"So the tradeoff is:")
print(f"  Cost now: +write(B)")
print(f"  Benefit later: can hit B instead of A, saving (B-A)*0.72 per round")
print(f"  Break-even: write(B) / ((B-A)*0.72) rounds")

for s, e in segments[:3]:
    tokens = [rounds[i]['total'] for i in range(s, e+1)]
    n = len(tokens)
    if n < 5:
        continue
    print(f"\nSegment [{s},{e}]: {n} rounds")
    for gap in range(1, min(6, n)):
        write_cost = tokens[gap] * 1.0
        benefit_per_round = (tokens[gap] - system_len) * 0.72
        remaining = n - gap - 1
        total_benefit = benefit_per_round * remaining
        net = total_benefit - write_cost
        print(f"  Write at round {gap}: cost={write_cost/1e6:.4f}, benefit={total_benefit/1e6:.4f}, net={net/1e6:.4f}")
