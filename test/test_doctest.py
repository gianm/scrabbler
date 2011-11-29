#!/opt/local/bin/python

import unittest
import doctest

import scrabbler.board
import scrabbler.lexicon
import scrabbler.move
import scrabbler.player
import scrabbler.referee

class TestDoctest(unittest.TestCase):
    def test_board(self):
        fail, total = doctest.testmod(scrabbler.board)
        self.assertEquals(fail, 0)
    def test_lexicon(self):
        fail, total = doctest.testmod(scrabbler.lexicon)
        self.assertEquals(fail, 0)
    def test_move(self):
        fail, total = doctest.testmod(scrabbler.move)
        self.assertEquals(fail, 0)
    def test_player(self):
        fail, total = doctest.testmod(scrabbler.player)
        self.assertEquals(fail, 0)
    def test_referee(self):
        fail, total = doctest.testmod(scrabbler.referee)
        self.assertEquals(fail, 0)

if __name__ == '__main__':
    unittest.main()
