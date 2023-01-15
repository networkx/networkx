from abc import ABC, abstractmethod
import numpy as np
from typing import *


class Valuation(ABC):
    @abstractmethod
    def eval(self, start: float, end: float) -> float:
        pass

    @abstractmethod
    def mark(self, start: float, targetValue: float) -> float:
        pass

    @abstractmethod
    def total_value(self):
        pass

    @abstractmethod
    def cake_length(self):
        pass

    def value(self, piece: List[tuple]):
        if piece == None:
            return 0
        return sum([self.eval(*interval) for interval in piece])

    def partition_values(self, partition: List[float]):
        values = []
        values.append(self.eval(0, partition[0]))
        for i in range(len(partition) - 1):
            values.append(self.eval(partition[i], partition[i + 1]))
        values.append(self.eval(partition[-1], self.cake_length()))
        return values


class PiecewiseConstantValuation(Valuation):

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
        # the cake to the left of 0 and to the right of length is considered worthless.
        start = max(0, min(start, self.length))
        end = max(0, min(end, self.length))
        if end <= start:
            return 0.0  # special case not covered by loop below

        fromFloor = int(np.floor(start))
        fromFraction = fromFloor + 1 - start
        toCeiling = int(np.ceil(end))
        toCeilingRemovedFraction = toCeiling - end

        val = 0.0
        val += self.values[fromFloor] * fromFraction
        val += self.values[fromFloor + 1 : toCeiling].sum()
        val -= self.values[toCeiling - 1] * toCeilingRemovedFraction

        return val

    def mark(self, start: float, target_value: float):
        # the cake to the left of 0 and to the right of length is considered worthless.
        start = max(0, start)
        if start >= self.length:
            return None  # value is too high

        if target_value < 0:
            raise ValueError(f"sum out of range (should be positive): {sum}")
        start_floor = int(np.floor(start))
        if start_floor >= len(self.values):
            raise ValueError(
                "mark({},{}): start_floor ({}) is >= length of values ({})".format(
                    start, target_value, start_floor, self.values
                )
            )

        start_fraction = start_floor + 1 - start

        value = self.values[start_floor]
        if value * start_fraction >= target_value:
            return start + (target_value / value)
        target_value -= value * start_fraction
        for i in range(start_floor + 1, self.length):
            value = self.values[i]
            if target_value <= value:
                return i + (target_value / value)
            target_value -= value

        # Value is too high: return None
        return None
