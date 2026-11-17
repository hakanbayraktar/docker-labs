package main

import (
	"fmt"
	"runtime"
)

func main() {
	fmt.Printf("Merhaba! Bu binary %s/%s icin derlendi.\n", runtime.GOOS, runtime.GOARCH)
}
