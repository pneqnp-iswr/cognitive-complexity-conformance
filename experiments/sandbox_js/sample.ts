export function f(a: number, b: number): number {
  if (a > 0) {
    if (b > 0) { return 1; } else if (a > 2) { return 2; } else { return 3; }
  }
  for (let i = 0; i < 3; i++) {
    while (a > 0 && b > 0 || !(a > 0)) { a--; }
  }
  return 0;
}
export function g(x: number): number { return x > 0 ? x : g(x - 1); }
export function m(items: number[]): void {
  try {
    items.forEach((i) => { if (i > 0) { switch (i) { case 1: break; default: break; } } });
  } catch (e) {}
  const v = items[0] ?? 0;
}
