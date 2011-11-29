import json
import logging
import random
import sys
import time

import lexicon
from board import Board
from move import Move, InvalidMoveError
from player import TrainingPlayer, ExternalPlayer

class Referee:
    """Manage a game between two Players."""

    def __init__(self, player1, player2, lexicon=None, board=None, random_draw=True):
        self.players = [
            { "obj": player1, "name": "p1", "rack": [], "score": 0, "lastmove": None, "lastdrawn": []},
            { "obj": player2, "name": "p2", "rack": [], "score": 0, "lastmove": None, "lastdrawn": []}, ]
        self.lexicon = lexicon
        self.board = board if board else Board()
        self.bag = self.board.alltiles
        self.moves = []
        self.random_draw = random_draw

    def draw(self, player):
        """Draw new tiles for some player."""
        ntiles = min(self.board.rack_size - len(player["rack"]), len(self.bag))
        if self.random_draw:
            # Normal case
            letters = random.sample(self.bag, ntiles)
        else:
            # Some test cases use this pathway
            letters = self.bag[0:ntiles]

        for letter in letters:
            self.bag.remove(letter)
        player["lastdrawn"] = letters
        player["rack"] += letters

    def run(self):
        # Draw starting racks
        for player in self.players:
            self.draw(player)

        # Track skips (too many consecutive means the game is over)
        skips = 0

        # Play a game!
        player, otherplayer = self.players[0], self.players[1]

        while 1:
            try:
                # If the last move by the other player was an exchange, mask its letters
                if otherplayer["lastmove"] and otherplayer["lastmove"].kind == Move.MOVE_TRADE:
                    otherplayer["lastmove"].mask_word()

                # Receive move from player, and time how long it takes
                t_start = time.time()
                move = player["obj"].move(player["lastdrawn"], otherplayer["lastmove"])
                t_elapsed = time.time() - t_start

                # Check move for validity
                if move.kind == Move.MOVE_TRADE:
                    # exchanges are only allowed if the bag has rack_size (normally 7) or more tiles
                    if move.word and len(self.bag) < self.board.rack_size:
                        raise InvalidMoveError("attempt to exchange with less than " + str(self.board.rack_size) + " tiles in the bag")
                else:
                    valid_moves = self.board.valid_moves(player["rack"], self.lexicon)
                    if move in valid_moves:
                        # replace move with the one from valid_moves
                        # so we get an accurate score
                        move = valid_moves[valid_moves.index(move)]
                    else:
                        raise InvalidMoveError("invalid move: " + str(move))

                # Record move for this player
                player["score"] += move.score
                player["lastmove"] = move
                self.moves.append({
                    "player": player["name"],
                    "rack": ''.join(player["rack"]),
                    "move": str(move),
                    "score": move.score,
                    "time": str(int(t_elapsed * 10**6)) })

                logging.info("{0:25s} {1:25s} {2:10s} {3:4d} {4:8d}".format(
                    player["name"],
                    str(move) + " " + str(move.score),
                    ''.join(player["rack"]),
                    player["score"],
                    int(t_elapsed * 10**6)))

                # Remove used tiles from rack and draw new tiles
                if move.kind == Move.MOVE_TRADE:
                    for letter in move.word:
                        player["rack"].remove(letter)
                    self.draw(player)
                    self.bag += list(move.word)
                else:
                    for letter, square in zip(list(move.word), self.board.walk_move(move)):
                        if not square.letter:
                            if letter.isupper():
                                player["rack"].remove(letter)
                            else:
                                player["rack"].remove('?')
                    self.draw(player)

                # Play move onto the board
                self.board.play(move)

                # Have there been six consecutive skips? If so, the game is over.
                if move.kind == Move.MOVE_TRADE:
                    skips += 1
                else:
                    skips = 0

                if skips == 6:
                    # Adjust final score based on racks
                    player["score"] -= sum(self.board.letter_value(letter) for letter in player["rack"])
                    otherplayer["score"] -= sum(self.board.letter_value(letter) for letter in otherplayer["rack"])
                    break

                # Did the player run out of tiles? If so, the game is over.
                if not self.bag and not player["rack"]:
                    # Adjust final score based on racks
                    otherplayer_rack_value = sum(self.board.letter_value(letter) for letter in otherplayer["rack"])
                    player["score"] += 2 * otherplayer_rack_value
                    break

            except InvalidMoveError as e:
                logging.info("[INVALID MOVE] " + player["name"] + ": " + str(e))
                player["score"] = -1
                break

            # swap players
            player, otherplayer = otherplayer, player

        # Show the board
        logging.info(str(self.board))

        # Return representation of this game
        return {
            "moves": self.moves,
            "players": [
                {"name": self.players[0]["name"], "rack": ''.join(self.players[0]["rack"]), "score": self.players[0]["score"]},
                {"name": self.players[1]["name"], "rack": ''.join(self.players[1]["rack"]), "score": self.players[1]["score"]}, ]}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    t = lexicon.TrieNode()
    with open('/usr/share/dict/words') as f:
        for word in f:
            t.add(word.rstrip().upper())

    if len(sys.argv) >= 2:
        p1 = ExternalPlayer(['/bin/sh', '-c', sys.argv[1]])
    else:
        p1 = TrainingPlayer(t)

    if len(sys.argv) >= 3:
        p2 = ExternalPlayer(['/bin/sh', '-c', sys.argv[2]])
    else:
        p2 = TrainingPlayer(t)

    ref = Referee(player1=p1, player2=p2, lexicon=t)

    game = ref.run()
    print json.dumps(game)
