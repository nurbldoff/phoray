from numpy import sqrt, where


def _quadratic(a, b, c):
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


def quadratic(a, b, c):
    """
    Solve a quadratic function a*x**2 + b*y + c = 0
    """
    delta = sqrt(b ** 2 - 4 * a * c)
    x1 = where(a == 0, -c / b, (-b + delta) / (2 * a))
    x2 = where(a == 0, x1, (-b - delta) / (2 * a))
    return (x1, x2)
