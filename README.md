# TChess - Play the Chess in the terminal
**TChess** is a simple chess game in terminal.
With this program, you can play chess in terminal.

This software is licensed under [MIT](/LICENSE).

### Installation
You can install it with pip:

```bash
$ pip install tchess
```

To start a game:

```bash
$ tchess
# OR
$ python3 -m tchess
```

Also if you don't want use pip, you can clone this project and:

```bash
$ cd /path/to/tchess
$ python3 tchess 
```

Command `python3 tchess` will run the tchess.

## Get Started

Tchess can save your game in a file, then you can continue that game later.
If you run the above command, game will be saved in `game.tchess` file in current working directory.

But you can customize the file:

```bash
$ tchess my-game.bin
```

Also if you played a game and closed that and now you want to continue that game, only give file name as argument:

```bash
$ tchess my-old-game.bin
```

(The `.bin` extension is a example, you can name it whatever you want).

## Basics
Basic command line usage:

```bash
$ tchess [options...] [?game-file-name]
```

### Cli options
- `--help`: shows the help
- `--version|-v`: shows version of the tchess
- `--no-ansi`: disables the Ansi color chars

### Game flow

when you run the game, you see something like this:

```
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| w-rock    | w-knight  | w-bishop  | w-king    | w-queen   | w-bishop  | w-knight  | w-rock    |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| w-pawn    | w-pawn    | w-pawn    | w-pawn    | w-pawn    | w-pawn    | w-pawn    | w-pawn    |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
|  3-1      |  3-2      |  3-3      |  3-4      |  3-5      |  3-6      |  3-7      |  3-8      |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
|  4-1      |  4-2      |  4-3      |  4-4      |  4-5      |  4-6      |  4-7      |  4-8      |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
|  5-1      |  5-2      |  5-3      |  5-4      |  5-5      |  5-6      |  5-7      |  5-8      |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
|  6-1      |  6-2      |  6-3      |  6-4      |  6-5      |  6-6      |  6-7      |  6-8      |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| b-pawn    | b-pawn    | b-pawn    | b-pawn    | b-pawn    | b-pawn    | b-pawn    | b-pawn    |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| b-rock    | b-knight  | b-bishop  | b-king    | b-queen   | b-bishop  | b-knight  | b-rock    |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
                                                                                                  
white Turn >>>
```

The above content will be showed in the terminal. and there is a command input in the bottom.
You should pass commands to that for running the game.

Also there is `white Turn`. this means its turn of white team. if you do something,
this will be changed to `black Turn`.

Also name of Pieces is `<team>-<type>`. for example `b-queen` (black queen) and `w-king` (white king).

The location of cells is accessible with this pattern: `<row>-<column>` or `<row>.<column>`.
For example `1-1` or `6.4`.

### `exit`
command exit, exits the program:

```
>>> exit
```

### Moving the pieces
For moving pieces, you should enter this command:

```
>>> move <src> to <dst>
```

for example:

```
>>> move 2.1 to 4.1
```

Also you can use `mv` keyword instead of `move`:

```
>>> mv a to b
``` 

Also you can don't use `to` keyword. for example:

```
>>> mv 2.1 3.1
```

Also you can see which pieces in the board are allowed to go to the which cells:

```
>>> s 2.2
```

The above command `s <cell-address>`, will show you the piece in the entered address can go to
which cells (The allowed cells will be highlighted with `*`).

### Replaying a saved game
If you played a game and it is saved, you can play that!

You should use option `--replay`:

```bash
$ tchess --replay my-saved-game.file
```

Then you can see your game is Replaying!

Also you can set frame speed of Replaying using `--replay-speed` option:

```bash
$ tchess --replay my-saved-game.file --replay-speed=3 # means 3 seound
$ tchess --replay my-saved-game.file --replay-speed=0.5
```

(sort of options is not important).

## Development
If you are developing this software, you can run the tests using `test.py`:

```bash
$ python3 test.py
# OR
$ ./test.py
```

For adding test, write a function in `test.py` and add the function to the `TESTS` list in `test.py`:

```python
def test_my_test_func():
    """ A Caption for my test """
    assert 1 == 1

TESTS = [
    # ...
    test_my_test_func,
    # ...
]
```

For using **pylint** to check code quality, you can use make:

```bash
$ make pylint
```
