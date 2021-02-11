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

TESTS = [
    test_default_state_is_valid,
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
