# Foo Language
Basic statically-typed programming language compiled with **LLVM** and **GCC**.

## Requirements
<table>
    <tr>
        <td> <strong> Operating system </strong> </td>
        <td> Ubuntu 24.04.2 </td>
    </tr>
    <tr>
        <td> <strong> Python </strong> </td>
        <td> 3.10+ </td>
    </tr>
    <tr>
        <td> <strong> LLVM </strong> </td>
        <td> Ubuntu LLVM 18.1.3 </td>
    </tr>
    <tr>
        <td> <strong> GCC </strong> </td>
        <td> Ubuntu 13.3.0 </td>
    </tr>
</table>

## Features
#### Print on terminal
Example:
```
print(5 + 1); // 6
```

#### Variable definition
Example:
```
number num = 5;
print(num); // 5
```

#### Variable assignment
Example:
```
number x = 10;
x = 9;
print(x); // 9

x += 2;
print(x); // 11

number x = 1; // Raises an error
```

## Setup on your local environment
Clone the repository
```bash
git clone https://github.com/noodles-1/basic-compiler.git

cd basic-compiler
```

Run `main.py` to create an LLVM IR (immediate representation) file `output.ll`, compile to an object file `output.o`, and create final executable `output`
```bash
python3 src/main.py && llc -filetype=obj output.ll && gcc -no-pie output.o -o output && ./output
```