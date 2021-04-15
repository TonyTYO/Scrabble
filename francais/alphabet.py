""" Français active """

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

ALPHABET = [" ", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
            "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
SCORES = {" ": 0, "a": 1, "b": 3, "c": 3, "d": 2, "e": 1, "f": 4,
          "g": 2, "h": 4, "i": 1, "j": 8, "k": 10, "l": 1,
          "m": 2, "n": 1, "o": 1, "p": 3, "q": 8, "r": 1,
          "s": 1, "t": 1, "u": 1, "v": 4, "w": 10, "x": 10,
          "y": 10, "z": 10}  # letter values
LETTERS = ["e"] * 15 + ["a"] * 9 + ["i"] * 8 + \
          ["n", "o", "r", "s", "t", "u"] * 6 + \
          ["l"] * 5 + ["d", "m"] * 3 + \
          [" ", "b", "c", "g", "f", "h", "p", "v"] * 2 + \
          ["k", "j", "x", "q", "z", "w", "y"]

WORD_CHECK = ["WebCheckerFr", 'http://www.funmeninges.com/dicoplus-consulter.html']
# WORD_CHECK = "francais\\ods6.p"

PC_NAME = "Ordinateur"
PC_RB_TITLE = "Capacité du joueur"
PC_VOCAB = [["Simple", "joueur0.p"], ["Excellent", "joueur1.p"]]

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
                  "y": (344, 363), "z": (455, 363), " ": (569, 359)}

TOOLTIPS = {"play": "Commencer le tour", "accept": "Finir le tour",
            "pass": "Passer le tour", "challenge": "Contestation",
            "exchange": "Échange", "quit": "Partir", "next": "Suivant",
            "back": "Retour", "end": "Quitter", "new": "Nouveau jeu"}

QLOAD_MSGS = {0: "Chargement de fichier ..."}

QSTATES_MSGS = {0: ("Deux tuiles, une de chaque c&ocirc;t&eacute;, "
                    "doivent &ecirc;tre choisies puis cliquez "
                    "sur le bouton ci-dessous"),
                1: ("Lettres pareil! Choisissez &agrave; nouveau "
                    "puis cliquez sur le bouton ci-dessous"),
                2: ("Choisissez un carreau chacun et faites-la glisser "
                    "de votre c&ocirc;t&eacute; de l'&eacute;cran puis "
                    "cliquez sur le bouton ci-dessous"),
                3: "Le blanc commence toujours.",
                4: " est plus proche de A que ",
                5: " va commencer",
                6: "Vous devez entrer une lettre pour tous les carreaux vides",
                7: ('Remplissez les lettres pour vos carreaux vides '
                    'et appuyez sur <font color="red">Enter</font> '
                    'quand complet'),
                8: "Vous avez 5 secondes pour contester",
                9: ("Tous les mots sont corrects. Votre contestation a "
                    "&eacute;chou&eacute; et vous perdez votre "
                    "prochain tour"),
                10: " un mot est",
                11: " mots sont",
                12: " inadmissible. Votre contestation est correct",
                13: ("Toutes les carreaux sont retourn&eacute;es "
                     "et vous perdez ce tour"),
                14: ("Jeu termin&eacute;!<br>Aucune carreau dans le rack "
                     "et aucun reste &agrave; tirer"),
                15: "Plus de carreaux de lettres disponibles",
                16: ("Donner les carreaux un petit coup de coude pour "
                     "sortir de rack.<br> Un autre &agrave; "
                     "annuler &agrave; nouveau"),
                17: ('Appuyez sur <font color="red">Commencer</font> '
                     'pour commence ton tour'),
                18: ("Impossible de v&eacute;rifier les mots - "
                     "Dictionnaire non disponible"),
                19: "Veuillez patienter pendant le chargement du lecteur",
                20: "Choisissez un niveau de capacit&eacute; pour l'ordinateur",
                21: ("Choisissez une tuile et faites-la glisser "
                     "&agrave; vos c&ocirc;t&eacute;s "
                     "puis cliquez ci-dessous"),
                22: "Entrez le nom 'pc' pour que l'ordinateur joue",
                23: "Pas de lecteur d'ordinateur disponible"}

ERROR_MSGS = {0: r"Vous devez utiliser au moins une lettre",
              1: (r"Le premier mot doit avoir une lettre sur le carr&eacute; "
                  "central"),
              2: r"Le mot doit &ecirc;tre continu",
              3: r"Le mot doit utiliser un carreau de bord",
              4: r"Le mot doit &ecirc;tre horizontal ou vertical",
              5: r"Ne peut pas utiliser le mot lettre unique comme premier mot"}

QENWAU_MSGS = {0: "Entrez vos noms, puis cliquez sur le bouton ci-dessous",
               1: "Entrez le nom du joueur ",
               2: "Gauche",
               3: "Droite",
               4: "\n"}

QCHWARAEWR_MSGS = {0: "Joueur"}

QTESTUN_MSGS = {0: " est le gagnant"}


class WebCheckerFr:
    """ Class to check words in French Scrabble
        Called with Web_Checker_fr("http://www.funmeninges.com/dicoplus-consulter.html") """

    def __init__(self, url):
        self.url = url

    def check_word(self, gair):
        """ Send word request to web page
            Check if word is in scrabble list
            Return True or False
            Return None if check not operational """

        gair = ''.join(gair)
        try:
            r = requests.post(self.url, data={"search_word": gair})
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        ans = self.parse(r)
        if "non trouvé, orthographe incorrecte." in ans:
            return False
        return True

    @staticmethod
    def parse(response):
        """ Parse returned html to get answer """
        # print(response.text.encode('utf-8'))
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('title')
        answer = title.string
        return answer
