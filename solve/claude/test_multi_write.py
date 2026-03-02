import sys
sys.path.insert(0, '.')
from challenge import Message, ApiProvider, token_count
import copy

api = ApiProvider()
sys_msg = Message(role='system', content='Example System Prompt' * 500, savepoint=False)

m1 = Message(role='user', content='A' * 100, savepoint=False)
m2 = Message(role='user', content='B' * 100, savepoint=False)
m3 = Message(role='user', content='C' * 100, savepoint=False)
m4 = Message(role='user', content='D' * 100, savepoint=False)

h1 = [copy.deepcopy(sys_msg), copy.deepcopy(m1), copy.deepcopy(m2)]
h1[0]['savepoint'] = True
h1[-1]['savepoint'] = True
r1 = api.chat_completion_raw(h1)
print(f'Call1 (write sys+AB): write={r1["cache_write_tokens"]}, cached={r1["cached_input_tokens"]}, input={r1["input_tokens"]}')

h2 = [copy.deepcopy(sys_msg), copy.deepcopy(m1), copy.deepcopy(m2), copy.deepcopy(m3)]
h2[1]['savepoint'] = True
h2[-1]['savepoint'] = True
r2 = api.chat_completion_raw(h2)
print(f'Call2 (write AB+ABC, hit sys): write={r2["cache_write_tokens"]}, cached={r2["cached_input_tokens"]}, input={r2["input_tokens"]}')
print(f'Caches: {len(api.caches)}')

h3 = [copy.deepcopy(sys_msg), copy.deepcopy(m1), copy.deepcopy(m2), copy.deepcopy(m3), copy.deepcopy(m4)]
h3[2]['savepoint'] = True
r3 = api.chat_completion_raw(h3)
print(f'Call3 (hit AB, no new write): write={r3["cache_write_tokens"]}, cached={r3["cached_input_tokens"]}, input={r3["input_tokens"]}')

h4 = [copy.deepcopy(sys_msg), copy.deepcopy(m1), copy.deepcopy(m2), copy.deepcopy(m3), copy.deepcopy(m4)]
h4[-1]['savepoint'] = True
r4 = api.chat_completion_raw(h4)
print(f'Call4 (hit ABC? write ABCD?): write={r4["cache_write_tokens"]}, cached={r4["cached_input_tokens"]}, input={r4["input_tokens"]}')
print(f'Caches: {len(api.caches)}')
