import os, sys
import json


def greet(name, greeting="hello"):
    """Say hello.

    Example:
        >>> greet("world")
        'hello, world'
    """
    msg = greeting + ", " + name
    return msg


class Animal:
    def __init__(self, name, species, age):
        self.name = name
        self.species = species
        self.age = age

    def describe(self):
        return {"name": self.name, "species": self.species, "age": self.age}


data = [1, 2, 3, 4, 5]
result = list(map(lambda x: x * 2, filter(lambda x: x % 2 == 0, data)))
print(result)

x = greet("Alice")
print(x)
