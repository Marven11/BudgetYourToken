def optimizer(history):
    for i, msg in enumerate(history):
        msg["savepoint"] = False
    
    user_indices = [i for i, msg in enumerate(history) if msg["role"] == "user"]
    
    for idx in user_indices[-4:]:
        history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
