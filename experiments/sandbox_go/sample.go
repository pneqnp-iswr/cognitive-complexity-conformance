package sample

func f(a, b int) int {
	if a > 0 {
		if b > 0 {
			return 1
		} else if a > 2 {
			return 2
		} else {
			return 3
		}
	}
	for i := 0; i < 3; i++ {
		for a > 0 && b > 0 || !(a > 0) {
			a--
		}
	}
	return 0
}

func g(x int) int {
	if x > 0 {
		return x
	}
	return g(x - 1)
}
