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


def Mapper():
    sentsNGrams = set()

    for line in sys.stdin:
        sent = tokens(line)
        sentLen = len(sent)

        if sentLen < 10 or sentLen > 25:
            continue

        for n in range(2, 6):
            for ngram in ngrams(sent, n):
                sentsNGrams.add(ngram)

        for ngram in sentsNGrams:
            terms = ngram.split()
            start = terms[0]
            end = terms[-1]
            n = len(terms)

            if isCollocation(start, end, n - 1):
                print('%s %s %s\t%s' % (start, end, str(n - 1), line))
            if isCollocation(end, start, 1 - n):
                print('%s %s %s\t%s' % (end, start, str(1 - n), line))

        sentsNGrams.clear()


Mapper()
