import random

def precompute():
    rng = random.Random(114514)
    system_len = len("Example System Prompt" * 500)
    output_len = len("Example output of cache match")
    msg_lens = [system_len]
    rounds_info = []
    all_msg_lens = []
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
        rounds_info.append({'total_tokens': total, 'truncated': truncated, 'n_msgs': len(msg_lens)})
        all_msg_lens.append(list(msg_lens))
        msg_lens.append(output_len)
    return rounds_info, all_msg_lens

rounds_info, all_msg_lens = precompute()

for seg_idx, r in enumerate(rounds_info[:5]):
    ml = all_msg_lens[seg_idx]
    cumsum = []
    s = 0
    for l in ml:
        s += l
        cumsum.append(s)
    total = cumsum[-1]
    n_msgs = len(ml)
    print(f"Round {seg_idx}: {n_msgs} msgs, total={total}")
    for frac in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        idx = int(n_msgs * frac) - 1
        if idx < 0: idx = 0
        if idx >= n_msgs: idx = n_msgs - 1
        prefix_tokens = cumsum[idx]
        write_cost = prefix_tokens * 1.0
        cached_benefit_per_round = (prefix_tokens * 0.08 + (total - prefix_tokens) * 0.8) - total * 0.8
        print(f"  frac={frac:.1f}: prefix={prefix_tokens}, write_cost={write_cost:.0f}, cached_benefit_per_round={cached_benefit_per_round:.0f}")
