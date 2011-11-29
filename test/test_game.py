import scrabbler.board
import scrabbler.lexicon
import scrabbler.move
import scrabbler.player
import scrabbler.referee
import unittest

# Play a simple game using a referee and two players.

class TestGame(unittest.TestCase):
    def setUp(self):
        self.t = scrabbler.lexicon.Lexicon()
        for word in ['aa', 'ab', 'aba', 'abba', 'abbe', 'abed', 'ace', 'aced', 'ad', 'add', 'ae', 'aff', 'ba', 'baa', 'baba', 'babe', 'bad', 'baff', 'be', 'bead', 'bed', 'bee', 'beef', 'cab', 'caca', 'cad', 'cade', 'cafe', 'caff', 'ceca', 'cede', 'cee', 'dab', 'dace', 'dad', 'de', 'deaf', 'deb', 'dee', 'deed', 'def', 'ebb', 'ed', 'ef', 'eff', 'fab', 'fad', 'fe', 'fee', 'feed']:
            self.t.add(word.upper())

        self.p1 = TestPlayer(self.t, board=scrabbler.board.Board(variant='test'))
        self.p2 = TestPlayer(self.t, board=scrabbler.board.Board(variant='test'))
        self.ref = scrabbler.referee.Referee(self.p1, self.p2, self.t, board=scrabbler.board.Board(variant='test'), random_draw=False)
        self.maxDiff = None

    def test_game(self):
        game = self.ref.run()
        for move in game["moves"]:
            move["time"] = 0
        self.assertEqual(game, {'players': [{'score': 110, 'name': 'p1', 'rack': 'EEEEEE'}, {'score': 156, 'name': 'p2', 'rack': 'EEE'}], 'moves': [{'player': 'p1', 'move': 'cAcA 8H', 'rack': '??AAAAA', 'score': 4, 'time': 0}, {'player': 'p2', 'move': 'AA 7K', 'rack': 'AAAAAAA', 'score': 4, 'time': 0}, {'player': 'p1', 'move': 'AA 6L', 'rack': 'AAAAAAA', 'score': 4, 'time': 0}, {'player': 'p2', 'move': 'AA 5M', 'rack': 'AAAAAAA', 'score': 4, 'time': 0}, {'player': 'p1', 'move': 'ABBA 4L', 'rack': 'AAAAABB', 'score': 27, 'time': 0}, {'player': 'p2', 'move': 'BABA O1', 'rack': 'AAAAABB', 'score': 24, 'time': 0}, {'player': 'p1', 'move': 'CACA 2L', 'rack': 'AAACCCC', 'score': 16, 'time': 0}, {'player': 'p2', 'move': 'DAD I7', 'rack': 'AAAADDD', 'score': 9, 'time': 0}, {'player': 'p1', 'move': 'CAcA H6', 'rack': 'AACCDDD', 'score': 11, 'time': 0}, {'player': 'p2', 'move': 'DAD G9', 'rack': 'AAAADDD', 'score': 14, 'time': 0}, {'player': 'p1', 'move': 'CEDE 11E', 'rack': 'CDDDEEE', 'score': 14, 'time': 0}, {'player': 'p2', 'move': 'DEE 12H', 'rack': 'AAADEEE', 'score': 11, 'time': 0}, {'player': 'p1', 'move': 'DEED 11J', 'rack': 'DDDEEEE', 'score': 15, 'time': 0}, {'player': 'p2', 'move': 'DEE M11', 'rack': 'AAAEEEE', 'score': 8, 'time': 0}, {'player': 'p1', 'move': 'DEE 13I', 'rack': 'DEEEEEE', 'score': 15, 'time': 0}, {'player': 'p2', 'move': 'AE F10', 'rack': 'AAAEEEE', 'score': 8, 'time': 0}, {'player': 'p1', 'move': 'CEE E11', 'rack': 'EEEEEEE', 'score': 5, 'time': 0}, {'player': 'p2', 'move': 'AA D12', 'rack': 'AAEEEEE', 'score': 9, 'time': 0}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEEE', 'score': 0, 'time': 0}, {'player': 'p2', 'move': 'FEE 12L', 'rack': 'EEEEEFF', 'score': 18, 'time': 0}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEEE', 'score': 0, 'time': 0}, {'player': 'p2', 'move': 'EFF N12', 'rack': 'EEEEFFF', 'score': 23, 'time': 0}, {'player': 'p1', 'move': 'FE 14N', 'rack': 'EEEEEEE', 'score': 5, 'time': 0}, {'player': 'p2', 'move': 'FEE O13', 'rack': 'EEEEF', 'score': 27, 'time': 0}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEE', 'score': 0, 'time': 0}, {'player': 'p2', 'move': '--', 'rack': 'EEE', 'score': 0, 'time': 0}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEE', 'score': 0, 'time': 0}, {'player': 'p2', 'move': '--', 'rack': 'EEE', 'score': 0, 'time': 0}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEE', 'score': 0, 'time': 0}, {'player': 'p2', 'move': '--', 'rack': 'EEE', 'score': 0, 'time': 0}]})

class TestPlayer(scrabbler.player.Player):
    def best_move(self, moves):
        if moves:
            return max(moves, key = lambda x: (x.score, x.word))
        else:
            # check if we can exchange tiles
            bag_tiles = len(self.board.alltiles) - sum([1 for row in self.board.squares for square in row if square.letter]) - 2 * self.board.rack_size
            if bag_tiles >= self.board.rack_size:
                # trade in one tile
                return scrabbler.move.Move(row=None, col=None, kind=scrabbler.move.Move.MOVE_TRADE, word=self.rack[0])
            else:
                # pass
                return scrabbler.move.Move(row=None, col=None, kind=scrabbler.move.Move.MOVE_TRADE, word='')

if __name__ == '__main__':
    unittest.main()
