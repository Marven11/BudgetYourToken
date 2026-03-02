def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    if len(history) > 1:
        history[-1]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
