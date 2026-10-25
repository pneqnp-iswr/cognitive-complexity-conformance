package probe

import "errors"

func p01_err_not_nil_return(f func() error) error {
	err := f()
	if err != nil {
		return err
	}
	return nil
}

func p02_err_eq_nil(f func() error) int {
	err := f()
	if err == nil {
		return 1
	}
	return 0
}

func p03_err_init_stmt(f func() error) error {
	if err := f(); err != nil {
		return err
	}
	return nil
}

func p04_err_not_nil_no_return(f func() error) int {
	err := f()
	if err != nil {
		println("x")
	}
	return 0
}

func p05_other_var_not_nil(x *int) int {
	if x != nil {
		return 1
	}
	return 0
}

func p06_bool_cond(a bool) int {
	if a {
		return 1
	}
	return 0
}

func p07_err_not_nil_else(f func() error) int {
	err := f()
	if err != nil {
		return 1
	} else {
		return 0
	}
}

func p08_err_and_cond(f func() error, a bool) int {
	err := f()
	if err != nil && a {
		return 1
	}
	return 0
}

func p09_nested_err_in_for(items []int, f func() error) int {
	for range items {
		if err := f(); err != nil {
			return 1
		}
	}
	return 0
}

func p10_err_wrap_return(f func() error) error {
	err := f()
	if err != nil {
		return errors.New("wrapped")
	}
	return nil
}

func p11_err_compare_sentinel(f func() error, s error) int {
	err := f()
	if err == s {
		return 1
	}
	return 0
}

func p12_len_check(items []int) int {
	if len(items) == 0 {
		return 0
	}
	return 1
}
