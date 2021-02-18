""" Piece move validators

In this module, we have some functions to validate different pieces moves.
"""

def pawn_move(self, game, src):
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

def rock_move(self, game, src):
    """ Validates rock move """
    x = src[0]
    y = src[1]
    result = []

    loop_condition = (lambda i: i < 8) if self.color == 'white' else (lambda i: i >= 0)
    reverse_loop_condition = (lambda i: i < 8) if self.color == 'black' else (lambda i: i >= 0)
    counter_eval = +1 if self.color == 'white' else -1
    reverse_counter_eval = -counter_eval

    loops = [
        [loop_condition, counter_eval],
        [reverse_loop_condition, reverse_counter_eval]
    ]

    for loop in loops:
        i = x
        while loop[0](i):
            if i != x:
                if game.board[i][y] is not None:
                    if game.board[i][y].color != self.color:
                        result.append([i, y])
                    break
                result.append([i, y])
            i += loop[1]

    for loop in loops:
        i = y
        while loop[0](i):
            if i != y:
                if game.board[x][i] is not None:
                    if game.board[x][i].color != self.color:
                        result.append([x, i])
                    break
                result.append([x, i])
            i += loop[1]

    return result

def king_move(self, game, src):
    """ Validates king move """
    x = src[0]
    y = src[1]
    result = [
        [x+1, y+1], [x+1, y], [x+1, y-1],
        [x,   y+1],           [x,   y-1],
        [x-1, y+1], [x-1, y], [x-1, y-1],
    ]

    new_result = []
    i = 0
    while i < len(result):
        a = result[i][0]
        b = result[i][1]
        if a >= 0 and b >= 0:
            try:
                if game.board[a][b] is not None:
                    if game.board[a][b].color != self.color:
                        new_result.append(result[i])
                else:
                    new_result.append(result[i])
            except IndexError:
                pass
        i += 1

    return new_result

def knight_move(self, game, src):
    """ Validates knight move """
    x = src[0]
    y = src[1]
    result = [
        [x+1, y+2],
        [x-1, y+2],
        [x+1, y-2],
        [x-1, y-2],
        [x+2, y+1],
        [x+2, y-1],
        [x-2, y+1],
        [x-2, y-1],
    ]

    new_result = []
    i = 0
    while i < len(result):
        a = result[i][0]
        b = result[i][1]
        if a >= 0 and b >= 0:
            try:
                if game.board[a][b] is not None:
                    if game.board[a][b].color != self.color:
                        new_result.append(result[i])
                else:
                    new_result.append(result[i])
            except IndexError:
                pass
        i += 1

    return new_result

def bishop_move(self, game, src):
    """ Validates bishop move """
    x = src[0]
    y = src[1]
    result = []

    loop_condition = (lambda i: i < 8) if self.color == 'white' else (lambda i: i >= 0)
    reverse_loop_condition = (lambda i: i < 8) if self.color == 'black' else (lambda i: i >= 0)
    counter_eval = +1 if self.color == 'white' else -1
    reverse_counter_eval = -counter_eval

    loops = [
        [loop_condition, counter_eval],
        [reverse_loop_condition, reverse_counter_eval]
    ]

    for loop in loops:
        i = x
        j = y
        while loop[0](i) and loop[0](j):
            if i != x and j != y:
                try:
                    if game.board[i][j] is not None:
                        if game.board[i][j].color != self.color:
                            result.append([i, j])
                        break
                except IndexError:
                    break
                result.append([i, j])
            i += loop[1]
            j += loop[1]

    for loop in loops:
        i = x
        j = y
        while loop[0](i) and loop[0](j):
            if i != x and j != y:
                try:
                    if game.board[i][j] is not None:
                        if game.board[i][j].color != self.color:
                            result.append([i, j])
                        break
                except IndexError:
                    break
                result.append([i, j])
            i += -loop[1]
            j += loop[1]

    new_result = []
    for item in result:
        if item[0] >= 0 and item[1] >= 0:
            if item != src:
                new_result.append(item)

    return new_result
