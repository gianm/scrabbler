#!/usr/bin/env python

from scrabbler.board import Board
from scrabbler.move import Move
from scrabbler.referee import Referee
from scrabbler.lexicon import Lexicon
from scrabbler import player

# You can define your own AI by subclassing Player
class MyPlayer(player.Player):
    def best_move(self, moves):
        # All your valid moves are in 'moves', including trades (where
        # move.kind == Move.MOVE_TRADE). You need to pick one move and
        # return it.

        # If you need the Board object, it is in self.board
        # And your rack is in self.rack as a list of letters

        # Let's pick the word that uses the most tiles, and prefer regular
        # moves over trades:

        return max(moves, key = lambda x: len(x.tiles) if x.kind != Move.MOVE_TRADE else -1)

# Let's play a game!

# First load a lexicon. Let's use /usr/share/dict/words on this system
l = Lexicon()
with open('/usr/share/dict/words') as words:
    for word in words:
        l.add(word.rstrip().upper())

# Set up the players.
# They can share a lexicon (since they won't change it) but each needs
# their own board
player1 = player.MaxScorePlayer(lexicon=l, board=Board())
player2 = MyPlayer(lexicon=l, board=Board())

# Set up a referee.
# It needs its own board too
referee = Referee(player1=player1, player2=player2, lexicon=l, board=Board())

# Run the game
game = referee.run()

# Print out the list of moves
for move_info in game["moves"]:
    # Note that move_info is not actually a Move object
    # It's just a dictionary with information about the move
    print "{0:25s} {1:25s} {2:10s} {3:8d}".format(
        move_info["player"],
        move_info["move"] + " " + str(move_info["score"]),
        move_info["rack"],
        move_info["time"])

# Print the final scores
print
print game["players"][0]["name"] + ": " + str(game["players"][0]["score"])
print game["players"][1]["name"] + ": " + str(game["players"][1]["score"])

# Print the final board
print
print referee.board
