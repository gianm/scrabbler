import logging
import random
import re
import subprocess
import sys

import lexicon
from board import Board
from move import Move

class Player:
    def __init__(self, lexicon, board=None):
        self.board = board if board else Board()
        self.rack = []
        self.lexicon = lexicon

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
        else:
            # skip our turn
            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word='')

class MinScorePlayer(Player):
    def best_move(self, moves):
        if moves:
            return min(moves, key = lambda x: x.score)
        else:
            # skip our turn
            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word='')

class MaxLengthPlayer(Player):
    def best_move(self, moves):
        if moves:
            return max(moves, key = lambda x: len(x.word))
        else:
            # skip our turn
            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word='')

class TrainingPlayer(Player):
    def best_move(self, moves):
        # randomly either trade letters or play a bad move
        if not moves or random.choice([0, 1]) == 1:
            # need to track number of tiles in the bag
            # so we don't make illegal trades
            bag_tiles = len(self.board.alltiles) - sum([1 for row in self.board.squares for square in row if square.letter]) - 2 * self.board.rack_size

            if bag_tiles >= self.board.rack_size:
                exchange = ''.join([letter for letter in random.sample(self.rack, random.randrange(1, len(self.rack)))])
            else:
                exchange = ''

            return Move(row=None, col=None, kind=Move.MOVE_TRADE, word=exchange)
        else:
            return min(moves, key = lambda x: x.score)

class ExternalPlayer:
    """Provides the same interface as Player, but backed by an external program."""
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

        move = Move.from_str(line.rstrip())
        return move

    def __del__(self):
        self.popen.stdin.close()
        self.popen.stdout.close()
        self.popen.wait()

class ExternalPlayerError(Exception):
    """Issued when communication breaks down with an external player."""
    pass

# Follow the stdin/stdout protocol
if __name__ == '__main__':
    t = lexicon.TrieNode()
    with open('/usr/share/dict/words') as f:
        for word in f:
            t.add(word.rstrip().upper())

    if sys.argv >= 2:
        player = globals()[sys.argv[1]](t)
    else:
        player = MaxScorePlayer(t)

    # We're ready
    sys.stdout.write("HELLO\n")
    sys.stdout.flush()

    while 1:
        line = sys.stdin.readline()

        if not line:
            break

        match = re.match('^([A-Z\?\*]*):(.*)', line)
        if match:
            if match.group(2):
                opponent_move = Move.from_str(match.group(2))
            else:
                opponent_move = None
            move = player.move( list(match.group(1)), opponent_move )

            if move:
                sys.stdout.write(str(move) + "\n")
                sys.stdout.flush()
            else:
                break
        else:
            raise ValueError("invalid line: " + line)
