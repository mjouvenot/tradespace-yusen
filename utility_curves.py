import numpy as np


def s_curve(x, slope, midpoint):
    y = 1 / (1 + np.exp(-slope * (x - midpoint)))
    return y


def linear(x):
    return x