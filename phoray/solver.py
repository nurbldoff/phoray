from numpy import sqrt


def quadratic(a, b, c):
    """
    Solve a quadratic function a*x**2 + b*y + c = 0
    """
    if a == 0.:
        x1 = -c / b
        return x1, x1
    delta = sqrt(b ** 2 - 4 * a * c)
    x1 = (-b + delta) / (2 * a)
    x2 = (-b - delta) / (2 * a)
    return (x1, x2)
