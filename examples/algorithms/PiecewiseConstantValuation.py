from abc import ABC, abstractmethod
import numpy as np
from typing import *

from scipy import integrate


class Valuation(ABC):
    """
    An abstract class that describes a valuation of a cake.
    It can answer the standard "mark" and "eval" queries.
    """

    @abstractmethod
    def eval(self, start: float, end: float) -> float:
        """
        Answer an Eval query: return the value of the interval [start,end].
        :param start: Location on cake where the calculation starts.
        :param end:   Location on cake where the calculation ends.
        :return: Value of [start,end]
        """
        pass

    @abstractmethod
    def mark(self, start: float, targetValue: float) -> float:
        """
        Answer a Mark query: return "end" such that the value of the interval [start,end] is targetValue.
        :param start: Location on cake where the calculation starts.
        :param targetValue: required value for the piece [start,end]
        :return: the end of an interval with a value of targetValue.
        """
        pass

    @abstractmethod
    def total_value(self):
        """
        :return: the value of the entire cake for the agent.
        """
        pass

    @abstractmethod
    def cake_length(self):
        """
        :return: the total length of the cake that the agent cares about.
        """
        pass

    def value(self, piece: List[tuple]):
        """
        Evaluate a piece made of several intervals.
        :param piece: a list of tuples [(start1,end1), (start2,end2),...]
        :return:
        """
        if (piece == None):
            return 0
        return sum([self.eval(*interval) for interval in piece])

    def partition_values(self, partition: List[float]):
        """
        Evaluate all the pieces in the given partition.
        :param partition: a list of k cut-points [cut1,cut2,...]
        :return: a list of k+1 values: eval(0,cut1), eval(cut1,cut2), ...
        >>> a = PiecewiseConstantValuation([1,2,3,4])
        >>> a.partition_values([1,2])
        [1.0, 2.0, 7.0]
        >>> a.partition_values([3,3])
        [6.0, 0.0, 4.0]
        """
        values = []
        values.append(self.eval(0, partition[0]))
        for i in range(len(partition) - 1):
            values.append(self.eval(partition[i], partition[i + 1]))
        values.append(self.eval(partition[-1], self.cake_length()))
        return values


class PiecewiseConstantValuation(Valuation):
    """
    A PiecewiseConstantValuation is a valuation with a constant density on a finite number of intervals.
    >>> a = PiecewiseConstantValuation([11,22,33,44]) # Four desired intervals: the leftmost has value 11, the second one 22, etc.
    >>> a.total_value()
    110
    >>> a.cake_length()
    4
    >>> a.eval(1,3)
    55.0
    >>> a.mark(1, 77)
    3.5
    >>> a.value([(0,1),(2,3)])
    44.0
    """

    def __init__(self, values: list):
        self.values = np.array(values)
        self.length = len(values)
        self.total_value_cache = sum(values)

    def __repr__(self):
        return f"Piecewise-constant valuation with values {self.values} and total value={self.total_value_cache}"

    def total_value(self):
        return self.total_value_cache

    def cake_length(self):
        return self.length

    def eval(self, start: float, end: float):
        """
        Answer an Eval query: return the value of the interval [start,end].
        :param start: Location on cake where the calculation starts.
        :param end:   Location on cake where the calculation ends.
        :return: Value of [start,end]
        >>> a = PiecewiseConstantValuation([11,22,33,44])
        >>> a.eval(1,3)
        55.0
        >>> a.eval(1.5,3)
        44.0
        >>> a.eval(1,3.25)
        66.0
        >>> a.eval(1.5,3.25)
        55.0
        >>> a.eval(3,3)
        0.0
        >>> a.eval(3,7)
        44.0
        >>> a.eval(-1,7)
        110.0
        """
        # the cake to the left of 0 and to the right of length is considered worthless.
        start = max(0, min(start, self.length))
        end = max(0, min(end, self.length))
        if end <= start:
            return 0.0  # special case not covered by loop below

        fromFloor = int(np.floor(start))
        fromFraction = (fromFloor + 1 - start)
        toCeiling = int(np.ceil(end))
        toCeilingRemovedFraction = (toCeiling - end)

        val = 0.0
        val += (self.values[fromFloor] * fromFraction)
        val += self.values[fromFloor + 1:toCeiling].sum()
        val -= (self.values[toCeiling - 1] * toCeilingRemovedFraction)

        return val

    def mark(self, start: float, target_value: float):
        """
        Answer a Mark query: return "end" such that the value of the interval [start,end] is target_value.
        :param start: Location on cake where the calculation starts.
        :param targetValue: required value for the piece [start,end]
        :return: the end of an interval with a value of target_value.
        If the value is too high - returns None.
        >>> a = PiecewiseConstantValuation([11,22,33,44])
        >>> a.mark(1, 55)
        3.0
        >>> a.mark(1.5, 44)
        3.0
        >>> a.mark(1, 66)
        3.25
        >>> a.mark(1.5, 55)
        3.25
        >>> a.mark(1, 99)
        4.0
        >>> a.mark(1, 100)
        >>> a.mark(1, 0)
        1.0
        """
        # the cake to the left of 0 and to the right of length is considered worthless.
        start = max(0, start)
        if start >= self.length:
            return None  # value is too high

        if target_value < 0:
            raise ValueError("sum out of range (should be positive): {}".format(sum))

        start_floor = int(np.floor(start))
        if start_floor >= len(self.values):
            raise ValueError(
                "mark({},{}): start_floor ({}) is >= length of values ({})".format(start, target_value, start_floor,
                                                                                   self.values))

        start_fraction = (start_floor + 1 - start)

        value = self.values[start_floor]
        if value * start_fraction >= target_value:
            return start + (target_value / value)
        target_value -= (value * start_fraction)
        for i in range(start_floor + 1, self.length):
            value = self.values[i]
            if target_value <= value:
                return i + (target_value / value)
            target_value -= value

        # Value is too high: return None
        return None
