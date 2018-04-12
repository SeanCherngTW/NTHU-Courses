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
                print('%s %s %d\t%s' % (start, end, n - 1, line))
            if isCollocation(end, start, 1 - n):
                print('%s %s %d\t%s' % (end, start, 1 - n, line))

        sentsNGrams.clear()


def Mapper_testing():
    print('---------- MAPPER START ----------')
    counter = 0
    sentsNGrams = set()
    mapperOutput = []

    for line in open('bnc.sents.txt'):
        sent = tokens(line)
        sentLen = len(sent)

        counter += 1
        if counter % 20000 == 0:
            print('MAPPER: Processing sentences ... %3d%%' % (counter / 2000))

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
                mapperOutput.append('%s %s %d\t%s' % (start, end, n - 1, line))
            if isCollocation(end, start, 1 - n):
                mapperOutput.append('%s %s %d\t%s' % (end, start, 1 - n, line))

        sentsNGrams.clear()

    print('MAPPER: Output length = %d' % len(mapperOutput))
    print('---------- MAPPER END ----------')

    return sorted(mapperOutput)


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
            try:
                ngm, sent = l.split('\t')
                word, col, dist = ngm.split()
                score = computeScore(word, sent)
                if score > max_score:
                    max_line = l
                    max_score = score
            except:
                pass

        ngm, sent = max_line.split('\t')
        word, col, dist = ngm.split()
        print('%s %s %s\t%s' % (word, col, dist, sent))

        prev_key = current_key
        lineList.clear()
        lineList.append(line)

    if lineList:
        max_score = -999
        max_line = ''
        for l in lineList:
            try:
                ngm, sent = l.split('\t')
                word, col, dist = ngm.split()
                score = computeScore(word, sent)
                if score > max_score:
                    max_line = l
                    max_score = score
            except:
                pass

        ngm, sent = max_line.split('\t')
        word, col, dist = ngm.split()
        print('%s %s %s\t%s' % (word, col, dist, sent))


def Reducer_testing(mapperOutput):
    print('---------- REDUCER START ----------')

    lineList = []
    reducerOutput = []
    prev_key = ''
    isFirst = True
    counter = 0
    mapperOutputCount = len(mapperOutput)

    print('REDUCER: Start processing the best sentence (data size = %d)' % mapperOutputCount)

    for line in mapperOutput:

        counter += 1
        if counter % (mapperOutputCount / 100) == 0:
            print('REDUCER: Processing the best sentence ... %3d%%' % (counter * 100 / mapperOutputCount))

#         print('prev_key = %s' % prev_key)
#         print('curr_key = %s' % line.split('\t')[0])
#         print(lineList)
#         print('--------')

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
            word, col, dist = ngm.split()
            score = computeScore(word, sent)
#             print(score, max_score, l)
            if score > max_score:
                max_line = l
                max_score = score

        ngm, sent = max_line.split('\t')
        word, col, dist = ngm.split()
#         print('BEST SENT:')
#         print('%s %s %s\t%s' % (word, col, dist, sent))
#         print()
        reducerOutput.append('%s %s %s\t%s' % (word, col, dist, sent))

        prev_key = current_key
        lineList.clear()
        lineList.append(line)

    if lineList:
        max_score = -999
        max_line = ''
        for l in lineList:
            try:
                ngm, sent = l.split('\t')
                word, col, dist = ngm.split()
                score = computeScore(word, sent)
                if score > max_score:
                    max_line = l
                    max_score = score
            except:
                pass
        ngm, sent = max_line.split('\t')
        word, col, dist = ngm.split()
#         print('%s %s %s\t%s' % (word, col, dist, sent))
        reducerOutput.append('%s %s %s\t%s' % (word, col, dist, sent))

    print('---------- REDUCER END ----------')

    return reducerOutput


def computeScore(word, sent):
    global PRONS
    global HiFreWords

    sent = sent.lower().split()

    locationOfWord = -1 if word not in sent else sent.index(word)
    hiFreWordsScore = len([w for w in sent if w not in HiFreWords])
    pronsScore = len([w for w in sent if w in PRONS])

    return locationOfWord - hiFreWordsScore - pronsScore


get_ipython().run_cell_magic('time', '', 'reducerOutput = Reducer_testing(Mapper_testing())')
with open('output.txt', 'w') as outputFile:
    for output in reducerOutput:
        outputFile.write(output)
Mapper()
Reducer()
