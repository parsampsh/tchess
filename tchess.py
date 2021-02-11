#!/usr/bin/env python3

""" Play the Chess in the terminal """

import pickle
import sys
import os

class Ansi:
    """ The terminal ansi chars """

    GREEN = '\033[32m'
    RED = '\033[31m'
    RESET = '\033[0m'

    @staticmethod
    def disable():
        """ Disables the ansi chars """
        Ansi.GREEN = ''
        Ansi.RED = ''
        Ansi.RESET = ''

class Piece:
    """ Each piece in the chess board """

    PAWN = 'pawn'
    KING = 'king'
    QUEEN = 'queen'
    KNIGHT = 'knight'
    BISHOP = 'bishop'
    ROCK = 'rock'

    def __init__(self, name: str, color: str, id: int, game):
        self.name = name
        self.game = game
        self.color = color
        self.id = id

    def __str__(self):
        return self.color + '-' + self.name

class Game:
    """ The running game handler """

    ROW_SEPARATOR = '|--------------|--------------|--------------|--------------|--------------|--------------|--------------|--------------|\n'

    def __init__(self):
        self.turn = 'white'
        self.logs = []

        # this item is used to validate saved games versions
        # if we load a file that created with old version of the game,
        # we can check it using this property
        # if we made backward IN-compatible changes on this class,
        # this number should be bumped.
        self.version = 1

        # initialize the board
        self.board = []
        for i in range(8):
            self.board.append([])
            for j in range(8):
                # handle default pieces location
                if i in (1, 6):
                    self.board[-1].append(
                        Piece(
                            name=Piece.PAWN,
                            color=('white' if i == 1 else 'black'),
                            id=int(str(i) + str(j)),
                            game=self
                        )
                    )
                elif i in (0, 7):
                    name = Piece.PAWN
                    if j in (0, 7):
                        name = Piece.ROCK
                    elif j in (0, 3):
                        name = Piece.KING
                    elif j in (3 ,7):
                        name = Piece.QUEEN
                    elif j in (0, 4):
                        name = Piece.QUEEN
                    elif j in (4, 7):
                        name = Piece.KING
                    elif j in (2, 5):
                        name = Piece.BISHOP
                    elif j in (1, 6):
                        name = Piece.KNIGHT
                    self.board[-1].append(
                        Piece(
                            name=name,
                            color=('white' if i == 0 else 'black'),
                            id=int(str(i) + str(j)),
                            game=self
                        )
                    )
                else:
                    self.board[-1].append(None)

    def change_turn(self):
        """ Changes the turn.

        If currently is white turn, set turn to black and reverse
        """
        self.turn = 'black' if self.turn == 'white' else 'white'

    def run_command(self, cmd: str):
        """ Gets a command as string and runs that on the game """
        # TODO : run the command

        # add command to the log
        self.logs.append(cmd)

        # change the turn
        self.change_turn()

    def render(self) -> str:
        """ Renders the board to show in the terminal """
        output = ''
        for row in list(reversed(self.board)):
            output += self.ROW_SEPARATOR
            for column in row:
                if column is None:
                    column_str = ' ' * 13
                    ansi_color = ''
                    ansi_reset = ''
                else:
                    column_str = str(column)
                    ansi_color = Ansi.GREEN if column.color == 'white' else Ansi.RED
                    ansi_reset = Ansi.RESET
                output += '| ' + ansi_color + column_str + ansi_reset + (' ' * (13-len(column_str)))
            output += '|\n'
        output += self.ROW_SEPARATOR
        return output

def run(args: list):
    """ The main cli entry point """

    # check the terminal size
    terminal_width = os.get_terminal_size().columns
    if terminal_width < len(Game.ROW_SEPARATOR):
        print(
            'ERROR: your terminal width is less than ' + str(len(Game.ROW_SEPARATOR)) + '.',
            file=sys.stderr
        )
        sys.exit(1)

    game_file_name = 'game.tchess'

    # parse the arguments
    options = [arg for arg in args if arg.startswith('-')]
    arguments = [arg for arg in args if not arg.startswith('-')]

    # handle `--no-ansi` option
    if '--no-ansi' in options:
        options.remove('--no-ansi')
        Ansi.disable()

    if len(arguments) > 0:
        game_file_name = arguments[0]

    if os.path.isfile(game_file_name):
        # if file exists, load the game from that
        # (means user wants to open a saved game)
        try:
            tmp_f = open(game_file_name, 'rb')
            game = pickle.load(tmp_f)
            tmp_f.close()

            # validate the game object
            if not isinstance(game, Game):
                raise

            # check the version
            if game.version != Game().version:
                print('ERROR: file `' + game_file_name + '` is created with OLD/NEW version of tchess and cannot be loaded', file=sys.stderr)
                raise
        except:
            # file is corrupt
            print('ERROR: file `' + game_file_name + '` is corrupt', file=sys.stderr)
            sys.exit(1)
    else:
        game = Game()

    while True:
        # render the game board on the terminal
        print('\033[H', end='')
        title = '*** Welcome to the TChess! ***'
        print(title, end='')
        print(' ' * (len(Game.ROW_SEPARATOR) - len(title)))
        print(' ' * len(Game.ROW_SEPARATOR))
        print(game.render())

        # get command from user and run it
        tmp_turn = game.turn
        ansi_color = Ansi.RED if tmp_turn == 'black' else Ansi.GREEN
        # fix whitespace
        print(' ' * len(Game.ROW_SEPARATOR), end='\r')
        command = input(ansi_color + game.turn + Ansi.RESET + ' Turn >>> ').strip().lower()

        # check the empty command
        if command == '':
            continue

        # check the exit command
        if command in ['exit', 'quit', 'q']:
            game_file_name = os.path.abspath(game_file_name)
            print('Your game was saved in file `' + game_file_name + '`.')
            print(
                'To continue this game again, run `' + sys.argv[0] + ' '+repr(game_file_name)+'`.'
            )
            print('Good bye!')
            sys.exit()

        # run the command on the game to make effects
        game.run_command(command)

        # save the game
        # open a file
        # this file is used to save the game state
        # after any command on the game, game will be re-write on this file
        game_file = open(game_file_name, 'wb')
        pickle.dump(game, game_file)
        game_file.close()

if __name__ == '__main__':
    run(sys.argv[1:])
