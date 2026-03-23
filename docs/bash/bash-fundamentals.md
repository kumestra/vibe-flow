# Bash Scripting Fundamentals

A self-contained reference covering core Bash concepts, with examples grounded in a real script: the `.githooks/pre-commit` hook in this repo.

---

## Data Types

Bash essentially has **one data type: strings**. Numbers, file paths, `true`/`false` — they're all text under the hood.

### Numbers are strings that Bash can do math on

```bash
x=5
echo $x          # prints: 5
echo $((x + 3))  # prints: 8 — Bash parsed the string "5" as a number
```

There is no `int` type. Bash parses strings into numbers on the fly when you use numeric operators, then the result goes back to being a string.

From the pre-commit hook:

```bash
found=0    # not an integer — it's the string "0"
found=1    # reassigned to the string "1"
```

### Booleans don't exist

There is no `true`/`false` type. The hook uses `0` and `1` as a convention, but Bash itself doesn't understand "boolean." What Bash does understand is **exit codes**: every command returns `0` for success or non-zero for failure. That's what `if` actually checks — not a boolean value, but whether a command succeeded.

### Collections

Beyond plain strings, Bash has two collection types, but every element inside them is still a string.

**Indexed arrays:**

```bash
fruits=("apple" "banana" "cherry")
echo ${fruits[0]}   # apple
echo ${fruits[@]}   # all elements
```

**Associative arrays (dictionaries):**

```bash
declare -A colors
colors[sky]="blue"
colors[grass]="green"
echo ${colors[sky]}   # blue
```

### Why is Bash like this?

Bash was designed as a **command launcher**, not a general-purpose programming language. Its job is to glue commands together, pass file names around, and handle text output from programs. Strings are the universal format for all of that — commands take string arguments and produce string output.

---

## Variables

### Assignment

The basic syntax is `name=value`. **No spaces around the `=` sign** — this is mandatory.

```bash
# Correct
greeting="hello"

# WRONG — Bash treats these as a command with arguments
greeting = "hello"
greeting ="hello"
greeting= "hello"
```

Why? Bash interprets words separated by spaces as a command followed by arguments. `greeting = "hello"` looks like running a command called `greeting` with `=` and `"hello"` as arguments.

### Quoting

```bash
name=Alice            # fine for a single word
greeting="hello world"  # need quotes when value contains spaces
path='$HOME/docs'       # single quotes: literal string, no expansion
path="$HOME/docs"       # double quotes: variables get expanded
```

### Reading variables

Prefix with `$` to read a variable's value:

```bash
name="Alice"
echo $name       # Alice
echo "$name"     # Alice (safer — always prefer this form)
echo "${name}"   # Alice (explicit boundary)
```

The `${name}` form with curly braces exists for cases where Bash can't tell where the variable name ends:

```bash
fruit="apple"
echo "$fruits"     # empty — Bash looks for a variable called "fruits"
echo "${fruit}s"   # apples — curly braces mark the boundary
```

### Reassignment

Just assign again. No keyword needed:

```bash
found=0
found=1    # overwritten, now "1"
```

### `declare` for constraints

```bash
declare -r PI=3.14      # readonly — can't reassign
declare -i count=5      # integer — arithmetic is automatic
declare -a list          # indexed array
declare -A map           # associative array
```

With `-i`, Bash auto-evaluates arithmetic on assignment:

```bash
declare -i x
x=5+3
echo $x   # 8 (without -i, you'd get the literal string "5+3")
```

### `export` for child processes

`export` makes a variable visible to child processes (commands launched from your script):

```bash
export PATH="$PATH:/my/custom/bin"
```

Without `export`, the variable only exists inside the current script or shell session.

### Temporary variable for a single command

Setting a variable directly before a command on the same line applies it **only for that command**:

```bash
IFS= read -r file
# IFS is set to empty only for this one `read` invocation
```

This is used in the pre-commit hook's while loop (see [While Loops](#while-loops) below).

---

## If Statements

### Basic syntax

```bash
if command; then
    # runs if command succeeded (exit code 0)
fi
```

With `else` and `elif`:

```bash
if command; then
    # success path
elif other_command; then
    # ...
else
    # failure path
fi
```

**Key concept:** `if` doesn't evaluate a boolean expression. It **runs a command** and checks its exit code. `0` = true, non-zero = false. This is backwards from most languages where `0` is falsy.

### Test commands: `[ ]` and `[[ ]]`

To do actual comparisons, you use a command whose purpose is to evaluate an expression and return an exit code:

```bash
# Old-style (POSIX)
if [ "$name" = "Alice" ]; then

# Modern Bash (preferred)
if [[ "$name" = "Alice" ]]; then
```

The spaces inside the brackets are **mandatory**. `[[$found -eq 1]]` is a syntax error.

### String comparisons

```bash
[[ "$a" = "$b" ]]     # equal
[[ "$a" != "$b" ]]    # not equal
[[ -z "$a" ]]         # is empty (zero length)
[[ -n "$a" ]]         # is not empty
```

### Numeric comparisons

Bash uses letter-based operators for numbers (because `<` and `>` mean redirection in the shell):

```bash
[[ $x -eq $y ]]    # equal
[[ $x -ne $y ]]    # not equal
[[ $x -lt $y ]]    # less than
[[ $x -gt $y ]]    # greater than
[[ $x -le $y ]]    # less than or equal
[[ $x -ge $y ]]    # greater than or equal
```

From the pre-commit hook:

```bash
# Check if any binary file was found
if [[ $found -eq 1 ]]; then
```

### File tests

Bash has built-in tests for files — natural for a shell language:

```bash
[[ -f "$path" ]]    # is a regular file
[[ -d "$path" ]]    # is a directory
[[ -e "$path" ]]    # exists (any type)
[[ -r "$path" ]]    # is readable
[[ -w "$path" ]]    # is writable
[[ -x "$path" ]]    # is executable
```

### Combining conditions

```bash
# AND (short-circuit)
if [[ $a -gt 0 ]] && [[ $a -lt 10 ]]; then

# OR
if [[ $a = "yes" ]] || [[ $a = "y" ]]; then

# NOT
if ! [[ -f "$file" ]]; then
```

### Any command works with `if`

Since `if` just checks exit codes, you can use any command directly — no `[[ ]]` needed:

```bash
if grep -q "error" logfile.txt; then
    echo "Found errors!"
fi

if mkdir mydir; then
    echo "Directory created"
else
    echo "Failed to create directory"
fi
```

---

## Pipes

The pipe operator `|` takes the output of one command and feeds it as input to the next:

```bash
git diff --cached --numstat -- "$file" | grep -q "^-"
```

This means: "run the git command, take its output, and hand it to `grep`."

From the pre-commit hook, this is how binary files are detected. `git diff --cached --numstat` outputs dashes for binary files (`-  -  filename`), and `grep -q "^-"` checks if the output starts with a dash. The `-q` flag makes grep quiet — it doesn't print anything, it just sets its exit code (0 for match found, 1 for no match).

---

## While Loops

### Basic form

```bash
while command; do
    # body runs as long as command succeeds (exit code 0)
done
```

Same idea as `if` — runs a command and checks the exit code, but keeps looping.

```bash
count=0
while [[ $count -lt 3 ]]; do
    echo "$count"
    count=$((count + 1))
done
# prints: 0, 1, 2
```

### Reading lines with `while read`

The most common Bash pattern — process text line by line:

```bash
while read line; do
    echo "Got: $line"
done < somefile.txt
```

`read` grabs one line of input, stores it in the variable, and returns success. When there's nothing left, it returns failure and the loop stops.

### The pre-commit hook's loop explained

```bash
while IFS= read -r file; do
    # ... process each file ...
done < <(git diff --cached --name-only)
```

Four pieces to understand:

#### `read file`

Takes one line of input and stores it in the variable `file`. Each loop iteration, `read` grabs the next line.

#### `-r` flag

Tells `read` not to interpret backslashes within the line. Without it, a filename like `my\file.txt` would get mangled.

**Important:** `-r` does not affect how `read` finds line boundaries. `read` splits lines by looking for the raw newline byte (`0x0A`) in the input stream — a single byte, not the two-character escape sequence `\n`. The `-r` flag only controls what happens to backslash characters *within* a line after it has already been split.

#### `IFS=`

Temporarily sets the Internal Field Separator to nothing, **only for the `read` command** (because it's on the same line). By default, IFS includes spaces and tabs, which causes `read` to strip leading/trailing whitespace. Setting it to empty preserves whitespace exactly:

```bash
# Default IFS:
echo "  hello  " | read line       # line = "hello"

# IFS= (empty):
echo "  hello  " | IFS= read line  # line = "  hello  "
```

Together, `IFS= read -r file` means: "read the next line exactly as-is — don't strip whitespace, don't interpret backslashes."

#### `< <(command)` — input redirection + process substitution

Two separate operators:

**`<(git diff --cached --name-only)`** is **process substitution**. It runs the command and makes its output available as if it were a file. Bash creates a temporary file-like path:

```bash
echo <(echo "hello")
# prints something like: /dev/fd/63
```

**`<`** is **input redirection**. It says "read input from this source instead of the keyboard."

Together: run git, capture its output into a file-like object, and feed that as input to the while loop.

**The space between `<` and `<(...)` is mandatory.** Without it, Bash sees `<<` and thinks you're starting a here-document (a different feature entirely).

#### Why not use a pipe instead?

```bash
# This looks simpler but has a subtle bug:
git diff --cached --name-only | while IFS= read -r file; do
    found=1
done
# found is still 0 here!
```

When you pipe into `while`, the loop runs in a **subshell** — a separate child process. Variables set inside (like `found=1`) are lost when the loop ends. The `< <(...)` form avoids this — the loop runs in the current shell, so variable assignments persist.

---

## The `--` Separator in Commands

```bash
git diff --cached --numstat -- "$file"
```

The `--` tells the command: "everything after this is a filename, not a flag." Without it, a file named `-v` would be interpreted as the `-v` option. It's a defensive convention used across most Unix commands.

---

## How Byte Streams and Newlines Work

Command output in Bash is a byte stream (typically UTF-8 encoded). When a command outputs multiple lines, the lines are separated by the **newline byte** (`0x0A`) — a single byte.

The `\n` notation is just how we represent this byte in source code and documentation. By the time output reaches a pipe or redirection, the compiler or interpreter has already converted `\n` into the raw `0x0A` byte. `read` scans for this byte to know where one line ends and the next begins — no decoding or interpretation required.

```
Actual bytes in the stream:
readme.md[0x0A]src/app.js[0x0A]image.png[0x0A]

read call 1 → consumes up to first 0x0A  → file="readme.md"
read call 2 → consumes up to second 0x0A → file="src/app.js"
read call 3 → consumes up to third 0x0A  → file="image.png"
read call 4 → nothing left               → returns failure, loop stops
```

---

## Reference: The Pre-Commit Hook

The complete `.githooks/pre-commit` script, annotated with the concepts above:

```bash
#!/bin/bash

# Flag to track whether any binary file was found. 0 = no, 1 = yes.
# This is a string "0", not an integer — Bash has no integer type.
found=0

# Process substitution feeds git output as a file-like stream.
# IFS= and -r ensure each filename is read exactly as-is.
while IFS= read -r file; do

  # Pipe: git outputs file stats, grep checks if output starts with "-".
  # Binary files produce dashes in numstat output.
  # -- separates flags from the filename argument.
  if git diff --cached --numstat -- "$file" | grep -q "^-"; then
    echo "Binary file detected: $file"
    found=1  # reassign the string to "1"
  fi

done < <(git diff --cached --name-only)

# -eq treats the strings as numbers for comparison.
# Exit code 1 tells git to abort the commit.
if [[ $found -eq 1 ]]; then
  echo "Commit blocked: remove binary files from staging area with 'git reset HEAD <file>'"
  exit 1
fi
# If we reach here, the default exit code 0 allows the commit.
```
