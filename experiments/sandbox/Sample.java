public class Sample {
    int f(int a, int b) {
        if (a > 0) {                 // +1
            if (b > 0) {             // +2
                return 1;
            } else if (a > 2) {      // +1
                return 2;
            } else {                 // +1
                return 3;
            }
        }
        for (int i = 0; i < 3; i++) {                  // +1
            while (a > 0 && b > 0 || !(a > 0)) {       // +2 loop, +2 boolean
                a--;
            }
        }
        return 0;
    }
    int g(int x) { return x > 0 ? x : g(x - 1); }    // +1 ternary, +1 recursion
    void m(java.util.List<Integer> items) {
        try {
            items.forEach(i -> {           // lambda: nesting +1
                if (i > 0) {               // +2
                    switch (i) {           // +3
                        case 1: break;
                        default: break;
                    }
                }
            });
        } catch (Exception e) {            // +1
        }
    }
}
