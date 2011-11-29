class Lexicon:
    """Lexicon represented as a trie -- a tree in which each edge is a character and each
    node represents a prefix composed of all edges from the root to that node. Nodes that
    represent words in the lexicon are specially marked as "final".

    >>> from lexicon import Lexicon
    >>> t = Lexicon()
    >>> t.all()
    []
    >>> t.add('foo')
    >>> t.add('bar')
    >>> t.exists('foo')
    True
    >>> t.exists('baz')
    False
    >>> t.add('baz')
    >>> t.exists('baz')
    True
    >>> t.exists('fo')
    False
    >>> t.exists('ba')
    False
    >>> t.exists('xxx')
    False
    >>> t.all()
    ['bar', 'baz', 'foo']
    >>> t.next()
    ['b', 'f']
    >>> t.subtree('ba').all()
    ['r', 'z']
    >>> t.subtree('x')
    >>> t.final
    False
    >>> t.subtree('bar').final
    True
    """

    def __init__(self, root=None):
        self.root = {} if root is None else root

    def add(self, word):
        """Add a word to this trie."""

        node = self.root
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]

        # We're at the final node -- mark it as such
        node["_final"] = True

    def exists(self, word):
        """Check if a word exists in this trie."""

        node = self.root
        for char in word:
            if char not in node:
                return False
            node = node[char]

        return '_final' in node

    def all(self):
        """Sorted list of all words in this trie."""

        wordlist = []

        # Search edges in alphabetical order
        # So we return a sorted list of words
        def search(node, word=''):
            if '_final' in node:
                wordlist.append(word)
            for char in sorted(node.keys()):
                if char is not '_final':
                    search(node[char], word + char)

        search(self.root)
        return wordlist

    def subtree(self, prefix):
        """Return subtree rooted at prefix, or, None if no such subtree exists."""

        # Start here and then walk out the edges for 'prefix'
        node = self.root

        for char in prefix:
            if char not in node:
                return None
            node = node[char]

        return Lexicon(root=node)

    def next(self):
        """Returns a list of edges leading out of this node."""
        return filter(lambda x: x is not '_final', self.root.keys())

    @property
    def final(self):
        return '_final' in self.root
