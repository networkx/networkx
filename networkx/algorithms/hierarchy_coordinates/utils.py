"""
Utilities for hierarchy coordinates
"""
import numpy as np

__all__ = ["distribute", "matrix_normalize"]


def distribute(n, end_value_range=None, dist=1, sampled_range_of_dist=(0, 1)):
    """Returns n floats distributed as within the sampled range of provided distribution, rescaled to end_value_range
    Defaults to an exponential distribution e^x, x = (0, 1), where int/float values of dist modify the coefficient on x

    Parameters
    ----------
    n : int
        Number of exponentially distributed points returned
    end_value_range : tuple, optional
        Range which final values of the distributed points occupy.
        Defaults to the distribution's native range
    dist : float, default: 1
       A in np.exp(A*x)
    dist: overloaded: types.FunctionType, optional
        Alternate distribution yielding single samples from 1d input
    sampled_range_of_dist: tuple, default: (0, 1)
        Range of distribution sampled

    Returns
    -------
    pts: numpy array
        numpy array of n floats

    Examples
    --------
    n, Max, Min = 100, 10, -10
    exp_dist_0 = hc.distribute(n=n, end_value_range=(Min, Max))
    exp_dist_1 = hc.distribute(n=n, dist=-2, end_value_range=(Min, Max), sampled_range_of_dist=(1, 2))

    dist = lambda x: 4*x*x - 3*x*x*x
    parabolic_dist = hc.distribute(n=n, dist=dist, end_value_range=(Min, Max), sampled_range_of_dist=(0, 2))

    # Visualization of sampling
    plt.xlabel('# samples')
    plt.ylabel('sampled value')
    plt.plot(exp_dist_0, label='e^x: (0, 1)')
    plt.plot(exp_dist_1, label='e^-2x: (1, 2)')
    plt.plot(parabolic_dist, label='4x^2 - 3x^3: (0, 2)')
    plt.legend()
    plt.show()
    """
    if isinstance(dist, float) or isinstance(dist, int):
        distribution = lambda x: np.exp(dist * x)
    else:
        distribution = dist

    x_increment = np.abs(max(sampled_range_of_dist) - min(sampled_range_of_dist)) / n
    pts = np.array([distribution(x_increment * i) for i in range(n)])
    pts /= abs(max(pts) - min(pts))

    if end_value_range is not None:
        pts = pts * (max(end_value_range) - min(end_value_range)) + min(end_value_range)
    return pts


def matrix_normalize(matrix, row_normalize=False):
    """normalizes 2d matrices.

    Parameters
    ----------
    matrix: square 2d numpy array, nested list,
        matrix to be normalized
    row_normalize: bool
        normalizes row *instead* of default columns if True

    Returns
    -------
    numpy array:
        column or row normalized array

    Examples
    --------
    a = np.repeat(np.arange(1, 5), 4).reshape(4, 4)
    print(a)
    print(np.round(hc.matrix_normalize(a), 2))
    print(np.round(hc.matrix_normalize(a, row_normalize=True), 2))

    Notes
    -----
    Should be replaced with appropriate generalized, efficient version
    """

    if row_normalize:
        row_sums = matrix.sum(axis=1)
        return np.array(
            [
                matrix[index, :] / row_sums[index]
                if row_sums[index] != 0
                else [0] * row_sums.size
                for index in range(row_sums.size)
            ]
        )
    else:
        column_sums = matrix.sum(axis=0)
        return np.array(
            [
                matrix[:, index] / column_sums[index]
                if column_sums[index] != 0
                else [0] * column_sums.size
                for index in range(column_sums.size)
            ]
        ).T
