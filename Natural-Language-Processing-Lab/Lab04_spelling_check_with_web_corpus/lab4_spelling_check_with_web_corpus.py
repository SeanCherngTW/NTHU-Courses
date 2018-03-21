# coding: utf-8
import re
import time
import math
import pickle
import dill
import itertools
from NetSpeakAPI import NetSpeak
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
    return states[:10]


SE = NetSpeak()
with open('stopwords.txt', 'r') as f:
    stopwords = [line.strip() for line in f]
stopwords


def save_trigram(obj, name):
    _dict = dill.dumps(obj)
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(_dict, f, pickle.HIGHEST_PROTOCOL)


def load_trigram(name):
    with open(name + '.pkl', 'rb') as f:
        return dill.loads(pickle.load(f))


def query_correction(query):
    query_split = query.lower().split()
    query_candidates = []
    for word in query_split:
        if word in stopwords:
            query_candidates.append(set([word]))
        else:
            # Get top 10 words from correction
            query_candidates.append(set([word] + [row[0] for row in correction(word)]))

    # List all
    query_candidates = list(itertools.product(*query_candidates))
    new_c = []
    iteration = len(query_split)

    # Get sentence if there's edit distance <= 1
    for candidate in query_candidates:
        threshold = iteration - 1
        for i in range(iteration):
            if candidate[i] == query_split[i]:
                threshold -= 1
        if threshold <= 0:
            new_c.append(candidate)
    return new_c


query_correction('the wind belu the leaves')
query_trigram = load_trigram('trigram')
query_trigram


def get_best_candidate(candidates):
    best_candidate = ''
    best_score = -1.0
    for candidate in candidates:
        trigram_score = []

        if len(candidate) == 2:
            current_trigram = (' '.join(candidate).strip())
            res = SE.search(current_trigram)
            if res:
                trigram_score.append(res[0][1])
                query_trigram[current_trigram] = res[0][1]
            else:
                trigram_score.append(0.0)
                query_trigram[current_trigram] = 0.0

        else:
            for i in range(len(candidate) - 2):
                current_trigram = (' '.join(candidate[i:i + 3]).strip())
                if current_trigram in query_trigram:
                    trigram_score.append(query_trigram[current_trigram])
                else:
                    res = SE.search(current_trigram)
                    if res:
                        trigram_score.append(res[0][1])
                        query_trigram[current_trigram] = res[0][1]
                    else:
                        trigram_score.append(0.0)
                        query_trigram[current_trigram] = 0.0

        candidate_score = min(trigram_score)

        if best_score < candidate_score:
            best_score = candidate_score
            best_candidate = candidate

    return best_candidate


def print_answer(best_candidate, query):
    correct_word = ''
    err = ''
    for w1, w2 in zip(best_candidate, query.split()):
        w1 = w1.lower()
        w2 = w2.lower()
        if w1 != w2:
            correct_word = w1
            err = w2
            break

    print('Error: %s' % err)
    print('Candidates: [%s]' % (', '.join([row[0] for row in correction(err)])))
    print('Correction: %s' % correct_word)
    print('%s  -> %s' % (query.lower(), ' '.join(best_candidate).lower()))

    out_file.write('Error: %s\n' % err)
    out_file.write('Candidates: [%s]\n' % (', '.join([row[0] for row in correction(err)])))
    out_file.write('Correction: %s\n' % correct_word)
    out_file.write('%s  -> %s\n' % (query.lower(), ' '.join(best_candidate).lower()))


ticks = time.time()
out_file = open('output_%d.txt' % ticks, 'a')

i = 0
hit = 0
for line in open('lab4.test.1.txt', 'r'):
    w, c = line.split('\t')[0], line.split('\t')[1]
    candidates = query_correction(w)
    best_candidate = get_best_candidate(candidates)
    print_answer(best_candidate, w)
    if ' '.join(best_candidate).lower().strip() == c.lower().strip():
        hit += 1

    print("hit = %d" % hit)
    print()
    out_file.write("hit = %d\n\n" % hit)

    i += 1
print('acc = %f' % (hit / i))
out_file.close()
save_trigram(query_trigram, 'trigram')
ticks = time.time()
out_file = open('output_%d_2.txt' % ticks, 'a')

i = 0
hit = 0
for line in open('lab4.test.2.txt', 'r'):
    w, c = line.split('\t')[0], line.split('\t')[1]
    candidates = query_correction(w)
    best_candidate = get_best_candidate(candidates)
    print_answer(best_candidate, w)
    if ' '.join(best_candidate).lower().strip() == c.lower().strip():
        hit += 1

    print("hit = %d" % hit)
    print()
    out_file.write("hit = %d\n\n" % hit)

    i += 1

print('acc = %f' % (hit / i))
print('false_alarm = %f' % ((i - hit) / i))
out_file.close()
save_trigram(query_trigram, 'trigram')
