package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"regexp"
	"strings"
)

type Crash struct {
	Package   string
	Exception string
	Message   string
	Stack     []string
}

func parseCrash(lines []string) *Crash {
	crash := &Crash{Stack: []string{}}

	pkgRe := regexp.MustCompile(`Package: ([\w.]+)`)
	excRe := regexp.MustCompile(`([\w.]+Exception): (.+)`)
	stackRe := regexp.MustCompile(`^\s+at (.+)$`)

	for _, line := range lines {
		if m := pkgRe.FindStringSubmatch(line); m != nil {
			crash.Package = m[1]
		}
		if m := excRe.FindStringSubmatch(line); m != nil {
			crash.Exception = m[1]
			crash.Message = m[2]
		}
		if m := stackRe.FindStringSubmatch(line); m != nil {
			crash.Stack = append(crash.Stack, m[1])
		}
	}

	return crash
}

func main() {
	file := flag.String("f", "", "Crash log file")
	topFrames := flag.Int("top", 5, "Top stack frames to show")
	flag.Parse()

	if *file == "" {
		fmt.Println("Usage: crash-analyzer -f logcat.txt [-top 5]")
		os.Exit(1)
	}

	content, _ := os.ReadFile(*file)
	lines := strings.Split(string(content), "\n")

	crashes := []*Crash{}
	var current []string

	for _, line := range lines {
		if strings.Contains(line, "FATAL EXCEPTION") || strings.Contains(line, "AndroidRuntime") {
			if len(current) > 0 {
				crashes = append(crashes, parseCrash(current))
			}
			current = []string{line}
		} else if len(current) > 0 {
			current = append(current, line)
		}
	}

	if len(current) > 0 {
		crashes = append(crashes, parseCrash(current))
	}

	fmt.Printf("Found %d crashes\n\n", len(crashes))

	for i, c := range crashes {
		fmt.Printf("[%d] %s\n", i+1, c.Package)
		fmt.Printf("    %s: %s\n", c.Exception, c.Message)
		fmt.Printf("    Stack trace:\n")
		for j, frame := range c.Stack {
			if j >= *topFrames {
				break
			}
			fmt.Printf("      %s\n", frame)
		}
		fmt.Println()
	}
}
