""" Module containing class for computer player operations

    Class Play contains all functions for finding
    and deciding on possible words

"""

import itertools
import qfile
from pygaddag import GADDAG


class Play:
    """Class using GADDAG to find and decide on possible moves."""

    def __init__(self, smachine, ability):

        self.smachine = smachine
        self.letters = self.smachine.checker.letters

        # self.least_used = ["q", "j", "z", "s", "x"]
        print("Loading:", self.smachine.scene.alphabet.rb_dict[ability])
        self.graph = GADDAG()
        ex = qfile.FileProgressWidget(self.graph,
                                      self.smachine.scene.alphabet.rb_dict[ability],
                                      self.smachine.scene)
        ex.set_colour("black")
        ex.reconnect_params(self.smachine.end_state)
        ex.Start()
        print("Loaded")

        # self.letters = [["."] * cons.SIZE for i in range(cons.SIZE)]  # letters in each cell
        # self.letters[7][7] = "a"
        # self.letters[7][8] = "c"
        # self.letters[7][9] = "t"
        # self.letters[8][8] = "o"
        # self.letters[9][8] = "r"
        # self.letters[7][6] = "e"
        # self.letters[7][5] = "o"
        # self.letters[7][4] = "b"
        # self.letters[9][9] = "d"
        # self.letters[9][10] = "a"

        # self.alphabet = [" ", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
        #                 "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w",
        #                 "x", "y", "z"]
        # self.scores = {" ": 0, "a": 1, "b": 3, "c": 3, "d": 2, "e": 1, "f": 4,
        #               "g": 2, "h": 4, "i": 1, "j": 8, "k": 5, "l": 1,
        #               "m": 3, "n": 1, "o": 1, "p": 3, "q": 10, "r": 1,
        #               "s": 1, "t": 1, "u": 1, "v": 4, "w": 4, "x": 8,
        #               "y": 4, "z": 10}               #letter values

        # self.l_frequencies = {"a": 8.2, "b": 1.5, "c": 2.8, "d": 4.3, "e": 12.7,
        #                      "f": 2.2, "g": 2.0, "h": 6.1, "i": 7.0, "j": 0.2,
        #                      "k": 0.8, "l": 4.0, "m": 2.4, "n": 6.7, "o": 7.5,
        #                      "p": 1.9, "q": 0.1, "r": 6.0, "s": 6.3, "t": 9.1,
        #                      "u": 2.8, "v": 1.0, "w": 2.4, "x": 0.2, "y": 2.0,
        #                      "z": 0.1}

        # self.least_used = sorted(list(self.l_frequencies.items()), key=lambda x: x[1])
        # self.least_used = [t[0] for t in self.least_used if t[1] < 1.0]
        # print("f:", self.l_frequencies)
        # print("least:", self.least_used)

        # self.graph = GADDAG()
        # self.graph.load("english\\player0.p")

        # Dictionary of all anchor squares as {(row, col): letters to left, to
        # right, above, below as strings}
        self.anchor_strings = {}
        # Dictionary of all possible words as {(row, col): list in horzontal and vertical}
        self.anchor_words = {}
        # Dictionary of all anchor words as {(row, col): [word, score, [chars
        # and positions]] in horizontal and vertical}
        self.anchor_scores = {}

        # Dictionary of all cross tiles as {(row, col): list of possible one
        # letter additions}
        self.cross_tiles = {}

        # List of all valid two letter words in pc player dictionary
        self.lett2 = self._load_2lett(self.smachine.scene.alphabet.lang
                                      + "\\" + self.smachine.scene.alphabet.PC_2LETT)

        self.rack = None  # List of letters in rack

    def _load_2lett(self, filename):
        """ Get list of all valid two letter words
            from file and check if player has in dictionary """

        words_2lett = []
        try:
            with open(filename, 'r') as f:
                for word in f.readlines():
                    stripped = word.rstrip()
                    if self.graph.is_in(stripped):
                        words_2lett.append(stripped)
        except IOError:
            words_2lett = None
        return words_2lett

    # ------------------------------------------------------------------------------------------
    # Check board for squares with adjacent letters
    # Store strings as [left, right, above, below] in self.anchor_strings
    # Store single letters that may be used in square in self.cross_tiles

    def update_cross_letters(self):
        """ Start the updating """

        for row in range(15):
            for col in range(15):
                if self.letters[row][col] == ".":
                    self.get_anchor_squ_letts(row, col)

    def get_anchor_squ_letts(self, row, col):
        """ Get letters on board starting or ending
            adjacent to (row, col) as string

            returns strings as {position:[left, right, above, below]}

            Get possible single letters for (row, col)
            returns letters as {position:[possible letters]}"""

        alphabet = self.smachine.scene.alphabet.ALPHABET
        letts = set(alphabet)
        clets = set(alphabet)

        # Get sequence of letters in each direction from cell
        left = self.get_letts((row, col - 1), lambda x: x, lambda x: x - 1, -1)
        right = self.get_letts((row, col + 1), lambda x: x, lambda x: x + 1, 1)
        above = self.get_letts((row - 1, col), lambda x: x - 1, lambda x: x, -1)
        below = self.get_letts((row + 1, col), lambda x: x + 1, lambda x: x, 1)

        if left and right:
            letts = self.get_cross(left, self.graph.starts_with_no, no=len(left) + len(right))
            letts = {w[len(left)] for w in letts
                     if w[len(left) + 1:] == right and len(w) > len(left)}
        elif left:
            letts = self.get_cross(left, self.graph.starts_with_no, -1)
        elif right:
            letts = self.get_cross(right, self.graph.ends_with_no, 0)
        clets = clets.intersection(letts)

        if above and below:
            letts = self.get_cross(above, self.graph.starts_with_no, no=len(above) + len(below))
            letts = {w[len(above)] for w in letts
                     if w[len(above) + 1:] == below and len(w) > len(above)}
            print("AB", letts, above, below)
        elif above:
            letts = self.get_cross(above, self.graph.starts_with_no, -1)
        elif below:
            letts = self.get_cross(below, self.graph.ends_with_no, 0)
        clets = clets.intersection(letts)

        # Keep list of strings in dictionary self.anchor_strings
        list_of_letts = [left, right, above, below]
        if any(list_of_letts):
            self.anchor_strings[(row, col)] = list_of_letts
            self.cross_tiles[(row, col)] = clets

    def get_letts(self, pos, func_row, func_col, form):
        """ Get sequence of letters in horizontal or vertical
            from (row, col) as string
            func_row, func_col increases/decreases/neither row or col
            form: 1 leaves string as is, -1 reverses string """

        row, col = pos
        # letts = ""
        letts = []
        if row < 0 or row > 14 or col < 0 or col > 14:
            return letts

        while self.letters[row][col] != ".":
            # letts += self.letters[row][col]
            letts.append(self.letters[row][col])
            row = func_row(row)
            col = func_col(col)
            if row < 0 or row > 14 or col < 0 or col > 14:
                break
        return letts[::form]

    @staticmethod
    def get_cross(lets, func, form=None, no=None):
        """ Get word starting or ending in lets
            and one letter longer (to get possible adjacent letters)
            func: function to use in GADDAG
            form: 0 gets first letter, -1 last letter returned as set,
                  None returns whole word as list rather than letter """

        if no is None:
            no = len(lets)
        clets = list(func(lets, no + 1))
        clets = [w for w in clets if w != lets]
        if clets and form is not None:
            clets = [lt[form] for lt in clets]
            clets = set(clets)
        return clets

    # ------------------------------------------------------------------------------------------
    # For each anchor square, get words that can be made up using
    # the adjacent left or above letter/string and any letters to right or below.
    # Store as [horizontal, vertical] in self.anchor_words
    # Each word stored as tuple (start of left board string in word, word)
    # eg (5, forward) if rd is string to left on board

    def check_board(self, row, col, dirn):
        """ For each anchor square
            get the immediate letters on board (left)
            then check for subsequent letter/s on board that could
            be included in the word (parts)
            parts dictionary {offset from left: letters} """

        parts = {}
        if dirn == "H":
            left = self.anchor_strings[(row, col)][0]
            if left:
                letts = [(key, self.anchor_strings[key][1]) for key in self.anchor_strings
                         if (self.anchor_strings[key][1] and key[0] == row
                             and col <= key[1] < col + 9)]
                letts = sorted(letts, key=lambda x: x[0][1])
                if letts:
                    parts = {max(t[0][1] + 1 - col, 0):
                             chars[1] for t in letts for chars in enumerate(t[1])}
            else:
                left = self.anchor_strings[(row, col)][1]
        else:
            left = self.anchor_strings[(row, col)][2]
            if left:
                letts = [(key, self.anchor_strings[key][3]) for key in self.anchor_strings
                         if (self.anchor_strings[key][3] and key[1] == col
                             and row <= key[0] < row + 9)]
                letts = sorted(letts, key=lambda x: x[0][0])
                if letts:
                    parts = {max(t[0][0] + 1 - row, 0):
                             chars[1] for t in letts for chars in enumerate(t[1])}
            else:
                left = self.anchor_strings[(row, col)][3]

        if parts:
            words = self.get_list(left, self.graph.contains_lett_patt, [self.rack, parts])
        else:
            words = self.get_list(left, self.graph.contains_lett, [self.rack])
        words = [t for t in words if t[1] != left]
        return words

    @staticmethod
    def get_list(letters, func, params=None):
        """ Get list of all words from GADDAG
            remove original letters if
            returned as a word """

        if params is None:
            words = list(func(letters))
        else:
            words = list(func(letters, *params))
        if letters in words:
            words.remove(letters)
        return words

    def get_poss_words(self):
        """ Get all possible horizontal and vertical words
            for each anchor square """

        for key, val in self.anchor_strings.items():
            row, col = key
            left, right, above, below = val
            # lword, rword, aword, bword = [], [], [], []
            hwords, vwords = [], []
            if left or (right and col + len(right) >= 14):
                hwords = self.check_board(key[0], key[1], "H")
            if above or (below and row + len(below) >= 14):
                vwords = self.check_board(key[0], key[1], "V")

            if any([hwords, vwords]):
                self.anchor_words[key] = [hwords, vwords]

    # ------------------------------------------------------------------------------------------
    # Get words that can be made up using rack letters only
    # Check for any that can be used alongside tiles on board

    def get_available(self):
        """ Return dictionary of words using adjacent letters
            Check for cross_tiles that are in the rack
            Store possible words in self.side_words """

        horiz, vert = None, None
        av_side = {k: [lt for lt in v if lt in self.rack] for k, v in self.cross_tiles.items()}

        words = self.get_rackwords()
        for key, val in av_side.items():
            asw = self.anchor_strings[key]
            if asw[0] or asw[1]:
                horiz = []
                vert = [(self.index(w, lt) - 1, w) for lt in val for w in words
                        if self.index(w, lt) != -1 and self.check_sides_v(
                        (key[0], key[1]), self.index(w, lt), w, av_side) is not None]
                temp = self.get_viable(words, self.check_sides_v, (key, val), av_side)
                print("VERT", vert, temp)
            if asw[2] or asw[3]:
                horiz = [(self.index(w, lt) - 1, w) for lt in val for w in words
                         if self.index(w, lt) != -1 and self.check_sides_h(
                        (key[0], key[1]), self.index(w, lt), w, av_side) is not None]
                temp = self.get_viable(words, self.check_sides_h, (key, val), av_side)
                print("HORIZ", horiz, temp)
                vert = []

            if any([horiz, vert]):
                if key in self.anchor_words:
                    hor, ver = self.anchor_words[key]
                    hor.extend(horiz)
                    ver.extend(vert)
                    self.anchor_words[key] = [hor, ver]

    def get_rackwords(self):
        """ Get list of all valid words using the
            rack letters only """

        combs = []
        words = []
        for no in range(1, len(self.rack) + 1):
            combs1 = list("".join(lets) for lets in itertools.combinations(self.rack, no))
            combs.extend(combs1)
        combs = list(set(combs))
        for seq in combs:
            if len(seq) > 1:  # one letter words not allowed as first turn
                if seq == "  ":
                    if self.lett2:
                        words.extend([(0, lt) for lt in self.lett2])
                else:
                    while seq[0] == " ":
                        seq = seq[1:] + seq[0]
                    letts = [r for r in seq if r != seq[0]]
                    words.extend(list(self.graph.contains_lett(list(seq[0]), letts)))
        words = [w[1] for w in words if len(w[1]) > 1]
        words = set(tuple(w) for w in words)
        return list(list(w) for w in words)

    def get_viable(self, words, func, item, av_side):
        """ Return list of viable words """
        key, val = item
        lst = []
        for w in words:
            for lt in val:
                pos = self.index(w, lt)
                if pos != -1 and func(
                        (key[0], key[1]), pos, w, av_side) is not None:
                    lst.append((pos - 1, w))
        return lst

    @staticmethod
    def index(a_list, value):
        """ Find item in list
            Return index or -1 if not found """

        try:
            return a_list.index(value)
        except ValueError:
            return -1

    @staticmethod
    def check_sides_v(rowcol, wpos, word, av_side):
        """ Check each letter allowed if adjacent letter present
            for vertical words """

        row, col = rowcol
        check_letts = {k: v for k, v in av_side.items() if k[1] == col}
        row = row - wpos
        pos = 0
        while pos < len(word):
            if (row, col) in check_letts and word[pos] not in check_letts[(row, col)]:
                word = None
                break
            pos += 1
            row += 1
        return word

    @staticmethod
    def check_sides_h(rowcol, wpos, word, av_side):
        """ Check each letter allowed if adjacent letter present
            for horizontal words """

        row, col = rowcol
        check_letts = {k: v for k, v in av_side.items() if k[0] == row}
        col = col - wpos
        pos = 0
        while pos < len(word):
            if (row, col) in check_letts and word[pos] not in check_letts[(row, col)]:
                word = None
                break
            pos += 1
            col += 1
        return word

    # ------------------------------------------------------------------------------------------
    # Check and score all potential moves
    # Store in self.anchor_scores as (word, score, letters)
    # score is total score from move
    # letters is list of tiles required as [letter, position, blank_required)

    def get_anchor_scores(self):
        """ Return all valid words, scores and letters needed
            self.anchor_scores
            {pos:[horiz word, score, list of [letters, position, True if blank][vertical]}"""

        for key, val in self.anchor_words.items():
            horiz, vert = val
            hwords, vwords = [], []
            row, col = key
            if horiz:
                for word in horiz:
                    wscore = self.word_score(word[1], row, col - word[0] - 1, "H")
                    if wscore[0]:
                        hwords.append(wscore)
            if vert:
                for word in vert:
                    wscore = self.word_score(word[1], row - word[0] - 1, col, "V")
                    if wscore[0]:
                        vwords.append(wscore)

            if any([hwords, vwords]):
                self.anchor_scores[key] = [hwords, vwords]

    def word_score(self, word, row, col, dirn):
        """ Get score for word
            Check and discard if too long (goes off board)
            Add any adjacent letters on board before or after word
            and check extended word.
            Check all relevant positions for inadmissible cross tiles
            returns (word, score [letters needed, position, True if blank]"""

        score = 0
        letters = []
        o_word = word[:]

        if dirn == "H":
            def func_row(x): return x
            def func_col(x): return x + 1
        else:
            def func_row(x): return x + 1
            def func_col(x): return x

        word, row, col = self.check_valid(word, row, col, dirn)

        if word and (word == o_word or self.graph.is_in(word)):

            for lett in word:
                if self.letters[row][col] == ".":

                    if (row, col) in self.cross_tiles:
                        hword_test = (dirn == "H" and
                                      ((row > 0 and self.letters[row - 1][col] != ".")
                                       or (row < 14 and self.letters[row + 1][col] != ".")))
                        vword_test = (dirn == "V" and
                                      ((col > 0 and self.letters[row][col - 1] != ".")
                                       or (col < 14 and self.letters[row][col + 1] != ".")))
                        if (hword_test or vword_test) and lett not in self.cross_tiles[(row, col)]:
                            return "", 10, letters

                    if lett not in self.rack and ' ' not in self.rack:
                        return "", 0, letters
                    letters.append((lett, (row, col), lett not in self.rack))
                else:
                    if lett != self.letters[row][col]:
                        return "", 0, letters

                row = func_row(row)
                col = func_col(col)
        else:
            return "", 0, letters

        turn = self.smachine.checker.get_wordscore(letters)
        if turn[0][0] != "":
            score = sum(n for _, n, _ in turn)
        else:
            word = ""
        return word, score, letters

    def check_valid(self, word, row, col, dirn):
        """ Check if too long (goes off board)
            Add any adjacent letters on board before or after word """
        if row < 0 or col < 0:
            return "", row, col

        if dirn == "H":
            cl = col + len(word)
            if cl > 14:
                return "", row, col

            while cl <= 14 and self.letters[row][cl] != ".":
                word.append(self.letters[row][cl])
                cl += 1
            cl = col - 1
            while cl >= 0 and self.letters[row][cl] != ".":
                word.insert(0, self.letters[row][cl])
                cl -= 1
            col = cl + 1
        else:
            rw = row + len(word)
            if rw > 14:
                return "", row, col

            while rw <= 14 and self.letters[rw][col] != ".":
                word.append(self.letters[rw][col])
                rw += 1
            rw = row - 1
            while rw >= 0 and self.letters[rw][col] != ".":
                word.append(self.letters[rw][col])
                rw -= 1
            row = rw + 1
        return word, row, col

    # ------------------------------------------------------------------------------------------
    # Evaluate/choose moves

    def get_max_score(self):
        """ Return dictionary of words with the maximum score """

        if self.anchor_scores:
            max_val = max(w[1] for v in self.anchor_scores.values() for t in v for w in t)
            return {k: [w for t in v for w in t
                        if w[1] == max_val] for k, v in self.anchor_scores.items()
                    if any(max_val in w for t in v for w in t)}
        return None

    def get_least_used(self):
        """ Return dictionary of words using the least used letters """

        l_frequencies = self.smachine.scene.alphabet.LETTER_FREQUENCIES
        # l_frequencies = self.l_frequencies
        least_used = sorted(list(l_frequencies.items()), key=lambda x: x[1])
        least_used = [t[0] for t in least_used if t[1] < 1.0]
        lu = {k: [w for t in v for w in t
                  if any(char in w[0] and char in self.rack
                         for char in least_used)]
              for k, v in self.anchor_scores.items()}
        return {k: v for k, v in lu.items() if v}

    def get_least_used_no(self):
        """ Return dictionary of words using the least used letters """

        print("DEBUG anchor_scores")
        l_frequencies = self.smachine.scene.alphabet.LETTER_FREQUENCIES
        # l_frequencies = self.l_frequencies
        least_used = sorted(list(l_frequencies.items()), key=lambda x: x[1])
        least_used = [t[0] for t in least_used if t[1] < 3.0]
        lu = {k: [x for x in ((sum(lt in least_used and lt in self.rack for lt in w[0]), w)
                              for t in v for w in t) if x[0] > 0]
              for k, v in self.anchor_scores.items()}
        print("DEBUG letters", least_used)
        print("DEBUG least used")
        return {k: v for k, v in lu.items() if v}

    @staticmethod
    def least_used_max_score(least):
        """ Return dictionary of words using the least used letters
            that have the highest score """

        if least:
            max_val = max(t[1][1] for v in least.values() for t in v)
            return {k: [t for t in v if t[1][1] == max_val]
                    for k, v in least.items() if any(max_val in t[1] for t in v)}
        return {}

    @staticmethod
    def least_used_max_letts(least):
        """ Return dictionary of words using the least used letters
            that have the highest no of those letters """

        if least:
            max_val = max(t[0] for v in least.values() for t in v)
            return {k: [t for t in v if t[0] == max_val]
                    for k, v in least.items() if any(max_val in t for t in v)}
        return {}

    def select_turn(self):
        """ Analyse possible turns and select """

        self.get_anchor_scores()
        turn = self.get_max_score()
        least = self.get_least_used_no()
        print("DEBUG least used max score", self.least_used_max_score(least))
        print("DEBUG least used max lett", self.least_used_max_letts(least))
        if turn:
            return list(turn.values())[0][0]
        return None

    # ------------------------------------------------------------------------------------------
    # Utility methods

    @staticmethod
    def all_same(items):
        """ Return True if all members of item the same """

        return all(x == items[0] for x in items)

    def empty_all(self):
        """ Clear all lists/dictionaries """

        self.anchor_strings.clear()
        self.anchor_words.clear()
        self.anchor_scores.clear()
        self.cross_tiles.clear()

    # ------------------------------------------------------------------------------------------
    # Main calling method

    def update_state(self, rack):
        """ Called by computer player to get next move """

        self.rack = rack
        first_word = self.all_same(self.letters)
        self.empty_all()
        if first_word:
            words = self.get_rackwords()
            words = [(0, w) for w in words]
            self.anchor_words = {(7, 6): [words, []], (6, 7): [[], words]}
        else:
            self.update_cross_letters()
            self.get_rackwords()
            self.get_poss_words()
            self.get_available()
        if all(value == [] for value in self.anchor_words.values()):
            return None
        return self.select_turn()

# pc = Play(None, None)
# rack = ["a", "d", "e", "m", "c", "p", "o"]
# pc.update_state(rack)
