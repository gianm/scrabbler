from move import Move, InvalidMoveError
import json

class Board:
    """Scrabble board"""

    def __init__(self, variant='scrabble'):
        self.empty = True

        with open("variants/" + variant) as f:
            vdat = json.loads(f.read())

        self.dim = vdat["dim"]
        self.bingo_bonus = vdat["bingo_bonus"]
        self.rack_size = vdat["rack_size"]

        self.letter_distribution = {}
        for letter in vdat["letter_distribution"]:
            self.letter_distribution[str(letter)] = vdat["letter_distribution"][letter]

        self.letter_values = {}
        for letter in vdat["letter_values"]:
            self.letter_values[str(letter)] = vdat["letter_values"][letter]

        self.squares = [[Square() for i in range(self.dim)] for j in range(self.dim)]
        for bonus in vdat["bonus"]:
            self.squares[bonus["row"]][bonus["col"]].bonus_type = bonus["type"]
            self.squares[bonus["row"]][bonus["col"]].bonus_multiplier = bonus["multiplier"]

    def play(self, move):
        """Play a move onto the board. Raises InvalidMoveError if the provided
        move is incompatible with tiles already on the board (although other
        forms of invalid moves may still be allowed; if you really care about
        full validity, check against valid_moves).

        >>> import board
        >>> b = Board()
        >>> b.play(Move.from_str("FOO 8G"))
        >>> b.play(Move.from_str("FOOD 8G"))
        >>> b.squares[6][9].letter == None
        True
        >>> b.play(Move.from_str("BAR J7"))
        Traceback (most recent call last):
        InvalidMoveError: invalid play
        >>> b.squares[6][9].letter == None
        True
        >>> b.play(Move.from_str("ODD J7"))
        >>> b.squares[6][9].letter
        'O'
        >>> b.play(Move.from_str("*** --"))
        """

        # Nothing to do if this was a skip/trade
        if move.kind == Move.MOVE_TRADE:
            return

        # Check if this is a valid move.
        for letter, square in zip(list(move.word), self.walk_move(move)):
            if square.letter and square.letter != letter:
                raise InvalidMoveError("invalid play")

        # Move is valid, play it.
        for letter, square in zip(list(move.word), self.walk_move(move)):
            square.letter = letter

        # If the board was empty, it isn't anymore.
        self.empty = False

    def walk_move(self, move):
        """Return a list of squares that a particular move would pass through.

        >>> import board
        >>> b = Board()
        >>> b.play(Move.from_str("FOO 8G"))
        >>> [ s.letter for s in b.walk_move(Move.from_str("FOOD 8G")) ]
        ['F', 'O', 'O', None]
        """

        squares = []
        if move.kind == Move.MOVE_ACROSS:
            return [ self.squares[move.row][move.col + i] for i in range(len(move.word)) ]
        elif move.kind == Move.MOVE_DOWN:
            return [ self.squares[move.row + i][move.col] for i in range(len(move.word)) ]

    def valid_moves(self, rack, lexicon):
        """Find valid moves on this board.

        >>> import board, lexicon
        >>> t = lexicon.Lexicon()
        >>> t.add("DOGGED")
        >>> t.add("BOSS")
        >>> t.add("GOB")
        >>> t.add("DOGGEDLY")
        >>> t.add("SUBWAY")
        >>> t.add("SUBWAYS")
        >>> t.add("ZVIEW")
        >>> t.add("ZVIEX")
        >>> t.add("OX")
        >>> t.add("WHAT")
        >>> t.add("NOPE")
        >>> b = board.Board()
        >>> sorted([str(move) + " " + str(move.score) for move in b.valid_moves("SSUBWA?", t)])
        ['BoSS 8E 10', 'BoSS 8F 10', 'BoSS 8G 10', 'BoSS 8H 10', 'BoSS H5 10', 'BoSS H6 10', 'BoSS H7 10', 'BoSS H8 10', 'SUBWAy 8C 22', 'SUBWAy 8D 22', 'SUBWAy 8E 20', 'SUBWAy 8F 20', 'SUBWAy 8G 20', 'SUBWAy 8H 22', 'SUBWAy H3 22', 'SUBWAy H4 22', 'SUBWAy H5 20', 'SUBWAy H6 20', 'SUBWAy H7 20', 'SUBWAy H8 22', 'SUBWAyS 8B 78', 'SUBWAyS 8C 74', 'SUBWAyS 8D 74', 'SUBWAyS 8E 72', 'SUBWAyS 8F 74', 'SUBWAyS 8G 72', 'SUBWAyS 8H 74', 'SUBWAyS H2 78', 'SUBWAyS H3 74', 'SUBWAyS H4 74', 'SUBWAyS H5 72', 'SUBWAyS H6 74', 'SUBWAyS H7 72', 'SUBWAyS H8 74']
        >>> b.play(Move(6, 7, Move.MOVE_DOWN,   "DoGGED"))
        >>> b.play(Move(7, 6, Move.MOVE_ACROSS, "BoSS"))
        >>> b.play(Move(9, 7, Move.MOVE_ACROSS, "GOB"))
        >>> sorted([str(move) + " " + str(move.score) for move in b.valid_moves("UVWXYZ?", t)])
        ['DoGGEDlY H7 13', 'SUBWaY J8 13', 'ZViEX 11E 55']
        >>> b = board.Board()
        >>> b.play(Move(3, 0, Move.MOVE_DOWN, "SUBWAY"))
        >>> sorted([str(move) + " " + str(move.score) for move in b.valid_moves("SUBWAYZ", t)])
        ['SUBWAY 10A 39', 'SUBWAY 4A 28', 'SUBWAYS 4A 30', 'SUBWAYS A4 15']
        """
        # Start with valid across moves
        moves = self.valid_moves_across(rack, lexicon)

        # Flip the board
        old_squares = self.squares
        new_squares = [[None for i in range(self.dim)] for j in range(self.dim)]
        for row, col in [ (row, col) for row in range(self.dim) for col in range(self.dim) ]:
            new_squares[col][row] = self.squares[row][col]
        self.squares = new_squares

        # Add down moves
        try:
            for move in self.valid_moves_across(rack, lexicon):
                # Flip this move from across to down
                move.row, move.col = move.col, move.row
                move.kind = Move.MOVE_DOWN
                moves.append(move)
        finally:
            self.squares = old_squares

        return moves

    def valid_moves_across(self, rack, lexicon):
        moves = []

        # Copy rack since we will edit it
        rack = list(rack)

        # Search for valid moves row by row.
        for row in range(self.dim):
            # Find anchors for this row
            if self.empty:
                # Special case for an empty board
                # There is one anchor square: the center
                if row == int(self.dim/2):
                    rowanchors = [ int(self.dim/2) ]
                else:
                    rowanchors = []
            else:
                rowanchors = [ col for col in range(self.dim) if self.is_anchor(row, col) ]

            # Find cross-checks for this row
            rowcross = [ self.cross_checks( row, col, lexicon ) for col in range(self.dim) ]

            # Find score of adjacent up/down fragments for this row
            rowscore = [ self.cross_score( row, col ) for col in range(self.dim) ]

            # For each anchor, find hookable words
            prevanchor = -1
            for anchor in rowanchors:
                # Hookable word will be something like:
                # D   O   G   G   E   D
                # |  1  | 2 |    3    |
                #
                # 1 - Left part (might be empty)
                # 2 - Anchor (must be filled)
                # 2 + 3 - Right part (must be at least the anchor)

                def score_word(word, col):
                    base_score = 0
                    base_mult = 1
                    extra_score = 0
                    played_tiles = 0

                    for i in range(col - len(word), col):
                        letter = word[i - col + len(word)]
                        letter_value = self.letter_value(letter)

                        if not self.squares[row][i].letter:
                            # This is a newly placed tile
                            played_tiles += 1

                            # Letter value increases if there is a letter bonus on this square
                            if self.squares[row][i].bonus_type == Square.BONUS_LETTER:
                                letter_value *= self.squares[row][i].bonus_multiplier

                            # Letter value is added to extra_score if there is a word down this column
                            if rowscore[i] is not None:
                                extra_score += rowscore[i] + letter_value

                            # Base multiplier is increased if there is a word bonus on this square
                            if self.squares[row][i].bonus_type == Square.BONUS_WORD:
                                base_mult *= self.squares[row][i].bonus_multiplier

                        # Letter value is added to base score even if not newly placed
                        base_score += letter_value

                    # Was it a bingo?
                    if played_tiles == self.rack_size:
                        extra_score += self.bingo_bonus

                    return base_score * base_mult + extra_score

                def extend_right(word, tree, col):
                    if not tree:
                        # No lexicon means no words.
                        return
                    elif col < self.dim and self.squares[row][col].letter:
                        # This column is occupied, we have to use the existing letter
                        subtree = tree.subtree(self.squares[row][col].letter.upper())
                        if subtree:
                            extend_right(
                                word + self.squares[row][col].letter,
                                subtree,
                                col + 1)
                    else:
                        # This column is not occupied
                        if col > anchor and tree.final:
                            # 'word' represents a valid move. Compute score:
                            moves.append(Move(
                                row       = row,
                                col       = col - len(word),
                                kind      = Move.MOVE_ACROSS,
                                word      = word,
                                score     = score_word(word, col)))

                        # Try to extend rightwards using a letter from the rack
                        if col < self.dim:
                            for letter in tree.next():
                                if letter in rowcross[col]:
                                    # Do we have this letter on a tile?
                                    if letter in rack:
                                        rack.remove(letter)
                                        extend_right(
                                            word + letter,
                                            tree.subtree(letter),
                                            col + 1)
                                        rack.append(letter)

                                    # Do we have a blank we can use?
                                    if '?' in rack:
                                        rack.remove('?')
                                        extend_right(
                                            word + letter.lower(),
                                            tree.subtree(letter),
                                            col + 1)
                                        rack.append('?')

                # Find all candidate left parts and try to extend them
                if anchor == 0 or self.squares[row][anchor - 1].letter:
                    # We're at the left edge of the board *or* there are tiles already
                    # on the board. Either way the left part is fixed
                    word = ''.join([self.squares[row][i].letter for i in range(prevanchor + 1, anchor)])
                    extend_right(word, lexicon.subtree(word.upper()), anchor)
                else:
                    # No tiles already on the board, find candidate left parts based on the lexicon
                    def search(tree, word='', limit=self.dim):
                        extend_right(word, tree, anchor)
                        if limit > 0:
                            for letter in tree.next():
                                # Do we have this letter on a tile?
                                if letter in rack:
                                    rack.remove(letter)
                                    search(tree.subtree(letter), word + letter, limit - 1)
                                    rack.append(letter)

                                # Do we have a blank we can use?
                                if '?' in rack:
                                    rack.remove('?')
                                    search(tree.subtree(letter), word + letter.lower(), limit - 1)
                                    rack.append('?')
                    search(lexicon, limit = anchor - prevanchor - 1)

                # Update prevanchor for the next loop
                prevanchor = anchor
        return moves

    def updown_fragments(self, row, col):
        """Return tuple containing (up, down) fragments bordering a particular square.

        >>> import board
        >>> b = board.Board()
        >>> b.play(Move(6, 7, Move.MOVE_DOWN,   "DoGGED"))
        >>> b.play(Move(7, 6, Move.MOVE_ACROSS, "BoSS"))
        >>> b.play(Move(9, 7, Move.MOVE_ACROSS, "GOB"))
        >>> b.updown_fragments(8, 8)
        ('S', 'O')
        >>> b.updown_fragments(8, 9)
        ('S', 'B')
        >>> b.updown_fragments(10, 8)
        ('O', '')
        >>> b.updown_fragments(0, 0)
        ('', '')
        >>> b.updown_fragments(5, 7)
        ('', 'DoGGED')
        >>> b.updown_fragments(12, 7)
        ('DoGGED', '')
        """
        up, down = '', ''

        for i in reversed(range(row)):
            if not self.squares[i][col].letter:
                break
            up = self.squares[i][col].letter + up

        for i in range(row + 1, self.dim):
            if not self.squares[i][col].letter:
                break
            down = down + self.squares[i][col].letter

        return up, down

    def cross_checks(self, row, col, lexicon):
        """Return list of letters that can be placed in (row, col) to yield valid down words.

        >>> import lexicon, board
        >>> t = lexicon.Lexicon()
        >>> t.add('SO')
        >>> t.add('GI')
        >>> b = board.Board()
        >>> b.play(Move(6,7,Move.MOVE_DOWN,   "DOGGED"))
        >>> b.play(Move(7,6,Move.MOVE_ACROSS, "BOSS"))
        >>> b.cross_checks( 7, 6, t )
        []
        >>> b.cross_checks( 8, 6, t )
        []
        >>> b.cross_checks( 8, 8, t )
        ['O']
        >>> b.cross_checks( 8, 10, t )
        ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        """

        if self.squares[row][col].letter:
            return []

        up, down = self.updown_fragments(row, col)
        letters = sorted(self.letter_values.keys())

        # If there are no neighboring word fragments, return a list of all letters
        if not up and not down:
            return list(letters)

        # Otherwise check the lexicon for valid words
        ret = []

        lexicon = lexicon.subtree(up.upper())
        if lexicon:
            down = down.upper()
            for letter in letters:
                if lexicon.exists(letter + down):
                    ret.append(letter)

        return ret

    def cross_score(self, row, col):
        """Return score of adjacent up/down fragments for (row, col), or None if
        there are no adjacent up/down fragments.

        >>> import board
        >>> b = board.Board()
        >>> b.play(Move(6, 7, Move.MOVE_DOWN,   "DoGGED"))
        >>> b.play(Move(7, 6, Move.MOVE_ACROSS, "BoSs"))
        >>> b.play(Move(9, 7, Move.MOVE_ACROSS, "GOB"))
        >>> b.cross_score(10, 8)
        1
        >>> b.cross_score(5, 7)
        9
        >>> b.cross_score(6, 9)
        0
        >>> b.cross_score(8, 9)
        3
        >>> b.cross_score(8, 10) is None
        True
        """
        up, down = self.updown_fragments(row, col)
        if not up and not down:
            return None

        # Start at 0 instead of None so we can differentiate 0-point
        # fragments (of all blanks) from no fragment at all
        score = 0

        # Total value of non-blank letters (uppercase)
        for letter in up + down:
            score += self.letter_value(letter)

        # Possible multiplier
        if self.squares[row][col].bonus_type == Square.BONUS_WORD:
            score *= self.squares[row][col].bonus_multiplier

        return score

    def is_anchor(self, row, col):
        """Check if a square is an anchor square (empty square adjacent to a filled square).

        >>> import board
        >>> b = board.Board()
        >>> b.play(Move(6,7,Move.MOVE_DOWN,   "DoGGED"))
        >>> b.play(Move(7,6,Move.MOVE_ACROSS, "BoSS"))
        >>> b.is_anchor( 0, 0 )
        False
        >>> b.is_anchor( 7, 6 )
        False
        >>> b.is_anchor( 8, 8 )
        True
        >>> b.is_anchor( 8, 9 )
        True
        >>> b.is_anchor( 8, 10 )
        False
        """

        # Anchor squares must be empty
        if self.squares[row][col].letter:
            return False

        # Check adjacent squares for letters
        for offset in [ (-1,0), (0,-1), (1,0), (0,1) ]:
            if (    row + offset[0] >= 0
                and row + offset[0] < self.dim
                and col + offset[1] >= 0
                and col + offset[1] < self.dim
                and self.squares[row+offset[0]][col+offset[1]].letter
            ):
                return True
        return False

    def letter_value(self, letter):
        if letter.isupper():
            return self.letter_values[letter]
        else:
            return 0

    @property
    def alltiles(self):
        """Returns a list of all tiles in the game represented by this board
        (including tiles still in the bag).

        >>> import board
        >>> b = Board()
        >>> b.alltiles
        ['?', '?', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'C', 'C', 'D', 'D', 'D', 'D', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'F', 'F', 'G', 'G', 'G', 'H', 'H', 'I', 'I', 'I', 'I', 'I', 'I', 'I', 'I', 'I', 'J', 'K', 'L', 'L', 'L', 'L', 'M', 'M', 'N', 'N', 'N', 'N', 'N', 'N', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'P', 'P', 'Q', 'R', 'R', 'R', 'R', 'R', 'R', 'S', 'S', 'S', 'S', 'T', 'T', 'T', 'T', 'T', 'T', 'U', 'U', 'U', 'U', 'V', 'V', 'W', 'W', 'X', 'Y', 'Y', 'Z']
        >>> b = Board(variant='test')
        >>> b.alltiles
        ['?', '?', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'C', 'C', 'C', 'C', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'F', 'F', 'F', 'F']
        """
        tiles = []
        for c in sorted(self.letter_distribution.keys()):
            tiles += list(c * self.letter_distribution[c])
        return tiles

    def __str__(self):
        r"""Human-readable string representation of a board.

        >>> import board
        >>> b = Board()
        >>> b.play(Move.from_str("FOO 8G"))
        >>> str(b)
        '        A     B     C     D     E     F     G     H     I     J     K     L     M     N     O \n  1 [  3W][    ][    ][  2L][    ][    ][    ][  3W][    ][    ][    ][  2L][    ][    ][  3W]\n  2 [    ][  2W][    ][    ][    ][  3L][    ][    ][    ][  3L][    ][    ][    ][  2W][    ]\n  3 [    ][    ][  2W][    ][    ][    ][  2L][    ][  2L][    ][    ][    ][  2W][    ][    ]\n  4 [  2L][    ][    ][  2W][    ][    ][    ][  2L][    ][    ][    ][  2W][    ][    ][  2L]\n  5 [    ][    ][    ][    ][  2W][    ][    ][    ][    ][    ][  2W][    ][    ][    ][    ]\n  6 [    ][  3L][    ][    ][    ][  3L][    ][    ][    ][  3L][    ][    ][    ][  3L][    ]\n  7 [    ][    ][  2L][    ][    ][    ][  2L][    ][  2L][    ][    ][    ][  2L][    ][    ]\n  8 [  3W][    ][    ][  2L][    ][    ][F   ][O 2W][O   ][    ][    ][  2L][    ][    ][  3W]\n  9 [    ][    ][  2L][    ][    ][    ][  2L][    ][  2L][    ][    ][    ][  2L][    ][    ]\n 10 [    ][  3L][    ][    ][    ][  3L][    ][    ][    ][  3L][    ][    ][    ][  3L][    ]\n 11 [    ][    ][    ][    ][  2W][    ][    ][    ][    ][    ][  2W][    ][    ][    ][    ]\n 12 [  2L][    ][    ][  2W][    ][    ][    ][  2L][    ][    ][    ][  2W][    ][    ][  2L]\n 13 [    ][    ][  2W][    ][    ][    ][  2L][    ][  2L][    ][    ][    ][  2W][    ][    ]\n 14 [    ][  2W][    ][    ][    ][  3L][    ][    ][    ][  3L][    ][    ][    ][  2W][    ]\n 15 [  3W][    ][    ][  2L][    ][    ][    ][  3W][    ][    ][    ][  2L][    ][    ][  3W]'
        """
        # Header
        mystr = '    '
        for i in range(0, self.dim):
            mystr += "{0:>5s} ".format(chr(ord("A")+i))
        mystr += "\n"

        # Body
        for rownum, row in enumerate(self.squares):
            mystr += "{0:3d} ".format(rownum+1)
            for square in row:
                mystr += str(square)
            mystr += "\n"

        return mystr.rstrip("\n")

class Square:
    """Square on a Scrabble board

    Each square can have:
    - zero or one "bonus" (word/letter multiplier)
    - zero or one "letter" (someone played a tile on the square)

    >>> import board
    >>> s = Square()
    >>> str(s)
    '[    ]'
    >>> s = Square(bonus_multiplier=3, bonus_type=Square.BONUS_WORD, letter="H")
    >>> str(s)
    '[H 3W]'
    >>> s = Square(bonus_multiplier=2, bonus_type=Square.BONUS_LETTER)
    >>> str(s)
    '[  2L]'
    """

    BONUS_NONE=0
    BONUS_WORD=1
    BONUS_LETTER=2

    def __init__(self, bonus_multiplier=0, bonus_type=BONUS_NONE, letter=None):
        self.bonus_multiplier = bonus_multiplier
        self.bonus_type = bonus_type
        self.letter = letter

    def __str__(self):
        return '[{0:1s} {1:2s}]'.format(
            self.letter if self.letter else ' ',
            self.bonus_str() )

    def bonus_str(self):
        if self.bonus_type == Square.BONUS_WORD:
            return str(self.bonus_multiplier) + 'W'
        elif self.bonus_type == Square.BONUS_LETTER:
            return str(self.bonus_multiplier) + 'L'
        else:
            return ''
