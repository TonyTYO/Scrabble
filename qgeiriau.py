""" All word formation and checking routines for game """

import Constants as Cons


class Words:
    """ Class for Word formation and checking """

    def __init__(self, scene):

        self.scene = scene
        self.word_check = scene.alphabet.set_checker(scene)
        self.letter_scores = scene.alphabet.SCORES

        self.letters = [["."] * Cons.SIZE for _ in range(Cons.SIZE)]  # letters in each cell

        self.words = []  # Words formed on board
        self.uses_letter = False

        # Convert premium word into a two-dimensional array
        premium_cells = Cons.PREMIUM_CELLS
        self.grid = [[0] * Cons.SIZE for _ in range(Cons.SIZE)]
        premium_cells = premium_cells.replace(" ", "")
        for row in range(Cons.SIZE):
            for col in range(Cons.SIZE):
                self.grid[row][col] = premium_cells[row * Cons.SIZE + col]

    def get_wordscore(self, word):
        """ Initialise variables and run check
            word is list of [(letter, (row, col), True if blank] """

        self.words = []
        self.uses_letter = False
        return self.check_word(word)

    # Form word from letters in play and letters on board if needed
    # Check word and calculate score
    def check_word(self, word):
        """ Form words, check valid and calculate score
            Return list of words in turn as [(word, score, valid)]
            valid is set True/False after word check otherwise None """

        turn = None
        wdirection = self.get_direction(word)

        if wdirection == "X":
            turn = [("", -5)]
            return turn
        if not word:
            turn = [("", -1)]
            return turn

        first_word = self.all_same(self.letters)

        self.uses_letter = False
        if wdirection == "H":
            word = sorted(word, key=lambda item: item[1][1])
            self.check_parallel_row(word)
            self.check_wordrow(word)
        else:
            word = sorted(word, key=lambda item: item[1][0])
            self.check_parallel_col(word)
            self.check_wordcol(word)
        if any(x[0] == "." for x in word) is True:
            turn = [("", -3)]
        elif self.uses_letter is False and first_word is False:
            turn = [("", -4)]
        elif first_word is True:
            if not [p for t, p, b in word if p == (7, 7)]:
                turn = [("", -2)]
            if len(word) < 2:
                turn = [("", -6)]

        if turn is None:
            turn = self.get_words(word)
        return turn

    @staticmethod
    def get_direction(word):
        """ Insert H/V/X for horizontal, vertical or incorrect direction """

        if all(r[1][0] == word[0][1][0] for r in word):
            direction = "H"
        elif all(r[1][1] == word[0][1][1] for r in word):
            direction = "V"
        else:
            direction = "X"
        return direction

    @staticmethod
    def all_same(items):
        """ Return True if all members of item the same """

        return all(x == items[0] for x in items)

    # Check for parallel words
    # Word in row
    def check_parallel_row(self, word):
        """ Check parallel words - word in a row """

        row = word[0][1][0]
        for letter in word:
            col = letter[1][1]
            newword = []
            i = row - 1
            while i >= 0 and self.letters[i][col] != ".":
                newword.insert(0, [self.letters[i][col], (i, col), False])
                i -= 1
            newword.append(letter)
            i = row + 1
            while i < Cons.SIZE and self.letters[i][col] != ".":
                newword.append([self.letters[i][col], (i, col), False])
                i += 1
            if len(newword) > 1:
                self.words.append(newword)
                self.uses_letter = True

    # Check for parallel words
    # Word in column
    def check_parallel_col(self, word):
        """ Check parallel words - word in a column """

        col = word[0][1][1]
        for letter in word:
            row = letter[1][0]
            newword = []
            i = col - 1
            while i >= 0 and self.letters[row][i] != ".":
                newword.insert(0, [self.letters[row][i], (row, i), False])
                i -= 1
            newword.append(letter)
            i = col + 1
            while i < Cons.SIZE and self.letters[row][i] != ".":
                newword.append([self.letters[row][i], (row, i), False])
                i += 1
            if len(newword) > 1:
                self.words.append(newword)
                self.uses_letter = True

    # If word is in a row check if consecutive cells
    # If yes check if any letters at start or end already on board
    # If not get relevant middle letters from board
    def check_wordrow(self, word):
        """ Word in a row """

        row = word[0][1][0]
        start = word[0][1][1]
        end = word[-1][1][1]
        consecutive = ((end - start) == (len(word) - 1))
        if not consecutive:
            j = 0
            for col in range(start, end + 1):
                if any(x[1] == (row, col) for x in word) is False:
                    word.insert(j, [self.letters[row][col], (row, col), False])
                    self.uses_letter = True
                j += 1

        i = start - 1
        while i >= 0 and self.letters[row][i] != ".":
            word.insert(0, [self.letters[row][i], (row, i), False])
            self.uses_letter = True
            i -= 1
        i = end + 1
        while i < Cons.SIZE and self.letters[row][i] != ".":
            word.append([self.letters[row][i], (row, i), False])
            self.uses_letter = True
            i += 1

    # If word is in a column check if consecutive cells
    # If yes check if any letters at start or end already on board
    # If not get relevant middle letters from board
    def check_wordcol(self, word):
        """ Word in a column """

        col = word[0][1][1]
        start = word[0][1][0]
        end = word[-1][1][0]
        consecutive = ((end - start) == (len(word) - 1))
        if not consecutive:
            j = 0
            for row in range(start, end + 1):
                if any(x[1] == (row, col) for x in word) is False:
                    word.insert(j, [self.letters[row][col], (row, col), False])
                    self.uses_letter = True
                j += 1

        i = start - 1
        while i >= 0 and self.letters[i][col] != ".":
            word.insert(0, [self.letters[i][col], (i, col), False])
            self.uses_letter = True
            i -= 1
        i = end + 1
        while i < Cons.SIZE and self.letters[i][col] != ".":
            word.append([self.letters[i][col], (i, col), False])
            self.uses_letter = True
            i += 1

    # Check and score all words found
    def get_words(self, gair):
        """ Check and score all words found """

        turn = []
        if self.words:
            for item in self.words:
                word, score, valid = self.get_word_score(item)
                turn.insert(0, [word, score, valid])
        word, score, valid = self.get_word_score(gair)
        if len(word) != 1:
            turn.insert(0, [word, score, valid])
        return turn

    # Get word from self.word
    # Calculate score
    def get_word_score(self, wlist):
        """ Get word from self.word and calculate score """

        lett_list = [str(lst[0]) for lst in wlist]
        score = 0
        word_multiplier = 1
        for item in wlist:
            lett = item[0]
            if item[2]:
                lett = " "
            square = self.grid[item[1][0]][item[1][1]]
            if self.letters[item[1][0]][item[1][1]] != ".":
                score += self.letter_scores[lett]
            else:
                if square == ".":
                    score += self.letter_scores[lett]
                elif square == "d":
                    score += (2 * self.letter_scores[lett])
                elif square == "t":
                    score += 3 * (self.letter_scores[lett])
                elif square == "D":
                    score += self.letter_scores[lett]
                    word_multiplier = 2 * word_multiplier
                elif square == "T":
                    score += self.letter_scores[lett]
                    word_multiplier = 3 * word_multiplier
        score = word_multiplier * score
        return lett_list, score, None

    def check_words(self, wlist):
        """ Check all words against standard list
            If None returned, a fault has occured and
            check has not been made"""

        if self.word_check is None:
            return [], True

        new_list = [(word[0], word[1], self.word_check.check_word(word[0])) for word in wlist]
        html_error = any(None in word for word in new_list)
        return [(word[0], word[1], self.word_check.check_word(word[0]))
                for word in wlist], html_error

    def set_letters(self, tiles):
        """ Set letters in internal board """
        for item in tiles:
            self.letters[item[1][0]][item[1][1]] = item[0]

    def val_letters(self, lettlist):
        """ Return total scoores of letters in list """
        return sum([self.letter_scores[let] for let in lettlist])
