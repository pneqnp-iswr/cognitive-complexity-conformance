// Micro-corpus (Go). One function per case. Expected values: experiments/microcorpus/expected.csv
package micro

import "strconv"

func c01_empty(a int) int {
	return a
}

func c02_if(a bool) int {
	if a {
		return 1
	}
	return 0
}

func c03_if_else(a bool) int {
	if a {
		return 1
	} else {
		return 0
	}
}

func c04_if_elseif_elseif_else(a int) int {
	if a == 1 {
		return 1
	} else if a == 2 {
		return 2
	} else if a == 3 {
		return 3
	} else {
		return 0
	}
}

func c06_switch(a int) int {
	switch a {
	case 1:
		return 1
	case 2:
		return 2
	default:
		return 0
	}
}

func c06b_switch_no_tag(a int) int {
	switch {
	case a > 1:
		return 1
	case a > 0:
		return 2
	default:
		return 0
	}
}

func c06c_type_switch(a interface{}) int {
	switch a.(type) {
	case int:
		return 1
	case string:
		return 2
	default:
		return 0
	}
}

func c06d_select(ch chan int, done chan bool) int {
	select {
	case v := <-ch:
		return v
	case <-done:
		return 0
	}
}

func c07_for(items []int) {
	for i := 0; i < len(items); i++ {
		println(i)
	}
}

func c07b_for_range(items []int) {
	for _, i := range items {
		println(i)
	}
}

func c08_for_condition_only(a int) int {
	for a > 0 {
		a--
	}
	return a
}

func c08b_for_infinite(a int) int {
	for {
		a--
		if a < 0 {
			break
		}
	}
	return a
}

func c14_if_in_if(a, b bool) int {
	if a {
		if b {
			return 1
		}
	}
	return 0
}

func c15_if_in_for_in_for(a int, items []int) int {
	for a > 0 {
		for _, i := range items {
			if i > 0 {
				a--
			}
		}
	}
	return a
}

func c18_if_in_else(a, b bool) int {
	if a {
		return 1
	} else {
		if b {
			return 2
		}
	}
	return 0
}

func c19_if_in_elseif(a, b bool) int {
	if a {
		return 1
	} else if b {
		if a == b {
			return 2
		}
	}
	return 0
}

func c19b_if_with_init(m map[string]int, k string) int {
	if v, ok := m[k]; ok {
		return v
	}
	return 0
}

func c23_and(a, b bool) int {
	if a && b {
		return 1
	}
	return 0
}

func c24_and_and(a, b, c bool) int {
	if a && b && c {
		return 1
	}
	return 0
}

func c25_or(a, b bool) int {
	if a || b {
		return 1
	}
	return 0
}

func c26_and_or(a, b, c bool) int {
	if a && b || c {
		return 1
	}
	return 0
}

func c27_or_and_or(a, b, c, d bool) int {
	if a || b && c || d {
		return 1
	}
	return 0
}

func c28_and_not_paren_and(a, b, c bool) int {
	if a && !(b && c) {
		return 1
	}
	return 0
}

func c29_and_paren_or(a, b, c bool) int {
	if a && (b || c) {
		return 1
	}
	return 0
}

func c30_and_paren_and(a, b, c bool) int {
	if a && (b && c) {
		return 1
	}
	return 0
}

func c31_bool_in_assignment(a, b bool) bool {
	x := a && b
	return x
}

func c32_bool_in_return(a, b bool) bool {
	return a || b
}

func c33_bool_in_call(a, b bool) string {
	return strconv.FormatBool(a && b)
}

func c35_and_or_and(a, b, c, d bool) int {
	if a && b || c && d {
		return 1
	}
	return 0
}

func c36_unlabeled_break_continue(items []int) int {
	for _, i := range items {
		if i < 0 {
			continue
		}
		if i > 10 {
			break
		}
	}
	return len(items)
}

func c37_early_return(a bool) int {
	if a {
		return 1
	}
	println(a)
	return 0
}

func c38_recursion_direct(n int) int {
	if n <= 1 {
		return 1
	}
	return n * c38_recursion_direct(n-1)
}

func c39_recursion_indirect_a(n int) int {
	if n <= 0 {
		return 0
	}
	return c39_recursion_indirect_b(n - 1)
}

func c39_recursion_indirect_b(n int) int {
	if n <= 0 {
		return 0
	}
	return c39_recursion_indirect_a(n - 1)
}

func c41_func_literal_with_if(a bool) int {
	r := func() {
		if a {
			println(a)
		}
	}
	r()
	return 0
}

func c43_func_literal_inside_if(a bool) int {
	if a {
		r := func() {
			if a {
				println(a)
			}
		}
		r()
	}
	return 0
}

func c55_deep_nesting_4(a, b, c, d bool) int {
	if a {
		if b {
			if c {
				if d {
					return 1
				}
			}
		}
	}
	return 0
}

func c57_two_sequential_ifs(a, b bool) int {
	if a {
		println(a)
	}
	if b {
		println(b)
	}
	return 0
}

func c58_elseif_nested_if(a, b, c bool) int {
	if a {
		return 1
	} else if b {
		if c {
			return 2
		}
		return 3
	} else {
		return 0
	}
}

func c63_labeled_continue(max int) int {
	total := 0
OUT:
	for i := 1; i <= max; i++ {
		for j := 2; j < i; j++ {
			if i%j == 0 {
				continue OUT
			}
		}
		total += i
	}
	return total
}

func c64_labeled_break_to_enclosing(items []int) int {
LOOP:
	for _, i := range items {
		if i > 10 {
			break LOOP
		}
	}
	return 0
}

func c65_goto(a int) int {
	for a > 0 {
		if a == 5 {
			goto END
		}
		a--
	}
END:
	return a
}

func c74_switch_with_nested_if(a int, b bool) int {
	switch a {
	case 1:
		if b {
			return 1
		}
		return 2
	default:
		return 0
	}
}

func c76_func_literal_in_func_literal(a bool) int {
	f := func(x int) func(int) int {
		return func(y int) int {
			if a {
				return x
			}
			return y
		}
	}
	return f(1)(2)
}

func c79_or_not_paren_or(a, b, c bool) int {
	if a || !(b || c) {
		return 1
	}
	return 0
}

func c92_defer_and_go(a bool) int {
	defer println("done")
	go println("async")
	return 0
}

func c93_switch_with_fallthrough(a int) int {
	switch a {
	case 1:
		fallthrough
	case 2:
		return 2
	default:
		return 0
	}
}

func c94_labeled_break_out_of_switch_in_loop(items []int) int {
LOOP:
	for _, i := range items {
		switch i {
		case 1:
			break LOOP
		}
	}
	return 0
}

type Micro struct{ x int }

func (m *Micro) c95_method_if(a bool) int {
	if a {
		return 1
	}
	return 0
}

func (m *Micro) c96_method_recursion(n int) int {
	if n <= 0 {
		return 0
	}
	return m.c96_method_recursion(n - 1)
}

func c97_bool_and_ternary_like(a, b bool) int {
	i := 0
	if a || b {
		i = 1
	}
	return i
}

// --- cases added 2026-09-17 after the real-code runs revealed an undocumented exemption in sonar-go
// (origin: real-code-derived; see expected.csv column origin)

func c98_if_err_not_nil_return(f func() error) error {
	err := f()
	if err != nil {
		return err
	}
	return nil
}

func c99_if_err_check_nested_if(f func() error, a bool) int {
	err := f()
	if err != nil {
		if a {
			return 2
		}
		return 1
	}
	return 0
}

func c100_two_err_checks(f, g func() error) error {
	if err := f(); err != nil {
		return err
	}
	if err := g(); err != nil {
		return err
	}
	return nil
}

func c101_err_check_with_else(f func() error) int {
	err := f()
	if err != nil {
		return 1
	} else {
		return 0
	}
}

func c102_err_named_e(f func() error) error {
	e := f()
	if e != nil {
		return e
	}
	return nil
}

// --- case added 2026-09-17 after the real-code audit (origin: real-code-derived): two recursive call sites
func c103_recursion_two_calls(n int) int {
	if n <= 1 {
		return 1
	}
	return c103_recursion_two_calls(n-1) + c103_recursion_two_calls(n-2)
}
