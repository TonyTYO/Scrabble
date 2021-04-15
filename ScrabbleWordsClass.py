""" Classes to check words in Scrabble """

import qfile
from pygaddag import GADDAG


class ScrabbleWords:
    """ Class to check words in English Scrabble """

    # Initialise values
    def __init__(self, filename, scene, player=None):
        self.player = player  # identify player

        print("Loading")
        self.graph = GADDAG()
        # self.graph.safeload(filename)
        ex = qfile.FileProgressWidget(self.graph, filename, scene)
        ex.set_colour("yellow")
        ex.reconnect(scene.states.end_load)
        ex.Start()
        print("Loaded")
        qfile.FileProgressWidget.reset_count()

    def check_word(self, word):
        """ Check if word is in scrabble list
            Return True or False """

        return self.graph.is_in(word)

    def valid_word(self, word):
        """ Check if word is in scrabble list
            Return word or None """
        if self.graph.is_in(word):
            return word
        return None

    def validate(self, word):
        """ Check if word is in scrabble list """

        return self.valid_word(word)


class ScrabbleWordsText:
    """ Class to check words in English Scrabble """

    # Initialise values
    def __init__(self, filename, player=None):
        self.player = player  # identify player
        wordfile = None
        try:
            wordfile = open(filename, 'r')  # list of allowed scrabble words
        except IOError as e:
            print(e)
            self.words = []
        wordsread = wordfile.readlines()  # read into list
        self.words = [i.strip() for i in wordsread]  # remove white space
        self.choice = []  # list of possible words from rack

    def check_word(self, word):
        """ Check if word is in scrabble list
            Return True or False
            Return None if check not operational """

        if not self.words:
            return None
        word = ''.join(word)
        return next((True for w in self.words if w == word), False)

    def valid_word(self, word):
        """ Check if word is in scrabble list
            Return word or None """

        word = ''.join(word)
        return next((w for w in self.words if w == word), None)

    def validate(self, word):
        """ Check if word is in scrabble list """

        return self.valid_word(word)
