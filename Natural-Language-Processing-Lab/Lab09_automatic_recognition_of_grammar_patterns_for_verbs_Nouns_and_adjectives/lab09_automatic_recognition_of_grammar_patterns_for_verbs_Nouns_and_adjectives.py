# coding: utf-8
import akl
import math
import operator
from pprint import pprint
from collections import defaultdict
akl = list(akl.akl.keys())
PRONS = set([line.strip('\n') for line in open('prons.txt')])
with open('HiFreWords') as f:
    HiFreWords = set(f.readline().split('\t'))


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


# Corpus
corpus = open('corpus_all.txt', 'r').read().strip('\n').split('\n')
corpus = create_sentence_pattern_list(corpus)


def build_pattern_dict():
    pattern_dict = defaultdict(lambda: defaultdict(list))
    example_sentences = defaultdict(lambda: defaultdict(list))
    for _object in corpus:
        sent = _object[0]
        for c in _object[1:]:
            term, grammar, pattern = c.split('\t')
            pattern_dict[term][grammar] += [pattern]
            example_sentences[term][grammar] += [sent.split()]

    return pattern_dict, example_sentences


pattern_dict, example_sentences = build_pattern_dict()


def check_pattern_dict():
    print('ABILITY -N')
    print('N to v \t\t(pd:%d, label:468)\n' % len(pattern_dict['ABILITY']['N to v']))

    print('VALUE -N')
    print('N to v \t\t(pd:%3d, label: 16)\n' % len(pattern_dict['VALUE']['N to v']))

    print('DISCUSS -V')
    print('V in n \t\t(pd:%3d, label: 47)' % len(pattern_dict['DISCUSS']['V in n']))
    print('V n \t\t(pd:%3d, label:270)' % len(pattern_dict['DISCUSS']['V n']))
    print('V wh to v \t(pd:%3d, label: 15)\n' % len(pattern_dict['DISCUSS']['V wh to v']))

    print('FAVOUR -V')
    print('V n \t\t(pd:%3d, label: 26)' % len(pattern_dict['FAVOUR']['V n']))
    print('V by n \t\t(pd:%3d, label:  5)\n' % len(pattern_dict['FAVOUR']['V by n']))

    print('CLASSIFY -V')
    print('V into n \t(pd:%3d, label:  8)' % len(pattern_dict['CLASSIFY']['V into n']))
    print('V as n \t\t(pd:%3d, label: 12)\n' % len(pattern_dict['CLASSIFY']['V as n']))

    print('USEFUL -ADJ')
    print('ADJ to v \t(pd:%3d, label: 30)' % len(pattern_dict['USEFUL']['ADJ to v']))
    print('ADJ for n \t(pd:%3d, label: 20)\n' % len(pattern_dict['USEFUL']['ADJ for n']))

    print('CERTAIN -ADJ')
    print('ADJ of n \t(pd:%3d, label: 23)' % len(pattern_dict['CERTAIN']['ADJ of n']))


check_pattern_dict()


def computeScore(word, sent):
    global PRONS
    global HiFreWords

    word = word.lower()
    sent = sent.lower().split()
    length = len(sent)

    locationOfWord = -1 if word not in sent else sent.index(word)
    hiFreWordsScore = len([w for w in sent if w not in HiFreWords])
    pronsScore = len([w for w in sent if w in PRONS])

    return locationOfWord - hiFreWordsScore - pronsScore


def get_best_pattern(word):
    avg = 0.0
    stddev = 0.0
    k0 = 1

    word = word.upper()

    print(word)

    # Total grammar count for the input word
    N = len(pattern_dict[word].keys())

    if N == 0:
        print('NO RESULT\n')
        return

    # Calculate sentence length avg of a grammar
    for grammar, sentences in pattern_dict[word].items():
        freqi = len(sentences)
        avg += freqi
    avg /= N

    # Calculate stddev
    for grammar, sentences in pattern_dict[word].items():
        freqi = len(sentences)
        stddev += (freqi - avg) ** 2
    stddev = math.sqrt(stddev / N - 1)

    if stddev == 0:
        print('NO RESULT\n')
        return

    best_score = -999.9
    best_sentence = ''

    # Filter good grammar
    for grammar, sentences in pattern_dict[word].items():
        freqi = len(sentences)
        strength = (freqi - avg) / stddev
        if not strength > k0:
            continue

        # Find Good Dictionary Example
        for sentence in sentences:
            score = computeScore(word, sentence)
            if score > best_score:
                best_score = score
                best_sentence = sentence

        print('%s (%d) %s' % (grammar, freqi, best_sentence))
    print()


def test_case():
    get_best_pattern('ability')
    get_best_pattern('value')
    get_best_pattern('discuss')
    get_best_pattern('favour')
    get_best_pattern('classify')
    get_best_pattern('useful')
    get_best_pattern('certain')


test_case()
