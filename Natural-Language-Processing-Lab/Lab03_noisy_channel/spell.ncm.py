from collections import Counter, defaultdict
import re


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
    edit, count = __________________
    w, c = __________________
    count_1edit[___] += __________________
    count_c[___] += __________________

r = 10
N = dict()
for i in range(1, r + ____):
    N[i] = ____________________________________
N[0] = 26 * 26 * 26 * 26 + 2 * 26 * 26 * 26 + 26 * 26 - sum(N.values())


def smooth(count, r=10):
    if count <= r:
        return __________________
    else:
        return __________________


def Pedit(w, c):
    if count_c[c] > 0:
        return __________________ / count_c[c]
    else:
        return 0


'''Combining channel probability with word probability to score states'''


def P(pedit, pw):
    return __________________


'''Next States'''
letters = 'abcdefghijklmnopqrstuvwxyz'


def next_states(state):
    L, R, edits, pw, pedit = state  # (str, str, list, float, float)
    R0, R1 = R[0], R[1:]
    if len(edits) == 2:
        return [(L + R0, R1, edits, pw, pedit * 0.8)]
    noedit = [(L + R0, R1, edits, pw, pedit * 0.8)]
    delete = [(__________________)]
    insert = [(__________________) for c in letters]
    replace = [(__________________) for c in letters]
    transpose = [(__________________)] if _________ else []
    return __________________


'''Correcting'''
MAXBEAM = 500


def correction(word):
    states = [('', word, [], Pw(word), 1)]  # initial state
    for i in range(len(word)):
        print(i, states[:3])
        states = [newstates for state in states for newstates in next_states(state)]
        states = [state for state in states if __________________]

        temp = defaultdict(list)
        for state in states:
            L, R, _, _, _ = state
            temp[L + R].append(state)
        states = [min(substates, key=lambda x: len(x[2])) for wd, substates in temp.items()]

        states = sorted(states, key=__________________)[:MAXBEAM]

    states = [state for state in states if __________________]

    return sorted(states, key=__________________)[:3]
