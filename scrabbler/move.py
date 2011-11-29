import re

class Move:
    """Move in a Scrabble game

    Each move has:
    - (row, col) start position
    - kind: across, down, or trade
    - the word which was played or letters which were traded
    - (optional) score -- for bookkeeping

    >>> import move
    >>> m = Move(word="ADDITiONAL", row=2, col=3, kind=Move.MOVE_DOWN, score=74)
    >>> str(m)
    'ADDITiONAL D3'
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

    def __init__(self, row, col, kind, word, score=0):
        self.row = row
        self.col = col
        self.kind = kind
        self.word = word
        self.score = score

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

        >>> m = Move.from_str('NITROGEnASE 3H')
        >>> str(m)
        'NITROGEnASE 3H'
        >>> m.row
        2
        >>> m.col
        7
        >>> m.kind is Move.MOVE_ACROSS
        True
        >>> m.word
        'NITROGEnASE'

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

        if s == '--':
            word, pos = '', '--'
        else:
            try:
                word, pos = s.split()
                word = word.replace('(', '').replace(')', '')
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
            if not re.search(r"^([A-Za-z\?]*|\**)$", word):
                raise InvalidMoveError("invalid word: " + word);
        else:
            if not re.search(r"^([A-Za-z]+|\*+)$", word):
                raise InvalidMoveError("invalid word: " + word);

        # Looks OK, so create the object
        return Move(row, col, kind, word)

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

    def __str__(self):
        if self.word:
            return self.word + " " + self.position
        else:
            return self.position

    def __eq__(self, other):
        """
        >>> Move.from_str('NITROGEnASE 3H') == Move.from_str('NITROGEnASE 3H')
        True

        >>> Move.from_str('NITROGEnASE 3H') == Move.from_str('NITROGEnASE H3')
        False
        """
        return str(self) == str(other)

    def __ne__(self, other):
        """
        >>> Move.from_str('NITROGEnASE 3H') != Move.from_str('NITROGEnASE 3H')
        False

        >>> Move.from_str('NITROGEnASE 3H') != Move.from_str('NITROGEnASE H3')
        True
        """
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
