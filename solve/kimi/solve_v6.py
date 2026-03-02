def optimizer(history):
    for i, msg in enumerate(history):
        msg["savepoint"] = False
        if i == 0:
            msg["savepoint"] = True
        elif len(msg["content"]) < 50:
            msg["savepoint"] = True
    return history


def billing_watcher(x):
    pass
