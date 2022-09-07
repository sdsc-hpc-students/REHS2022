class foo:
    def __init__(self):
        print(self.__class__.__name__)

class bar(foo):
    def __init__(self):
        super().__init__()

foo = foo()
print(foo.__class__.__name__)

bar = bar()
