package evaluator

import (
	"fmt"
	"gato/src/object"
	"net/http"
	"os"
	"time" // <--- Butuh ini untuk sleep
)

// 1. Fungsi-fungsi Aman
var builtins = map[string]*object.Builtin{
	"len": {
		Fn: func(args ...object.Object) object.Object {
			if len(args) != 1 {
				return newError("wrong number of arguments. got=%d, want=1", len(args))
			}
			switch arg := args[0].(type) {
			case *object.Array:
				return &object.Integer{Value: int64(len(arg.Elements))}
			case *object.String:
				return &object.Integer{Value: int64(len(arg.Value))}
			default:
				return newError("argument to `len` not supported, got %s", args[0].Type())
			}
		},
	},
	"first": {
		Fn: func(args ...object.Object) object.Object {
			if len(args) != 1 {
				return newError("wrong number of arguments. got=%d, want=1", len(args))
			}
			if args[0].Type() != object.ARRAY_OBJ {
				return newError("argument to `first` must be ARRAY, got %s", args[0].Type())
			}
			arr := args[0].(*object.Array)
			if len(arr.Elements) > 0 {
				return arr.Elements[0]
			}
			return object.NULL
		},
	},
	"push": {
		Fn: func(args ...object.Object) object.Object {
			if len(args) != 2 {
				return newError("wrong number of arguments. got=%d, want=2", len(args))
			}
			if args[0].Type() != object.ARRAY_OBJ {
				return newError("argument to `push` must be ARRAY, got %s", args[0].Type())
			}
			arr := args[0].(*object.Array)
			length := len(arr.Elements)
			newElements := make([]object.Object, length+1)
			copy(newElements, arr.Elements)
			newElements[length] = args[1]
			return &object.Array{Elements: newElements}
		},
	},
	"print": {
		Fn: func(args ...object.Object) object.Object {
			for _, arg := range args {
				if arg == nil {
					fmt.Println("<nil>")
				} else {
					fmt.Println(arg.Inspect())
				}
			}
			return object.NULL
		},
	},
	// --- BARU: READ FILE ---
	"readFile": {
		Fn: func(args ...object.Object) object.Object {
			if len(args) != 1 {
				return newError("wrong number of args. usage: readFile(path)")
			}
			path, ok := args[0].(*object.String)
			if !ok {
				return newError("argument must be STRING, got %s", args[0].Type())
			}
			content, err := os.ReadFile(path.Value)
			if err != nil {
				fmt.Println("IO Error:", err)
				return object.NULL
			}
			return &object.String{Value: string(content)}
		},
	},
	// --- BARU: WRITE FILE ---
	"writeFile": {
		Fn: func(args ...object.Object) object.Object {
			if len(args) != 2 {
				return newError("wrong number of args. usage: writeFile(path, content)")
			}
			path, ok := args[0].(*object.String)
			if !ok {
				return newError("arg 1 must be STRING")
			}
			content, ok := args[1].(*object.String)
			if !ok {
				return newError("arg 2 must be STRING")
			}
			err := os.WriteFile(path.Value, []byte(content.Value), 0644)
			if err != nil {
				fmt.Println("IO Error:", err)
				return object.FALSE
			}
			return object.TRUE
		},
	},
	// --- BARU: SLEEP (Jeda Waktu) ---
	"sleep": {
		Fn: func(args ...object.Object) object.Object {
			if len(args) != 1 {
				return newError("usage: sleep(milliseconds)")
			}
			ms, ok := args[0].(*object.Integer)
			if !ok {
				return newError("argument must be INTEGER")
			}
			time.Sleep(time.Duration(ms.Value) * time.Millisecond)
			return object.NULL
		},
	},
}

// 2. Fungsi Kompleks (Cycle Aware)
func init() {
	// --- HTTP SERVER ---
	builtins["listen"] = &object.Builtin{
		Fn: func(args ...object.Object) object.Object {
			if len(args) != 2 {
				return newError("wrong number of args. usage: listen(port, handler)")
			}
			port, ok := args[0].(*object.String)
			if !ok {
				return newError("port must be STRING")
			}
			handler, ok := args[1].(*object.Function)
			if !ok {
				return newError("handler must be FUNCTION")
			}

			http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
				reqHash := &object.Hash{Pairs: make(map[object.HashKey]object.HashPair)}

				insertStr := func(key, val string) {
					k := &object.String{Value: key}
					v := &object.String{Value: val}
					reqHash.Pairs[k.HashKey()] = object.HashPair{Key: k, Value: v}
				}

				insertStr("method", r.Method)
				insertStr("path", r.URL.Path)
				insertStr("host", r.Host)

				response := applyFunction(handler, []object.Object{reqHash})

				if isError(response) {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(response.Inspect()))
				} else {
					if response == object.NULL {
						w.WriteHeader(http.StatusNotFound)
						w.Write([]byte("404 Not Found"))
					} else {
						w.Write([]byte(response.Inspect()))
					}
				}
			})

			fmt.Printf("🚀 GatoScript Server berjalan di http://localhost:%s\n", port.Value)
			err := http.ListenAndServe(":"+port.Value, nil)
			if err != nil {
				return newError("Server error: %s", err)
			}
			return object.NULL
		},
	}

	// --- SPAWN (CONCURRENCY) ---
	builtins["spawn"] = &object.Builtin{
		Fn: func(args ...object.Object) object.Object {
			if len(args) < 1 {
				return newError("usage: spawn(function, args...)")
			}

			// Argumen pertama adalah Fungsi
			fn := args[0]

			// Sisanya adalah argumen untuk fungsi tersebut
			fnArgs := args[1:]

			// JALANKAN DI BACKGROUND (GOROUTINE)
			go func() {
				applyFunction(fn, fnArgs)
			}()

			return object.NULL
		},
	}
}
