package object

func NewEnclosedEnvironment(outer *Environment) *Environment {
	env := NewEnvironment()
	env.outer = outer
	return env
}

type Environment struct {
	store map[string]Object
	outer *Environment
}

func NewEnvironment() *Environment {
	s := make(map[string]Object)
	return &Environment{store: s, outer: nil}
}

func (e *Environment) Get(name string) (Object, bool) {
	obj, ok := e.store[name]
	if !ok && e.outer != nil {
		obj, ok = e.outer.Get(name)
	}
	return obj, ok
}

func (e *Environment) Set(name string, val Object) Object {
	e.store[name] = val
	return val
}

// --- BARU: UPDATE (RECURSIVE) ---
func (e *Environment) Update(name string, val Object) Object {
	// 1. Cek di scope sendiri
	if _, ok := e.store[name]; ok {
		e.store[name] = val
		return val
	}
	// 2. Cek di scope luar
	if e.outer != nil {
		return e.outer.Update(name, val)
	}
	// 3. Tidak ketemu
	return nil
}
