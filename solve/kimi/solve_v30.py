def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    user_msgs = [(i, len(history[i]["content"])) for i, msg in enumerate(history) if msg["role"] == "user" and i > 0]
    if user_msgs:
        user_msgs.sort(key=lambda x: x[1])
        history[user_msgs[0][0]]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
