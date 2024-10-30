"""Custom Trie Node implementation along with relevant functions"""
from collections import deque


class TrieNode:
    """Custom Trie Node implementation"""

    def __init__(self, w_up="", level=0):
        """
        Trie Node Implementation with levels and words
        :param w_up: Word formed from the root node up till the current node
        :param level: Level of the node relative to the root node (Level 0)
        """
        self.child = [None] * 128
        self.word_end = False
        self.level = level
        self.word_up_till_node = w_up

    def __str__(self):
        """Return string representation of Trie Node"""
        return self.word_up_till_node


def get_index(ch: str) -> int:
    """
    Returns usable index
    :param ch: The character to get the Index of
    :return: The Index of the character
    :rtype: int
    """
    return ord(ch)


def insert_key(root: TrieNode, key: str) -> None:
    """
    Inserts key into trie
    :param root: The root node of the trie
    :param key: The key to insert into the trie
    :return: None
    :rtype: None
    """
    curr = root
    w_up = ""
    level = 0
    for ch in key:
        level += 1
        w_up += ch
        index = get_index(ch)
        if curr.child[index] is None:
            new_node = TrieNode(w_up, level)
            curr.child[index] = new_node
        curr = curr.child[index]
    curr.word_end = True


def search_key(root: TrieNode, key: str) -> bool:
    """
    Searches for a key in a trie structure
    :param root: The root node of the trie
    :param key: The key to search for in the trie
    :return: True if key is found, False otherwise
    :rtype: bool
    """
    curr = root
    for ch in key:
        if curr.child[get_index(ch)] is None:
            return False
        else:
            curr = curr.child[get_index(ch)]
    return curr.word_end


def load_root(path: str) -> TrieNode:
    """
    Loads given wordlist into trie tree and returns root node
    :param path: The path of the wordlist
    :return: Returns the root node of the trie
    :rtype: TrieNode
    """
    root = TrieNode()
    with open(path) as f:
        words = set()
        for line in f:
            words.add(line.rstrip().lower())
    for word in words:
        insert_key(root, word)
    return root


def custom_search(root: TrieNode, key_spec: str) -> list:
    """
    Custom search function made to search for matching words in the trie
    :param root: The root node of the trie
    :param key_spec: The key pattern to search for in the trie
    :return: Returns list of matching words
    :rtype: list
    """
    queue = deque()
    queue.append(root)
    level = 0
    words = []
    # Perform a custom BFS on our trie implementation to find matching words
    while len(queue) > 0 and level < len(key_spec):
        curr = queue.popleft()
        level = curr.level
        index = 0
        if curr.level <= len(key_spec) - 1:
            for ch in curr.child:
                if ch is not None:
                    if key_spec[ch.level - 1] == '_':
                        if ch.level == len(key_spec) and ch.word_end:
                            words.append(ch.word_up_till_node)
                        else:
                            queue.append(ch)
                    else:
                        if index == get_index(key_spec[ch.level - 1]):
                            if ch.level == len(key_spec) and ch.word_end:
                                words.append(ch.word_up_till_node)
                            else:
                                queue.append(ch)

                index += 1

    return words
