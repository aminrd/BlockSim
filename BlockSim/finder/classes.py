import statistics


def custom_mean(arr):
    if len(arr) < 1:
        return 0
    else:
        return statistics.mean(arr)


def custom_var(arr):
    if len(arr) < 2:
        return 0
    else:
        return statistics.variance(arr)


class FinderAccount:
    def __init__(self, balance, identifier):
        self.balance = balance
        self.identifier = identifier

        # Confidence Level
        self.cl = 0.0
        self.voters = 0

    def __eq__(self, other):
        if isinstance(other, FinderAccount):
            return self.balance == other.balance

    def __lt__(self, other):
        if isinstance(other, FinderAccount):
            return self.balance < other.balance

    def __le__(self, other):
        if isinstance(other, FinderAccount):
            return self.balance <= other.balance

    def __ge__(self, other):
        if isinstance(other, FinderAccount):
            return self.balance >= other.balance

    def __gt__(self, other):
        if isinstance(other, FinderAccount):
            return self.balance > other.balance

    def __str__(self):
        return f"(balance: {self.balance}, id:{self.identifier}, score: {self.get_score()})"

    def __repr__(self):
        return self.__str__()

    def get_score(self):
        if self.voters < 1:
            return self.cl
        return self.cl / self.voters


class FinderAnswer:
    def __init__(self, dictionary):
        self.d = dictionary

    def __eq__(self, other):
        if isinstance(other, FinderAnswer):
            a1, v1 = self.get_score()
            a2, v2 = other.get_score()
            return a1 == a2 and v1 == v2

    def __lt__(self, other):
        if isinstance(other, FinderAnswer):
            a1, v1 = self.get_score()
            a2, v2 = other.get_score()
            if a1 < a2:
                return True
            elif a1 == a2:
                return v1 > v2
            else:
                return False

    def __le__(self, other):
        if isinstance(other, FinderAnswer):
            a1, v1 = self.get_score()
            a2, v2 = other.get_score()
            return a1 <= a2

    def __ge__(self, other):
        if isinstance(other, FinderAnswer):
            a1, v1 = self.get_score()
            a2, v2 = other.get_score()
            return a1 >= a2

    def __gt__(self, other):
        if isinstance(other, FinderAnswer):
            a1, v1 = self.get_score()
            a2, v2 = other.get_score()
            if a1 > a2:
                return True
            elif a1 == a2:
                return v1 < v2
            else:
                return False

    def __str__(self):
        a, v = self.get_score()
        return f"({len(self.d.keys())} answers, avg={statistics.mean(a)})"

    def __repr__(self):
        return self.__str__()

    def get_score(self):
        averages = [custom_mean([acc.get_score() for acc in arr]) for arr in self.d.values()]
        variances = [custom_var([acc.get_score() for acc in arr]) for arr in self.d.values()]
        return averages, variances
