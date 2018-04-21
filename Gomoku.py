# Gomoku Main Game
from __future__ import print_function
import numpy as np
import argparse

# parse the input parameters
parser = argparse.ArgumentParser()

parser.add_argument('--width',type = int)
parser.add_argument('--height',type = int)

args = parser.parse_args()

WIDTH = args.width
HEIGHT = args.height

class Board(object):
    """
    board for the game
    like a x-y Cartesian coordinate system
    the (0,0) is 0 and coming to the right
    each row/column starts with 0(array-like)
    """

    def __init__(self, **kwargs):
        self.width = int(kwargs.get('width', 8))
        self.height = int(kwargs.get('height', 8))
        # kwargs is a parameter in the form of dictionary
        # key: move as location on the board,
        # value: player as pieces type
        self.states = {}                                # board states stored as a dict,
        self.n_in_row = int(kwargs.get('n_in_row', 5))  # need how many pieces in a row to win
        self.players = [1, 2]                           # player1 and player2

    def init_board(self, start_player=0):
        if self.width < self.n_in_row or self.height < self.n_in_row:
            raise Exception('board width and height can not be '
                            'less than {}'.format(self.n_in_row))

        self.current_player = self.players[start_player]  # start player
        # keep available moves in a list
        self.availables = list(range(self.width * self.height)) # a list including all the MOVE in the board starting from 0
        self.states = {}
        self.last_move = -1

    # move is a single value marking the position of the current point, while location is a (x,y) location
    def move_to_location(self, move):
        """
        3*3 board's moves like:
        6 7 8
        3 4 5
        0 1 2
        and move 5's location is (1,2)
        """
        h = move // self.width  #return the integer part of the result after the divide
        w = move % self.width
        return [h, w]

    def location_to_move(self, location):
        if len(location) != 2:
            return -1
        h = location[0]
        w = location[1]
        move = h * self.width + w
        if move not in range(self.width * self.height):
            return -1
        return move

    ######################
    def current_state(self):
        """return the board state from the perspective of the current player.
        state shape: 4*width*height --- a 4 level matrix
        """

        square_state = np.zeros((4, self.width, self.height))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width,
                            move_curr % self.height] = 1.0
            # 0 stores cur move
            square_state[1][move_oppo // self.width,
                            move_oppo % self.height] = 1.0
            # 1 stores oppo move
            square_state[2][self.last_move // self.width,
                            self.last_move % self.height] = 1.0
            # 2 indicate last move
        if len(self.states) % 2 == 0:
            square_state[3][:, :] = 1.0  # indicate the colour to play
            # all 3 are 1
        return square_state[:, ::-1, :]

    def do_move(self, move):
        # since states is a dictionary, so each time we do a move
        # we select from the dict by the move as a key and insert current_player
        # to mark that the player has put a pawn here.
        self.states[move] = self.current_player
        self.availables.remove(move)
        self.current_player = (
            # switch players
            self.players[0] if self.current_player == self.players[1]
            else self.players[1]
        )
        self.last_move = move

    def has_a_winner(self):
        width = self.width
        height = self.height
        states = self.states
        n = self.n_in_row

        moved = list(set(range(width * height)) - set(self.availables))
        ## find the difference between two sets
        if len(moved) < self.n_in_row + 2:
            return False, -1
            # if there is some space left, game continue

        for m in moved:
            # for every used space
            h = m // width
            w = m % width
            player = states[m]

            #row
            if (w in range(width - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n))) == 1):
                    # here we use the length of the set, it means only unqiue value could appears here
                    # so if len()==1 it means there are n pawns belongs to same player
                    # note 3 states: empty(-1)/player1/player2
                return True, player
            #column
            if (h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
                return True, player
            #x=y direction
            if (w in range(width - n + 1) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
                return True, player
            #x=-y direction
            if (w in range(n - 1, width) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
                return True, player

        return False, -1

    def game_end(self):
        """Check whether the game is ended or not"""
        win, winner = self.has_a_winner()
        if win:
            return True, winner
        elif not len(self.availables):
            return True, -1
        return False, -1

    def get_current_player(self):
        return self.current_player


class Game(object):
    """game server"""

    def __init__(self, board, **kwargs):
        self.board = board

    def graphic(self, board, player1, player2):
        """Draw the board and show game info"""
        width = board.width
        height = board.height

        print("Player", player1, "with X".rjust(3))
        print("Player", player2, "with O".rjust(3))
        print()
        for x in range(width):
            print("{0:8}".format(x), end='')
        print('\r\n')
        for i in range(height - 1, -1, -1):     # print from top to the bottom
            print("{0:4d}".format(i), end='')
            for j in range(width):
                loc = i * width + j
                p = board.states.get(loc, -1)
                if p == player1:
                    print('X'.center(8), end='')
                elif p == player2:
                    print('O'.center(8), end='')
                else:
                    print('_'.center(8), end='')
            print('\r\n\r\n')

    def start_play(self, player1, player2, start_player=0, is_shown=1):
        """start a game between two players"""
        if start_player not in (0, 1):
            raise Exception('start_player should be either 0 (player1 first) '
                            'or 1 (player2 first)')
        self.board.init_board(start_player)
        p1, p2 = self.board.players
        player1.set_player_ind(p1)
        player2.set_player_ind(p2)
        players = {p1: player1, p2: player2}
        if is_shown:
            self.graphic(self.board, player1.player, player2.player)
        while True:
            current_player = self.board.get_current_player()
            player_in_turn = players[current_player]
            move = player_in_turn.get_action(self.board)
            self.board.do_move(move)
            if is_shown:
                self.graphic(self.board, player1.player, player2.player)
            end, winner = self.board.game_end()
            if end:
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is", players[winner])
                    else:
                        print("Game end. Tie")
                return winner

class player(object):
    """
    human player
    """

    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        try:
            location = input("Your move: ")
            if isinstance(location, str):  # for python3
                location = [int(n, 10) for n in location.split(",")]
            move = board.location_to_move(location)
        except Exception as e:
            move = -1

        if move == -1 or move not in board.availables:
            print("invalid move")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)

def run():
    n = 5
    width = WIDTH
    height = HEIGHT
    if not width:
        width = 9
    if not height:
        height = 9
    try:
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)
        player1 = player()
        player2 = player()
        # set start_player=0 for human first
        game.start_play(player1, player2, start_player=1, is_shown=1)
    except KeyboardInterrupt:
        print('\n\rquit')

if __name__ == '__main__':
    run()

