#!/usr/bin/env python3

""" Play the Chess in the terminal """

import pickle
import sys
import os
import copy
import time
import threading
import requests

try:
    from . import moves
except ImportError:
    import moves

try:
    from . import server
except ImportError:
    import server

VERSION = '0.0.17'

class Ansi:
    """ The terminal ansi chars """

    GREEN = '\033[32m'
    RED = '\033[31m'
    RESET = '\033[0m'
    GRAY = '\033[37m'
    CYAN = '\033[96m'

    @staticmethod
    def disable():
        """ Disables the ansi chars """
        Ansi.GREEN = ''
        Ansi.RED = ''
        Ansi.RESET = ''
        Ansi.GRAY = ''
        Ansi.CYAN = ''

class Piece:
    """ Each piece in the chess board """

    PAWN = 'pawn'
    KING = 'king'
    QUEEN = 'queen'
    KNIGHT = 'knight'
    BISHOP = 'bishop'
    ROCK = 'rock'

    ICONS = {
        'pawn': 'pawn',
        'king': 'king',
        'queen': 'queen',
        'knight': 'knight',
        'bishop': 'bishop',
        'rock': 'rock',
    }

    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color

    def __str__(self):
        return ('w' if self.color == 'white' else 'b') + '-' + self.ICONS[self.name]

    def allowed_moves(self, game, src, dst, return_locations=False):
        """ Returns the allowed targets for move for this piece

        Returned structure:
        [
            [x, y],
            [x, y],
            ...
        ]
        """
        x = src[0]
        y = src[1]
        result = []
        if self.name == Piece.PAWN:
            result = moves.pawn_move(self, game, src)
        elif self.name == Piece.ROCK:
            result = moves.rock_move(self, game, src)
        elif self.name == Piece.QUEEN:
            result = [*moves.rock_move(self, game, src), *moves.bishop_move(self, game, src)]
        elif self.name == Piece.KING:
            result = moves.king_move(self, game, src)
        elif self.name == Piece.KNIGHT:
            result = moves.knight_move(self, game, src)
        elif self.name == Piece.BISHOP:
            result = moves.bishop_move(self, game, src)
        else:
            result = []
        if return_locations:
            return result
        if dst in result:
            return True
        if self.name == Piece.PAWN:
            return False
        return False

class Game:
    """ The running game handler """

    ROW_SEPARATOR = ('|-----------'*8) + '|\n'
    CELL_WIDTH = 10
    IS_TEST = False

    def __init__(self):
        self.turn = 'white'
        self.logs = []

        # this item is used to validate saved games versions
        # if we load a file that created with old version of the game,
        # we can check it using this property
        # if we made backward IN-compatible changes on this class,
        # this number should be bumped.
        self.version = 1

        # each cell location be in this list, will be highlighted in rendering
        self.highlight_cells = []

        # this item determines the selected piece using `s` command
        self.selected_cell = None

        # the player names
        self.white_player = 'White'
        self.black_player = 'Black'

        # game status
        self.is_end = False
        self.winner = None

        # currently which team is check
        self.current_check = None

        # if this is True, beep sound will be enabled
        self.enable_beep = True

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
                        )
                    )
                else:
                    self.board[-1].append(None)

    def beep(self):
        """ Plays a beep sound """
        if self.enable_beep:
            if not Game.IS_TEST:
                print('\a', end='')

    def change_turn(self):
        """ Changes the turn.

        If currently is white turn, set turn to black and reverse
        """
        self.turn = 'black' if self.turn == 'white' else 'white'

        self.handle_check()

    def handle_check(self):
        """ Handle the check and checkmate """
        for color in ('white', 'black'):
            for i in range(0, len(self.board)):
                for j in range(0, len(self.board[i])):
                    if self.board[i][j] is not None:
                        if self.board[i][j].color == color:
                            for item in self.board[i][j].allowed_moves(self, [i, j], [0, 0], return_locations=True):
                                if self.board[item[0]][item[1]] is not None:
                                    if self.board[item[0]][item[1]].color != color:
                                        if self.board[item[0]][item[1]].name == Piece.KING:
                                            if color == self.turn:
                                                self.checkmate()
                                            else:
                                                self.check(self.board[item[0]][item[1]].color)

    def checkmate(self):
        """ Changes game status to the checkmate """
        self.is_end = True
        self.winner = self.turn
        self.beep()

    def check(self, color):
        """ Sets check status for a color """
        self.current_check = color
        self.beep()

    def move(self, src, dst):
        """ Moves src to dst """
        self.beep()
        dst_p = copy.deepcopy(self.board[dst[0]][dst[1]])
        src_p = copy.deepcopy(self.board[src[0]][src[1]])

        if not src_p.allowed_moves(self, src, dst):
            return False, 'Error: Target location is not allowed. enter `s '+str(src[0]+1)+'.'+str(src[1]+1)+'` to see where you can go'

        if dst_p is not None:
            if dst_p.color == self.turn:
                # killing self!
                return False, 'Error: You cannot kill your self!'

        self.board[src[0]][src[1]] = None

        self.board[dst[0]][dst[1]] = src_p

        return True, ''

    def run_command(self, cmd: str) -> str:
        """ Gets a command as string and runs that on the game. Returns result message as string """
        self.beep()

        cmd_parts = cmd.split()

        self.highlight_cells = []
        self.selected_cell = None

        invalid_msg = 'Invalid Command!'

        result_msg = 'Runed'

        if len(cmd_parts) == 1:
            if cmd_parts[0] == 'back':
                if not self.logs:
                    invalid_msg = 'Please move something first!'
                else:
                    # back
                    new_game = Game()
                    while self.logs:
                        if not self.logs[-1].startswith('m'):
                            self.logs.pop()
                        else:
                            self.logs.pop()
                            break
                    for cmd in self.logs:
                        new_game.run_command(cmd)
                    self.logs = new_game.logs
                    self.board = new_game.board
                    self.turn = new_game.turn
                    return 'OK! now you are one step back!'
        elif len(cmd_parts) == 2:
            # s <location>
            if cmd_parts[0] == 's':
                location = cmd_parts[1].replace('.', '-').split('-')
                if len(location) == 2:
                    try:
                        location[0] = int(location[0])-1
                        location[1] = int(location[1])-1

                        valid_range = list(range(0, 8))
                        if not (location[0] in valid_range and location[1] in valid_range):
                            return 'Error: Location is out of range!'

                        if self.board[location[0]][location[1]] is None:
                            return 'Error: selected cell is empty!'

                        allowed_moves = self.board[location[0]][location[1]].allowed_moves(self, (location[0], location[1]), (location[0], location[1]), return_locations=True)

                        # show allowed moves
                        self.highlight_cells = allowed_moves
                        self.selected_cell = location

                        return '' if self.highlight_cells else 'This piece cannot move!'
                    except:
                        return 'Error: Invalid location!'

        if len(cmd_parts) == 3:
            if cmd_parts[0] in ('move', 'mv'):
                cmd_parts.insert(2, 'to')

        if len(cmd_parts) == 4:
            # the move operation
            if cmd_parts[0] in ('move', 'mv') and cmd_parts[2] == 'to':
                src = cmd_parts[1].replace('.', '-').split('-')
                dst = cmd_parts[3].replace('.', '-').split('-')
                if len(src) == 2 and len(dst) == 2:
                    try:
                        src[0] = int(src[0])-1
                        src[1] = int(src[1])-1
                        dst[0] = int(dst[0])-1
                        dst[1] = int(dst[1])-1

                        valid_range = list(range(0, 8))
                        if not (src[0] in valid_range and src[1] in valid_range and dst[0] in valid_range and dst[1] in valid_range):
                            return 'Error: Locations are out of range!'
                    except:
                        return 'Error: Invalid locations!'
                    result_msg = cmd_parts[1] + ' Moved to ' + cmd_parts[3]
                else:
                    return invalid_msg

                if self.board[src[0]][src[1]] is not None:
                    pass
                else:
                    return 'Error: source location is empty cell!'
                if src == dst:
                    return 'Error: source and target locations are not different!'
                if self.board[src[0]][src[1]].color != self.turn:
                    return 'Error: its ' + self.turn + ' turn, you should move ' + self.turn + ' pieces!'
                result = self.move(src, dst)
                if not result[0]:
                    return result[1]
            else:
                return invalid_msg
        else:
            return invalid_msg

        # add command to the log
        self.logs.append(cmd)

        # change the turn
        self.change_turn()

        return result_msg

    def get_dead_items(self):
        """ Returns list of dead items like this:
        {
            "black": {
                "pawn": 3, # count
                "rock": 1
            },
            "white": {
                # ...
            }
        }
        """
        result = {
            "white": {},
            "black": {},
        }
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j] is not None:
                    try:
                        result[self.board[i][j].color][self.board[i][j].name] += 1
                    except:
                        result[self.board[i][j].color][self.board[i][j].name] = 1

        # now, `result` contains live items.
        # we want dead items
        for team in result:
            for item in result[team]:
                if item == Piece.PAWN:
                    result[team][item] = 8 - result[team][item]
                elif item not in (Piece.QUEEN, Piece.KING):
                    result[team][item] = 2 - result[team][item]
                else:
                    result[team][item] = 1 - result[team][item]

        # delete items contains 0
        new_result = {
            "white": {},
            "black": {},
        }
        for team in result:
            for item in result[team]:
                if result[team][item] > 0:
                    new_result[team][item] = result[team][item]

        return new_result

    def render(self) -> str:
        """ Renders the board to show in the terminal """
        output = ''

        # render the player names
        white_player = 'B. ' + self.white_player + (' (Check!)' if 'white' == self.current_check else '')
        black_player = 'W. ' + self.black_player + (' (Check!)' if 'black' == self.current_check else '')
        white_space_len = (len(self.ROW_SEPARATOR) - (len(white_player)+len(black_player))) - 2
        white_space_len = int(white_space_len/2)
        player_names = Ansi.CYAN + white_player + Ansi.RESET + (' ' * white_space_len) + 'Vs' + (' ' * white_space_len) + Ansi.RED + black_player + Ansi.RESET

        output += player_names + '\n'
        output += ('_' * len(self.ROW_SEPARATOR)) + '\n'
        output += (' ' * len(self.ROW_SEPARATOR)) + '\n'

        for i in range(1, 9):
            output += (int(self.CELL_WIDTH/2) * ' ') + str(i) + (' ' * (int(self.CELL_WIDTH/2)+1))
        output += '\n'
        i = 0
        for row in self.board:
            output += '  ' + self.ROW_SEPARATOR + str(i+1) + ' '
            j = 0
            for column in row:
                if column is None:
                    column_str = ' ' + str(i+1) + '-' + str(j+1)
                    ansi_color = Ansi.GRAY
                    ansi_reset = Ansi.RESET
                else:
                    column_str = str(column)
                    ansi_color = Ansi.CYAN if column.color == 'white' else Ansi.RED
                    ansi_reset = Ansi.RESET
                if [i, j] in self.highlight_cells:
                    column_str = '*' + column_str.lstrip() + '*'
                elif self.selected_cell == [i, j]:
                    column_str = '<' + column_str.lstrip() + '>'
                output += '| ' + ansi_color + column_str + ansi_reset + (' ' * (self.CELL_WIDTH-len(column_str)))
                j += 1
            output += '|\n'
            i += 1
        output += '  ' + self.ROW_SEPARATOR
        lines = output.splitlines()
        output = ''
        for line in lines:
            output += ' ' + line + '\n'

        # show dead items
        dead_items = self.get_dead_items()
        dead_items_str = 'Deads:\n'
        for team in dead_items:
            if dead_items[team]:
                color = (Ansi.CYAN if team == 'white' else Ansi.RED)
                current_line = color + team + Ansi.RESET + ': '
                for item in dead_items[team]:
                    if item in (Piece.QUEEN, Piece.KING):
                        current_line += color + item + Ansi.RESET + ', '
                    else:
                        current_line += color + str(dead_items[team][item]) + ' ' + item + Ansi.RESET + ', '
                current_line = current_line.strip().strip(',')
                current_line += (' ' * (len(self.ROW_SEPARATOR) - len(current_line)))
                dead_items_str += current_line + '\n'

        if dead_items_str == 'Deads:\n':
            dead_items_str = ''

        output += dead_items_str.strip()

        return output

def show_help():
    """ Prints the help message """
    print('''tchess - Play the chess in terminal

SYNOPSIS
    $ '''+sys.argv[0]+''' [options...] [?game-file-name]

DESCRIPTION
    The TChess is a chess game in terminal.
    This software can handle saving the game in a file
    Then you can continue your game later by loading that file

OPTIONS
    --help: shows this help
    --help --verbose: show full help
    --version|-v: shows the version of tchess
    --no-ansi: disable terminal ansi colors
    --replay: play the saved game
    --replay-speed: delay between play frame (for example `3`(secound) or `0.5`)
    --dont-check-terminal: do not check terminal size
    --player-white=[name]: set name of white player
    --player-black=[name]: set name of black player
    --no-beep: do not play beep sound
    --online: serve a online game
    --online --host=[host]: set host of online game
    --online --port=[port]: set port of online game
    --online --guest-color=[color]: color of guest player (black or white)
    --connect [host]:[port]: connect to a online game
    --connect --name=[name]: set your name white joining to a game

AUTHOR
    This software is created by Parsa Shahmaleki <parsampsh@gmail.com>
    And Licensed under MIT
''')

    if '--verbose' in sys.argv:
        print('''
GAME
    GET STARTED
        Tchess can save your game in a file, then you can continue that game later. If you run the above command, game will be saved in game.tchess file in current working directory.
        Also Tchess can handle online multiplayer game on local network (P2P).

        But you can customize the file:

        $ tchess my-game.bin

        Also if you played a game and closed that and now you want to continue that game, only give file name as argument:

        $ tchess my-old-game.bin

        (The .bin extension is a example, you can name it whatever you want).

    BASICS

        when you run the game, you see something like this:

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

        The above content will be showed in the terminal. and there is a command input in the bottom. You should pass commands to that for running the game.

        Also there is white Turn. this means its turn of white team. if you do something, this will be changed to black Turn.

        Also name of Pieces is <team>-<type>. for example b-queen (black queen) and w-king (white king).

        The location of cells is accessible with this pattern: <row>-<column> or <row>.<column>. For example 1-1 or 6.4.
        exit

        command exit, exits the program:

        >>> exit

        Moving the pieces

        For moving pieces, you should enter this command:

        >>> move <src> to <dst>

        for example:

        >>> move 2.1 to 4.1

        Also you can use mv keyword instead of move:

        >>> mv a to b

        Also you can don't use to keyword. for example:

        >>> mv 2.1 3.1

        Also you can see which pieces in the board are allowed to go to the which cells:

        >>> s 2.2

        The above command s <cell-address>, will show you the piece in the entered address can go to which cells (The allowed cells will be highlighted with *).
        Back

        You can revert your moves and back to the previous status.

        >>> back

        This is useful if you insert a wrong command or move wrong.
        (This command will be disabled for guest in online mode)

        Replaying a saved game

        If you played a game and it is saved, you can play that!

        You should use option --replay:

        $ tchess --replay my-saved-game.file

        Then you can see your game is Replaying!

        Also you can set frame speed of Replaying using --replay-speed option:

        $ tchess --replay my-saved-game.file --replay-speed=3 # means 3 seound
        $ tchess --replay my-saved-game.file --replay-speed=0.5

        (sort of options is not important).

        Online multiplayer

        By default, Tchess runs a offline game for you that you should play on one terminal. Means both of players should use one computer alongside together.

        But you can play with your friend with two computers (on local network).

        Means one player will be Server and othe player will be guest.

        Game will be handled by Server computer. and guest will be connected to server and play.

        To serve a game, run this command:

        $ tchess --online
        # OR
        $ tchess --online --port=<port> --host=<host>
        # Example
        $ tchess --online --port=5000 --host=0.0.0.0

        then, the guest player can join the game by running this command:

        $ tchess --connect <host>:<port>
        # Example
        $ tchess --connect 192.168.1.2:5000

        Also guest can determine the name:

        $ tchess --connect 192.168.1.2:5000 --name="guest name"

        Also server player can use more options:

        # set color of guest player (default is black)
        $ tchess --online --guest-color=white
'''.strip())

def load_game_from_file(path: str):
    """ Loads the game object from a file """
    tmp_f = open(path, 'rb')
    file_game = pickle.load(tmp_f)
    tmp_f.close()
    game = Game()
    game.turn = str(file_game.turn)
    game.logs = list(file_game.logs)
    game.version = int(file_game.version)
    game.highlight_cells = list(file_game.highlight_cells)
    game.white_player = str(file_game.white_player)
    game.black_player = str(file_game.black_player)
    game.board = list(file_game.board)
    game.is_end = bool(file_game.is_end)
    game.winner = file_game.winner
    game.current_check = file_game.current_check
    return game

def online_connect(target, options=[], arguments=[]):
    """ Connects user to a served game """
    my_name = None
    for option in options:
        if option.startswith('--name='):
            my_name = option.split('=', 1)[1]

    target = 'http://' + target
    session_id = None
    my_color = None
    try:
        print('Waiting for server confirmation...')
        connect_args = {}
        if my_name is not None:
            connect_args['name'] = my_name
        res = requests.get(target + '/connect', connect_args)
        if not res.ok:
            print('ERROR: invalid response from server: ' + str(res.status_code) + ': ' + res.text, file=sys.stderr)
            sys.exit(1)

        session_id = res.text.strip()
        if session_id == '':
            session_id = None

        if session_id is None:
            print('ERROR: invalid session id', file=sys.stderr)
            sys.exit(1)

        # get my color
        try:
            my_color = requests.get(target + '/me', {'session': session_id}).text.strip()
        except:
            print('ERROR: error while getting guest color', file=sys.stderr)
            sys.exit(1)
    except:
        print('ERROR: cannot make http connection to the target', file=sys.stderr)
        sys.exit(1)

    while True:
        print('\033[H', end='')
        try:
            render = requests.get(target + '/render', {'session': session_id}).text
            render = render.split('\n', 1)
            turn = render[0]
            render = render[1]
            print(render)
            if turn == my_color:
                command = input(turn + ' Turn >>> ').strip()
                if command == '':
                    continue
                cmd_res = requests.get(target + '/command', {'session': session_id, 'cmd': command})
                print(cmd_res.text)
        except KeyboardInterrupt:
            break
        except:
            print('WARNING: unable to connect to server. retrying...', file=sys.stderr)
            continue
        time.sleep(0.5)

def run(args=[]):
    """ The main cli entry point """

    game_file_name = 'game.tchess'

    # parse the arguments
    options = [arg for arg in args if arg.startswith('-')]
    arguments = [arg for arg in args if not arg.startswith('-')]

    # check `--version` option
    if '--version' in options or '-v' in options:
        print(VERSION)
        sys.exit()

    # check the `--help` option
    if '--help' in options:
        options.remove('--help')
        show_help()
        sys.exit()

    # handle `--no-ansi` option
    if '--no-ansi' in options:
        options.remove('--no-ansi')
        Ansi.disable()

    # handle `--connect`
    if '--connect' in options:
        if len(arguments) <= 0:
            print('ERROR: <host>:<port> argument is required', file=sys.stderr)
            sys.exit(1)
        target = arguments[0]
        online_connect(target, options, arguments)
        return

    # handle `--replay` option
    is_play = False
    log_counter = 0
    if '--replay' in options:
        options.remove('--replay')
        is_play = True

    # handle `--replay-speed` option
    play_speed = 1
    for option in options:
        if option.startswith('--replay-speed='):
            options.remove(option)
            value = option.split('=', 1)[-1]
            try:
                play_speed = float(value)
            except:
                pass
            break

    # check the terminal size
    if not '--dont-check-terminal' in options:
        try:
            terminal_width = os.get_terminal_size().columns
        except:
            terminal_width = len(Game.ROW_SEPARATOR)+3
        if terminal_width < len(Game.ROW_SEPARATOR)+3:
            print(
                'ERROR: your terminal width is less than ' + str(len(Game.ROW_SEPARATOR)+3) + '. use --dont-check-terminal to ignore it.',
                file=sys.stderr
            )
            sys.exit(1)

    if len(arguments) > 0:
        game_file_name = arguments[0]

    if os.path.isfile(game_file_name):
        # if file exists, load the game from that
        # (means user wants to open a saved game)
        try:
            game = load_game_from_file(game_file_name)

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

    game_logs = game.logs
    if is_play:
        game = Game()

    # set player names
    for option in options:
        if option.startswith('--player-white='):
            game.white_player = option.split('=', 1)[-1]
        elif option.startswith('--player-black='):
            game.black_player = option.split('=', 1)[-1]

    if '--no-beep' in options:
        game.enable_beep = False

    # last result of runed command
    last_message = ''

    is_online = False
    game.guest_color = 'black'
    if '--online' in options:
        for option in options:
            if option.startswith('--guest-color='):
                game.guest_color = option.split('=', 1)[1].lower()
                if game.guest_color != 'white':
                    game.guest_color = 'black'
        is_online = True
        print('Server is served, waiting for guest...')
        game.guest_ran = False
        game.guest_connected = False
        host = '0.0.0.0'
        port = 8799
        for option in options:
            if option.startswith('--host='):
                host = option.split('=', 1)[1]
            elif option.startswith('--port='):
                try:
                    port = int(option.split('=', 1)[1])
                except:
                    pass
        server_thread = threading.Thread(target=server.serve, args=[game, host, port])
        server_thread.daemon = True
        server_thread.start()

        # wait for connection
        while not game.guest_connected:
            pass

    while True:
        # render the game board on the terminal
        print('\033[H', end='')
        title = ' Welcome to the TChess! '
        stars_len = len(Game.ROW_SEPARATOR) - len(title)
        title = (int(stars_len/2) * '*') + title + (int(stars_len/2) * '*')
        print(title, end='')
        print(' ' * (len(Game.ROW_SEPARATOR) - len(title)))
        print(' ' * len(Game.ROW_SEPARATOR))
        print(game.render())

        if game.is_end:
            # game is finished
            print(Ansi.GREEN + 'Checkmate!' + Ansi.RESET + (' ' * (len(Game.ROW_SEPARATOR)-10)))
            color = Ansi.CYAN if game.winner == 'white' else Ansi.RED
            print(color + game.winner + Ansi.GREEN + ' won!' + Ansi.RESET + (' ' * (len(Game.ROW_SEPARATOR)-10)))
            next_step = input('Press enter to continnue or type `back`: ').strip().lower()
            if next_step == 'back':
                game.is_end = False
                game.winner = None
                game.run_command('back')
                continue
            else:
                break

        # get command from user and run it
        tmp_turn = game.turn
        ansi_color = Ansi.RED if tmp_turn == 'black' else Ansi.CYAN
        # fix whitespace
        print(last_message, end='')
        print(' ' * (len(Game.ROW_SEPARATOR)-len(last_message)))
        print(' ' * len(Game.ROW_SEPARATOR), end='\r')
        if is_play:
            time.sleep(play_speed)
            try:
                command = game_logs[log_counter]
            except:
                print('Finished.')
                sys.exit()
            log_counter += 1
        else:
            if is_online and game.turn == game.guest_color:
                print('Waiting for guest command...')
                while not game.guest_ran:
                    pass
                print(game.guest_ran)
                game.guest_ran = False
                continue
            else:
                command = input(ansi_color + game.turn + Ansi.RESET + ' Turn >>> ').strip().lower()

        game.highlight_cells = []
        game.selected_cell = None

        # check the empty command
        if command == '':
            last_message = ''
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
        last_message = game.run_command(command)

        # save the game
        # open a file
        # this file is used to save the game state
        # after any command on the game, game will be re-write on this file
        if not is_play:
            game_file = open(game_file_name, 'wb')
            pickle.dump(game, game_file)
            game_file.close()

if __name__ == '__main__':
    run(sys.argv[1:])
