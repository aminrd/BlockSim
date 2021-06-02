class FinderAccount:
    def __init__(self, balance, identifier):
        self.balance = balance
        self.identifier = identifier
        self.confidence_level = 1.0

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
        return f"(balance: {self.balance}, id:{self.identifier})"

    def __repr__(self):
        return self.__str__()
