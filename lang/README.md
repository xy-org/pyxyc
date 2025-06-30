## Functions

```xy
def <func-name>(arg1: ref Type, arg2: Type2) -> (RetType, x: RetType2) || ErrorType
;; doc strings
>> wall expression (only input args);
<< x > 0 ;; check for overflow crash if fails
<< x > a'len ;; check for high overflow
>> a > b ;; crash if fails checked only if return
{body}

def read(...) -> (numRead: USize) <> ErrorType
<< if (numRead > 0) error;
{
	
}

bytes := read(...);
<>

def fuc(x: int) -> (x: int, y: int) || Error {
}

def (func-name)(args...) = block|expression

```

```xy
what-are-we-declaring name : Type = Value;
var name := 0
def func-name [:=] (Int)->Int|Error {
}

Values is
* when variable, type and value, docstring
* when func, args, output, body, guards, docstring
* when struct, fields, docstring
```

## Error Handling

We want:

1. Ignoring an error in expression and providing a default value
2. Executing a function, if success execute one code else execute something else
3. Non-local handling i.e. returning to parent

```xy
def main() {
	# 1
	a := func() || 0; # catches any error in the execution of func
	b := func1(func2(a)) || 0; catches any error in func1 or func2
	
	f := open("file.txt") || {
		e := ||;
		print(||);
		return; # if this is missing than we should get an error
	}
	
	# 2
	a: || e: = func();
	if (!?e) {
		success
	} else {
		failure
	}
	
	# 3
	a := -> (res: %func) {
		res = func();
		|| res = 0;
	}
	if (|a := func()|) {
		doSomething with a
	} else {
		fail();
	}
	
	;; retries until func succeedes
	while (!|func()|) {
		change something;
	}
	
	
	a := func1();
	b := func2();
	|e: MathError| {
		handle any error but no access to local variables
	}
	# continue execution from here a, b may be initialized to default values
	<=>
	{
		a := func1();
		b := func2();
		|e: MathError| {..}
	}
	<=>
	try {
		a := func1();
		b := func2();
	} catch(MathError) {
	...
	}
	
    || break "All errors must be caught"
}
```



## Structs

No ctor, no copy/move ctor, but dtor, copy can be disabled

```xy
struct Name
implements FileLike
;; docstring
{
	fname: FType = defaultValue; comment
}



interface FileLike
;; docstring
{
	def read(FileLike) -> bytes;
	def write(FileLike, bytes) -> void;
}

assert file'implements(FileLike);

struct Point{
	x : uint32;
	y : uint32;
}
p := Point(x=0, y=5); # NO! We want separation!
p := Point{x=0, y=5};
p := array{x, y}
p: Point; # var with default arguments
p := Point();
```

## Arrays

```xy
;; Array Literal
@{1, 2, 3}
or more explicitly
int[4]@{1, 2, 3}

;; Array Comprehension
@for(i in ..) ...

;; List Literal
List~int@{1, 2, 3}
or
existingLIst@{1, 2, 3} so we append
a @ elem;; append element
a @= elem;
a @= {1, 2, 3}

;; list comprehension
List~int @ for(i in ...) ...

int@[4]{sdfsd}
int@{sdfsdf}
[4]int@{sdfsdf}
[]int@{sdfsdf
[4]int@{123}
[4]int
int[5]
[4]
get(4)
[4]@{sdfsd}
int[]
[]int@{sfd}
Arr[4]
get(Arr, 5)
MyObjects[ptr]
Obj[ptr]
def x
@int[4]{sdfsdf}
@int[4]
@List~int{0, 1, 2, 3}
@{0,1,2,3}
@int[4]{1,2,3,4}
```



## Tags

A mechanism to attach a compile-time known value or Class to a struct, func, variable. Multiple tags can be attached to a single object. Attaching tags can be positional or named. But accessing tags is always using a name. Just as args can be passed positional or named by accessing them is always using a name.

```xy
struct EntryPoint {}
def main~EntryPoint() {
}

struct MyStr~[xyCopy=false] {
}

~ is the highest precedence operator so
a := -a~Tag <=> a := -(a~Tag)
a~Tag-b <=> (a~Tag) - b <!=> a~[Tag-b]
```

Strings in tags are treated differently. Problems is runtime strings are glorified pointers compile time strings don't have addresses. So they are treated differently with the help of a special type `xy.ctti.str`.

## Selection based on tags

```xy
# def                 matches
def f(a: Type~Tag1) - Type with Tag1
def f(a: Type~Tag2) - Type with Tag2
def f(a: Type) - Type with any tags or no tags
def f(a: Type~[]) - Type with no tags
def f(a: Type~[!units]) - Type with no units but other tags are still allowed

a := Type{};
f(a);
# the matching algorithm with go though all functions called f and compare the parameters to the provided arguments one by one. At each step it will match the most general one. So in this case it will match f(a: Type).

def f(a: T1, b: T2~[Tag1, Tag2])
def f(a: T1~Tag1, b: T2)

a := T1~Tag1{};
b := T2~[Tag1, Tag2]{};
f(a, b) # will match def f(a: T1~Tag1, b: T2) because a is first compared agains the parameters of the function list
```



```xy
def main() {
	funcs = def~EntryPoint();
	func = callback'def(args)
	funcs = def(
		tags=EntryPoint, positional=[?, Tag2], named=[name=5], args=(Str[]), 					returns=RType, exact=Yes, min=0, max=1
	)
	funcs = def~[?, Tag2, ??, EntryPoint, name=5](Str[]);
	assert funcs'len<=1, "Too many entry points", funcs
	switch (funcs'len) {
	case 0: don't generate anything
	case 1: generate call to funcs[0]
	} else {
		generate error
	}
	entry_points = def~[??, EntryPoint]()
}
```

## Injection

```xy
;; command line args need to be injected because Str is a std lib type

def cmdArgs~Injector -> Array~Str {
	???
}
```

## Flags

```xy
struct OpenFlags~BitFlags {
    append := ...;
    read := ....;
    write := ...;
}

flags := OpenFlags{.read, .write, .append};
open("file.txt", .flags);
open("file.txt", OpenFlags{.read, .write});
open("file.txt", OpenFlags.read | OpenFlags.write);
open("file.txt", OpenFlags.read);
open("file.txt", OpenFlags.read | OpenFlags.write);
open("file.txt", .read | .write);; Auto convert to OpenFlags

.read is called UnboundFlags

def open(s: Str, flags: OpenFlags);;
```

## Enums

```xy.
struct CpuType~Enum {
	x86;
	x64;
	arm;
	power;
}

semantics are the same as Flags but only one can be active at a time i.e. no | operator
```

## Multiple Assignment and Return Values

```xy
def func(x: uint) -> (y: uint, z: uint) {
	return (y, z);
}

x = func(5); # Ignore z
(x, _) = func(5); # Equivalent
(x:, y:) = func(5);
(x:, y: var) = func(5).(y, x);
x := Struct{a=6, b=10, c=SubStruct(d=10, e=5)};

func(5).(x, y)
func(5).(x, y)
```

## Tests

```xy
def testAdd~Test() {
	assert a == b; is equivalent to ->
	assert(a == b, "a", a, "==", "b", b);
}
```

## Numbers

```xy
123
0xFAE
0b1111
0b123333
0AnyStringYouLike(36)
0xFFAF(36); the 0x part is interpreted as part of the num because of the (36)
```

## Bit Operations

```xy
a'bits and b'bits; binary and/or
a'bits or 1; turn all bits to 1
a'bits and 0; turn all bits to 0
a'bits xor 1; flip all bits aka bit-wise not
a += 1;
a xor= b; a = a xor b;
a call= b; a = a \call b;
```

## Logical Operators

There must be symbols for the logical operators and, or because they are used very often and it simplifies the visual parsing

## Symbols

```xy
! not
@ (maybe dot?) or reverse func call notation (array creation)
# (maybe comment? or cardinality)
$ select
% typeof
!= (xor) we don't need a symbol for xor
^ expression in caller context
& (and)
&& (may be used to suppress errors?)
* (mult)
** (power)
| (or)
|| (may be used as a parallel operator)
> (greater than)
< (less than)
~ (bind ctti)
`char`
"string"
;; doc comments
=> is the move operator
=< is the move operator in the other direction
$func() # select

|e: MathError| {
	if ( (a & b))
}
>> input guard
<< output guard
|| on-return-or-error
|return| on-normal-return
|error| on-error
in(obj or module) { code; }

Available:
->   <-
-<   >-
<>
><

<< >>
!!
?
??
@func() #
[+][-][*][^][@]....
(+)(-)(*)(^)(@)....
{+}{-}{*}{^}{@}....
<expr> - triangle brackets. Can be easily parsed without the need for backtracking.
@> - rose operator/flowers operator
@=
[[ ]] (playes with your eyes)
{{ }} (playes with your eyes)
::
<% %>
<: :>
%:
<>< - something is fishy
;; ><> or <>< - mark fishy/smelly code
!func()
/ unary

keywords:
def, with, macro
switch, case, as, static,
```

## String

Xy has completely delegated support for string to external libraries. It only supports string literals, which can be either ASCII or UTF-8 encoded.

```xy
"abc" is shorthand for def~StringCtor{prefix=""}("abc"'addr, size("abc"))
c"abc" is shorthand for def~StringCtor{prefix="c"}("abc"'addr, size("abc"))
char"a" is shorthand for def~StringCtor{prefix="char"}("abc"'addr, size("abc"))
res := f"abc{num}{res.4}" is shorthand for formated i.e.
tmp := def~StringCtor{prefix="f"}()
tmp'sizeHint(3)
tmp'append("abc")
tmp'append(num)
tmp'append(res, 2)
res := tmp'as(String)

String interpolation cannot be parsed without knowing all of the preficies so this breaks this idea!

"abc{name, 5}"
"abc{name, ".2f"}"

sb"abc{name}{age}"
<=>
sb := stringBuilder()
sb'append("abc")'append(name)'append(age)
output := sb'asString

a := "abc" <=>
json"{a=5}"

len() is the number of codepoints in the case of utf8 maybe codes

"Your name is {name}"
"Your name is {= name}"
"Your name is {.2f name}"
"Your name is {name ".2f"}"
b"{name, 4}"
b"abc{name, 5}"
"{name:int}{age:int, 5}" = inputString <=>
name := inputString'read(int, 5)
age := inputString'read(int, 5)
b"{header: uint, 4~Bytes}{version : ushort, 2~Bytes}" = mem
header := mem'read(int, 4~Bytes)
version := mem'read(ushort, 2~Bytes)
Ptr~Type{type}~Type
def str~StrCtor{prefix=""}()

c"string" -> no interpolation
"string" -> no interpolation
f"interpolation"
r"regex" -> no interpolation
a"scii string" -> interpolation
f""

Always interpolation. But can be disabled in the string ctor
```

## Slicing and Indexing

```
c[a:b] <=> c'get(slice(start=a, end=b))
c[a:] <=> c'get(slice(start=a))
c[:b] <=> c'get(slice(end=b))
c[a::s] <=> c'get(slice(start=a, step=s))
c[:] <=> c'get(slice())
c[a:b, d] = v <=> c'set(slice(a, b), v)
c[a:b, .atom] = v <=> c'set(slice(a, b), .atom, v)
a:b~Kelvin:c <=> slice(a, b~Kelvin, c)
```

## Units

```xy
deg : uint~Kelvin = 0; we want the kelvin part to strippable

a := b~Kelvin * 5 ;; will produce just int
a : ~Kelvin = b * 5 ;; will attach the Kelvin to b
a := b~Degrees'to(Kelvin) ;; will convert and attach the Kelvin label
def dispersion(y: uint~Kelvin, y: uint~Kelvin)

a : uint~Kelvin = 0;
b : uint~Celcius = b;
c : ~Radians = a * b ;; will not produce an error. Units are left completely to the developer
```

## Variables

```xy
<name> : <type> = <value>
a : int = 5;
```

## For iteration

```
for (i in arr) <=>
for (it := &iter(arr); valid(arr, it); inc(arr, it))

for (k := arr'keys) <=>
for (it := &keys(arr); valid(arr, it); inc(arr, it))
# Note that keys must be marked as IterCtor

# How about compiling the following ???
for (k in arr'keys(.name > 5); )

# examples:
for (e in arr) -> (sum: int = 0) sum += e
for (e in arr) -> (sum: int) sum += e
arr'sum
arr @ [1]

for (k in d'keys) <=>
for (it := &d'keys; d'valid(it); d'inc(it))

for (k in arr[m:n]) <=>
for (it := &arr'iter(m:n); d'valid(it); d'inc(it))
```



## Func Pointers and Callbacks

```xy
cb := func'def(int, int)
cb(5)

def cb(int, int) -> int;

struct {
	cb: %cb;
	str: %makeStr
	str: %makeStr(Int, Int)
	str: %""
	str: %b""
}
```

## Indices

```xy
struct Point {
    coords: float[3];

    x: pseudo = XField{};
    ...
}

struct XField {}
...

struct XYField {}
...

struct XYZField {}
...

def get(p: Point, idx: pseudo XField) = p.coords[0]
def set(p: Point, idx: pseudo XField, v: float) = p.coords[0] = v
def get(p: Point, idx: pseudo YField) = p.coords[1]
def set(p: Point, idx: pseudo YField, v: float) = p.coords[1] = v
def get(p: Point, idx: pseudo ZField) = p.coords[2]
def set(p: Point, idx: pseudo ZField, v: float) = p.coords[2] = v

def get(p: Point, idx: pseudo XYField) = [p.coords[0], p.coords[1]]
def set(p: Point, idx: pseudo XYField, v: float) = p.coords[0] = p.coords[1] = v
def get(p: Point, idx: pseudo XZField) = [p.coords[0], p.coords[2]]
def set(p: Point, idx: pseudo XZField, v: float) = p.coords[0] = p.coords[2] = v
def get(p: Point, idx: pseudo YXField) = [p.coords[1], p.coords[0]]
def set(p: Point, idx: pseudo YXField, v: float) = p.coords[0] = p.coords[0] = v
def get(p: Point, idx: pseudo YZField) = [p.coords[1], p.coords[2]]
def set(p: Point, idx: pseudo YZField, v: float) = p.coords[1] = p.coords[2] = v
def get(p: Point, idx: pseudo ZXField) = [p.coords[2], p.coords[0]]
def set(p: Point, idx: pseudo ZXField, v: float) = p.coords[2] = p.coords[0] = v
def get(p: Point, idx: pseudo ZYField) = [p.coords[2], p.coords[1]]
def set(p: Point, idx: pseudo ZYField, v: float) = p.coords[2] = p.coords[1] = v

def get(p: Point, idx: pseudo XYZField) = p
def get(p: Point, idx: pseudo XZYField) = Point{p.coords[0], p.coords[2], p.coords[1]}
def get(p: Point, idx: pseudo YXZField) = Point{p.coords[1], p.coords[0], p.coords[2]}
def get(p: Point, idx: pseudo YZXField) = Point{p.coords[1], p.coords[2], p.coords[0]}
def get(p: Point, idx: pseudo ZXYField) = Point{p.coords[2], p.coords[0], p.coords[1]}
def get(p: Point, idx: pseudo ZYXField) = Point{p.coords[2], p.coords[1], p.coords[0]}

def set(p: Point, idx: pseudo XYZField, v: float[3]) = p.coords = v
def set(p: Point, idx: pseudo XZYField, v: float[3]) = p.coords = [v[0], v[2], v[1]]
def set(p: Point, idx: pseudo YXZField, v: float[3]) = p.coords = [v[1], v[0], v[2]]
def set(p: Point, idx: pseudo YZXField, v: float[3]) = p.coords = [v[1], v[2], v[0]]
def set(p: Point, idx: pseudo ZXYField, v: float[3]) = p.coords = [v[2], v[0], v[1]]
def set(p: Point, idx: pseudo ZYXField, v: float[3]) = p.coords = [v[2], v[1], v[0]]

def dot(p1: Point, p2: Point) = p1.x * p2.x + p1.y * p2.y + p1.z * p2.z

def test() {
    p1 : var = Point{.23, .92};
    p2 : var = Point{.4837, .127, -0.314};
    p3 : Point;
    p1.x = p2.z;
    p2.y = .0;
    p3.zx = Point{p1.x + p2.y, p1 \dot p2};
    p3 = p3.zyx;
}

# List

struct List {
    mem: Memory;
    len: Size;
}

def index(list: List, idx: Size) -> ref(list) Size = idx

def get(list: List, idx: Size) -> ref() Ptr~elemType {
    return mem.addr(idx * elemType'sizeof);
}

def set(list: List, idx: Size, elem: ?) {
    mem.addr[idx*elem'sizeof +: elem'sizeof] = elem'addrof;
}

def iter(list: List) -> ref(list) Size = 0
def valid(list: List, idx: Size) = ...
def next(list: List, idx: Size) -> ref(list) Size = idx+1

for (v in list) {
    # v is unmut only if list is unmut
    print(v); -> print(get(list, v));
    v[0] = 10; -> set(list, v, 10);
}

# Table
struct Table {
}

def index(t: Table, idx: Size) -> ref(t) Size = idx
def get(t: Table, idx: Size, resMem : stackAlloc(elemType'sizeof)) -> ref() Ptr~elemType {
    resMem[:] = t.field[0].mem, field[1].mem ....
}
def set(t: Table, idx: Size, v: ?) {
    set at appropriate value;
}

def get(t: Table, ridx: Size, f: pseudo ctti.Field, fidx: f.num) -> ref(t) Loc
>> if (f.isProperty) break "Cannot access properties";
{
    return Loc{ridx, cidx}
}

def set(t: Table, loc: Loc, value: ?) {
    ...
}

c[idx].field = value
set(c, index(c, idx), Point.x, value)

for (v in table) {
    print(*v); # print(get(table, v))
    v = 5; # set(table, v, 5)
    v.field  = 5; # set(table, v, elemType.field, 5);
}

for (v in table) {
    func(v.field1, v.field2);
    func(get(table, v, field1), get(table, v, field1)); # errors get(..) is not on the stack move it. get(table, v, field) is not on the stack. Move it
}

# Array

struct A

# ------------ Fib Exampe -------------

struct FibIter {
    a := 0;
    b := 1;
}

def fibonacci~IterCtor() -> ref() FibIter = FibIter{}

def valid(fib: FibIter) = true

def next(fib: FibIter) -> ref() FibIter = FibIter{fib.a + fib.b, fib.a}

def get(fib: Fib) = fib.a

for (fib in fibonacci()) {
    print(fib); # print(get(fib))
    print(&fib): # print(fib)
}
```

## Funcs

* **Argument** - a value given  to a function 
* **Parameter** - A variable that holds the argument value given to a function.

A function is called with arguments i.e. values given to that function. Once in the function body we don't have access to the original arguments just the parameters i.e. the variables that hold the arguments. The type of an argument must be compatible with that of the corresponding parameter. This is guaranteed by the language. However extra tags carried by the arguments will be ignored at the point of a function call. These arguments may be relevant to the function. To provide a mechanism to handle them the following rules apply:

* In a parameter type expression any previously defined parameter name that appears is treated as a parameter i.e. cannot carry additional knowledge than what is defined for the parameter.
* In a default value expression any previously defined parameter name that appears is treated as a argument i.e. it may carry additional knowledge than what is defined by the parameter.
* In a return type expression parameter names refer to the arguments.

#### Func Call Algorithm

1. Arguments are evaluated left to right
2. The correct function is selected based on the types of the arguments and the function name
3. Any default arguments are evaluated in the callee context left to right as they appear in the function definition
4. The input invariances are evaluated and/or runtime checked in the callee context
5. Any argument dependent return type tags are calculated
6. The function is called
7. The function result is checked for an erro
8. The output invariances are evaluated and/or runtime checked in the callee context

## External Libraries

A programing language should account for both communication with the external worlds and for the external world to communicate with it

```xy
import posix~[CLib{headers=[c"unistd.h"]}] in c
import libc~[CLib{headers=[c"errno.h"]}] in c

plugin = open("my.so", DynamicObject)
fn = open'get("init")'as(def(int, int)->int)
res := fn'call(5, 5)
```

## Name ambiguity resolution

```xy
import a
import b
import a.x
import b.y ;; implicit as y in .

def func() {
	return compute() ;; Which one is it?
	return a.compute();
	return a.x.compute() ;; Doesn't work because the parsing would be a'elem(x)'elem(compute) and there is no symbol a
	return x.compute()
}
```

## Visibility

```xy
def -x()=... => module visibility
def +x() => project visibility
def x() => project visiblity the plus is not required as in math
def ^x() => public visibility
```

## References

```xy
def index(p: Point, idx: byte) -> p[byte] ... p[byte]
def index() -> ref(arr) int
def index() -> ref(arr, int)
def index() -> ref(arr, int)
def index() -> [arr] int

p[byte] - looks too much like an array
p.byte - looks like a member field
p.[byte] - forget one dot and everything goes haywired
[byte](p)
[3]
I think original syntax is still the best ref(p) byte
def index(p: Point, idx: byte) -> ref(p, .chain) byte
def index(p: Point, idx: byte) -> byte ref(p)
def index(p: Point, idx: byte) -> &p byte
def index(p: Point, idx: byte) -> &byte(p)
def index(p: Point, idx: byte) -> &byte[p]
def index(p: Point, idx: byte) -> [p] byte

def index(p: Point, idx: byte) -> ref(p) byte
def index(p: Point, idx: byte) -> [p] byte
def get(arr: Array, idx: byte, column: pseudo ctti.Field, offset: column'offsetOf)
def get(elem: [arr: Array] byte, colomn: pseudo ctti.Field, offset :=...)
def get(elem: ref(arr: Array) byte, column: pseudo ctti.Field)
def get(arr: Array, i: [arr] size, column: pseudo ctti.Field)
def get(arr: Array, elem: ref(arr) size, column: pseudo ctti.Field)
elem => arr[elem]
def get(arr: EEEE, elem: 3, arr'refof, &arr)

def get(elem: ref(Array) size, column: pseudo ctti.Field, arr: Array = elem'refof)
def get([arr: Array] i: size, col: ctti.Field)

def get(arr: Array, elem: ref(arr) size) {
	arr[i], arr[i]
}

def get(arr: Array, elem: ref(arr) size) {
}

def get(elem) -> byte~Ref{p, decay=false}

def get()

def get(arr: Array, i: size, column: ctti.Column)

def get(get(arr: Array, i: Size), column: ctti.Column) 

def get~.decay=no(i: size~Ref(Array), column: ctti.Column)

def get(i: Size)
def get(ref i: Size)
def get(ref(arr: Array) i: Size, col: ctti.Column)

non pointer refs don't decay

it's not about decay. It's about chaining gets

def get~[.chain] maybe all gets should be chained?

def (i: ref(arr) Size, col: column, arr: Array)

color[0].x.y[z] = 0
def get(
) -> ref(size) Size

triangle[0].x = 10
get(triangle, get(triangle, 0), .x)

triangle[0].y = 10
mesh[i] .= {x, y, z}

triangle[0].y = 0

triangle[0]

def get

get(color, 0)
get(^, x)
get(^, y)
get(^, z)
set(^, 0)

if we get a point than it is decayed immediatelly to the appropriate value

gets are always chained

ref a := b

-> ref(a) Size
def get()

arr[i].field

def get()

refs are always chained unless we get a pointer which is fairly easy to collapse

def(arr: Array, elem: ref(arr) ElemType)

def(arr: Array, elem: ref(arr) size)

print(elem) => print(arr'get(elem))
elem++ => inc(arr'get(elem))

def(arr: Array, elem: (arr: Array, i: Size)->ElemType)

-> arr[Size->ElemType]

get(elem: ref(arr: Array) Size, )

the reference can never be modified
the referenced value can be modified but only if the container can be modified
def func(arr: inout Array, b: ref(arr) Size);
func(arr, arr[i], b: ref(arr) Size)

refs are weird because they require 3 thing
1) another variable as the container
2) type of the reference
3) type of the referenced object

def func(p: inout Person, name: ref(p) ctti.Field don't know the type, name2: ref(p) String)
// I want to point to String but don't know the exact reference type exactly
func(p, p.name, p.lastName)
func(p, p.lastName, p.name)
```



## Conditional Compilation

```xy
def func~[disabled=platform.linux] ???
```



## Principles and observations

* Operators must be symbols in order to help with visual parsing
* There must be destructive/mutating operations because this is how computers work - filesystems, databases and so on.
* Command separated expressions (arags, incl. kwargs) are evaluated left-to-right. If all the expressions are non-mutating than the expressions can be evaluated in any order.
* Object references are bad because it creates a web of interconnectedness. OOP makes referencing objects easy. This is a step in the wrong direction.
* Parser just parses not transformations
* KISS
* Metaprogramming leads to two in one language i.e. one language that is interpreted by the compiler and generates the code that is in a different language. Just create one language and be done with it.
* No selection based on tags because function mangling becomes too difficult.
* Minimal code generation because otherwise it gets too complicated and slow.
* Code is communication - with the hardware, with the compiler and with the developers.
* General algorithm for solving problems:
  * Identify input data
  * Identify output data
  * Convert between the two
  * Maybe slip the conversion process into multiple steps each one is also a conversion.
  * Questions: what happens with data from any previous step? Don't change it! If you need it copy it. that leads to many copies how do we fix those. The compiler should do the copying only if it is needed. 
* Multiple output because nodes have it and it is very useful
* Humans are goal oriented. Language should reflect that! Is that true! When coding you want the code right

## Config files

### Declerative Approach

* a markup or markdown format (i.e.` yaml`, `.md`, or custom formats like `puppet`) are great for shorter examples but get increasingly difficult as the scope grows.

* Using `.xy` as a markup language is doable but kinda has the same problems as other markup languages. Not to mention the fact that structures which are not built into the language (like dynamic arrays and dictionaries) are fairly difficult to describe

* `+` We can generate fairly efficient code

* `-` Difficulties debugging and significant complications to the compiler/builder

### Imperative Approach

   * Very clunky doesn't feel great

### Imperative disguised as declarative

   * Similar in spirit to infrastructure-as-code. Should get best of both worlds but we get.

   * `-` Runs runtime so there may be a bit of a penalty

   * `-` Feels kinda shitty like we are doing the imperative approach but dressed in a prettier dress. 

## PRINCIPLE! Configuration as code

It would be great if we can choose if we want to run and parse the config runtime or compile time.

Example:

```
# run apt update
aptUpdate := exec("apt-update",
    command="/usr/bin/apt-get update"
)

# install apache2 package
package("apache2",
    require=aptUpdate, 
    ensure=installed,
)

# ensure apache2 is running
service("apache2",
    ensure=running
)
```

This generates a config which we then apply somehow. Like calling `apply()`

The generation is at run time. But can we move it to compile time? The answer is No because the config can have a very complicated way of being represented. So we have to call some functions. So it is the same.

What we can do is generate code but code generation is a completely different subject IMHO.

That idea sucks! How are we going to write simple configs like ini files. Are we really going to compile stuff?



Can we describe the CLI api in a config. Yes we can but so what. We need code. Not configuration, not a bunch of values we reed of somewhere. We need structs and stuff. I hate code generation. Code should be easy to instrument tought.

```
struct Args{
	k: str;
	verbosity: int;
	command: Command;
	build: Build;
	init: Init;
}

def parseArgs(p := ConfigParser{}) -> (args: Args) {
	p'var(args.k);
	p'var(args.verbosity);
	p'var(args.command);
	# does the following
	#command : var str;
	#p'var(command, enum=["build", "init"]);
	#args.command := switch(command) case("builder") Command.Build case() Command.Init;
	if args.command.build?
		p'var(args.build)
	else
		p'var(args.init)
	p'var() # DOESN"T WORM we don't know if we should stop or continue when we encouter build or init. We could keep the addresses but that is just asking for trouble.
}
```
It appears we have two options 

1. Parse the elements one by one using a huge if/else a.k.a. getops wich disconnects the documentation from the parsing too much for my tast.
2. Describe the configuration. And then parse it using the description.

3. CTTI for an entire dependancy tree.

```xy
# With a markup language you don't need a schema you can just run. With a cli you need a schema
def cli(p: Parser) {
	k := p'str("k", desc="Expression");
	v := p'int("v", desc="Increase verbosity");
	build := p'sub("command", value="build");
	p'int("..", sub=build)
	init := p'sub("command", value="init");
	p'int("..", sub=init)
	. one possibility is to simply generate source code.
}

and then

args.k = p[k]
args.v = p'count[v]
```

```xy
First a markdown chich is like the schema. Then:
```

```xy
def loadArgs() {
	p.cli(."file"))
	p.parse()
	args := Args();
	p'conf(args.k);
	p'conf(command);
	args.command = command # so we repeat command 3 times!!!
	p'command("build", args.build)
	p'load(built)
}
```

```xy
def config(p := Parser, args: Args) = cli.autoconfig(p, args)
p: Parser()
p'config(args); # we do that here
p'parse(args);
p'auto(args);

def auto(p: Parser, args: pseudo ?, _ := p'autoconfigure(args))) {
	for prop in p.props:
		args.at[i] = p[];
}

def autoconfigure(p: inout Parser, args: pseudo ?, desc=[p'buildDesc(f) for f in args'fieldsof]) {

}

def buildDesc(p: inout Parser, name, comment, ) -> void
```

```xy
For each type a need a parser.
```

It is just very difficult to happen automagically. We sould have some sort of conversion.

p'config(args.k);

p'config(args.v);

p.parse();

p'load(args.k);

p'load(args.v);

p'load(args.verbosity);

## Principle: Keep the compiler to a minimum use the language to resolve issue (like entry point selection)

## Per Struct Static Functions

Usecase: stuff like struct ids

```xy
struct Obj {}

def describe~Injector{static}(:Obj) {
}

def desribe := autoDescribe(:Obj) {}

# we use the default expression as a form of auto generation which is shitty
def autoDescribe(:?, res := [for (f in fieldsof) Descriptor{}]) -> Description {
	# add to container
}

def autoDescbie(p:, res := rtti(%p, ))

def auto := auto

def describe(:int) {}

# And then
p := ArgParser{}

p'parse(Obj)

def parse(p, obj: ?, description := desribe(obj, container))
```

 Conclulstion for parsing command

Neither .md, nor .yaml are sutable for this. Significant compromises must be made either way. So config as code seems to be the best option for now.

`fieldsof` cannot return an iterator or a special type because it won't work with for loops. If we want for loops than we must have an array or something homogeneous.

## Callbacks

```xy
struct Def {} an actual function. The type is compile time only. Not a function pointer. Something much more.

func(a, b, c) => (def func(%a, %b, %c))(a, b, c);
				 # The types here are int, double etc. At calltime we do the actual conversion to inouts and pseudo and so on.

struct Api {
	get: def(int, int)->(int); # not allowed because def is CT only
	get: Ptr~[def(int, int)->int];
}

api Http{
	def get(int, int) -> int || error;
	get: def (int, int) -> int || error;
	get: Ptr~[def(int, int)->int]
}
```

We need 3 things:

* Type that defines a callback

  ```xy
  x: def(int)->int||Error  # All of these are needed
  y: Ptr~def(int)->int
  ```

* A way to find an appropriate function based on name and or tags, param types and probably return type

  ```xy
  x := def name(int)->int
  y := def~Tag(int)->int
  z := def name~Tag(int)->int # the '-> int' is optional
  ```

* A way to all all approparite functions based on param types and maybe return type

  ```xy
  x := def (int)->int
  y := def~Tag(int)->int
  ```

* A way to check if a specific function corresponds to an api (we need that for auto discovery)

  ```xy
  def testAdd~Test -> void || Error {
  	\assert a == b;
  }
  ```

Alternatives: No indirection. Just a giant switch statement. What about c interop

Idea: A generalized syntax for generating table data:

```xy
struct Type {
...
}

struct TypeDesc {

}

descType
descVar
descTag

struct MyDescription {
}

def type(:MyDescription, );
def var();
def tag();

idx = rtti(MyDescription, Type);

MyDescription.types[idx]
MyDescription.types[idx]

struct TypeDesc {
	user: UserData;
	args: ...;
	tags: ...;
}

TypeIdx;

rtti(Type, TypeDesc);
for (arg in d.args) {
	type = rtti[idx];
}

Just types alone form a graph and they are completely non trivial. So it is normal to be difficult.

rtti desc(type) Desc{
	name =,
	fullname =,
	...
}

rtti desc(var) Desc{
	name =...
}

rtti desc() # maybe just the idea is wrong

# this idea is just shit to begin with
struct CliArgs {
	;; enable verbose output
	verbose: bool;
}

cli[
	;; enable verbose output
	verbose: bool
	
	arg(type=Bool, comment="Enable verbose output")
]

verbose = cli.int("verbose", "Enable verbose output")

verbose'to(int)

args := {
	verbose=cli.int("verbose", Enable verbose output"),
	vs=cli.count("v", "Increase verbose output")
	args=cli.strs("List of ints"),
	_ = cli.finish(),
}

This RTTI is just garbage

# PRINCIPLE: All grograms convert data from one format to another
what is the input data:
	a description of arguments ...
what is the output data:
	values ...
	
def parse(CliParams) -> CliArgs
CliParam := [cliParam]

CliArgs := methods {
	getInt
	getLong
}

CliArgs := methods {
	
}

```

```xy
options := Option[][
	{name=...},
	{name=...},
	{name=...},
	{name=...} as x,
	{name=...},
	{name=...},
	{name=...},
]
dict := [
	"item1"={name=...},
	"item2"={name=..., option=x},
]

OK but what if I want to work more like first the group than the options for that group

options : Option[];
groups : Group[];

push:
options << x
options << xxx

def (int, int, int) -> int

@(int, int, int)->int
$(int, int, int)->int
$*(int, int, int) -> int
$+(int, int, int) -> int

(:int, :int, :inout int) -> int || Error  # This is the type type
$ (int, int, int) -> int # this is looking up for a function
$ module.symbol(types, ...) find symbol from module
$ symbol(...) find symbol here, if not found, find in global context
$ module.(type,) find in namespace module
$* ~Tag(....) # find all with tag in current namespace
$* ~Test()->void||Error
$* ~Test()->void||Error
$ symbol()
$ ~Test()
[for (f in $* ~Test()) f'to(()->void||Error)'addrof]

def parseNormalFile~Test() -> void || Error {
}

def positiveInts~Test() {
	@assert a == b
	@ssert
	@ssert a == b
	@ssume a == b
}
```

```xy
Calling a callback
cb := $name~tag(type1, type2);
(cb)(type1, type2); # no need for that as these callbacks are usually stored in an expression

struct.cb(type1, type2);
.cb(type1, type2);
self.cb(type1, type2);

Select and adapt
no need for adapt just 
```



## Language for data structures:

* Add/Create

  ```xy
  d[key] = value # when we know the key => set(d, key, value)
  d[] = value # when the key is auto gen? => set(d, value)
  d[next] = value
  d[...] = value
  d[] = value
  d[] = value
  d[] = value
  
  options = (Option[])[
  	name: ref = {a="b", c="d"},
  	idx: ref = {a="b", c="d"}, => idx := options'push(Option{...}),
  	[idx] = {a="b", c="d"}
  	[index] = {...","},
  	{....},
  ]
  
  groups := Group*[
  	
  ]
  
  := e
  ```

* Remove

  ```xy
  d[next]
  d[idx] = void => del(d, idx)
  d[idx] = void
  d[idx] => void
  ```

* Substitute

  ```xy
  d[idx] = x
  d[idx] =<> b[idx]
  ```

* Update

  ```xy
  d[idx].field = 3
  d[idx].field = 4
  ```

* Dtor

  ```xy
  del d[:]
  ```

  

* Define

  ```
  options := *Option[
  	[name] {xxx="sdfsdf"}
  	[name] {}
      [    ] {sdfsd}
  ]
  
  options : Option$
  
  struct {
  	options : Option$[4]
  	options : Option$(4);
  	options : Option$4$5;
  	Person$ 10;
  }
  
  
  x: Person$
  
  options : [4]Option = Option$[
  	{...} [name],
  	{...} [name],
  ]
  
  config: Config = Option$;
  
  shorthand $ = Vector
  
  Option$
  
  options := Option$[
  	
  ]
  
  shorthand $ = Vector
  
  $ = Vector
  shorthand $ = Vector
  shorthand $ = Vector
  shorthand $ = Vector
  
  x : Vector$
  y : [Key]->Value
  y : Dict~[Key, Value]
  x :
  
  a [func] b
  a [+] b
  a [+] b
  a [=] b
  a (+) b
  a (x) b
  a (c) b
  a {+} b
  b {+} b
  
  [func](a, b)
  
  a [\func] b  parallel
  or maybe go
  or maybe
  
  for[>] 
  
  a {+} b
  
  vec [\push] int$[
  	4, 5, 6
  ]
  
  vec [+] int$[
  	
  ]
  
  vec [+]
  vec [-]
  vec [+] int$[
  ]
  
  vec [+] int[][]
  
  vec [+] [
  	Option$
  ]
  
  vec := [
  	....
  ]
  
  vec [+] [
  	[+]
  ]
  
  [+] => addAll
  [-] => subAll
  [+] => extend
  [-] => shrink
  vec [-] [1, 2, 3];
  [vec] => derefing a pointer
  vec[3] => derefing a pointer
  [vec + 3] => derefing a pointer
  
  [vec] [+] [1, 2, 3]
  [*]
  [^]
  (+) 
  dict[:] *= 3;
  dict[:] *= 3;
  
  def mulEq()
  def mulEq()
  
  dict [+] [
  	....
  ]
  
  dict : var;
  operation + 3
  a [+] b;
  a [*] b;
  a {*} b;
  a (*) b;
  c [+] b;
  
  operator+
  def [+]
  def [[+]]
  def operator[]
  def set
  def set
  def operator[]
  def operator[]=
  def operator[]*=
  def operator()
  def operator[]*=
  xy_module_operatorAdd
  xy_module_operatorAdd
  def operato+-
  xy_module_operator
  def operator*+(a, b, c) => a * b + c
  def operator*
  operatorAdd
  def xy_module_
  def xy_ops_module_add(a, b, c)
  def module_add(a, b, c)
  def module_add(a,)
  def operator[+]
  
  dict [+]
  dict [-];
  [-]dict;
  dict[-];
  dict[-];
  dict[+];
  x: int*;
  shorthand operator(*)(int) = 
  def operator*(:int) = Array*int{}
  x: int$
  def operator$()
  
  operator$(:?) = Vector~[<< :?]
  operator*(:?)
  operator^
  ```

  

## Group definitions of structures

```
struct {
	struct Person {
		name: Str;
		bdate: Date;
	}
	
	students: List~Person;
	
	struct Class {
		enrolled: List~[students[uint]];
	}
	
	classes: List~Class;
	
	struct 
}

struct CliArgs {
	struct ArgDesc {
		name: Str;
		prefix: Str;
		group: ref(groups[uint]);
		group: groups[uint];
		group: ref(grups) uint;
		group: uint ref(groups);
		group: [uint] in groups;
		group: [uint] groups;
		group: ref(groups) uint;
		group: ref(groups)[uint];
	}
	
	struct Group {
		name: Str;
		args: List~[ref(groups) uint];
		args: List~[ref(groups) uint];
		args: List~[uint [] groups];
		args: List~[uint [groups]];
		args: List~[ref(groups) uint];
		args: List~[[groups] uint];
		
		name: [strings] ulong;
	}
	
	args: List~ArgDesc;
	groups: List~Group;
}
```

## Asserts

```xy
assert a == b
what we need is the values of
a == b
f"{a}"
f"{b}"
diff a b

def assert(a == b, a == b, a, b, diff a b)

def assert_eq(a, b, )
assert(a == b); => assertEq(a, b);

expression sdf: assert(a == b) assertEq(a, b)
macro assert(expr: BinExpression) {
	if epxr'op == "==" {assertEq(expr'arg1, expr'arg2)}
}

a == b in the context of assert should be
Cmp(a == b, f"{a}", f"{b}", Diff(a, b) if a and b are not equal)

def assert~[context=contextWhere==IsOverwritten]

def a == b

def emptyStr~Test {

}
the Test provides the context for the write operators

import xy.builtins
import xytest

maybe the order of the imports?

def assert(!cond: bool, v := a'!to(Str))
v := a'@to(Str)
!(sdfsdf)
v := a'to!(str)
a'to!(str)
def (cond!: bool)
!cond
a'to!(cond)
$(sdfsdf)!!
a'to!!(cond)
def assert(cond!: pseudo bool)
cond: bool => create a parameter called cond
cond: bool = cond!!
a'to!!(cond)
a'to!(cond)
bool: cond!
cond!
!cond
cond!
a <> b
<> a;
$to(int, int)!
a!'
-> Ptr[a!..elemType]
#a
%a
^a
^a
)

^a..elemType
^a..elemType
a'^to(Str)
^(sdfsdf)
^a'to(Str)
^a
^Str
a'^hash(int)
b := a)
b := ^a
a'^hash()
^list..Types

def assert(cond: bool, src := srcof(^cond), line := lineof(^cond)) {
}
```

## Fields

```xy
struct Struct {
	age: int;
	name: String;
}

Struct.age => Field~[name=..., offset=..., ] {}
Struct.name.ptr => Field~[name=..., offset=offsetof(name) + offsetof(ptr) in String, ] {}

struct A {
	struct B {
		a: ref(cs) int;
	}
	
	struct C {
		
	}
	
	cs: List~C;
	b: B;  # cannot separate the b from the rest. Have to do a
	bs: List~B;
}

a: A;
a.cs'append(a.C{asdf})
a.b = a.B;

A.B{0}.a; ! Now what
a.B{0}.a; B

a.bs[10].a ! Now what => a.bs[10] => a.B => a.B.a => get(a.cs)

A.B.a

A.B.a => Field~[offset=a in B]
```

## With Statements

The with statement says that a block of code will make use of all the fields of a structure. Usually this is a way to ensure that if a new field is added old the appropriate code will be updated. It also allows for mapping a function across all fields.

```
with (Struct) {

	# all fields must be touched or an error is reported.

	# alternatively _ can be used to idikate that remeaning fields are not required.

}

with (Struct) {
	func(_); # _ will expand to func(field) for every field that hasn't been touched
}

with (val) -> (out: Struct) {
	out._ = func(_); # will generate out.field = func(field) for each untoched field in val. In this case it will be all of the fields
	out = Struct {
		_ = func(_); is an alternative syntax
	}
}

with (val) -> func(_) is shorthand for
with (val) -> (out: %val) {
	out._ = func(_);
}

def copy(s: Struct) with(s) copy(_); this is how we implement a per field copy

basically with says I want to use all the fields. To be read with *all the fields of*(val)

maybe we can do a with any(val) or with any(val) call(...);

shorthand with(val) func(_) = 

This is the opposite of Struct{
fiel=val,
field=val,
. # all fields have been specified
}

and with is all fields have been used
```

## in Statements

Mnemonic: in the con

```xy
tree: Tree~Nodes;
varDecl := tree'make(VarDecl)
in (tree) {
    [varDecl := 'new(VarDecl)] .= {...}
    [varDecl] .= {name=..., value=..., type=...}
}
```

## Data Literals

```
# Struct Type Name

StructName

# Struct Literals

StructName {
	field1=value,
	field2=value,
	....
}

# Array Type Name

StructName[4] # 1d array Notice the single expression in square brackets
StructName[4][5] # 2d array
array_type ::= <expression>[<expression>]

# Array Literals
int[]{Value, Value};
int[2][value, value]; # alternative notation
[value, value]; this is deref

# List Literal
List~int[1, 2, 3]

# Array Literal
Dict~[Key, Value][
	"key"=value,
]
```

## Binary Strings and Matchers

```
b"{a}{b}" # creates a binary string with a and b accoriding to their leng

b"{a: int}{b: int}" = b"..."
-or-
b"{a}{b}" = binary
=>
tmp := BinaryReader{}
a: int;
read(tmp, a);
read(tmp, b);

s"{a:int} name is {b: Str}" = line;

read(a, line);
readCodepoints(10) == "name is ";
read(b, line);
```

## BE BOLD

## No selection based on tags because it gets extremely complicated

## Str in this context means just the Str with any tags stripped. because we don't know them.

## Array of Tables

```xy
array of tables optimized for iteration and indexing

data := Aot{};
it1 := data'table(Struct1);
data'attach(Struct3, to=it1);
it2 := data'table(Struct2);

def new(VarDecl) {
inode := data'new(it1); has type IElem~Struct1
data[inode];
data[data'index(inode, Struct3)];
['index(inode, Struct3)]
}

def table(aot: Aot, type: struct, desc := describe(type, AotTypeRtti)) {

}
```

## private parameters:

Private in the sense of `Designed or intended for one's exclusive use.` or `Of or confined to the individual; personal.` 

```xy
in - we copy i.e. =
out - we move i.e. => or =<

a := 5;
func(a);

list.append("str") append gets in i.e. copy; "str" is tmp so no need to do any copying
list.append(a) copy; a is not tmp so we do a copy unless a is never used after.

sum(list) sum gets in i.e. copy; list is not tmp so we need to do a copy unless list is never used after, but it is. so we do a copy.

The need for a copy is determined by the function. For example append does an internal copy so we need to express this in a way different than checking if it is trivially copyable and manually doing the copy otherwise which is very error prone.

Version 2)
in - we move in but not out
out - we move out but not in
inout - we move in and out
var or mut - we define mutability

list.append("str") append gets an in i.e. move in; "str" is tmp so we move it in and its very easy.
list.append(a) append gets and in i.e. move in; so we say no not possible unless explicitly say append(a=>) or append(a'copy)

sum(list) sum gets inout so we do a reference if possible. Otherwise we get an error.

by default they are inouts. 

what if we need a copy!
arr: List~Array; # move in and out
arr: =>in List~Array; # move in and out
arr: =inout;

def swap(arr1, arr1); # will give out an error
def swap(arr[i], arr[j]); # will move them automatically

SO THE SEMANTICS OF PARAMETERS ARE MOVE (NOT VALUE OR REFERENCE)
```

We assume trivial movability, non trivial copy, non trivial dtor.

Separate namespaces for functions and objects

## Collecting Error Information

Can be achieved by tagged function at the point of the error that use injection to find info they need.

## Injection

Injected objects cannot be moved, they have to be passed by ref.

```
def state~[Inject{scope="global"}]() {
	return List~int;  # doesn't work because we want a fucking ref!!!
}

def func(list := state()) {
	func2(list); # if in we have to explicitly move, if inout we don't
	func2(list, list); # if inout then we move it once, and the second list is empty
}

def func2(list, state:=state()) {
 what is state? is state emtpy? It should be by ref!
}
```

## type invariants

```
a: int~[range=Range{1, 10}] = 5;; this is what I want

def validate~[Validator](^a: int, {
	range := a..(range, Range{});
	range.low <= a < range.high;
})

struct int~[range=SliceExpr]

>> value > range.low & value < range.high
>> {
>> }

def Range~TagCtor[validator=true]
{
	low: int; high: int;
}

def validate(^a: int, validate(a, a..(range, Range{}))
def validate(a: int~[range=Range])

def validate(a: int, r: Range) {
}

def

def validate~Validator(a: int, (
	if (^a has tag range) {
		^a..range.start <= a < ^a..range.end
	}
)) {}

def validate(a: type)

borrow - @borrow
steal - @steal
share - @share Array
ref - @ref(d) Array
def func(borrowed: = inout, steal :=< Input, share: @idx(index), Ptr~Type =)
def func(shared : Array)

No
two kinds of params: 
in    - default values which simply say I need a value of that kind
inout - I need a value of that kind and I am going to modify it and the caller should see the changes
private - I want exculusive control over that value. The caller should not see anychanges at all. i.e. I want a copy

And let the caller deal with all the complexity

in/inout/private
value/ref/move (caller should deal with it)
```

```xy
Ptr is Ptr with missing type.
```



## Instrumentation

```xy
def instFuncCall~[Instrument{"funcCall"}](ptr: Ptr, ) {
}

def instMalloc~[Instrument{$malloc(Memory)}](same arguments as malloc) {

}
```

```xy
Invariants a.k.a assumptions are more importaint than boundary layer expression
>> - input assumption
<< - output assumption
|| - assumption
```

```
Idea: programmable function calls:
def func(x: Type) -> (out: Type)
>>
<<

def func(x: Type) -> (out: Type)
in boudnary code
function body
out boundary code

def func(x: Type) -> (out: Type)
> {}
{}
< {}
It is way to complicated. Even normal stuff gets way too difficult. It's not self explanatory at all!
```

```
The result of assignment
a = b - b only if b is trivially copyable
a = copy(b) - 
a =< b - void
```

## ; Rule

Expression or statement ends in ; if it is not a block i.e. no }

## Imports

```xy
import libxy.module, libxy.module, libxy.module;
```

## Boundary Expressions

```xy
^metadata(x)
metadata(^x)
```

## Notes

```xy
ref instead of inout - inout is more descriptive and clearly captures the fact that we are gonna modify it. We don't want people using ref when it's not gonna get modified simply because they want a ref.
```

## Macros

```xy
;; Functions that just have a boundary expression as a body
def func() expr;
-or-
def func() (-> (out: Output) {
	body
}); notice the require
```

## Visibility

```xy
func visibility: module, package, public

struct visibility: module, package, public

what about field visibility giving access to a single field is absurd either all fields or no fields.

module - struct & fields visible in only module - sounds reasonable
package - struct & fields visible in package and module - maybe not so reasonable
public - struct & fields visibile in everywhere - public with private fields, public with public fields.

so we need two visibilities. One for the structure and one for the fields.

struct *DTO {
}

struct *Str {

}

The question is who cat see them.

struct *Dto {}
struct *Str {}
struct *Str {}

How can you process data if you don't know what it is!
```

Idea:

No plurals. Japanese like: plural is determined from context.

First the object than the adjectives

```xy
in: ref(d) S = ...;
in: in(d) S = ...;
in: [d] S = ...;
x: [v] D = ...;
(x: in[v] D)
v: in[x] S
v: in[x, 3] S = ...
x: in[arr] S
x: index[arr] S
x: s in(arr)
y: [arr] S

any is a keyword
```

## Dtors

```
def del(a: Arr) {
	// delete a
    // auto call del on all of its fields
}

def delete(a) - delte and resets a

value semantyxs and ! value Semantics

.valueSemantics
~valueSemantics
ReferenceSemantics
```

## Parameters

```xy
default - 
	if !valueSemantics - ref
	if valueSemantics - compiler decides
mut - ref
exclusive - move
```

## Memory Aliasing

* Get Rid of Memory Aliasing and everything simplifies

  ```xy
  # If we get a ref from an object we immediately freeze the entire object
  f(a[i], a[j]) - not possible because a[i] and a[j] may alias
  f(a[i], a) - same
  f(a, a[i]) - same
  f(a, mut a) - not allowed because first a aliases with second a
  
  f(a.f1, a.f2) - same b/c they may alias!
  f(a[0].f1, a[1].f2) - same b/c they may alias!
  
  + May be improved through static analysis
  + Allow for some optimizations
  - We may allow the programmer to hint at non aliasable refs but we open the door for errors
  + Memory aliasing is still more than welcome in read-only cases
  ```

* Allow Aliasing but impose restrictions on their usage in order to eliminate memory errors

    ``` xy
    # We allow limited aliasing
    f(a[i], a) is allowed but we impose the rule to change first a[i] and then a
    f(a, a[i]) is still not allowed because chaning a may destroy a[i]
    f(a, mut a) is allowed - but changing a and then reading first a will give strange results - so we arrange for the muts to go from least to most common
    
    No more difficult to implement than before
    ```

* What about double buffering

  ```xy
  f(a[i%2], a[i%2+1]) - how can we allow that
  f([&&a[i%2]], [&&a[i%2 + 1]]) - looks awful
  f(**a[i%2], **a[i%2+1])
  f(a[i], a[i+1]) - read one, write to other, and then switch
  f(b.a, b.c) - not allowed for some reason
  f(b.a, b.c)
  ```

  

### Reading

Memory Aliasing is the best. It allows us to do fun stuff. It plays well with caches. Nothing really to worry about (as it is usually the case with reading).

### Writing

Aliasing read and write variables leads to wierd resuults and hard to find bugs. Most programs are not implemented with that in mind.

Aliasing write and write variables may result in invalid memory - again rather hard to find. So we need to avoid memory aliasing as much as possible and going further, imposing restriction is justified.

```xy
s: Struct;

f(s.a, s.b);; What about interdependancy between a and b ???
s.a += s.b;; First calculate than write ??? Even bolder!!!

def push(
    arr: mut Array,
    elem: pseudo any,
    elemMem: Ptr = elem'addrof,
    elemSize := sizeof(elem)
)
# >> compatible(arr..elemType, %elem, arr, elem)
{
    arr'ensureCapacity(arr.len + 1, elemSize=elemSize);
    arr.mem[arr.len * elemSize +: elemSize] = elemMem;
    arr.len++;
}
```

So maybe allow limited aliasing: We can have variables to the fields of the same object alias!

```xy
f(a[i], a[j]) # fine as these are pointers in a
f(a[i], a[j].b) # fine as these are pointers in a
f(a[i], a) # not fine as a[i] is in a and a is in stack
f(a, c) # fine both in stack
f(a, a) # fine both on stack
f(a[i], a[j][k]) # a[i] this level is already taken 
#       ^^^^^^^ 
# Error: References to the containing object may have already been taken
# ^^^ - Reference taken here

def test(a: mut IntList, b: mut IntList) {
	# a and b may be aliasing
    func(a[0], b);; not safe as a and b are bot
    func(a[0], a[10]);; not allowed as 0 and 10 may alias!
    func(a[0], a);; not allowed as we have aliasing again
}

so should inout and outs be allowed to interlace

so should inouts and outs be alloed to interleave
```

## APIs

1. A separate API per use case - let a houndred flowers bloom
2. One as general as possible API per use case - jack of all traits master of none
   1. We optimize for the most general case not for the most common
   2. Easy, once you learn one api the rest is easy
3. Storage - data is kind-a known and it's about the functions
4. Maybe mix and match APIs
   1. Blocking File API, ProtonDrive API, DropBox API, All of these have things in common. You can communicate by saying remember this, tell me that.

## Global Stack

global/globalize set of functions

maybe funcs that support :struct or keep thinkgs as type are at the moment considering sizeof works perfectly or and reduces complexity. You can have check in funcs like addrof e.g. def f(a: Any, b:= a'addr) if a is a type then error. So a type expr has the same typeof as the type but is different kind of expression as it points to a type instead of a value.

support for globalize(a: Int = 0);