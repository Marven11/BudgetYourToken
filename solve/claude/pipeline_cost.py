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

cache_write = 0
cached = 0
uncached = 0
output = 0
output_len = len("Example output of cache match")

last_write_total = 0

for i, r in enumerate(rounds):
    t = r['total']
    if r['truncated']:
        last_write_total = 0
    
    output += output_len
    
    if last_write_total > 0:
        cached += last_write_total
        uncached += t - last_write_total
        cache_write += t
        last_write_total = t
    else:
        uncached += t
        cache_write += t
        last_write_total = t

total_cost = (cache_write * 1.0 + cached * 0.08 + uncached * 0.8 + output * 4.8) / 1_000_000
baseline = 226.12
print(f"Pipeline (write every round):")
print(f"  cache_write={cache_write/1e6:.2f}M, cached={cached/1e6:.2f}M, uncached={uncached/1e6:.2f}M, output={output/1e6:.2f}M")
print(f"  Cost: {total_cost:.2f} = {total_cost/baseline*100:.2f}%")
print(f"  Write cost: {cache_write*1.0/1e6:.2f}")
print(f"  Cached cost: {cached*0.08/1e6:.2f}")
print(f"  Uncached cost: {uncached*0.8/1e6:.2f}")
print(f"  Output cost: {output*4.8/1e6:.2f}")

print("\n--- Pipeline with gap ---")
for gap in [2, 3, 5, 10]:
    cache_write = 0
    cached = 0
    uncached = 0
    output = 0
    last_write_total = 0
    last_write_round = -999
    
    for i, r in enumerate(rounds):
        t = r['total']
        if r['truncated']:
            last_write_total = 0
            last_write_round = -999
        
        output += output_len
        
        if last_write_total > 0:
            cached += last_write_total
            uncached += t - last_write_total
        else:
            uncached += t
        
        if i - last_write_round >= gap:
            cache_write += t
            last_write_total = t
            last_write_round = i
    
    total_cost = (cache_write * 1.0 + cached * 0.08 + uncached * 0.8 + output * 4.8) / 1_000_000
    print(f"  Gap={gap}: cost={total_cost:.2f} = {total_cost/baseline*100:.2f}%, write={cache_write/1e6:.2f}M, cached={cached/1e6:.2f}M, uncached={uncached/1e6:.2f}M")

print("\n--- Key insight: multi-savepoint pipeline ---")
print("In one call: hit old cache at position A, write new cache at end B")
print("Result: cached=A, uncached=B-A, write=B")
print("Next call: hit B (now cached), write new end C")
print("Result: cached=B, uncached=C-B, write=C")
print("This means: every round we pay write=total but get cached on prev total")
print("vs DP: we skip writing for many rounds, paying uncached for entire total")

print("\n--- Comparison: write-2 pipeline vs no-write ---")
for seg_idx in range(3):
    seg_rounds = []
    seg_start = None
    seg_i = 0
    for i, r in enumerate(rounds):
        if r['truncated']:
            if seg_i == seg_idx:
                break
            seg_i += 1
            seg_start = i
            seg_rounds = []
        elif seg_start is not None or seg_i == 0:
            seg_rounds.append(r)
    
    if not seg_rounds:
        continue
    
    tokens = [r['total'] for r in seg_rounds]
    n = len(tokens)
    sys_len = 10500
    
    no_write_cost = sum(sys_len * 0.08 + (t - sys_len) * 0.8 for t in tokens)
    
    pipeline_write = sum(tokens)
    pipeline_cached = sum(tokens[i-1] for i in range(1, n))
    pipeline_uncached = sum(tokens[i] - tokens[i-1] for i in range(1, n)) + tokens[0]
    pipeline_cost = pipeline_write * 1.0 + pipeline_cached * 0.08 + pipeline_uncached * 0.8
    
    print(f"\nSegment {seg_idx}: {n} rounds, tokens {tokens[0]}-{tokens[-1]}")
    print(f"  No write: {no_write_cost/1e6:.4f}M RMB")
    print(f"  Pipeline: {pipeline_cost/1e6:.4f}M RMB (write={pipeline_write/1e6:.2f}M)")
    print(f"  Pipeline saves: {(no_write_cost - pipeline_cost)/1e6:.4f}M RMB")
