import subprocess
import random

import lexicon
from board import Board
from move import Move

class Player:
    def __init__(self, lexicon, board=None):
        self.board = board if board else Board()
        self.rack = []
        self.lexicon = lexicon

    def can_trade(self):
        # We can trade if there are more than self.board.rack_size tiles left in the bag
        if len(self.board.alltiles) - sum([1 for row in self.board.squares for square in row if square.letter]) - 3 * self.board.rack_size >= 0:
            return True
        else:
            return False

    def move(self, tiles, opponent_move):
        if opponent_move:
            self.board.play(opponent_move)

        if tiles:
            self.rack += tiles

        moves = self.board.valid_moves(self.rack, self.lexicon)
        move = self.best_move(moves)

        if move.kind == Move.MOVE_TRADE:
            for letter in move.word:
                self.rack.remove(letter)
        else:
            # figure out how many tiles were used by this move
            # XXX maybe should be in b.play
            for letter, square in zip(list(move.word), self.board.walk_move(move)):
                if not square.letter:
                    if letter.isupper():
                        self.rack.remove(letter)
                    else:
                        self.rack.remove('?')
            self.board.play(move)

        return move

class MaxScorePlayer(Player):
    def best_move(self, moves):
        if moves:
            return max(moves, key = lambda x: x.score)
        elif self.can_trade():
            # toss these useless tiles
            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word=''.join(self.rack))
        else:
            # skip our turn
            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word='')

class MinScorePlayer(Player):
    def best_move(self, moves):
        if moves:
            return min(moves, key = lambda x: x.score)
        elif self.can_trade():
            # toss these useless tiles
            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word=''.join(self.rack))
        else:
            # skip our turn
            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word='')

class MaxLengthPlayer(Player):
    def best_move(self, moves):
        if moves:
            return max(moves, key = lambda x: len(x.word))
        elif self.can_trade():
            # toss these useless tiles
            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word=''.join(self.rack))
        else:
            # skip our turn
            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word='')

class TrainingPlayer(Player):
    def best_move(self, moves):
        # randomly either trade letters or play a bad move
        if not moves or random.choice([0, 1]) == 1:
            if self.can_trade():
                exchange = ''.join([letter for letter in random.sample(self.rack, random.randint(1, len(self.rack)))])
            else:
                exchange = ''

            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word=exchange)
        else:
            return min(moves, key = lambda x: x.score)

class ExternalPlayer:
    """Provides the same interface as Player, but backed by an external
    program. See bin/scrabbler-player for an example implementation."""
    def __init__(self, cmd):
        self.popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)

        # Wait for "HELLO"
        line = self.popen.stdout.readline()
        if not line or line.rstrip() != "HELLO":
            raise ExternalPlayerError("no HELLO")

    def move(self, tiles, opponent_move):
        opponent_move_str = str(opponent_move) if opponent_move else ''
        self.popen.stdin.write(''.join(tiles) + ":" + opponent_move_str + "\n")
        self.popen.stdin.flush()

        line = self.popen.stdout.readline()
        if not line:
            raise ExternalPlayerError("no move")

        # Might raise InvalidMoveError
        move = Move.from_str(line.rstrip())
        return move

    def __del__(self):
        self.popen.stdin.close()
        self.popen.stdout.close()
        self.popen.wait()

class ExternalPlayerError(Exception):
    """Issued when communication breaks down with an external player."""
    pass
