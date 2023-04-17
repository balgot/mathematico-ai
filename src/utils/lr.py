import matplotlib.pyplot as plt


def display_learning_rate(cls, steps, **params):
    scheduler = cls(**params)
    rl = []
    for _ in range(steps):
        rl.append(scheduler.get_last_lr())
        scheduler.step()
    return plt.plot(rl)
