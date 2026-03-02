def optimizer(history):
    for i, msg in enumerate(history):
        msg["savepoint"] = (i == 0)
    return history


def billing_watcher(x):
    pass
