# Foo Language
Basic programming language compiled with **LLVM** and **GCC**.

## Features
### Printing

#### Display numbers on the terminal
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