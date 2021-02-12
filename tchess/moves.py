""" Piece move validators

In this module, we have some functions to validate different pieces moves.
"""

def pawn_move(self, game, src, dst):
    """ Validates pawn move """
    x = src[0]
    y = src[1]
    result = []
    if self.color == 'white':
        if x == 1:
            result = [
                [2, y],
                [3, y],
            ]
        else:
            result = [
                [x + 1, y],
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
            except:
                pass
            a += 1
        try:
            if game.board[x + 1][y + 1] is not None:
                if game.board[x + 1][y + 1].color != self.color:
                    result.append([x + 1, y + 1])
        except:
            pass
        try:
            if game.board[x + 1][y - 1] is not None:
                if game.board[x + 1][y - 1].color != self.color:
                    result.append([x + 1, y - 1])
        except:
            pass
    else:
        if x == 6:
            result = [
                [5, y],
                [4, y],
            ]
        else:
            result = [
                [x - 1, y],
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
            except:
                pass
            a += 1
        try:
            if game.board[x - 1][y + 1] is not None:
                if game.board[x - 1][y + 1].color != self.color:
                    result.append([x - 1, y + 1])
        except:
            pass
        try:
            if game.board[x - 1][y - 1] is not None:
                if game.board[x - 1][y - 1].color != self.color:
                    result.append([x - 1, y - 1])
        except:
            pass
        a = 0
        while a < len(result):
            tmp = result[a]
            try:
                if game.board[tmp[0]][tmp[1]] is not None:
                    if tmp[1] == y:
                        result.pop(a)
            except:
                pass
            a += 1
    return result
