class TrieNode:
    """Node in a trie -- a tree in which each edge is a character and each node represents
    a prefix composed of all edges from the root to that node. Nodes that represent words
    in a lexicon are specially marked.

    >>> import lexicon
    >>> t = lexicon.TrieNode()
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
    """

    def __init__(self, final=False):
        self.final = final
        self.out = {}

    def add(self, word):
        """Add a word to this trie."""

        # Start here and then walk out the edges for this word
        node = self

        for char in word:
            if char not in node.out:
                node.out[char] = TrieNode()
            node = node.out[char]

        # We're at the final node -- mark it as such
        node.final = True

    def exists(self, word):
        """Check if a word exists in this trie."""

        word_subtree = self.subtree(word)
        if word_subtree and word_subtree.final:
            return True
        else:
            return False

    def all(self):
        """Sorted list of all words in this trie."""

        wordlist = []

        # Search edges in alphabetical order
        # So we return a sorted list of words
        def search(node, word=''):
            if node.final:
                wordlist.append(word)
            for char in sorted(node.out.keys()):
                search(node.out[char], word + char)

        search(self)
        return wordlist

    def subtree(self, prefix):
        """Return subtree rooted at prefix, or, None if no such subtree exists."""

        # Start here and then walk out the edges for 'prefix'
        node = self

        for char in prefix:
            if char not in node.out:
                return None
            node = node.out[char]

        return node

    def next(self):
        """Returns a list of edges leading out of this node."""
        return self.out.keys()
