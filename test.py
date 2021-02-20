#!/usr/bin/env python3

""" Runs the tchess tests """

import os
import sys
import subprocess
import threading
import time
import requests
from tchess import Game, Piece, load_game_from_file

Game.IS_TEST = True

PY_EXE = sys.executable

def str_contains_all(string, items):
    """ Gets a string and a list of string and checks all of list items are in string """
    for item in items:
        if not item in string:
            return False
    return True

def test_default_state_is_valid():
    """ Default state of chess board is valid """
    game = Game()
    assert game.board[2:6] == ([[None] * 8] * 4)

    for item in game.board[1]:
        assert item.name == Piece.PAWN
        assert item.color == 'white'

    for item in game.board[6]:
        assert item.name == Piece.PAWN
        assert item.color == 'black'

    colors = [
        ['white', 0],
        ['black', 7],
    ]

    for color in colors:
        index = color[1]
        color = color[0]
        assert game.board[index][0].name == Piece.ROCK
        assert game.board[index][7].color == color

        assert game.board[index][1].name == Piece.KNIGHT
        assert game.board[index][6].color == color

        assert game.board[index][2].name == Piece.BISHOP
        assert game.board[index][5].color == color

        assert game.board[index][3].name == Piece.KING
        assert game.board[index][4].color == color

def test_turn_changer_works():
    """ Game turn can be changed correctly """
    game = Game()
    assert game.turn == 'white'
    game.change_turn()
    assert game.turn == 'black'
    game.change_turn()
    assert game.turn == 'white'

def test_command_runner_works():
    """ Game command runner works """
    game = Game()

    assert 'invalid' in game.run_command('fdfgdd').lower()
    assert str_contains_all(game.run_command('mv 4.3 to 6-3').lower(), ['error', 'source', 'empty'])
    assert game.run_command('mv hi to 43543').lower().startswith('invalid')
    assert str_contains_all(game.run_command('mv 7.2 to 5.3').lower(), ['error', 'turn'])
    assert str_contains_all(game.run_command('mv 1.4 to 2.4').lower(), ['not', 'allowed'])

    assert game.board[1][0] is not None
    assert game.board[3][0] is None
    assert str_contains_all(game.run_command('mv 2.1 to 4.1').lower(), ['moved', '2.1', '4.1'])
    assert game.board[1][0] is None
    assert game.board[3][0] is not None
    assert game.board[3][0].name == Piece.PAWN

def test_log_list_is_working():
    """ Logs will be saved """
    game = Game()

    commands = [
        'move 2.1 to 3.1',
        'move 7.1 5.1',
    ]

    game.run_command('gfdgfd')

    for command in commands:
        game.run_command(command)

    assert game.logs == commands

def test_game_file_system_works():
    """ Game file system working correct """
    if os.path.exists('game.tchess'):
        os.remove('game.tchess')
    if os.path.exists('other.tchess'):
        os.remove('other.tchess')

    proc = subprocess.Popen(
        PY_EXE + ' tchess', shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
    )
    proc.communicate(input='mv 2.1 to 3.1\nexit'.encode())

    assert os.path.isfile('game.tchess')
    saved_game = load_game_from_file('game.tchess')
    assert isinstance(saved_game, Game)
    assert saved_game.version == Game().version
    assert saved_game.logs == ['mv 2.1 to 3.1']

    proc = subprocess.Popen(
        PY_EXE + ' tchess other.tchess', shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
    )
    proc.communicate(input='mv 2.2 to 3.2\nexit'.encode())

    assert os.path.isfile('other.tchess')
    saved_game2 = load_game_from_file('other.tchess')
    assert isinstance(saved_game2, Game)
    assert saved_game2.version == Game().version
    assert saved_game2.logs == ['mv 2.2 to 3.2']

    proc = subprocess.Popen(
        PY_EXE + ' tchess other.tchess', shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
    )
    proc.communicate(input='mv 7.3 to 6.3\nexit'.encode())

    assert os.path.isfile('other.tchess')
    saved_game2 = load_game_from_file('other.tchess')
    assert isinstance(saved_game2, Game)
    assert saved_game2.version == Game().version
    assert saved_game2.logs == ['mv 2.2 to 3.2', 'mv 7.3 to 6.3']

    proc = subprocess.Popen(
        PY_EXE + ' tchess --replay --replay-speed=0.1 other.tchess', shell=True,
        stdout=subprocess.PIPE
    )
    proc.communicate()

    os.remove('game.tchess')
    os.remove('other.tchess')

def test_command_s_works():
    """ Command `s` for show allowed cells to go working correct """
    game = Game()
    game.run_command('s 2.1')

    assert game.highlight_cells == [[2, 0], [3, 0]]

    game.run_command('mv 2.1 3.1')

    game.run_command('s 3.1')
    assert game.highlight_cells == [[3, 0]]

def test_pawn_move_validation_works():
    """ Pawn move validation working correct """
    game = Game()

    game.run_command('mv 2.1 3.1')
    assert game.board[1][0] is None
    assert game.board[2][0].name == Piece.PAWN

    game.run_command('mv 7.1 5.1')
    assert game.board[6][0] is None
    assert game.board[4][0].name == Piece.PAWN

    assert str_contains_all(game.run_command('mv 2.2 3.5').lower(), ['error'])
    assert game.board[1][1] is not None
    assert game.board[2][4] is None

    game = Game()

    game.run_command('mv 2.1 4.1')
    game.run_command('mv 7.1 5.1')
    assert str_contains_all(
        game.run_command('mv 4.1 5.1').lower(),
        ['error', 'location', 'allowed', 'not']
    )

    assert str_contains_all(game.run_command('s 4.1').lower(), ['cannot', 'move'])

    game = Game()

    game.run_command('mv 2.1 4.1')
    game.run_command('mv 7.8 6.8')
    game.run_command('mv 4.1 5.1')
    game.run_command('mv 6.8 5.8')
    game.run_command('mv 5.1 6.1')
    game.run_command('mv 7.2 6.1')
    assert str_contains_all(game.run_command('s 7.1').lower(), ['piece', 'move', 'cannot'])

def test_rock_move_validation_works():
    """ Rock move validation working correct """
    game = Game()

    assert str_contains_all(game.run_command('s 1.1').lower(), ['piece', 'move', 'cannot'])
    assert str_contains_all(game.run_command('s 8.1').lower(), ['piece', 'move', 'cannot'])
    game.run_command('mv 2.1 4.1')
    game.run_command('s 1.1')
    assert game.highlight_cells == [[1, 0], [2, 0]]
    game.run_command('mv 7.1 5.1')
    game.run_command('s 8.1')
    assert game.highlight_cells == [[6, 0], [5, 0]]
    game.run_command('mv 1.1 3.1')
    game.run_command('s 3.1')
    assert game.highlight_cells == [
        [1, 0], [0, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7]
    ]
    game.run_command('mv 8.1 6.1')
    game.run_command('s 6.1')
    assert game.highlight_cells == [
        [6, 0], [7, 0], [5, 1], [5, 2], [5, 3], [5, 4], [5, 5], [5, 6], [5, 7]
    ]
    game.run_command('mv 2.2 4.2')
    game.run_command('mv 5.1 4.2')
    game.run_command('s 6.1')
    assert game.highlight_cells == [
        [4, 0], [3, 0], [6, 0], [7, 0], [5, 1], [5, 2], [5, 3], [5, 4], [5, 5], [5, 6], [5, 7]
    ]
    game.run_command('mv 3.1 3.2')
    game.run_command('s 3.2')
    assert game.highlight_cells == [
        [3, 1], [1, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 0]
    ]

def test_king_move_validation_works():
    """ King move validation working correct """
    game = Game()
    assert str_contains_all(game.run_command('s 1.4').lower(), ['piece', 'move', 'cannot'])
    assert str_contains_all(game.run_command('s 8.4').lower(), ['piece', 'move', 'cannot'])
    game.run_command('mv 2.4 4.4')
    game.run_command('s 1.4')
    assert game.highlight_cells == [[1, 3]]
    game.run_command('mv 7.4 5.4')
    game.run_command('s 8.4')
    assert game.highlight_cells == [[6, 3]]
    game.run_command('mv 1.4 2.4')
    game.run_command('s 2.4')
    assert game.highlight_cells == [[2, 4], [2, 3], [2, 2], [0, 3]]
    game.run_command('mv 8.4 7.4')
    game.run_command('s 7.4')
    assert game.highlight_cells == [[7, 3], [5, 4], [5, 3], [5, 2]]
    game.run_command('mv 2.3 4.3')
    game.run_command('mv 5.4 4.3')
    game.run_command('mv 4.4 5.4')
    game.run_command('mv 7.4 6.4')
    game.run_command('s 6.4')
    assert game.highlight_cells == [[6, 3], [5, 4], [5, 2], [4, 4], [4, 3], [4, 2]]
    game.run_command('mv 2.2 3.2')
    assert str_contains_all(game.run_command('mv 6.4 5.4').lower(), ['moved', 'to'])

def test_knight_move_validation_works():
    """ Knight move validation working correct """
    game = Game()
    game.run_command('s 1.2')
    assert game.highlight_cells == [[2, 2], [2, 0]]
    game.run_command('s 8.7')
    assert game.highlight_cells == [[5, 7], [5, 5]]
    game.run_command('mv 1.2 3.3')
    game.run_command('s 3.3')
    assert game.highlight_cells == [[3, 4], [3, 0], [4, 3], [4, 1], [0, 1]]
    game.run_command('mv 7.2 5.2')
    assert str_contains_all(game.run_command('mv 3.3 5.2').lower(), ['moved', 'to'])

def test_bishop_move_validation_works():
    """ Bishop move validation working correct """
    game = Game()

    assert str_contains_all(game.run_command('s 1.3'), ['cannot', 'move'])
    assert str_contains_all(game.run_command('s 8.6'), ['cannot', 'move'])

    game.run_command('mv 2.4 3.4')
    game.run_command('s 1.3')
    assert game.highlight_cells == [[1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]
    game.run_command('mv 7.1 6.1')
    game.run_command('mv 1.3 4.6')
    game.run_command('s 4.6')
    assert game.highlight_cells == [
        [4, 6], [5, 7], [2, 4], [1, 3], [0, 2], [2, 6], [4, 4], [5, 3], [6, 2]
    ]
    game.run_command('mv 7.4 6.4')
    game.run_command('mv 4.6 6.4')
    assert game.board[3][5] is None
    assert game.board[5][3].name == Piece.BISHOP
    game.run_command('s 8.3')
    assert game.highlight_cells == [[6, 3], [5, 4], [4, 5], [3, 6], [2, 7]]
    game.run_command('mv 8.3 5.6')
    game.run_command('s 5.6')
    assert game.highlight_cells == [[3, 4], [2, 3], [5, 6], [5, 4], [6, 3], [7, 2], [3, 6], [2, 7]]
    game.run_command('mv 2.1 3.1')
    game.run_command('mv 5.6 3.4')
    assert game.board[4][5] is None
    assert game.board[2][3].name == Piece.BISHOP

def test_command_back_works():
    """ Command `back` works """
    game = Game()
    assert game.logs == []
    game.run_command('mv 2.1 3.1')
    game.run_command('mv 7.3 5.3')
    assert game.logs == ['mv 2.1 3.1', 'mv 7.3 5.3']
    assert game.board[1][0] is None
    assert game.board[2][0] is not None
    assert game.board[6][2] is None
    assert game.board[4][2] is not None
    game.run_command('back')
    assert game.logs == ['mv 2.1 3.1']
    assert game.board[1][0] is None
    assert game.board[2][0] is not None
    assert game.board[6][2] is not None
    assert game.board[4][2] is None

    game = Game()
    assert str_contains_all(game.run_command('back'), ['first', 'move'])

def test_checkmate_and_example():
    """ Checkmate works with a example """
    commands = [
        'mv 2.6 3.6',
        'mv 7.1 6.1',
        'mv 1.5 3.7',
        'mv 6.1 5.1',
        'mv 1.2 3.3',
        'mv 5.1 4.1',
        'mv 3.3 5.4',
        'mv 4.1 3.1',
        'mv 3.7 7.3',
    ]

    game = Game()

    for command in commands:
        assert game.current_check is None
        game.run_command(command)

    assert game.current_check == 'black'

    game.run_command('mv 8.4 7.3',)

    assert game.is_end
    assert game.winner == 'white'

def test_online_playing_system_works():
    """ Online playing system works """
    if os.name == 'nt' or '--no-server' in sys.argv:
        print('Igonred...', end=' ', flush=True)
        return

    def first_asserts(game):
        assert game.black_player == 'the-guest'
        assert game.logs == ['mv 2.1 3.1', 'mv 7.1 6.1', 'mv 2.2 3.2']
        assert game.board[1][0] is None
        assert game.board[6][0] is None
        assert game.board[1][1] is None

    def second_asserts(game):
        assert game.logs == ['mv 2.1 3.1', 'mv 7.1 6.1']
        assert game.board[6][0] is None
        assert game.board[5][0] is not None

    tests = [
        [[[
        'y',
        'mv 2.1 3.1',
        's 7.1',
        'mv 2.2 3.2',
        'q',
        ], '--online --port=8799 --host=127.0.0.1'], [[
        'mv 7.1 6.1',
        's 1.1',
        'back',
        'gfdhg',
        'mv 6.1 5.1',
        ], '--connect 127.0.0.1:8799 --name=the-guest'], first_asserts],

        [[[
        'y',
        'mv 7.1 6.1',
        'q',
        ], '--online --port=8799 --host=127.0.0.1 --guest-color=white'], [[
        'mv 2.1 3.1',
        'mv 2.2 3.2',
        ], '--connect 127.0.0.1:8799'], second_asserts],
    ]

    for test in tests:
        # remove game file
        if os.path.isfile('server.tchess'):
            os.remove('server.tchess')

        os.system('printf "' + '\\n'.join(test[0][0]) + '\\n" | ' + PY_EXE + ' tchess ' + test[0][1] + ' server.tchess >/dev/null 2>&1 &')

        time.sleep(2)

        os.system('printf "' + '\\n'.join(test[1][0]) + '\\n" | ' + PY_EXE + ' tchess ' + test[1][1] + ' >/dev/null 2>&1')

        game = load_game_from_file('server.tchess')

        test[2](game)

        os.remove('server.tchess')

def test_server_http_api_works():
    """ Game server http APIs working correct """
    if os.name == 'nt' or '--no-server' in sys.argv:
        print('Igonred...', end=' ', flush=True)
        return

    # remove game file
    if os.path.isfile('server.tchess'):
        os.remove('server.tchess')

    os.system('printf "y\\nmv 2.1 3.1\\nq\\n" | ' + PY_EXE + ' tchess --online --host=127.0.0.1 --port=8799 server.tchess >/dev/null 2>&1 &')

    time.sleep(4)

    r = requests.get('http://127.0.0.1:8799/me')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])
    r = requests.get('http://127.0.0.1:8799/me?session=foo')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])

    r = requests.get('http://127.0.0.1:8799/render')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])
    r = requests.get('http://127.0.0.1:8799/render?session=foo')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])

    r = requests.get('http://127.0.0.1:8799/command')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])
    r = requests.get('http://127.0.0.1:8799/command?session=foo')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])

    r = requests.get('http://127.0.0.1:8799/connect')
    assert r.status_code == 200
    session_id = r.text.strip()

    r = requests.get('http://127.0.0.1:8799/connect')
    assert r.status_code == 401
    assert str_contains_all(r.text, ['started', 'currently'])

    r = requests.get('http://127.0.0.1:8799/me')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])
    r = requests.get('http://127.0.0.1:8799/me?session=foo')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])
    r = requests.get('http://127.0.0.1:8799/me?session=' + session_id)
    assert r.status_code == 200
    assert str_contains_all(r.text, ['black'])

    r = requests.get('http://127.0.0.1:8799/render')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])
    r = requests.get('http://127.0.0.1:8799/render?session=foo')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])
    r = requests.get('http://127.0.0.1:8799/render?session=' + session_id)
    assert r.status_code == 200

    r = requests.get('http://127.0.0.1:8799/command')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])
    r = requests.get('http://127.0.0.1:8799/command?session=foo')
    assert r.status_code == 403
    assert str_contains_all(r.text, ['invalid', 'session'])
    r = requests.get('http://127.0.0.1:8799/command?session=' + session_id)
    assert r.status_code == 401
    assert str_contains_all(r.text, ['missing', 'cmd'])
    r = requests.get('http://127.0.0.1:8799/command?cmd=test&session=' + session_id)
    assert r.status_code == 200
    r = requests.get('http://127.0.0.1:8799/command?cmd=back&session=' + session_id)
    assert r.status_code == 401
    assert str_contains_all(r.text, ['command', 'disabled'])
    r = requests.get('http://127.0.0.1:8799/command?cmd=mv 7.1 6.1&session=' + session_id)
    assert r.status_code == 200

    os.remove('server.tchess')

TESTS = [
    test_default_state_is_valid,
    test_turn_changer_works,
    test_command_runner_works,
    test_log_list_is_working,
    test_game_file_system_works,
    test_command_s_works,
    test_pawn_move_validation_works,
    test_rock_move_validation_works,
    test_king_move_validation_works,
    test_knight_move_validation_works,
    test_bishop_move_validation_works,
    test_command_back_works,
    test_checkmate_and_example,
    test_server_http_api_works,
    test_online_playing_system_works,
]

# running the tests
def run():
    """ Run the tests """
    i = 1
    for test in TESTS:
        print(f'[{i}/{len(TESTS)}] ' + test.__doc__.strip().splitlines()[0] + '...', end=' ', flush=True)
        test()
        print('PASS', flush=True)
        i += 1
    print('All tests passed successfully.')

if __name__ == '__main__':
    run()
