def f(a, b):
    if a:                      # +1
        if b:                  # +2 (nesting 1)
            return 1
        elif a > 2:            # +1
            return 2
        else:                  # +1
            return 3
    for i in range(3):         # +1
        while a and b or not a:  # +2 (loop) +2 (&& and ||)
            a -= 1
    return 0

def g(x):
    return x if x else g(x-1)  # +1 ternary, +1 recursion

class C:
    def m(self, items):
        try:
            for i in items:            # +1
                if i:                  # +2
                    def inner(y):
                        if y:          # ?
                            return y
                        return 0
                    inner(i)
        except ValueError:             # +1
            pass
        return [i for i in items if i]
