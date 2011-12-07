import re

class Move:
    """Move in a Scrabble game

    Each move has:
    - (row, col) start position
    - kind: across, down, or trade
    - the word which was played or letters which were traded
    - (optional) tmask -- 1 where a tile was played, 0 where it was already on the board
    - (optional) score -- for bookkeeping

    >>> import move
    >>> m = Move(word="ADDITiONAL", tmask=[False] * 8 + [True] * 2, row=2, col=3, kind=Move.MOVE_DOWN, score=74)
    >>> str(m)
    '(ADDITiON)AL D3'
    >>> m.word
    'ADDITiONAL'
    >>> m.position
    'D3'
    >>> m.score
    74
    """

    MOVE_ACROSS = 1
    MOVE_DOWN = 2
    MOVE_TRADE = 3

    def __init__(self, row, col, kind, word, tmask=None, score=0):
        self.row = row
        self.col = col
        self.kind = kind
        self.word = word
        self.score = score

        if tmask is None:
            tmask = [True] * len(word)
        self.tmask = tmask

    @staticmethod
    def from_str(s):
        """Create Move object from a string like "NITROGEnASE H3". Raises
        InvalidMoveError if the provided string cannot be converted into a Move.

        >>> import board
        >>> m = Move.from_str('NITROGEnASE H3')
        >>> str(m)
        'NITROGEnASE H3'
        >>> m.row
        2
        >>> m.col
        7
        >>> m.kind is Move.MOVE_DOWN
        True
        >>> m.word
        'NITROGEnASE'
        >>> m.tiles
        ['N', 'I', 'T', 'R', 'O', 'G', 'E', 'n', 'A', 'S', 'E']

        >>> m = Move.from_str('N(ITRO)GEn(ASE) 3H')
        >>> str(m)
        'N(ITRO)GEn(ASE) 3H'
        >>> m.row
        2
        >>> m.col
        7
        >>> m.kind is Move.MOVE_ACROSS
        True
        >>> m.word
        'NITROGEnASE'
        >>> m.tiles
        ['N', 'G', 'E', 'n']

        >>> m = Move.from_str('DEW? --')
        >>> str(m)
        'DEW? --'
        >>> m.row is None
        True
        >>> m.col is None
        True
        >>> m.kind is Move.MOVE_TRADE
        True
        >>> m.word
        'DEW?'
        >>> m.tiles
        ['D', 'E', 'W', '?']

        >>> m = Move.from_str('**** --')
        >>> str(m)
        '**** --'
        >>> m.row is None
        True
        >>> m.col is None
        True
        >>> m.kind is Move.MOVE_TRADE
        True
        >>> m.word
        '****'
        >>> m.tiles
        ['*', '*', '*', '*']

        >>> m = Move.from_str('--')
        >>> str(m)
        '--'
        >>> m.row is None
        True
        >>> m.col is None
        True
        >>> m.kind is Move.MOVE_TRADE
        True
        >>> m.word
        ''
        >>> m.tiles
        []

        >>> m = Move.from_str('NITROGEnASE 33')
        Traceback (most recent call last):
        InvalidMoveError: invalid position

        >>> m = Move.from_str('??? 3H')
        Traceback (most recent call last):
        InvalidMoveError: invalid word: ???

        >>> m = Move.from_str('... --')
        Traceback (most recent call last):
        InvalidMoveError: invalid word: ...

        >>> m = Move.from_str('NITROGEnASE')
        Traceback (most recent call last):
        InvalidMoveError: need more than 1 value to unpack

        >>> m = Move.from_str('')
        Traceback (most recent call last):
        InvalidMoveError: need more than 0 values to unpack
        """

        kind = None
        tmask = None

        if s == '--':
            word, pos = '', '--'
        else:
            try:
                word, pos = s.split()
            except ValueError as e:
                raise InvalidMoveError(str(e))

        if pos == '--':
            # TRADE move
            kind = Move.MOVE_TRADE
            row = None
            col = None
        else:
            m = re.search('^([A-Z])([0-9]+)$', pos)
            if m:
                # DOWN move
                kind = Move.MOVE_DOWN
                row = int(m.group(2)) - 1
                col = ord(m.group(1)) - ord('A')

            m = re.search('^([0-9]+)([A-Z])$', pos)
            if m:
                # ACROSS move
                kind = Move.MOVE_ACROSS
                row = int(m.group(1)) - 1
                col = ord(m.group(2)) - ord('A')

        # Input validation
        if not kind:
            raise InvalidMoveError("invalid position")

        if kind is Move.MOVE_TRADE:
            # TRADE
            if not re.search(r"^([A-Za-z\?]*|\**)$", word):
                raise InvalidMoveError("invalid word: " + word);
        else:
            # ACROSS or DOWN
            if not re.search(r"^([A-Za-z\(\)]+|\*+)$", word):
                raise InvalidMoveError("invalid word: " + word);

            # Scan word so we can create tmask
            tmask = []
            mode = True
            for letter in word:
                if letter == '(':
                    mode = False
                elif letter == ')':
                    mode = True
                else:
                    tmask.append(mode)
            word = word.replace('(', '').replace(')', '')

        # Looks OK, so create the object
        return Move(row, col, kind, word, tmask)

    def mask_word(self):
        """Replace letters in this word with stars (*). Useful for hiding
        the identity of traded tiles.

        >>> import move
        >>> m = Move.from_str('NITROGEnASE 3B')
        >>> m.mask_word()
        >>> m.word
        '***********'
        >>> str(m)
        '*********** 3B'
        """

        self.word = '*' * len(self.word)

    @property
    def position(self):
        row_str = str(self.row + 1) if self.row is not None else '-'
        col_str = chr(ord('A') + self.col) if self.col is not None else '-'

        if self.kind == Move.MOVE_DOWN:
            return col_str + row_str
        else:
            return row_str + col_str

    @property
    def tiles(self):
        """List of tiles played by a Move."""
        return [self.word[i] for i in range(len(self.word)) if self.tmask[i]]

    def __str__(self):
        if self.word:
            mode = True
            display = ''
            for i in range(len(self.word)):
                if mode and not self.tmask[i]:
                    display += '('
                elif not mode and self.tmask[i]:
                    display += ')'
                display += self.word[i]
                mode = self.tmask[i]
            if not mode:
                display += ')'
            return display + " " + self.position
        else:
            return self.position

    def __eq__(self, other):
        """
        >>> Move.from_str('NITROGEnASE 3H') == Move.from_str('NITROGEnASE 3H')
        True

        >>> Move.from_str('NITROGEnASE 3H') == Move.from_str('(NITRO)GEnASE 3H')
        False

        >>> Move.from_str('NITROGEnASE 3H') == Move.from_str('NITROGEnASE H3')
        False
        """
        return str(self) == str(other)

    def __ne__(self, other):
        return not self == other

class InvalidMoveError(ValueError):
    """Raised when a player attempts to play an invalid move.

    >>> e = InvalidMoveError("exciting reason")
    >>> str(e)
    'exciting reason'
    """
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return str(self.reason)
