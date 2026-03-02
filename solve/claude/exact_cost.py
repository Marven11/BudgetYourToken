import random

CACHED_RATE = 0.08
INPUT_RATE = 0.8
WRITE_RATE = 1.0
OUTPUT_RATE = 4.8

def precompute():
    rng = random.Random(114514)
    system_len = len("Example System Prompt" * 500)
    output_len = len("Example output of cache match")
    output_nomatch_len = len("Example output of matching no cache")
    
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
    
    return rounds_info, system_len, output_len

def simulate_cost(rounds_info, write_rounds, system_len, output_len):
    segments = []
    seg_start = 0
    for i, r in enumerate(rounds_info):
        if r['truncated']:
            segments.append((seg_start, i - 1))
            seg_start = i
    segments.append((seg_start, len(rounds_info) - 1))
    
    total_write = 0
    total_cached = 0
    total_uncached = 0
    total_output = 0
    
    for seg_start_idx, seg_end_idx in segments:
        last_write = -1
        for i in range(seg_start_idx, seg_end_idx + 1):
            t = rounds_info[i]['total']
            
            if i in write_rounds:
                if last_write >= 0:
                    hit_tokens = rounds_info[last_write]['total']
                    total_cached += hit_tokens
                    total_uncached += t - hit_tokens
                else:
                    total_cached += system_len
                    total_uncached += t - system_len
                total_write += t
                last_write = i
            else:
                if last_write >= 0:
                    hit_tokens = rounds_info[last_write]['total']
                    total_cached += hit_tokens
                    total_uncached += t - hit_tokens
                else:
                    total_cached += system_len
                    total_uncached += t - system_len
            
            total_output += output_len
    
    cost = (total_write * WRITE_RATE + total_cached * CACHED_RATE + total_uncached * INPUT_RATE + total_output * OUTPUT_RATE) / 1_000_000
    return cost, total_write, total_cached, total_uncached, total_output

if __name__ == '__main__':
    rounds_info, system_len, output_len = precompute()
    
    import sys
    sys.path.insert(0, '.')
    from solve.claude.solve import _write_rounds
    cost, tw, tc, tu, to = simulate_cost(rounds_info, _write_rounds, system_len, output_len)
    print(f'Simulated cost: {cost:.2f}')
    print(f'write={tw/1e6:.2f}M cached={tc/1e6:.2f}M uncached={tu/1e6:.2f}M output={to/1e6:.2f}M')
    print(f'write_cost={tw*WRITE_RATE/1e6:.2f} cached_cost={tc*CACHED_RATE/1e6:.2f} uncached_cost={tu*INPUT_RATE/1e6:.2f} output_cost={to*OUTPUT_RATE/1e6:.2f}')
    print(f'Percentage: {cost / 226.12 * 100:.2f}%')
    
    print(f'\nWrite rounds: {len(_write_rounds)}')
    print(f'Sorted: {sorted(_write_rounds)[:20]}...')
