def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    user_indices = [i for i, msg in enumerate(history) if msg["role"] == "user"]
    short_users = [(i, len(history[i]["content"])) for i in user_indices]
    short_users.sort(key=lambda x: x[1])
    
    for idx, _ in short_users[:3]:
        history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
