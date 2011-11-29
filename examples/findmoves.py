#!/usr/bin/env python

from scrabbler.board import Board
from scrabbler.move import Move
from scrabbler import lexicon

# Load a lexicon
# Let's use /usr/share/dict/words on this system
l = lexicon.TrieNode()
with open('/usr/share/dict/words') as words:
    for word in words:
        l.add(word.rstrip().upper())

# Let's use the official variant, "scrabble".
# Variants are different board layouts and letter distributions, stored
# as JSON files in the variants/ directory
b = Board(variant='scrabble')

# Play a few words
b.play(Move(row=6, col=7, kind=Move.MOVE_DOWN, word="DoGGED"))
b.play(Move(row=7, col=6, kind=Move.MOVE_ACROSS, word="BoSS"))
b.play(Move.from_str("GOB 10H"))

# Let's say our player has a rack of UVWXYZ and a blank (?).
# Print each valid move, sorted by score
moves = b.valid_moves(rack=list("UVWXYZ?"), lexicon=l)
for move in sorted(moves, key = lambda x: x.score):
    print str(move) + " (" + str(move.score) + ")"

# Print the board
print b