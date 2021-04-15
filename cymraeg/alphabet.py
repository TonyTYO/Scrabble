""" Cymraeg active """

import requests
from bs4 import BeautifulSoup

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

ALPHABET = [" ", "a", "b", "c", "ch", "d", "dd", "e", "f", "ff", "g", "ng", "h",
            "i", "j", "l", "ll", "m", "n", "o", "p", "r", "rh", "s", "t",
            "th", "u", "w", "y"]
SCORES = {" ": 0, "a": 1, "b": 3, "c": 4, "ch": 5, "d": 1, "dd": 1, "e": 1,
          "f": 2, "ff": 4, "g": 2, "ng": 10, "h": 4, "i": 1, "j": 8,
          "l": 2, "ll": 5, "m": 3, "n": 1, "o": 1, "p": 5, "r": 1,
          "rh": 10, "s": 3, "t": 3, "th": 4, "u": 2, "w": 1, "y": 1}  # letter values
LETTERS = ["a"] * 10 + ["e", "n"] * 8 + ["i", "r", "y"] * 7 + ["d", "o"] * 6 + \
          ["w"] * 5 + ["dd"] * 4 + ["f", "g", "l", "u", "s"] * 3 + \
          [" ", "b", "m", "t", "c", "ff", "h", "th"] * 2 + \
          ["ch", "ll", "p", "j", "ng", "rh"]

WORD_CHECK = ["WebCheckerCym", "http://www.geiriadur.net/"]

PC_NAME = "Cyfrifiadur"
PC_RB_TITLE = "Gallu'r Chwaraewr"
PC_VOCAB = [["Syml", "player0.p"], ["Da", "player1.p"]]
PC_2LETT = r"lett2.txt"
LETTER_FREQUENCIES = {}

TILE_POSITIONS = {"a": (11, 12), "b": (122, 12), "c": (233, 12),
                  "d": (344, 12), "e": (455, 12), "f": (566, 12),
                  "g": (677, 12), "h": (11, 129), "i": (122, 129),
                  "j": (233, 129), "k": (344, 129), "l": (455, 129),
                  "m": (566, 129), "n": (677, 129), "o": (11, 246),
                  "p": (122, 246), "q": (233, 246), "r": (344, 246),
                  "s": (455, 246), "t": (566, 246), "u": (677, 246),
                  "v": (11, 363), "w": (122, 363), "x": (233, 362),
                  "y": (344, 363), "z": (455, 363), " ": (569, 359),
                  "ch": (11, 494), "dd": (122, 494), "ff": (233, 494),
                  "ng": (344, 494), "ll": (455, 494), "ph": (566, 494),
                  "rh": (677, 494), "th": (11, 611)}

TOOLTIPS = {"play": "Dechrau tro", "accept": "Diwedd tro",
            "pass": "Pasio", "challenge": "Herio", "exchange": "Cyfnewid",
            "quit": "Gadael", "next": "Ymlaen", "back": "Dychwelyd",
            "end": "Gorffen", "new": "Gêm newydd"}

QLOAD_MSGS = {0: "Ffeil yn llwytho ..."}

QSTATES_MSGS = {0: ("Rhaid dewis dwy deil, un ar bob ochr, "
                    "wedyn clicio'r bwtwm isod"),
                1: ("Mae'r llythrennau yr un peth! Dewiswch eto wedyn "
                    "clicio'r bwtwm isod"),
                2: ("Dewiswch deil yr un a'i dragio i'ch ochr chi o'r sgrin, "
                    "wedyn cliciwch y bwtwm isod"),
                3: "Mae teil wag ohyd yn dechrau.",
                4: " yn agosach i A nag yw ",
                5: " i ddechrau",
                6: "Rhaid rhoi llythyren ar gyfer pob teil wag",
                7: ('Llanwch y llythennau ar gyfer y teiliau gwag a cliciwch '
                    '<font color="red">Enter</font> wedi gorffen'),
                8: "5 eiliad i herio!",
                9: ("Pob gair yn gywir. Mae'ch her wedi methu. "
                    "Rydych yn colli eich tro"),
                10: " gair yn",
                11: " o eiriau yn",
                12: " anghywir. Mae'ch her wedi llwyddo",
                13: "Mae'r teiliau i gyd yn dychwelyd a rydych yn colli'r tro hwn",
                14: ("G&ecirc;m drosodd!<br>Dim teiliau yn y rhestl "
                     "a dim mwy ar gael"),
                15: "Nid oes mwy o teiliau ar gael",
                16: ("Gwthiwch y teiliau i gyfnewid i fyny allan o'r rhestl."
                     "<br> Gwthiwch eto i ganslo"),
                17: ('Gwasgwch y bwtwm <font color="red">Dechrau</font> '
                     'i gychwyn eich tro'),
                18: "Methu gwirio - Geiriadur ddim ar gael",
                19: "Please wait as computer player loads",
                20: "Choose an ability level for the computer",
                21: ("Dewiswch deil a'i dragio i'ch ochr chi o'r sgrin "
                     "wedyn cliciwch y bwtwm isod"),
                22: "Mewnbynnwch 'pc' fel enw i gael y cyfrifiadur fel chwaraewr",
                23: "Nid yw'r cyfrifiadur ar gael fel chwaraewr"}

ERROR_MSGS = {0: r"Rhaid defnyddio o leiaf un lythyren",
              1: (r"Rhaid i'r gair cyntaf fod ag un llythyren ar y sgw&acirc;r "
                  "canol"),
              2: r"Rhaid i'r gair fod yn ddi-fwlch",
              3: r"Rhaid defnyddio teil sydd ar y bwrdd yn barod",
              4: r"Rhaid i'r gair fod yn fertigol neu llorweddol",
              5: r"Ni ellir defnyddio gair un lythyren fel y gair cyntaf"}

QENWAU_MSGS = {0: "Teipiwch eich henwau, wedyn cliciwch y bwtwm isod",
               1: "Enw'r chwaraewr ",
               2: "Chwith",
               3: "Dde",
               4: "\n"}

QCHWARAEWR_MSGS = {0: "Chwaraewr"}

QTESTUN_MSGS = {0: " yw'r enillydd"}


class WebCheckerCym:
    """ Class to check words in Welsh Scrabble
        Called with Web_Checker_cym("http://www.geiriadur.net/") """

    def __init__(self, url):
        self.url = url

    def check_word(self, gair):
        """ Send word request to web page
            Check if word is in scrabble list
            Return True or False
            Return None if check not operational """

        gair = ''.join(gair)
        try:
            r = requests.post(self.url, params=dict(
                page="ateb",
                term=gair,
                direction="we",
                type="all",
                whichpart="exact"
            ))
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        ans = self.parse(r)
        if "No matches" in ans:
            return False
        return True

    @staticmethod
    def parse(response):
        """ Parse returned html to get answer """
        soup = BeautifulSoup(response.text, 'lxml')
        tb = soup.find_all('table')[3]
        ans_row = tb.find_all('tr')[2]
        answer = ans_row.find_all('td')[0].get_text()
        return answer
