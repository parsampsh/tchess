#!/usr/bin/env python3

""" Runs the tchess tests """

import os
import pickle
import subprocess
from tchess import Game, Piece, load_game_from_file

PY_EXE = 'python3'
if os.name == 'nt':
    PY_EXE = 'python'

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
        assert item.name == 'pawn'
        assert item.color == 'white'

    for item in game.board[6]:
        assert item.name == 'pawn'
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
    assert str_contains_all(game.run_command('mv 2.3 to 2.4').lower(), ['error', 'kill', 'self'])

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

TESTS = [
    test_default_state_is_valid,
    test_turn_changer_works,
    test_command_runner_works,
    test_log_list_is_working,
    test_game_file_system_works,
]

# running the tests
def run():
    """ Run the tests """
    i = 1
    for test in TESTS:
        print(f'[{i}/{len(TESTS)}] ' + test.__doc__ + '...', end=' ')
        test()
        print('PASS')
        i += 1
    print('All tests passed successfully.')

if __name__ == '__main__':
    run()
