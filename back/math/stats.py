def moving_average(data, window=5):
    return sum(data[-window:]) / window

def exponential_smoothing(data, alpha=0.2):
    s = data[0]
    for x in data[1:]:
        s = alpha * x + (1 - alpha) * s
    return s

def linear_trend(data):
    n = len(data)
    x = range(n)
    x_mean = sum(x) / n
    y_mean = sum(data) / n

    num = sum((x[i] - x_mean) * (data[i] - y_mean) for i in range(n))
    den = sum((x[i] - x_mean) ** 2 for i in range(n))

    return num / den  # наклон линии
