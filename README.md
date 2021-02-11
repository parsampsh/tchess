# TChess : Play the Chess in the terminal
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
- `--no-ansi`: disables the Ansi color chars
