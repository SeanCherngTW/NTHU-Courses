# coding: utf-8
from collections import defaultdict, Counter
from operator import itemgetter
from pprint import pprint
from akl import akl
import operator
import math


def read_ngrams():
    nGrams = defaultdict(int)
    for line in open('citeseerx.ngms', 'r'):
        ngram, count = line.split('\t')
        count = int(count)
        nGrams[ngram] += count

    return nGrams


nGrams = read_ngrams()
print(nGrams['play-v a-det role-n'])
print(nGrams['play-v a-det important-adj role-n'])


def generate_skip_bigrams(nGrams):
    """
    input  nGrams     : (nGram, count)
    output skipBigrams: (skipBigram, position, count)
    """
    skipBigrams = defaultdict(lambda: defaultdict(int))

    for nGram, count in nGrams.items():
        terms = nGram.split()

        start = terms[0]
        end = terms[-1]
        n = len(terms)

        key1 = '%s %s' % (start, end)
        key2 = '%s %s' % (end, start)

        skipBigrams[key1][n - 1] += count
        skipBigrams[key2][-n + 1] += count

    return skipBigrams


skipBigrams = generate_skip_bigrams(nGrams)


def generate_distance_counts(skipBigrams):
    dcSkipBigrams = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for nGram, distanceCounts in skipBigrams.items():
        terms = nGram.split()
        start = terms[0]
        end = terms[1]
        for distance, count in distanceCounts.items():
            dcSkipBigrams[start][end][distance] += count

    return dcSkipBigrams


dcSkipBigrams = generate_distance_counts(skipBigrams)


def collocation_extraction(word):
    global nGrams
    global dcSkipBigrams

    C1 = defaultdict(lambda: defaultdict(int))
    final_skipBigrams = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    final_nGrams = []

    sum_freqi = 0
    N = len(dcSkipBigrams[word].keys())
    targetItem = dcSkipBigrams[word].items()
    for end, distanceCounts in targetItem:
        freqi = sum(distanceCounts.values())
        sum_freqi += freqi

    avg_freq = sum_freqi / N
    std_freq = 10e-6

    # Calculate standard deviation
    for end, distanceCounts in targetItem:
        freqi = sum(distanceCounts.values())
        std_freq += math.sqrt((freqi - avg_freq) ** 2) / N

    strength = 0.0

    # Condition 1
    for end, distanceCounts in targetItem:
        freqi = sum(distanceCounts.values())
        strength = (freqi - avg_freq) / std_freq
        if strength > 1:
            C1[end] = distanceCounts

    # Condition 2, 3
    for end, distanceCounts in C1.items():
        avg_pi = sum(distanceCounts.values()) / 10
        Vi = 0.0

        # Condition 2
        for distance, count in distanceCounts.items():
            Vi += math.sqrt((count - avg_pi) ** 2) / 10

        if Vi <= 10:
            continue

        # Condition 3
        best_distance = 0
        best_count = 0
        for distance, count in distanceCounts.items():
            threshold = avg_pi + math.sqrt(Vi)
            if count > threshold:
                if count > best_count:
                    best_distance, best_count = distance, count

        final_skipBigrams[(end, best_distance)] = best_count

    # Sort in count
    final_skipBigrams = sorted(final_skipBigrams.items(), key=operator.itemgetter(1), reverse=True)

    # Get correponding nGram through skipBigrams
    for distance, count in final_skipBigrams:
        filter_nGrams = defaultdict(lambda: defaultdict(int))
        collocation, length = distance
        for k, v in nGrams.items():
            terms = k.split()
            start = terms[0]
            end = terms[-1]

            if length > 0:
                if start == word and end == collocation and len(terms) == length + 1:
                    filter_nGrams[k] = v
            else:
                if start == collocation and end == word and len(terms) == 1 - length:
                    filter_nGrams[k] = v

        final_nGrams.append(sorted(filter_nGrams.items(), key=operator.itemgetter(1), reverse=True)[0])

    return final_skipBigrams, final_nGrams


def main(word):
    final_skipBigrams, final_nGrams = collocation_extraction(word)
    print('Skip-Bigrams', 'Ngrams')
    for a, b in zip(final_skipBigrams, final_nGrams):
        print(a, b)


main('role-n')
