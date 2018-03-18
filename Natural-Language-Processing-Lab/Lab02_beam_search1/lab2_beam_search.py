# coding: utf-8
import re
from pprint import pprint
from collections import Counter

letters = 'abcdefghijklmnopqrstuvwxyz'


def words(text):
    return re.findall(r'\w+', text.lower())


WORDS = Counter(words(open('big.txt').read()))


def P(word, N=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / N


# Using Pw(word) or P(word) may result in different answers
def next_states(state):
    L, R, edit, prob = state
    R0, R1 = R[0], R[1:]
    if edit == 2:
        return [(L + R0, R1, edit, prob)]
    noedit = [(L + R0, R1, edit, prob)]
    delete = [(L, R1, edit + 1, P(L + R1))]
    replaces = [(L + c, R1, edit + 1, P(L + c + R1)) for c in letters]
    inserts = [(L + R0 + c, R1, edit + 1, P(L + R0 + c + R1)) for c in letters]
    return noedit + delete + replaces + inserts


# Using Pw(word) or P(word) may result in different answers
def correction(word):
    states = [('', word, 0, P(word))]
    MAXBEAM = 550

    for i in range(len(word)):
        states = [state for states in map(next_states, states) for state in states]

        word_dict = {}
        for state in states:
            L, R, edit, prob = state
            word = L + R
            if word not in word_dict or edit < word_dict[word][2]:
                word_dict[word] = state

        states = list(word_dict.values())
        states = sorted(states, key=lambda x: x[3], reverse=True)
        states = sorted(states, key=lambda x: x[2])[:MAXBEAM]

    states = [state for state in states if state[2] == 0 or state[3] > 0]

    return sorted(states, key=lambda x: x[3], reverse=True)[:3]


pprint(correction("appearant"))
pprint(correction("beleive"))
pprint(correction("writen"))
pprint(correction("happy"))
