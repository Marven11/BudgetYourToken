import sys
sys.path.insert(0, '.')
import copy
import random
from challenge import Message, token_count
from solve.claude.solve import _write_rounds, _state, optimizer, _find_best_cache_hit_len, _msg_key

random.seed(114514)

system_content = "Example System Prompt" * 500
history = [Message(role="system", content=system_content, savepoint=False)]

rng = random.Random(114514)

for round_idx in range(20):
    for _ in range(rng.randint(1, 3)):
        c = chr(rng.randint(32, 127))
        if rng.randint(1, 100) < 95:
            l = rng.randint(20, 100)
        else:
            l = rng.randint(500, 2000)
        history.append(Message(role="user", content=c * l, savepoint=False))
    
    if token_count(history) > 128 * 1024:
        n = len(history)
        cut = int(n * rng.randint(40, 60) / 100)
        history = history[0:1] + history[cut:]
    
    h_copy = copy.deepcopy(history)
    optimized = optimizer(h_copy)
    
    sps = [i for i, m in enumerate(optimized) if m['savepoint']]
    is_write = round_idx in _write_rounds
    best_hit = _find_best_cache_hit_len(history)
    
    print(f'Round {round_idx}: msgs={len(history)}, write={is_write}, savepoints={sps}, best_hit_len={best_hit}, known_caches={len(_state.known_caches)}')
    
    if is_write:
        output = "Example output of cache match"
    else:
        output = "Example output of cache match"
    history.append(Message(role="assistant", content=output, savepoint=False))
