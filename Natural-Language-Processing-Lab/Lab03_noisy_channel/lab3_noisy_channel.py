# coding: utf-8
import re
import math
from pprint import pprint
from collections import Counter, defaultdict
'''Word Probability'''


def words(text):
    return re.findall(r'\w+', text.lower())


count_word = Counter(words(open('big.txt').read()))
Nw = sum(count_word.values())
Pdist = {word: float(count) / Nw for word, count in count_word.items()}


def Pw(word):
    return Pdist[word] if word in Pdist else 10 / 10**len(word) / Nw


'''Channel Probability'''
count_1edit = defaultdict(lambda: 0)
count_c = defaultdict(lambda: 0)
for line in open('count_1edit.txt'):
    edit, count = line.split('\t')[0], int(line.split('\t')[1].replace('\n', ''))
    w, c = edit.split('|')[0], edit.split('|')[1]
    count_1edit[(w, c)] = count
    count_c[c] += count

r = 10
N = dict()
for i in range(1, r + 2):
    N[i] = (sum(count for count in count_1edit.values() if count == i)) // i

N[0] = 26 * 26 * 26 * 26 + 2 * 26 * 26 * 26 + 26 * 26 - sum(N.values())
Nall = len(count_1edit.keys())


def smooth(count, r=10):
    if count <= r:
        return (count + 1) * N[count + 1] / N[count]
    else:
        return count


smooth(0)
Nall
count_c['e']


def Pedit(w, c):
    if (w, c) in count_1edit:
        return smooth(count_1edit[w, c]) / count_c[c]
    else:
        if c in count_c:
            return smooth(0) / count_c[c]
        else:
            return 10**(-20)


Pedit("e", "i")
'''Combining channel probability with word probability to score states'''


def P(pedit, pw):
    return math.log(pedit) + math.log(pw)


'''Next States'''
letters = 'abcdefghijklmnopqrstuvwxyz'


def next_states(state):
    L, R, edits, prob, pedit = state
    R0, R1 = R[0], R[1:]

    if len(edits) == 2:
        return [(L + R0, R1, edits, prob, pedit * 0.8)]

    noedit = [(L + R0, R1, edits, prob, pedit * 0.8)]
    delete = [(L, R1, edits + [(L[-1:] + R0, L[-1:])], Pw(L + R1), pedit * Pedit(L[-1:] + R0, L[-1:]))]
    replace = [(L + c, R1, edits + [(R0, c)], Pw(L + c + R1), pedit * Pedit(R0, c)) for c in letters]
    insert = [(L + R0 + c, R1, edits + [(R0, R0 + c)], Pw(L + R0 + c + R1), pedit * Pedit(R0, R0 + c)) for c in letters]
    transpose = [(L + R1[0], R0 + R1[1:], edits + [(R0 + R1[0], R1[0] + R0)], Pw(L + R1[0] +
                                                                                 R0 + R1[1:]), pedit * Pedit(R0 + R1[0], R1[0] + R0))] if len(R1) > 0 else []

    return noedit + delete + insert + replace + transpose
# Using Pw(word) or P(word) may result in different answers


def correction(word):
    states = [("", word, [], Pw(word), 1)]
    MAXBEAM = 550

    for i in range(len(word)):
        states = [state for states in map(next_states, states) for state in states]

        word_dict = {}
        for state in states:
            L, R, edits, prob, pedit = state
            word = L + R
            if word not in word_dict or len(edits) < len(word_dict[word][2]):
                word_dict[word] = state

        states = list(word_dict.values())
        states = sorted(states, key=lambda x: P(x[3], x[4]), reverse=True)
        states = sorted(states, key=lambda x: len(x[2]))[:MAXBEAM]

    states = sorted(states, key=lambda x: P(x[3], x[4]), reverse=True)
    return states[:3]


correction('appearant')
correction("runing")
correction("particpate")
correction("beleive")
correction('writtung')
correction('happy')
correction('thenks')
get_ipython().magic('save lab3_noisy_channel.py 1-20')
