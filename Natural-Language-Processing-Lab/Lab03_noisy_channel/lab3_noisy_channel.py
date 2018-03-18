# coding: utf-8
import re
import math
from collections import Counter, defaultdict
from pprint import pprint
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
    count_1edit[(w, c)] += count
    count_c[c] += 1

r = 10
N = dict()
for i in range(1, r):
    N[i] = (sum(count for count in count_1edit.values() if count == i)) // i
N[0] = 26 * 26 * 26 * 26 + 2 * 26 * 26 * 26 + 26 * 26 - sum(N.values())


def smooth(count, r=10):
    if count <= r:
        return (count + 1) * N[count + 1] / N[count]
    else:
        return count


def Pedit(w, c):
    if count_c[c] > 0:
        return smooth(count_c[c]) / count_c[c]
    else:
        return 0


'''Combining channel probability with word probability to score states'''


def P(pedit, pw):
    return (pedit * pw) * 10 ** 7


'''Next States'''
letters = 'abcdefghijklmnopqrstuvwxyz'


def next_states(state):
    L, R, edits, pw, pedit = state  # (str, str, list, float, float)
    R0, R1 = R[0], R[1:]
    if edits == 2:
        return [(L + R0, R1, edits, pw, pedit * 0.8)]
    noedit = [(L + R0, R1, edits, pw, pedit * 0.8)]
    if len(L) > 0:
        delete = [(L, R1, edits + 1, Pw(L + R1), P(Pedit(L[-1], L[-1] + R0), Pw(L + R1)))]
    else:
        delete = [(L, R1, edits + 1, Pw(L + R1), P(Pedit('', R0), Pw(L + R1)))]
    insert = [(L + R0 + c, R1, edits + 1, Pw(L + R0 + c + R1), P(Pedit(R0, R0 + c), Pw(L + R0 + c + R1))) for c in letters]
    replace = [(L + c, R1, edits + 1, Pw(L + c + R1), P(Pedit(R0, R1), Pw(L + c + R1))) for c in letters]
    if len(R1) > 0:
        transpose = [(L + R1[0], R0 + R1[1:], edits + 1, Pw(L + R1[0] + R0 + R1[1:]),
                      P(Pedit(R0 + R1[0], R1[0] + R0), Pw(L + R1[0] + R0 + R1[1:])))]
    else:
        transpose = []
    return noedit + delete + insert + replace + transpose


'''Correcting'''
MAXBEAM = 1000


def correction(word):
    states = [('', word, 0, Pw(word), 1)]  # initial state
    for i in range(len(word)):
        states = [newstates for state in states for newstates in next_states(state)]
        states = [state for state in states if state[4] > 0]

        temp = defaultdict(list)
        for state in states:
            L, R, edits, pw, pedit = state
            temp[L + R].append(state)
        states = [min(substates, key=lambda x: x[2]) for wd, substates in temp.items()]

        states = sorted(states, key=lambda x: x[4], reverse=True)
        states = sorted(states, key=lambda x: x[2])[:MAXBEAM]

    states = [state for state in states if state[4] > 0]

    return sorted(states, key=lambda x: x[4], reverse=True)[:3]


correction("appearant")
