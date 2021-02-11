#!/usr/bin/env python3

""" Runs the tchess tests """

from tchess.tchess import Game, Piece

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
    #assert game.run_command('mov ') in result.lower()

def test_game_file_system_works():
    """ Game file system working correct """
    pass

TESTS = [
    test_default_state_is_valid,
    test_turn_changer_works,
    test_command_runner_works,
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
