_call_count = 0
_saved_length = None

def optimizer(history):
    global _call_count, _saved_length
    _call_count += 1
    
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    if len(history) > 10 and _call_count % 10 == 0:
        history[-1]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
