# coding: utf-8
import re
import sys
from pprint import pprint
from collections import defaultdict, Counter


def read_collocation():
    collocation = set()
    for line in open('bnc.coll.small.txt'):
        start, end, distance, count = line.split('\t')
        collocation.add(start + ' ' + end + ' ' + distance)
    return collocation


collocation = read_collocation()
PRONS = set([line.strip('\n') for line in open('prons.txt')])
with open('HiFreWords') as f:
    HiFreWords = set(f.readline().split('\t'))
print(len(collocation), len(PRONS), len(HiFreWords))


def tokens(str1):
    return re.findall('[a-z]+', str1.lower())


def ngrams(sent, n):
    return [' '.join(x) for x in zip(*[sent[i:] for i in range(n) if i <= len(sent)])]


def isCollocation(start, end, d):
    global collocation
    if start + ' ' + end + ' ' + str(d) in collocation:
        return True
    else:
        return False


def Reducer():
    lineList = []
    prev_key = ''
    isFirst = True

    for line in sys.stdin:

        if not isFirst:
            current_key = line.split('\t')[0]
            if line.split('\t')[0] == prev_key:
                lineList.append(line)
                prev_key = current_key
                isFirst = False
                continue
        else:
            isFirst = False
            prev_key = line.split('\t')[0]
            lineList.append(line)
            continue

        # All sentences in one group are read
        max_score = -999
        max_line = ''
        for l in lineList:
            ngm, sent = l.split('\t')
            word, col, dist = ngm.split(' ')
            score = computeScore(word, sent)
            if score > max_score:
                max_line = l
                max_score = score

        ngm, sent = max_line.split('\t')
        word, col, dist = ngm.split(' ')
        print('%s %s %s\t%s' % (word, col, dist, sent))

        prev_key = current_key
        lineList.clear()
        lineList.append(line)

    if lineList:
        max_score = -999
        max_line = ''
        for l in lineList:
            ngm, sent = l.split('\t')
            word, col, dist = ngm.split(' ')
            score = computeScore(word, sent)
            if score > max_score:
                max_line = l
                max_score = score

        ngm, sent = max_line.split('\t')
        word, col, dist = ngm.split(' ')
        print('%s %s %s\t%s' % (word, col, dist, sent))


def computeScore(word, sent):
    global PRONS
    global HiFreWords

    sent = sent.lower().split()

    locationOfWord = -1 if word not in sent else sent.index(word)
    hiFreWordsScore = len([w for w in sent if w not in HiFreWords])
    pronsScore = len([w for w in sent if w in PRONS])

    return locationOfWord - hiFreWordsScore - pronsScore


Reducer()
