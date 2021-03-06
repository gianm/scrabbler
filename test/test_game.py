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
        self.maxDiff = None

    def test_game(self):
        p1 = TestPlayer(self.t, board=scrabbler.board.Board(variant='test'))
        p2 = TestPlayer(self.t, board=scrabbler.board.Board(variant='test'))
        ref = scrabbler.referee.Referee(p1, p2, self.t, board=scrabbler.board.Board(variant='test'), random_draw=False)

        game = ref.run()
        for move in game["moves"]:
            del move["time"]
        self.assertEqual(game, {'players': [{'score': 110, 'id': 'p1', 'rack': 'EEEEEE'}, {'score': 156, 'id': 'p2', 'rack': 'EEE'}], 'moves': [{'player': 'p1', 'move': 'cAcA 8H', 'rack': '??AAAAA', 'score': 4}, {'player': 'p2', 'move': 'AA 7K', 'rack': 'AAAAAAA', 'score': 4}, {'player': 'p1', 'move': 'AA 6L', 'rack': 'AAAAAAA', 'score': 4}, {'player': 'p2', 'move': 'AA 5M', 'rack': 'AAAAAAA', 'score': 4}, {'player': 'p1', 'move': 'ABBA 4L', 'rack': 'AAAAABB', 'score': 27}, {'player': 'p2', 'move': 'BAB(A) O1', 'rack': 'AAAAABB', 'score': 24}, {'player': 'p1', 'move': 'CAC(A) 2L', 'rack': 'AAACCCC', 'score': 16}, {'player': 'p2', 'move': 'D(A)D I7', 'rack': 'AAAADDD', 'score': 9}, {'player': 'p1', 'move': 'CA(c)A H6', 'rack': 'AACCDDD', 'score': 11}, {'player': 'p2', 'move': 'DAD G9', 'rack': 'AAAADDD', 'score': 14}, {'player': 'p1', 'move': 'CE(D)E 11E', 'rack': 'CDDDEEE', 'score': 14}, {'player': 'p2', 'move': 'DEE 12H', 'rack': 'AAADEEE', 'score': 11}, {'player': 'p1', 'move': 'DEED 11J', 'rack': 'DDDEEEE', 'score': 15}, {'player': 'p2', 'move': '(D)EE M11', 'rack': 'AAAEEEE', 'score': 8}, {'player': 'p1', 'move': 'DEE 13I', 'rack': 'DEEEEEE', 'score': 15}, {'player': 'p2', 'move': 'A(E) F10', 'rack': 'AAAEEEE', 'score': 8}, {'player': 'p1', 'move': '(C)EE E11', 'rack': 'EEEEEEE', 'score': 5}, {'player': 'p2', 'move': 'AA D12', 'rack': 'AAEEEEE', 'score': 9}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEEE', 'score': 0}, {'player': 'p2', 'move': 'F(E)E 12L', 'rack': 'EEEEEFF', 'score': 18}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEEE', 'score': 0}, {'player': 'p2', 'move': '(E)FF N12', 'rack': 'EEEEFFF', 'score': 23}, {'player': 'p1', 'move': '(F)E 14N', 'rack': 'EEEEEEE', 'score': 5}, {'player': 'p2', 'move': 'F(E)E O13', 'rack': 'EEEEF', 'score': 27}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEE', 'score': 0}, {'player': 'p2', 'move': '--', 'rack': 'EEE', 'score': 0}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEE', 'score': 0}, {'player': 'p2', 'move': '--', 'rack': 'EEE', 'score': 0}, {'player': 'p1', 'move': '--', 'rack': 'EEEEEE', 'score': 0}, {'player': 'p2', 'move': '--', 'rack': 'EEE', 'score': 0}]})

    def test_exception_badmove(self):
        p1 = TestPlayer(self.t, board=scrabbler.board.Board(variant='test'))
        p2 = BadMovePlayer(self.t, board=scrabbler.board.Board(variant='test'))
        ref = scrabbler.referee.Referee(p1, p2, self.t, board=scrabbler.board.Board(variant='test'), random_draw=False)

        game = ref.run()
        for move in game["moves"]:
            del move["time"]
        self.assertEqual(game, {'moves': [{'move': 'cAcA 8H', 'player': 'p1', 'rack': '??AAAAA', 'score': 4}], 'players': [{'id': 'p1', 'rack': 'AAAAAAA', 'score': 4}, {'exception': 'invalid move: ZZZZZZZ A1', 'id': 'p2', 'rack': 'AAAAAAA', 'score': 0}]})

    def test_exception_badtrade(self):
        p1 = TestPlayer(self.t, board=scrabbler.board.Board(variant='test'))
        p2 = BadTradePlayer(self.t, board=scrabbler.board.Board(variant='test'))
        ref = scrabbler.referee.Referee(p1, p2, self.t, board=scrabbler.board.Board(variant='test'), random_draw=False)

        game = ref.run()
        for move in game["moves"]:
            del move["time"]
        self.assertEqual(game, {'moves': [{'move': 'cAcA 8H', 'player': 'p1', 'rack': '??AAAAA', 'score': 4}, {'move': 'ZZZZZZZ --', 'player': 'p2', 'rack': 'AAAAAAA', 'score': 0}], 'players': [{'id': 'p1', 'rack': 'AAAAAAA', 'score': 4}, {'exception': 'letter Z not in rack', 'id': 'p2', 'rack': 'AAAAAAA', 'score': 0}]})

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

# Always trades 7 Z's
class BadTradePlayer(scrabbler.player.Player):
    def move(self, tiles, opponent_move):
        return scrabbler.move.Move.from_str("ZZZZZZZ --");

# Always plays 7 Z's
class BadMovePlayer(scrabbler.player.Player):
    def move(self, tiles, opponent_move):
        return scrabbler.move.Move.from_str("ZZZZZZZ A1");

if __name__ == '__main__':
    unittest.main()
