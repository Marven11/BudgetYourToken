from challenge import Message, Billing, ApiProvider, token_count
import copy

api = ApiProvider()
system = Message(role="system", content="Example System Prompt" * 500, savepoint=False)

history1 = [
    copy.deepcopy(system),
    Message(role="user", content="hello", savepoint=False),
    Message(role="user", content="world", savepoint=False),
]
history1[0]["savepoint"] = True
history1[2]["savepoint"] = True

result1, _ = api.chat_completion(history1)
print(f"Call 1: {result1}")
print(f"Caches: {len(api.caches)}")

history2 = [
    copy.deepcopy(system),
    Message(role="user", content="different", savepoint=False),
    Message(role="user", content="messages", savepoint=False),
]
history2[0]["savepoint"] = True

result2, _ = api.chat_completion(history2)
print(f"Call 2 (sys prompt hit after 'truncation'): {result2}")
print(f"Caches: {len(api.caches)}")

history3 = [
    copy.deepcopy(system),
    Message(role="user", content="different", savepoint=False),
    Message(role="user", content="messages", savepoint=False),
    Message(role="user", content="more", savepoint=False),
]
history3[0]["savepoint"] = True

result3, _ = api.chat_completion(history3)
print(f"Call 3 (sys prompt hit, no cache for rest): {result3}")
