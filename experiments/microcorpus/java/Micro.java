import java.util.List;
import java.util.function.Function;

/** Micro-corpus (Java). One method per case. Expected values: experiments/microcorpus/expected.csv */
public class Micro {

    int c01_empty(int a) {
        return a;
    }

    int c02_if(boolean a) {
        if (a) {
            return 1;
        }
        return 0;
    }

    int c03_if_else(boolean a) {
        if (a) {
            return 1;
        } else {
            return 0;
        }
    }

    int c04_if_elseif_elseif_else(int a) {
        if (a == 1) {
            return 1;
        } else if (a == 2) {
            return 2;
        } else if (a == 3) {
            return 3;
        } else {
            return 0;
        }
    }

    int c05_ternary(boolean a) {
        return a ? 1 : 0;
    }

    int c06_switch(int a) {
        switch (a) {
            case 1:
                return 1;
            case 2:
                return 2;
            default:
                return 0;
        }
    }

    int c06b_switch_expression(int a) {
        return switch (a) {
            case 1 -> 1;
            case 2 -> 2;
            default -> 0;
        };
    }

    void c07_for(List<Integer> items) {
        for (int i = 0; i < items.size(); i++) {
            System.out.println(i);
        }
    }

    void c07b_foreach(List<Integer> items) {
        for (Integer i : items) {
            System.out.println(i);
        }
    }

    int c08_while(int a) {
        while (a > 0) {
            a--;
        }
        return a;
    }

    int c08b_do_while(int a) {
        do {
            a--;
        } while (a > 0);
        return a;
    }

    int c09_try_catch(String a) {
        try {
            return Integer.parseInt(a);
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    int c10_try_two_catches(String a) {
        try {
            return Integer.parseInt(a);
        } catch (NumberFormatException e) {
            return 0;
        } catch (NullPointerException e) {
            return -1;
        }
    }

    int c11_multi_catch(String a) {
        try {
            return Integer.parseInt(a);
        } catch (NumberFormatException | NullPointerException e) {
            return 0;
        }
    }

    int c12_try_finally(String a) {
        try {
            return Integer.parseInt(a);
        } finally {
            System.out.println("done");
        }
    }

    int c13_try_catch_finally(String a) {
        try {
            return Integer.parseInt(a);
        } catch (NumberFormatException e) {
            return 0;
        } finally {
            System.out.println("done");
        }
    }

    int c14_if_in_if(boolean a, boolean b) {
        if (a) {
            if (b) {
                return 1;
            }
        }
        return 0;
    }

    int c15_if_in_for_in_while(int a, List<Integer> items) {
        while (a > 0) {
            for (Integer i : items) {
                if (i > 0) {
                    a--;
                }
            }
        }
        return a;
    }

    int c16_if_in_catch(String a) {
        try {
            return Integer.parseInt(a);
        } catch (NumberFormatException e) {
            if (a != null) {
                return 1;
            }
        }
        return 0;
    }

    int c17_if_in_try(boolean a) {
        try {
            if (a) {
                return 1;
            }
        } catch (RuntimeException e) {
            return -1;
        }
        return 0;
    }

    int c18_if_in_else(boolean a, boolean b) {
        if (a) {
            return 1;
        } else {
            if (b) {
                return 2;
            }
        }
        return 0;
    }

    int c19_if_in_elseif(boolean a, boolean b) {
        if (a) {
            return 1;
        } else if (b) {
            if (a == b) {
                return 2;
            }
        }
        return 0;
    }

    int c20_nested_ternary(boolean a, boolean b) {
        return a ? 1 : (b ? 2 : 0);
    }

    int c21_ternary_in_if_condition(boolean a, boolean b) {
        if (b ? a : !a) {
            return 1;
        }
        return 0;
    }

    int c22_ternary_in_while_condition(int a, boolean b) {
        while ((b ? a : 0) > 0) {
            a--;
        }
        return a;
    }

    int c23_and(boolean a, boolean b) {
        if (a && b) {
            return 1;
        }
        return 0;
    }

    int c24_and_and(boolean a, boolean b, boolean c) {
        if (a && b && c) {
            return 1;
        }
        return 0;
    }

    int c25_or(boolean a, boolean b) {
        if (a || b) {
            return 1;
        }
        return 0;
    }

    int c26_and_or(boolean a, boolean b, boolean c) {
        if (a && b || c) {
            return 1;
        }
        return 0;
    }

    int c27_or_and_or(boolean a, boolean b, boolean c, boolean d) {
        if (a || b && c || d) {
            return 1;
        }
        return 0;
    }

    int c28_and_not_paren_and(boolean a, boolean b, boolean c) {
        if (a && !(b && c)) {
            return 1;
        }
        return 0;
    }

    int c29_and_paren_or(boolean a, boolean b, boolean c) {
        if (a && (b || c)) {
            return 1;
        }
        return 0;
    }

    int c30_and_paren_and(boolean a, boolean b, boolean c) {
        if (a && (b && c)) {
            return 1;
        }
        return 0;
    }

    boolean c31_bool_in_assignment(boolean a, boolean b) {
        boolean x = a && b;
        return x;
    }

    boolean c32_bool_in_return(boolean a, boolean b) {
        return a || b;
    }

    boolean c33_bool_in_call(boolean a, boolean b) {
        return Boolean.valueOf(a && b);
    }

    int c35_and_or_and(boolean a, boolean b, boolean c, boolean d) {
        if (a && b || c && d) {
            return 1;
        }
        return 0;
    }

    int c36_unlabeled_break_continue(List<Integer> items) {
        for (Integer i : items) {
            if (i < 0) {
                continue;
            }
            if (i > 10) {
                break;
            }
        }
        return items.size();
    }

    int c37_early_return(boolean a) {
        if (a) {
            return 1;
        }
        System.out.println(a);
        return 0;
    }

    int c38_recursion_direct(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * c38_recursion_direct(n - 1);
    }

    int c39_recursion_indirect_a(int n) {
        if (n <= 0) {
            return 0;
        }
        return c39_recursion_indirect_b(n - 1);
    }

    int c39_recursion_indirect_b(int n) {
        if (n <= 0) {
            return 0;
        }
        return c39_recursion_indirect_a(n - 1);
    }

    int c40_lambda_with_ternary(List<Integer> items) {
        Function<Integer, Integer> f = x -> x > 0 ? x : 0;
        return f.apply(items.size());
    }

    int c41_lambda_with_if(boolean a) {
        Runnable r = () -> {
            if (a) {
                System.out.println(a);
            }
        };
        r.run();
        return 0;
    }

    int c43_lambda_inside_if(boolean a) {
        if (a) {
            Runnable r = () -> {
                if (a) {
                    System.out.println(a);
                }
            };
            r.run();
        }
        return 0;
    }

    int c47_anonymous_class_method_if(boolean a) {
        Runnable r = new Runnable() {
            @Override
            public void run() {
                if (a) {
                    System.out.println(a);
                }
            }
        };
        r.run();
        return 0;
    }

    int c55_deep_nesting_4(boolean a, boolean b, boolean c, boolean d) {
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

    void c56_for_in_catch_in_for(List<String> items) {
        for (String i : items) {
            try {
                Integer.parseInt(i);
            } catch (NumberFormatException e) {
                for (String j : items) {
                    System.out.println(j);
                }
            }
        }
    }

    int c57_two_sequential_ifs(boolean a, boolean b) {
        if (a) {
            System.out.println(a);
        }
        if (b) {
            System.out.println(b);
        }
        return 0;
    }

    int c58_elseif_nested_if(boolean a, boolean b, boolean c) {
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

    int c63_labeled_continue(int max) {
        int total = 0;
        OUT:
        for (int i = 1; i <= max; ++i) {
            for (int j = 2; j < i; ++j) {
                if (i % j == 0) {
                    continue OUT;
                }
            }
            total += i;
        }
        return total;
    }

    int c64_labeled_break_to_enclosing(List<Integer> items) {
        LOOP:
        for (Integer i : items) {
            if (i > 10) {
                break LOOP;
            }
        }
        return 0;
    }

    int c71_synchronized(boolean a) {
        synchronized (this) {
            if (a) {
                return 1;
            }
        }
        return 0;
    }

    int c72_try_with_resources(String path) {
        try (java.io.StringReader r = new java.io.StringReader(path)) {
            return r.read();
        } catch (java.io.IOException e) {
            return 0;
        }
    }

    int c73_throw_in_if(boolean a) {
        if (a) {
            throw new IllegalArgumentException();
        }
        return 0;
    }

    int c74_switch_with_nested_if(int a, boolean b) {
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

    int c75_bitwise_and_on_booleans(boolean a, boolean b) {
        if (a & b) {
            return 1;
        }
        return 0;
    }

    int c76_lambda_in_lambda(boolean a) {
        Function<Integer, Function<Integer, Integer>> f = x -> y -> {
            if (a) {
                return x;
            }
            return y;
        };
        return f.apply(1).apply(2);
    }

    int c77_instanceof_pattern(Object o) {
        if (o instanceof String s) {
            return s.length();
        }
        return 0;
    }

    int c78_recursion_via_this(int n) {
        if (n <= 0) {
            return 0;
        }
        return this.c78_recursion_via_this(n - 1);
    }

    int c79_or_not_paren_or(boolean a, boolean b, boolean c) {
        if (a || !(b || c)) {
            return 1;
        }
        return 0;
    }

    int c80_bool_and_ternary_top_level(boolean a, boolean b) {
        int i = (a || b) ? 1 : 0;
        return i;
    }

    // --- case added 2026-09-17 after the real-code audit (origin: real-code-derived): two recursive call sites
    int c103_recursion_two_calls(int n) {
        if (n <= 1) {
            return 1;
        }
        return c103_recursion_two_calls(n - 1) + c103_recursion_two_calls(n - 2);
    }

    @Override
    public boolean equals(Object o) {
        if (o == null) {
            return false;
        }
        return o == this;
    }

    @Override
    public int hashCode() {
        return 1;
    }
}


class AppendixC {
    // C.1 overriddenSymbolFrom — expected 19 (Appendix C)
    private Object overriddenSymbolFrom(ClassJavaType classType) {
        if (classType.isUnknown()) {
            return Symbols.unknownMethodSymbol;
        }
        boolean unknownFound = false;
        List<JavaSymbol> symbols = classType.getSymbol().members().lookup("name");
        for (JavaSymbol overrideSymbol : symbols) {
            if (overrideSymbol.isKind(JavaSymbol.MTH)
                    && !overrideSymbol.isStatic()) {
                MethodJavaSymbol methodJavaSymbol = (MethodJavaSymbol) overrideSymbol;
                if (canOverride(methodJavaSymbol)) {
                    Boolean overriding = checkOverridingParameters(methodJavaSymbol, classType);
                    if (overriding == null) {
                        if (!unknownFound) {
                            unknownFound = true;
                        }
                    } else if (overriding) {
                        return methodJavaSymbol;
                    }
                }
            }
        }
        if (unknownFound) {
            return Symbols.unknownMethodSymbol;
        }
        return null;
    }

    // C.2 addVersion — expected 35 (Appendix C)
    private void addVersion(final Entry entry, final Transaction txn)
            throws PersistitInterruptedException, RollbackException {
        final TransactionIndex ti = _persistit.getTransactionIndex();
        while (true) {
            try {
                synchronized (this) {
                    if (frst != null) {
                        if (frst.getVersion() > entry.getVersion()) {
                            throw new RollbackException();
                        }
                        if (txn.isActive()) {
                            for (Entry e = frst; e != null; e = e.getPrevious()) {
                                final long version = e.getVersion();
                                final long depends = ti.wwDependency(version, txn.getTransactionStatus(), 0);
                                if (depends == TIMED_OUT) {
                                    throw new WWRetryException(version);
                                }
                                if (depends != 0
                                        && depends != ABORTED) {
                                    throw new RollbackException();
                                }
                            }
                        }
                    }
                    entry.setPrevious(frst);
                    frst = entry;
                    break;
                }
            } catch (final WWRetryException re) {
                try {
                    final long depends = _persistit.getTransactionIndex()
                            .wwDependency(re.getVersionHandle(), txn.getTransactionStatus(), SharedResource.DEFAULT_MAX_WAIT_TIME);
                    if (depends != 0
                            && depends != ABORTED) {
                        throw new RollbackException();
                    }
                } catch (final InterruptedException ie) {
                    throw new PersistitInterruptedException(ie);
                }
            } catch (final InterruptedException ie) {
                throw new PersistitInterruptedException(ie);
            }
        }
    }

    // C.3 toRegexp — expected 20 (Appendix C)
    private static String toRegexp(String antPattern, String directorySeparator) {
        final String escapedDirectorySeparator = '\\' + directorySeparator;
        final StringBuilder sb = new StringBuilder(antPattern.length());
        sb.append('^');
        int i = antPattern.startsWith("/") ||
                antPattern.startsWith("\\") ? 1 : 0;
        while (i < antPattern.length()) {
            final char ch = antPattern.charAt(i);
            if (SPECIAL_CHARS.indexOf(ch) != -1) {
                sb.append('\\').append(ch);
            } else if (ch == '*') {
                if (i + 1 < antPattern.length()
                        && antPattern.charAt(i + 1) == '*') {
                    if (i + 2 < antPattern.length()
                            && isSlash(antPattern.charAt(i + 2))) {
                        sb.append("(?:.*").append(escapedDirectorySeparator).append("|)");
                        i += 2;
                    } else {
                        sb.append(".*");
                        i += 1;
                    }
                } else {
                    sb.append("[^").append(escapedDirectorySeparator).append("]*?");
                }
            } else if (ch == '?') {
                sb.append("[^").append(escapedDirectorySeparator).append("]");
            } else if (isSlash(ch)) {
                sb.append(escapedDirectorySeparator);
            } else {
                sb.append(ch);
            }
            i++;
        }
        sb.append('$');
        return sb.toString();
    }

    // body example sumOfPrimes — expected 7
    int sumOfPrimes(int max) {
        int total = 0;
        OUT: for (int i = 1; i <= max; ++i) {
            for (int j = 2; j < i; ++j) {
                if (i % j == 0) {
                    continue OUT;
                }
            }
            total += i;
        }
        return total;
    }

    // body example getWords — expected 1
    String getWords(int number) {
        switch (number) {
            case 1:
                return "one";
            case 2:
                return "a couple";
            case 3:
                return "a few";
            default:
                return "lots";
        }
    }

    // section 2.9 example myMethod — expected 9
    void myMethod(boolean condition1, boolean condition2) {
        try {
            if (condition1) {
                for (int i = 0; i < 10; i++) {
                    while (condition2) { condition2 = false; }
                }
            }
        } catch (IllegalStateException | IllegalArgumentException e) {
            if (condition2) { return; }
        }
    }

    // section 2.9 example myMethod2 — expected 2
    void myMethod2(boolean condition1) {
        Runnable r = () -> {
            if (condition1) { return; }
        };
        r.run();
    }

    // --- stubs so that the file is syntactically self-contained (never analysed as cases)
    static final long TIMED_OUT = -1L, ABORTED = -2L;
    static final String SPECIAL_CHARS = "()[]^$.{}+|";
    Entry frst; Persistit _persistit;
    static boolean isSlash(char c) { return c == '/' || c == '\\'; }
    boolean canOverride(MethodJavaSymbol m) { return true; }
    Boolean checkOverridingParameters(MethodJavaSymbol m, ClassJavaType t) { return null; }
    static class Symbols { static Object unknownMethodSymbol; }
    static class JavaSymbol { static final int MTH = 1; boolean isKind(int k) { return true; } boolean isStatic() { return false; } }
    static class MethodJavaSymbol extends JavaSymbol { }
    static class ClassJavaType { boolean isUnknown() { return false; } Scope getSymbol() { return new Scope(); } }
    static class Scope { Scope members() { return this; } List<JavaSymbol> lookup(String n) { return null; } }
    static class Entry { long getVersion() { return 0; } Entry getPrevious() { return null; } void setPrevious(Entry e) { } }
    static class Transaction { boolean isActive() { return true; } Object getTransactionStatus() { return null; } }
    static class TransactionIndex { long wwDependency(long v, Object s, long w) { return 0; } }
    static class Persistit { TransactionIndex getTransactionIndex() { return new TransactionIndex(); } }
    static class SharedResource { static final long DEFAULT_MAX_WAIT_TIME = 1; }
    static class RollbackException extends RuntimeException { }
    static class WWRetryException extends Exception { WWRetryException(long v) { } long getVersionHandle() { return 0; } }
    static class PersistitInterruptedException extends Exception { PersistitInterruptedException(Exception e) { } }
}
