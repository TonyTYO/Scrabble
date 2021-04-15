""" Methods and values based on language choice
    Read in from alphabet.py in the language sub-directory """

import sys
import importlib
import ScrabbleWordsClass


class Alphabet:
    """ Class holding all values and functions dependent on language choice

        Set each of the following for the language

        ALPHABET:          All letters in an ordered list
        SCORES:            Dictionary of letter scores
        LETTERS:           List of all letters in game pool
        WORD_CHECK:        Filename for text(.txt) or GADDAG (.p) file or
                           Class that checks validity of words in list [Name, [parameters]]
        PC_NAME:           Name to call computer player
        PC_RADIOBUTTONS:   Title, label and text for computer player level radio buttons
                           ["title", "label", ["label for 1st button",.... ]]
        PC_VOCAB:          Dictionary of wordlists for each ability level {level:wordlist}
        PC_2LETT:          List of allowable two-letter words
        LETTER_FREQUENCIES:Frequencies of use of each letter in alphabet {letter:frequency}
        TILE_POSITIONS:    Dictionary of coordianes of top left corner
                           of each letter tile in image
        TOOL_TIPS:         Tool tips for each button
        QLOAD_MSGS:        Message when loading files
        QSTATES_MSGS:      Dictionary of all messages for qstates.py
        ERROR_MSGS:        Dictionary of all error messages (qstates.py)
        QENWAU_MSGS:       Dictionary of all messages for qenwau.py
        QCHWARAEWR_MSGS:   Dictionary of all messages for qchwaraewr.py
        QTESTUN_MSGS:      Dictionary of all messages for qtestun.py

    """

    def __init__(self, lang):

        self.lang = lang
        self.alphabet = importlib.import_module(self.lang + ".alphabet")
        self.ALPHABET = self.alphabet.ALPHABET
        self.SCORES = self.alphabet.SCORES
        self.LETTERS = self.alphabet.LETTERS

        self.WORD_CHECK = self.alphabet.WORD_CHECK

        self.PC_NAME = self.alphabet.PC_NAME
        self.PC_RB_TITLE = self.alphabet.PC_RB_TITLE

        self.PC_VOCAB = self._set_variable("PC_VOCAB", [])
        self.PC_2LETT = self._set_variable("PC_2LETT", "")
        self.LETTER_FREQUENCIES = self._set_variable("LETTER_FREQUENCIES", {})

        self.TILE_POSITIONS = self.alphabet.TILE_POSITIONS

        self.TOOLTIPS = self.alphabet.TOOLTIPS

        self.QLOAD_MSGS = self.alphabet.QLOAD_MSGS
        self.QSTATES_MSGS = self.alphabet.QSTATES_MSGS
        self.ERROR_MSGS = self.alphabet.ERROR_MSGS
        self.QENWAU_MSGS = self.alphabet.QENWAU_MSGS
        self.QCHWARAEWR_MSGS = self.alphabet.QCHWARAEWR_MSGS
        self.QTESTUN_MSGS = self.alphabet.QTESTUN_MSGS

        self.rb_text = None
        self.rb_dict = None
        self.max_char_len = len(max(self.ALPHABET, key=len))
        self.multi_char = [s[0] for s in self.ALPHABET if len(s) > 1]
        self._set_rb()

    def _set_variable(self, name, default=None):
        """ Set variable to value specified in
            alphabet.py else default """
        if hasattr(self.alphabet, name):
            return getattr(self.alphabet, name)
        return default

    def _set_rb(self):
        """ Create text list and file dictionary for
            pc player ability radio buttons """
        self.rb_text = [lst[0] for lst in self.PC_VOCAB]
        rb_files = [lst[1] for lst in self.PC_VOCAB]
        self.rb_dict = {k: self.lang + "\\" + v for (k, v) in enumerate(rb_files)}

    def pc_player(self):
        """ Returns True if computer player available """
        return self.PC_VOCAB

    def to_letter(self, index):
        """ Convert index position in alphabet to letter
            Required for sorting """
        return self.ALPHABET[index]

    def to_index(self, letter):
        """ Convert letter in alphabet to index position
            Required for sorting """
        return self.ALPHABET.index(letter)

    def to_list(self, string):
        """ Convert string in alphabet to list of letters """
        letters = []
        if self.max_char_len == 1:
            letters = list(string)
        else:
            i = 0
            while i < len(string):
                char = string[i]
                if char in self.multi_char:
                    k = 1
                    while k < self.max_char_len:
                        if string[i:i + k + 1] not in self.ALPHABET:
                            break
                        char = string[i:i + k + 1]
                        k += 1
                letters.append(char)
                i += len(char)
        return letters

    def set_checker(self, scene):
        """ Set the word checker as specified """
        word_check = self.WORD_CHECK[:]
        if word_check is not None:
            if isinstance(word_check, str):
                if word_check.lower().endswith(".txt"):
                    return ScrabbleWordsClass.ScrabbleWordsText(word_check)
                elif word_check.lower().endswith(".p"):
                    return ScrabbleWordsClass.ScrabbleWords(word_check, scene)
                else:
                    word_check = [word_check, ""]
            if isinstance(word_check, list):
                mod = sys.modules[self.lang + ".alphabet"]
                fnct = getattr(mod, word_check[0])  # Gives fnct as mod.word_check[0]
                if word_check[1]:  # Allow for parameters
                    if isinstance(word_check[1], str):
                        word_check[1] = [word_check[1]]
                    return fnct(*word_check[1])
                else:
                    return fnct()
