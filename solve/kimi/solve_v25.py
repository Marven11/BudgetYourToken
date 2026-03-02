_call_count = 0

def optimizer(history):
    global _call_count
    _call_count += 1
    
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    if _call_count % 50 == 0 and len(history) > 1:
        candidates = [(i, len(history[i]["content"])) for i in range(1, len(history))]
        candidates.sort(key=lambda x: x[1])
        for idx, _ in candidates[:1]:
            history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
