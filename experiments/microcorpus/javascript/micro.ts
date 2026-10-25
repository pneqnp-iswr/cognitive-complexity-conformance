// Micro-corpus (TypeScript). One function per case. Expected values: experiments/microcorpus/expected.csv
// (no lint directives: eslint-disable comments would silence ESLint-based tools)

export function c01_empty(a: number): number {
  return a;
}

export function c02_if(a: boolean): number {
  if (a) {
    return 1;
  }
  return 0;
}

export function c03_if_else(a: boolean): number {
  if (a) {
    return 1;
  } else {
    return 0;
  }
}

export function c04_if_elseif_elseif_else(a: number): number {
  if (a === 1) {
    return 1;
  } else if (a === 2) {
    return 2;
  } else if (a === 3) {
    return 3;
  } else {
    return 0;
  }
}

export function c05_ternary(a: boolean): number {
  return a ? 1 : 0;
}

export function c06_switch(a: number): number {
  switch (a) {
    case 1:
      return 1;
    case 2:
      return 2;
    default:
      return 0;
  }
}

export function c07_for(items: number[]): void {
  for (let i = 0; i < items.length; i++) {
    console.log(i);
  }
}

export function c07b_for_of(items: number[]): void {
  for (const i of items) {
    console.log(i);
  }
}

export function c07c_for_in(obj: Record<string, number>): void {
  for (const k in obj) {
    console.log(k);
  }
}

export function c08_while(a: number): number {
  while (a > 0) {
    a--;
  }
  return a;
}

export function c08b_do_while(a: number): number {
  do {
    a--;
  } while (a > 0);
  return a;
}

export function c09_try_catch(a: string): number {
  try {
    return parseInt(a, 10);
  } catch (e) {
    return 0;
  }
}

export function c09b_optional_catch_binding(a: string): number {
  try {
    return parseInt(a, 10);
  } catch {
    return 0;
  }
}

export function c12_try_finally(a: string): number {
  try {
    return parseInt(a, 10);
  } finally {
    console.log("done");
  }
}

export function c13_try_catch_finally(a: string): number {
  try {
    return parseInt(a, 10);
  } catch (e) {
    return 0;
  } finally {
    console.log("done");
  }
}

export function c14_if_in_if(a: boolean, b: boolean): number {
  if (a) {
    if (b) {
      return 1;
    }
  }
  return 0;
}

export function c15_if_in_for_in_while(a: number, items: number[]): number {
  while (a > 0) {
    for (const i of items) {
      if (i > 0) {
        a--;
      }
    }
  }
  return a;
}

export function c16_if_in_catch(a: string): number {
  try {
    return parseInt(a, 10);
  } catch (e) {
    if (a) {
      return 1;
    }
  }
  return 0;
}

export function c17_if_in_try(a: boolean): number {
  try {
    if (a) {
      return 1;
    }
  } catch (e) {
    return -1;
  }
  return 0;
}

export function c18_if_in_else(a: boolean, b: boolean): number {
  if (a) {
    return 1;
  } else {
    if (b) {
      return 2;
    }
  }
  return 0;
}

export function c19_if_in_elseif(a: boolean, b: boolean): number {
  if (a) {
    return 1;
  } else if (b) {
    if (a === b) {
      return 2;
    }
  }
  return 0;
}

export function c20_nested_ternary(a: boolean, b: boolean): number {
  return a ? 1 : (b ? 2 : 0);
}

export function c21_ternary_in_if_condition(a: boolean, b: boolean): number {
  if (b ? a : !a) {
    return 1;
  }
  return 0;
}

export function c22_ternary_in_while_condition(a: number, b: boolean): number {
  while ((b ? a : 0) > 0) {
    a--;
  }
  return a;
}

export function c23_and(a: boolean, b: boolean): number {
  if (a && b) {
    return 1;
  }
  return 0;
}

export function c24_and_and(a: boolean, b: boolean, c: boolean): number {
  if (a && b && c) {
    return 1;
  }
  return 0;
}

export function c25_or(a: boolean, b: boolean): number {
  if (a || b) {
    return 1;
  }
  return 0;
}

export function c26_and_or(a: boolean, b: boolean, c: boolean): number {
  if (a && b || c) {
    return 1;
  }
  return 0;
}

export function c27_or_and_or(a: boolean, b: boolean, c: boolean, d: boolean): number {
  if (a || b && c || d) {
    return 1;
  }
  return 0;
}

export function c28_and_not_paren_and(a: boolean, b: boolean, c: boolean): number {
  if (a && !(b && c)) {
    return 1;
  }
  return 0;
}

export function c29_and_paren_or(a: boolean, b: boolean, c: boolean): number {
  if (a && (b || c)) {
    return 1;
  }
  return 0;
}

export function c30_and_paren_and(a: boolean, b: boolean, c: boolean): number {
  if (a && (b && c)) {
    return 1;
  }
  return 0;
}

export function c31_bool_in_assignment(a: boolean, b: boolean): boolean {
  const x = a && b;
  return x;
}

export function c32_bool_in_return(a: boolean, b: boolean): boolean {
  return a || b;
}

export function c33_bool_in_call(a: boolean, b: boolean): boolean {
  return Boolean(a && b);
}

export function c34_or_default_idiom(a: any): any {
  a = a || {};
  return a;
}

export function c35_and_or_and(a: boolean, b: boolean, c: boolean, d: boolean): number {
  if (a && b || c && d) {
    return 1;
  }
  return 0;
}

export function c36_unlabeled_break_continue(items: number[]): number {
  for (const i of items) {
    if (i < 0) {
      continue;
    }
    if (i > 10) {
      break;
    }
  }
  return items.length;
}

export function c37_early_return(a: boolean): number {
  if (a) {
    return 1;
  }
  console.log(a);
  return 0;
}

export function c38_recursion_direct(n: number): number {
  if (n <= 1) {
    return 1;
  }
  return n * c38_recursion_direct(n - 1);
}

export function c39_recursion_indirect_a(n: number): number {
  if (n <= 0) {
    return 0;
  }
  return c39_recursion_indirect_b(n - 1);
}

export function c39_recursion_indirect_b(n: number): number {
  if (n <= 0) {
    return 0;
  }
  return c39_recursion_indirect_a(n - 1);
}

export function c40_arrow_with_ternary(items: number[]): number[] {
  const f = (x: number) => (x ? x : 0);
  return items.map(f);
}

export function c41_arrow_with_if(a: boolean): number {
  const r = () => {
    if (a) {
      console.log(a);
    }
  };
  r();
  return 0;
}

export function c42_nested_function_only(a: boolean): number {
  function inner(x: boolean): number {
    if (x) {
      return 1;
    }
    return 0;
  }
  return inner(a);
}

export function c43_arrow_inside_if(a: boolean): number {
  if (a) {
    const r = () => {
      if (a) {
        console.log(a);
      }
    };
    r();
  }
  return 0;
}

export function c44_declarative_outer(): any {
  var foo;
  const bar: any = {};
  bar.myFun = function (condition: boolean) {
    if (condition) {
      return 1;
    }
    return 0;
  };
  return bar;
}

export function c45_non_declarative_outer(condition: boolean): any {
  var foo;
  if (condition) {
    foo = 1;
  }
  const bar: any = {};
  bar.myFun = function (c: boolean) {
    if (c) {
      return 1;
    }
    return 0;
  };
  return bar;
}

export function c55_deep_nesting_4(a: boolean, b: boolean, c: boolean, d: boolean): number {
  if (a) {
    if (b) {
      if (c) {
        if (d) {
          return 1;
        }
      }
    }
  }
  return 0;
}

export function c56_for_in_catch_in_for(items: string[]): void {
  for (const i of items) {
    try {
      parseInt(i, 10);
    } catch (e) {
      for (const j of items) {
        console.log(j);
      }
    }
  }
}

export function c57_two_sequential_ifs(a: boolean, b: boolean): number {
  if (a) {
    console.log(a);
  }
  if (b) {
    console.log(b);
  }
  return 0;
}

export function c58_elseif_nested_if(a: boolean, b: boolean, c: boolean): number {
  if (a) {
    return 1;
  } else if (b) {
    if (c) {
      return 2;
    }
    return 3;
  } else {
    return 0;
  }
}

export function c63_labeled_continue(max: number): number {
  let total = 0;
  OUT: for (let i = 1; i <= max; ++i) {
    for (let j = 2; j < i; ++j) {
      if (i % j === 0) {
        continue OUT;
      }
    }
    total += i;
  }
  return total;
}

export function c64_labeled_break_to_enclosing(items: number[]): number {
  LOOP: for (const i of items) {
    if (i > 10) {
      break LOOP;
    }
  }
  return 0;
}

export function c74_switch_with_nested_if(a: number, b: boolean): number {
  switch (a) {
    case 1:
      if (b) {
        return 1;
      }
      return 2;
    default:
      return 0;
  }
}

export function c76_arrow_in_arrow(a: boolean): number {
  const f = (x: number) => (y: number) => {
    if (a) {
      return x;
    }
    return y;
  };
  return f(1)(2);
}

export function c79_or_not_paren_or(a: boolean, b: boolean, c: boolean): number {
  if (a || !(b || c)) {
    return 1;
  }
  return 0;
}

export function c80_bool_and_ternary_top_level(a: boolean, b: boolean): number {
  const i = (a || b) ? 1 : 0;
  return i;
}

export function c81_nullish_coalescing(a: any): any {
  return a ?? 0;
}

export function c82_optional_chaining(a: any): any {
  return a?.b?.c;
}

export function c83_nullish_then_or(a: any, b: any, c: any): any {
  return (a ?? b) || c;
}

export function c84_and_in_jsx_like_callback(items: number[], a: boolean): number[] {
  return items.filter((i) => a && i > 0);
}

export async function c85_async_await(p: Promise<number>): Promise<number> {
  const v = await p;
  return v;
}

export function* c86_generator(items: number[]): Generator<number> {
  for (const i of items) {
    yield i;
  }
}

export class Micro {
  c87_method_if(a: boolean): number {
    if (a) {
      return 1;
    }
    return 0;
  }

  get c88_getter_ternary(): number {
    return this.x ? 1 : 0;
  }

  c89_method_recursion(n: number): number {
    if (n <= 0) {
      return 0;
    }
    return this.c89_method_recursion(n - 1);
  }

  x = 1;
}

export const c90_arrow_const = (a: boolean, b: boolean): number => {
  if (a && b) {
    return 1;
  }
  return 0;
};

export function c91_typeof_guard(a: unknown): number {
  if (typeof a === "string") {
    return 1;
  }
  return 0;
}

// Appendix C.4 save — expected 20
export const yuiModel: any = {
  save: function (options: any, callback: any) {
    var self: any = this;
    if (typeof options === 'function') {
      callback = options;
      options = {};
    }
    options || (options = {});
    self._validate(self.toJSON(), function (err: any) {
      if (err) {
        callback && callback.call(null, err);
        return;
      }
      self.sync(self.isNew() ? 'create' : 'update',
        options, function (err: any, response: any) {
          var facade: any = { options: options, response: response }, parsed;
          if (err) {
            facade.error = err;
            facade.src = 'save';
            self.fire('error', facade);
          } else {
            if (!self._saveEvent) {
              self._saveEvent = self.publish('save', { preventable: false });
            }
            if (response) {
              parsed = facade.parsed = self._parse(response);
              self.setAttrs(parsed, options);
            }
            self.changed = {};
            self.fire('save', facade);
          }
          callback && callback.apply(null, arguments);
        });
    });
    return self;
  }
};

// --- case added 2026-09-17 after the real-code audit (origin: real-code-derived): two recursive call sites
export function c103_recursion_two_calls(n: number): number {
  if (n <= 1) {
    return 1;
  }
  return c103_recursion_two_calls(n - 1) + c103_recursion_two_calls(n - 2);
}
