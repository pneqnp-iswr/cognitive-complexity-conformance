package probe

import "errors"

func q01_error_named_e(f func() error) error {
	e := f()
	if e != nil {
		return e
	}
	return nil
}

func q02_err_named_but_int(x *int) int {
	err := x
	if err != nil {
		return 1
	}
	return 0
}

func q03_err_else_if(f func() error, a bool) int {
	err := f()
	if err != nil {
		return 1
	} else if a {
		return 2
	}
	return 0
}

func q04_errors_is(f func() error, s error) int {
	err := f()
	if errors.Is(err, s) {
		return 1
	}
	return 0
}

func q05_nil_check_then_if(f func() error, a bool) int {
	err := f()
	if err != nil {
		if a {
			return 2
		}
		return 1
	}
	return 0
}

func q06_two_err_checks(f, g func() error) error {
	if err := f(); err != nil {
		return err
	}
	if err := g(); err != nil {
		return err
	}
	return nil
}

func q07_err_ne_nil_or(f func() error, a bool) int {
	err := f()
	if err != nil || a {
		return 1
	}
	return 0
}

func q08_reversed_nil_ne_err(f func() error) error {
	err := f()
	if nil != err {
		return err
	}
	return nil
}

func q09_err_check_with_for_after(f func() error, items []int) int {
	err := f()
	if err != nil {
		return 0
	}
	n := 0
	for range items {
		n++
	}
	return n
}
