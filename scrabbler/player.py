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

        # Start with valid words
        moves = self.board.valid_moves(self.rack, self.lexicon)

        # Add a pass
        moves.append(Move(row=None, col=None, kind=Move.MOVE_TRADE, word=''))

        # Add trades
        if self.can_trade():
            for x in range(2 ** len(self.rack)):
                word = ''
                for i in range(len(self.rack)):
                    if x & (1<<i):
                        word += self.rack[i]
                moves.append(Move(row=None, col=None, kind=Move.MOVE_TRADE, word=word))

        move = self.best_move(moves)

        # Remove tiles used from our rack
        for letter in move.tiles:
            if letter.isupper():
                self.rack.remove(letter)
            else:
                self.rack.remove('?')

        # Play move onto the board
        self.board.play(move)

        return move

class MaxScorePlayer(Player):
    def best_move(self, moves):
        return max(moves, key = lambda x: x.score)

class MaxLengthPlayer(Player):
    def best_move(self, moves):
        return max(moves, key = lambda x: len(x.word) if x.kind != Move.MOVE_TRADE else -1)

class MaxTilesPlayer(Player):
    def best_move(self, moves):
        return max(moves, key = lambda x: len(x.tiles) if x.kind != Move.MOVE_TRADE else -1)

class RandomPlayer(Player):
    def best_move(self, moves):
        return random.choice(moves)

class TrainingPlayer(Player):
    def best_move(self, moves):
        # Randomly either trade letters or play a bad move
        trades = filter(lambda x: x.kind == Move.MOVE_TRADE, moves)
        plays = filter(lambda x: x.kind != Move.MOVE_TRADE, moves)

        if plays and random.choice([0, 1]) == 1:
            return random.choice(plays)
        else:
            return random.choice(trades)

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
