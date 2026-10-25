# Micro-corpus (Python). One function per case. Expected values: experiments/microcorpus/expected.csv
# Derivations refer to the white paper v1.7: B1 (increments), B2 (nesting level), B3 (nesting increments),
# sections 2.2-2.9 (rules), Appendix A (exceptions), Appendix C (examples).


def c01_empty(a):
    return a


def c02_if(a):
    if a:
        return 1
    return 0


def c03_if_else(a):
    if a:
        return 1
    else:
        return 0


def c04_if_elif_elif_else(a):
    if a == 1:
        return 1
    elif a == 2:
        return 2
    elif a == 3:
        return 3
    else:
        return 0


def c05_ternary(a):
    return 1 if a else 0


def c06_match(a):
    match a:
        case 1:
            return 1
        case 2:
            return 2
        case _:
            return 0


def c07_for(items):
    for i in items:
        print(i)


def c08_while(a):
    while a > 0:
        a -= 1
    return a


def c09_try_except(a):
    try:
        return int(a)
    except ValueError:
        return 0


def c10_try_two_excepts(a):
    try:
        return int(a)
    except ValueError:
        return 0
    except TypeError:
        return -1


def c11_except_tuple(a):
    try:
        return int(a)
    except (ValueError, TypeError):
        return 0


def c12_try_finally(a):
    try:
        return int(a)
    finally:
        print("done")


def c13_try_except_finally(a):
    try:
        return int(a)
    except ValueError:
        return 0
    finally:
        print("done")


def c14_if_in_if(a, b):
    if a:
        if b:
            return 1
    return 0


def c15_if_in_for_in_while(a, items):
    while a:
        for i in items:
            if i:
                a -= 1
    return a


def c16_if_in_except(a):
    try:
        return int(a)
    except ValueError:
        if a:
            return 1
    return 0


def c17_if_in_try(a):
    try:
        if a:
            return 1
    except ValueError:
        pass
    return 0


def c18_if_in_else(a, b):
    if a:
        return 1
    else:
        if b:
            return 2
    return 0


def c19_if_in_elif(a, b):
    if a:
        return 1
    elif b:
        if a == b:
            return 2
    return 0


def c20_nested_ternary(a, b):
    return 1 if a else (2 if b else 0)


def c21_ternary_in_if_condition(a, b):
    if (a if b else not a):
        return 1
    return 0


def c22_ternary_in_while_condition(a, b):
    while (a if b else 0):
        a -= 1
    return a


def c23_and(a, b):
    if a and b:
        return 1
    return 0


def c24_and_and(a, b, c):
    if a and b and c:
        return 1
    return 0


def c25_or(a, b):
    if a or b:
        return 1
    return 0


def c26_and_or(a, b, c):
    if a and b or c:
        return 1
    return 0


def c27_or_and_or(a, b, c, d):
    if a or b and c or d:
        return 1
    return 0


def c28_and_not_paren_and(a, b, c):
    if a and not (b and c):
        return 1
    return 0


def c29_and_paren_or(a, b, c):
    if a and (b or c):
        return 1
    return 0


def c30_and_paren_and(a, b, c):
    if a and (b and c):
        return 1
    return 0


def c31_bool_in_assignment(a, b):
    x = a and b
    return x


def c32_bool_in_return(a, b):
    return a or b


def c33_bool_in_call(a, b):
    return bool(a and b)


def c34_or_default_idiom(a):
    a = a or {}
    return a


def c35_and_or_and(a, b, c, d):
    if a and b or c and d:
        return 1
    return 0


def c36_unlabeled_break_continue(items):
    for i in items:
        if i < 0:
            continue
        if i > 10:
            break
    return items


def c37_early_return(a):
    if a:
        return 1
    print(a)
    return 0


def c38_recursion_direct(n):
    if n <= 1:
        return 1
    return n * c38_recursion_direct(n - 1)


def c39_recursion_indirect_a(n):
    if n <= 0:
        return 0
    return c39_recursion_indirect_b(n - 1)


def c39_recursion_indirect_b(n):
    if n <= 0:
        return 0
    return c39_recursion_indirect_a(n - 1)


def c40_lambda_with_ternary(items):
    f = lambda x: x if x else 0
    return [f(i) for i in items]


def c41_nested_def_with_if(a):
    def inner(x):
        if x:
            return 1
        return 0
    return inner(a) + 1 if a else 0


def c42_nested_def_only(a):
    def inner(x):
        if x:
            return 1
        return 0
    return inner(a)


def c43_nested_def_inside_if(a):
    if a:
        def inner(x):
            if x:
                return 1
            return 0
        return inner(a)
    return 0


def c44_decorator(a, b):
    def inner(func):
        if a:
            print(b)
        func()
    return inner


def c45_not_a_decorator(a, b):
    my_var = a * b
    def inner(func):
        if my_var:
            print(b)
        func()
    return inner


def c46_decorator_generator(a):
    def generator(func):
        def decorator(func):
            if a:
                print(a)
            return func()
        return decorator
    return generator


def c47_nested_class_method_if(a):
    class Inner:
        def m(self, x):
            if x:
                return 1
            return 0
    return Inner().m(a)


def c48_comprehension_if(items):
    return [i for i in items if i]


def c49_comprehension_plain(items):
    return [i * 2 for i in items]


def c50_for_else(items):
    for i in items:
        if i:
            break
    else:
        return 0
    return 1


def c51_while_else(a):
    while a:
        a -= 1
    else:
        return 0
    return 1


def c52_try_else(a):
    try:
        x = int(a)
    except ValueError:
        return 0
    else:
        return x


def c53_with(a):
    with open(a) as f:
        return f.read()


def c54_walrus(items):
    if (n := len(items)) > 3:
        return n
    return 0


def c55_deep_nesting_4(a, b, c, d):
    if a:
        if b:
            if c:
                if d:
                    return 1
    return 0


def c56_for_in_except_in_for(items):
    for i in items:
        try:
            int(i)
        except ValueError:
            for j in items:
                print(j)
    return items


def c57_two_sequential_ifs(a, b):
    if a:
        print(a)
    if b:
        print(b)
    return 0


def c58_else_if_nested_if(a, b, c):
    if a:
        return 1
    elif b:
        if c:
            return 2
        return 3
    else:
        return 0


def c59_bool_inside_comprehension(items, a):
    return [i for i in items if i and a]


def c60_bool_and_ternary_top_level(a, b):
    i = 1 if (a or b) else 0
    return i


def c61_async_await():
    return None


async def c62_async_for(items):
    async for i in items:
        print(i)


class Micro:
    def c63_method_if(self, a):
        if a:
            return 1
        return 0

    def c64_method_recursion(self, n):
        if n <= 0:
            return 0
        return self.c64_method_recursion(n - 1)

    @staticmethod
    def c65_static_and_or(a, b, c):
        if a and b or c:
            return 1
        return 0


def c66_lambda_in_for(items):
    for i in items:
        f = lambda x: x if x else i
        print(f(i))


def c67_lambda_with_bool(a, b):
    f = lambda: a and b
    return f()


def c68_raise_in_if(a):
    if a:
        raise ValueError(a)
    return 0


def c69_assert(a):
    assert a
    return a


def c70_generator_expression_if(items):
    return sum(i for i in items if i)


# --- case added 2026-09-17 after the real-code audit (origin: real-code-derived): two recursive call sites
def c103_recursion_two_calls(n):
    if n <= 1:
        return 1
    return c103_recursion_two_calls(n - 1) + c103_recursion_two_calls(n - 2)
