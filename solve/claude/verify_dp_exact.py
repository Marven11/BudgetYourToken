import sys
sys.path.insert(0, '.')
from challenge import Message, Billing, LlmApplication, calculate_consumption
import random
import copy

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

from solve.claude.solve import _write_rounds

round_costs = []
prev_billing = Billing(cache_write_tokens=0, cached_input_tokens=0, input_tokens=0, output_tokens=0)

class Tracker:
    def __init__(self):
        self.billings = []
    def watch(self, b):
        self.billings.append(b.copy())

from solve.claude.solve import optimizer, billing_watcher, _state, State
import solve.claude.solve as sol
sol._state = State()

tracker = Tracker()
app = LlmApplication(optimizer, tracker.watch)
billing, consumption = app.run_application()

last_write = -1
last_write_tokens = system_len

for i in range(len(tracker.billings)):
    b = tracker.billings[i]
    if i == 0:
        prev = Billing(cache_write_tokens=0, cached_input_tokens=0, input_tokens=0, output_tokens=0)
    else:
        prev = tracker.billings[i-1]
    
    dw = b['cache_write_tokens'] - prev['cache_write_tokens']
    dc = b['cached_input_tokens'] - prev['cached_input_tokens']
    di = b['input_tokens'] - prev['input_tokens']
    
    is_write = i in _write_rounds
    is_trunc = rounds_info[i]['truncated']
    total = rounds_info[i]['total_tokens']
    
    if is_trunc or is_write or dc == 0:
        if i < 10 or is_trunc:
            print(f"Round {i}: trunc={is_trunc} write={is_write} dw={dw} dc={dc} di={di} total={total}")

print(f"\nFinal: {consumption:.2f} yuan, {consumption/calculate_consumption(Billing(cache_write_tokens=0,cached_input_tokens=0,input_tokens=billing['cached_input_tokens']+billing['input_tokens'],output_tokens=billing['output_tokens']))*100:.2f}%")
print(f"{billing=}")
