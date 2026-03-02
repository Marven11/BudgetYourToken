from challenge import Message, Billing, ApiProvider, token_count
import copy

api = ApiProvider()
sys_msg = Message(role="system", content="Example System Prompt" * 500, savepoint=False)

h1 = [copy.deepcopy(sys_msg), Message(role="user", content="hello", savepoint=False)]
h1[0]["savepoint"] = True
result1 = api.chat_completion_raw(h1)
print(f"First call: write={result1['cache_write_tokens']}, cached={result1['cached_input_tokens']}, input={result1['input_tokens']}")

h2 = [copy.deepcopy(sys_msg), Message(role="user", content="world", savepoint=False)]
h2[0]["savepoint"] = True
result2 = api.chat_completion_raw(h2)
print(f"Second call (sys only): write={result2['cache_write_tokens']}, cached={result2['cached_input_tokens']}, input={result2['input_tokens']}")

h3 = [copy.deepcopy(sys_msg), Message(role="user", content="hello", savepoint=False), Message(role="user", content="extra", savepoint=False)]
h3[0]["savepoint"] = True
result3 = api.chat_completion_raw(h3)
print(f"Third call (sys only, more msgs): write={result3['cache_write_tokens']}, cached={result3['cached_input_tokens']}, input={result3['input_tokens']}")

print(f"\nCaches count: {len(api.caches)}")
for i, c in enumerate(api.caches):
    print(f"Cache {i}: len={len(c)}, tokens={token_count(c)}")
