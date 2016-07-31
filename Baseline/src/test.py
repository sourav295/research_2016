import functools

def x(a,b):
    return a+b

p1 = functools.partial(x, b=4)
print p1(10)


