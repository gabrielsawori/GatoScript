package main

import (
	"bufio"
	"fmt"
	"gato/src/evaluator"
	"gato/src/lexer"
	"gato/src/object"
	"gato/src/parser"
	"io"
	"os"
	"os/user"
)

const GATO_VERSION = "1.0.0"

func main() {
	// Cek apakah ada argumen
	if len(os.Args) > 1 {
		arg := os.Args[1]

		// 1. Cek Flag Khusus
		switch arg {
		case "--version", "-v":
			fmt.Printf("GatoScript version %s\n", GATO_VERSION)
			fmt.Println("Created by Gabriel Eduardi Sawori")
			return // Keluar program
		case "--help", "-h":
			printHelp()
			return // Keluar program
		default:
			// 2. Jika bukan flag, anggap sebagai Nama File
			runFile(arg)
		}
	} else {
		// 3. Jika tidak ada argumen, masuk Mode REPL
		user, err := user.Current()
		if err != nil {
			panic(err)
		}
		fmt.Printf("🐱 Halo %s! GatoScript v%s (REPL Mode)\n", user.Username, GATO_VERSION)
		fmt.Println("Ketik '--help' untuk bantuan atau nama file untuk menjalankannya.")
		Start(os.Stdin, os.Stdout)
	}
}

func printHelp() {
	fmt.Println("Usage: gato [options] [file.gs]")
	fmt.Println("")
	fmt.Println("Options:")
	fmt.Println("  --version, -v    Tampilkan versi GatoScript")
	fmt.Println("  --help, -h       Tampilkan bantuan ini")
	fmt.Println("")
	fmt.Println("Examples:")
	fmt.Println("  gato             Jalankan mode interaktif (REPL)")
	fmt.Println("  gato server.gs   Jalankan file script")
}

func runFile(filename string) {
	file, err := os.ReadFile(filename)
	if err != nil {
		fmt.Printf("Gagal membaca file: %s\n", err)
		os.Exit(1)
	}

	code := string(file)
	l := lexer.New(code)
	p := parser.New(l)
	program := p.ParseProgram()

	if len(p.Errors()) != 0 {
		printParserErrors(os.Stdout, p.Errors())
		os.Exit(1)
	}

	env := object.NewEnvironment()
	evaluated := evaluator.Eval(program, env)

	if evaluated != nil && evaluated.Type() != object.NULL_OBJ {
		fmt.Println(evaluated.Inspect())
	}
}

func Start(in io.Reader, out io.Writer) {
	scanner := bufio.NewScanner(in)
	env := object.NewEnvironment()

	for {
		fmt.Printf(">> ")
		if !scanner.Scan() {
			return
		}
		line := scanner.Text()
		l := lexer.New(line)
		p := parser.New(l)

		program := p.ParseProgram()

		if len(p.Errors()) != 0 {
			printParserErrors(out, p.Errors())
			continue
		}

		evaluated := evaluator.Eval(program, env)
		if evaluated != nil {
			io.WriteString(out, evaluated.Inspect())
			io.WriteString(out, "\n")
		}
	}
}

func printParserErrors(out io.Writer, errors []string) {
	io.WriteString(out, "Error Syntax:\n")
	for _, msg := range errors {
		io.WriteString(out, "\t"+msg+"\n")
	}
}
