""" English active """
""" The first word in the above is the menu entry for the language choice menu """
""" Alter as required for new language """
""" The second word needs to be set to active to make the language operational """
""" It must be the first line in this file """

""" Settings based on language choice
    Set each of the following for the language

    ALPHABET:          All letters in an ordered list
    SCORES:            Dictionary of letter scores for the game
    LETTERS:           List of all letters in game pool
    WORD_CHECK:        Filename for text(.txt) or GADDAG (.p) file or
                       Class that checks validity of words in list [Name, [parameters]]
    PC_NAME:           Name to call computer player
    PC_RB_TITLE:       Title for Radio Button ability menu for computer player
    PC_VOCAB:          List of wordlists for each ability level. One entry for each ability level.
                       [Ability level for menu, GADDAG file for level]
    PC_2LETT:          List of allowable two-letter words. Can be removed or left as []
                       if list not available.
    LETTER_FREQUENCIES:Frequencies of use of each letter in alphabet in normal usage
                       {letter:frequency}. Leave empty if not known {}.
    TILE_POSITIONS:    Dictionary of coordianes of top left corner
                       of each letter tile in scrabble_letters.png.
                       Position of any letters added needs to be added here
    TOOL_TIPS:         Tool tips for each button
    QLOAD_MSGS:        Message when loading files
    QSTATES_MSGS:      Dictionary of all messages for qstates.py
    ERROR_MSGS:        Dictionary of all error messages (qstates.py)
    QENWAU_MSGS:       Dictionary of all messages for qenwau.py
    QCHWARAEWR_MSGS:   Dictionary of all messages for qchwaraewr.py
    QTESTUN_MSGS:      Dictionary of all messages for qtestun.py

"""

ALPHABET = [" ", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
            "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w",
            "x", "y", "z"]
SCORES = {" ": 0, "a": 1, "b": 3, "c": 3, "d": 2, "e": 1, "f": 4,
          "g": 2, "h": 4, "i": 1, "j": 8, "k": 5, "l": 1,
          "m": 3, "n": 1, "o": 1, "p": 3, "q": 10, "r": 1,
          "s": 1, "t": 1, "u": 1, "v": 4, "w": 4, "x": 8,
          "y": 4, "z": 10}  # letter values
LETTERS = ["e"] * 12 + ["a", "i"] * 9 + ["o"] * 8 + ["n", "r", "t"] * 6 + \
          ["l", "s", "u", "d"] * 4 + ["g"] * 3 + \
          [" ", "b", "c", "m", "p", "f", "h", "v", "w", "y"] * 2 + \
          ["k", "j", "x", "q", "z"]

WORD_CHECK = r'english\sowpods.txt'
# WORD_CHECK = "english\\pygaddag.p"

PC_NAME = "Computer"
PC_RB_TITLE = "Player ability"
PC_VOCAB = [["Simple", "player0.p"], ["Good", "player1.p"],
            ["Excellent", "player2.p"]]
PC_2LETT = r"lett2.txt"

LETTER_FREQUENCIES = {"a": 8.2, "b": 1.5, "c": 2.8, "d": 4.3, "e": 12.7,
                      "f": 2.2, "g": 2.0, "h": 6.1, "i": 7.0, "j": 0.2,
                      "k": 0.8, "l": 4.0, "m": 2.4, "n": 6.7, "o": 7.5,
                      "p": 1.9, "q": 0.1, "r": 6.0, "s": 6.3, "t": 9.1,
                      "u": 2.8, "v": 1.0, "w": 2.4, "x": 0.2, "y": 2.0,
                      "z": 0.1}

TILE_POSITIONS = {"a": (11, 12), "b": (122, 12), "c": (233, 12),
                  "d": (344, 12), "e": (455, 12), "f": (566, 12),
                  "g": (677, 12), "h": (11, 129), "i": (122, 129),
                  "j": (233, 129), "k": (344, 129), "l": (455, 129),
                  "m": (566, 129), "n": (677, 129), "o": (11, 246),
                  "p": (122, 246), "q": (233, 246), "r": (344, 246),
                  "s": (455, 246), "t": (566, 246), "u": (677, 246),
                  "v": (11, 363), "w": (122, 363), "x": (233, 363),
                  "y": (344, 363), "z": (455, 363), " ": (569, 359)}

TOOLTIPS = {"play": "Start turn", "accept": "End turn",
            "pass": "Pass", "challenge": "Challenge", "exchange": "Exchange",
            "quit": "Leave", "next": "Next", "back": "Return",
            "end": "Quit", "new": "New game"}

QLOAD_MSGS = {0: "File Loading ..."}

QSTATES_MSGS = {0: ("Two tiles, one on each side, must be chosen "
                    "then click button below"),
                1: "Letters the same! Choose again then click button below",
                2: ("Choose a tile each and drag it to your side of the screen "
                    "then click button below"),
                3: "Blank always starts.",
                4: " is nearer to A than ",
                5: " will start",
                6: "You must enter a letter for all blank tiles",
                7: ('Fill in the letters for your blank tiles and press '
                    '<font color="red">Enter</font> when complete'),
                8: "You have 5 secs to challenge",
                9: ("All words are correct. Your challenge has failed "
                    "and you lose your next turn"),
                10: " one word is",
                11: " words are",
                12: " inadmissible. Your challenge is correct",
                13: "All the tiles are returned and you lose this turn",
                14: "Game over!<br>No tiles in rack and none left to draw",
                15: "No more letter tiles available",
                16: ("Nudge tiles to be exchanged up out of rack.<br> "
                     "Nudge again to cancel"),
                17: 'Press <font color="red">Start</font> to begin turn',
                18: "Unable to check words - Dictionary not available",
                19: "Please wait as computer player loads",
                20: "Choose an ability level for the computer",
                21: ("Choose a tile and drag it to your side of the screen "
                     "then click button below"),
                22: ("Enter the name <font color='red'>pc</font> "
                     "for the computer to play"),
                23: "No computer player available"}

ERROR_MSGS = {0: r"You must use at least one letter",
              1: r"First word must have one letter on the centre square",
              2: r"Word must be continuous",
              3: r"Word must use tile from board",
              4: r"Word must be horizontal or vertical",
              5: r"Can't use single letter word as first word"}

QENWAU_MSGS = {0: "Enter your names, then click button below",
               1: "Enter name of ",
               2: "Left",
               3: "Right",
               4: " player\n"}

QCHWARAEWR_MSGS = {0: "Player"}

QTESTUN_MSGS = {0: " is the winner"}
