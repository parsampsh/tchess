""" Piece move validators

In this module, we have some functions to validate different pieces moves.
"""

def pawn_move(self, game, src, dst):
    """ Validates pawn move """
    x = src[0]
    y = src[1]
    result = []
    pawns_row = 1 if self.color == 'white' else 6
    pawns_front_two_cells = [2, 3] if self.color == 'white' else [5, 4]
    pawns_one_row_front = 1 if self.color == 'white' else -1

    if x == pawns_row:
        result = [
            [pawns_front_two_cells[0], y],
            [pawns_front_two_cells[1], y],
        ]
    else:
        result = [
            [x + pawns_one_row_front, y],
        ]
    a = 0
    while a < len(result):
        tmp = result[a]
        try:
            if game.board[tmp[0]][tmp[1]] is not None:
                result.pop(a)
                if a == 0:
                    result.pop(0)
                    break
                a -= 1
        except IndexError:
            pass
        a += 1
    try:
        if game.board[x + pawns_one_row_front][y + 1] is not None:
            if game.board[x + pawns_one_row_front][y + 1].color != self.color:
                result.append([x + pawns_one_row_front, y + 1])
    except IndexError:
        pass
    try:
        if game.board[x + pawns_one_row_front][y - 1] is not None:
            if game.board[x + pawns_one_row_front][y - 1].color != self.color:
                result.append([x + pawns_one_row_front, y - 1])
    except IndexError:
        pass

    return result
