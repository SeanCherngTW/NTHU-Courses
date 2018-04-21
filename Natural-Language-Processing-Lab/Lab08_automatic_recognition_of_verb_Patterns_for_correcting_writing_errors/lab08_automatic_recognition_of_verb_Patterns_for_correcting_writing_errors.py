# coding: utf-8
import operator
from pprint import pprint
from collections import defaultdict


def create_sentence_pattern_list(input_pat):
    pattern = []
    final = []
    for i in input_pat:
        if i != '':
            pattern.append(i)
        else:
            final.append(pattern.copy())
            pattern.clear()

    # Last one
    final.append(pattern)
    return final


# Training data
correct_pat = open('correct_pattern.txt', 'r').read().strip('\n').split('\n')
correct_pat = create_sentence_pattern_list(correct_pat)
wrong_pat = open('wrong_pattern.txt', 'r').read().strip('\n').split('\n')
wrong_pat = create_sentence_pattern_list(wrong_pat)

# Testing data
test_pat = open('test_pattern.txt', 'r').read().strip('\n').split('\n')
test_pat = create_sentence_pattern_list(test_pat)

# Label of testing data
test_label = []
for line in open('ef_test.ref.txt', 'r'):
    sent, verb, pattern = line.strip('\n').split('\t')
    test_label.append('%s, %s' % (verb[1:-1], pattern))


def pattern_pos(sent1, sent2):
    lst = sent1.split()
    sublst = sent2.split()
    if len(lst) < len(sublst):
        lst, sublst = sublst, lst
    count = 0
    n = len(sublst)
    for i in range(len(lst)):
        for j in range(n):
            if lst[i] == sublst[j]:
                count += 1
            if count == n:
                return i - n + 1
    return -10


def build_noisy_channel():
    noisy_channel = defaultdict(lambda: defaultdict(int))
    for objectW, objectC in zip(wrong_pat, correct_pat):
        sentW, sentC = objectW[0], objectC[0]

        for c in objectC[1:]:
            verbC, grammarC, patternC = c.split('\t')

            for w in objectW[1:]:
                verbW, grammarW, patternW = w.split('\t')

                # Same word but different grammar pattern -> Add to the nosiy channel
                # Consider 2 words as the same word if their position index difference < 3
                if verbC == verbW:
                    if grammarC != grammarW and abs(pattern_pos(sentC, patternC) - pattern_pos(sentW, patternW)) < 3:
                        noisy_channel[grammarW]['COUNT'] += 1
                        noisy_channel[grammarW][grammarC] += 1
                        break

    return noisy_channel


noisy_channel = build_noisy_channel()


def build_lexical_language_model():
    language_model = defaultdict(lambda: defaultdict(int))
    for objectW, objectC in zip(wrong_pat, correct_pat):
        sentW, sentC = objectW[0], objectC[0]

        for c in objectC[1:]:
            verbC, grammarC, patternC = c.split('\t')

            for w in objectW[1:]:
                verbW, grammarW, patternW = w.split('\t')
                # Same word but different grammar pattern -> Add to the nosiy channel
                if verbC == verbW:
                    if grammarC != grammarW and abs(pattern_pos(sentC, patternC) - pattern_pos(sentW, patternW)) < 3:
                        language_model['%s, %s' % (verbC, grammarW)][grammarC] += 1
                        language_model['%s, %s' % (verbC, grammarC)][grammarC] += 1
                        language_model[verbC]['EXIST'] = 1
                        break

    return language_model


language_model = build_lexical_language_model()


def Pedit(verb, w):
    candidates = {}
    key = '%s, %s' % (verb, w)
    language_model_smooth = sum(language_model[key].values()) + len(language_model[key].values())
    if key in language_model:
        for candidate, count in language_model[key].items():
            language_model_prob = (count + 1) / language_model_smooth

            noisy_channel_smooth = len(noisy_channel[w]) + noisy_channel[w]['COUNT']
            noisy_channel_prob = (noisy_channel[w][candidate] + 1) / noisy_channel_smooth

            candidate_prob = language_model_prob * noisy_channel_prob
            candidates[candidate] = candidate_prob

        best_candidate, prob = max(candidates.items(), key=operator.itemgetter(1))
        return best_candidate, prob
    else:
        return key


def correction():
    hit = 0
    index = 0
    for objectT, labelT in zip(test_pat, test_label):
        index += 1
        sentT = objectT[0]
        verbL, grammarL = labelT.split(',')
        grammarL = grammarL.split('->')[0][2:-1]

        for t in objectT[1:]:
            verbT, grammarT, patternT = t.split('\t')

            if verbT != verbL:
                continue

            if verbT in language_model and grammarT == grammarL:
                best_candidate, prob = Pedit(verbT, grammarT)
                prediction = '%s, (%s -> %s)' % (verbT, grammarT, best_candidate)

                if labelT == prediction:
                    hit += 1
                    print('%d Correct' % index)
                else:
                    print('%d Wrong' % index)

                print('Label: %s' % labelT)
                print('Pred : %s' % prediction)
                print('Prob : %.4f\n' % prob)

    total = len(test_label)
    print('hit = %d, total = %d, accuracy = %f' % (hit, total, hit / total))


correction()
