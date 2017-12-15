import random
import faker


class Property(object):
    def __init__(self, name, values=[], static=False, **kwargs):
        self.name = name
        self.vals = values
        self.static = static
        self.hasChosen = False
        self.value = None

    def shouldChooseNewValue(self):
        return not (self.static and self.hasChosen)

    def chooseVal(self):
        if self.shouldChooseNewValue():
            self.value = random.choice(self.vals)
            self.hasChosen = True

        return self.value

    def reset(self):
        self.hasChosen = False


class PropOrdinal(Property):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

        if 'high' not in kwargs:
            raise TypeError("Ordinal properties require 'high' arg for range")
        if 'low' not in kwargs:
            raise TypeError("Ordinal properties require 'low' arg for range")

        self.high = kwargs.get('high', 0)
        self.low = kwargs.get('low', 0)
        if self.high < self.low:
            raise ValueError("Ordinal 'low' range val must be greater than or equal to 'high'.")

    def chooseVal(self):
        if self.shouldChooseNewValue():
            self.value = random.randint(self.low, self.high)
            self.hasChosen = True

        return self.value


class PropDateTime(Property):
    def __init__(self, name, fmt='%m/%d/%Y %I:%M %p', **kwargs):
        super().__init__(name, **kwargs)
        self.fmt = fmt
        self.faker = faker.Faker()

    def chooseVal(self):
        if self.shouldChooseNewValue():
            dt = self.faker.date_time()
            self.value = dt.strftime(self.fmt)
            self.hasChosen = True

        return self.value


class PropertyFactory(object):

    @classmethod
    def makeProperty(cls, name, **kwargs):
        propType = kwargs.get('type', '')

        if propType == 'ordinal':
            return PropOrdinal(name, **kwargs)
        elif propType == 'datetime':
            return PropDateTime(name, **kwargs)
        else:
            return Property(name, **kwargs)
