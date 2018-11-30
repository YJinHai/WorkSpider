from abc import ABC

class MyABC(ABC):
    pass


class A:
    def __init__(self):
        print('A')

a = MyABC.register(A)
print(a())