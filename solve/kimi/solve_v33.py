def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    if len(history) > 1:
        recent_short = [(i, len(history[i]["content"])) for i in range(max(1, len(history)-3), len(history))]
        recent_short.sort(key=lambda x: x[1])
        if recent_short:
            history[recent_short[0][0]]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
