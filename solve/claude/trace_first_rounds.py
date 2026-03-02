import sys
sys.path.insert(0, '.')
from challenge import Message, Billing, ApiProvider, LlmApplication, token_count, is_content_equal, calculate_consumption
import copy
import random

random.seed(114514)

from solve.claude.solve import _rounds_info, _write_rounds

rng_main = random.Random(114514)
system_content = "Example System Prompt" * 500
history = [Message(role="system", content=system_content, savepoint=False)]

api = ApiProvider()

for round_idx in range(20):
    for _ in range(rng_main.randint(1, 3)):
        c = chr(rng_main.randint(32, 127))
        if rng_main.randint(1, 100) < 95:
            l = rng_main.randint(20, 100)
        else:
            l = rng_main.randint(500, 2000)
        history.append(Message(role="user", content=c * l, savepoint=False))
    
    if token_count(history) > 128 * 1024:
        n = len(history)
        cut = int(n * rng_main.randint(40, 60) / 100)
        history = history[0:1] + history[cut:]
    
    is_write = round_idx in _write_rounds
    print(f'Round {round_idx}: total={token_count(history)}, msgs={len(history)}, write={is_write}, caches_count={len(api.caches)}')
    
    history_copy = copy.deepcopy(history)
    for m in history_copy:
        m['savepoint'] = False
    
    history_copy[0]['savepoint'] = True
    if is_write:
        history_copy[-1]['savepoint'] = True
    
    result = api.chat_completion_raw(history_copy)
    print(f'  -> cache_write={result["cache_write_tokens"]}, cached={result["cached_input_tokens"]}, uncached={result["input_tokens"]}')
    
    history.append(Message(role="assistant", content=result["output"], savepoint=False))
