# coding: utf-8
import math
import operator
from pprint import pprint
from orderedset import OrderedSet
from collections import defaultdict, OrderedDict
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


# English
english_corpus = open('corpus.txt', 'r').read().strip('\n').split('\n')
english_corpus = create_sentence_pattern_list(english_corpus)
for ec, es in zip(english_corpus, english_sent):
    ec[0] = es

# English correct sentences
english_sent = open('UM-Corpus.en.200k.txt', 'r').read().split('\n')

# Chinese
chinese_corpus = open('UM-Corpus.ch.200k.tagged.txt', 'r').read().split('\n')

# Align
aligns = open('align.final.200k', 'r').read().split('\n')


def pattern_pos(sent1, sent2):
    if not isinstance(sent1, list):
        sent1 = sent1.split()

    if not isinstance(sent2, list):
        sent2 = sent2.split()

    if len(sent1) < len(sent2):
        sent1, sent2 = sent2, sent1

    # sent1 is the whole sentence
    # sent2 is the sub sentence

    count = 0
    n = len(sent2)
    for i in range(len(sent1)):
        count = 0
        for j in range(n):
            if sent1[i] == sent2[j]:
                count += 1
                i += 1
                if count == n:
                    return (i - n, i)
            else:
                i -= count
                break
    return (-1, -1)


def compute_score(word, sent):
    global PRONS
    global HiFreWords

    word = word.lower()
    sent = sent.lower().split()
    length = len(sent)

    locationOfWord = -1 if word not in sent else sent.index(word)
    hiFreWordsScore = len([w for w in sent if w not in HiFreWords])
    pronsScore = len([w for w in sent if w in PRONS])

    return locationOfWord - hiFreWordsScore - pronsScore


def extract_ch_grammar(ch_pat):
    ch_grammar = []

    # "莊稼_N 了_ASP 收割_V 莊稼_N" -> ['N', 'ASP', 'V', 'N']
    for cg in ch_pat.split():
        if not ch_grammar:
            ch_grammar.append(cg)
        else:
            if cg != ch_grammar[-1]:
                ch_grammar.append(cg)

    ch_grammar = [cg.split('_')[1] for cg in ch_grammar if '_' in cg]
    ch_grammar = [cg for cg in ch_grammar if cg == 'V' or cg == 'P' or cg == 'N']

    if ch_grammar == ['V', 'V']:
        ch_grammar = 'V v'
    else:
        ch_grammar = OrderedSet(ch_grammar)
        ch_grammar = ' '.join(ch_grammar).lower().replace('v', 'V')

    return ch_grammar


def extract_pattern():
    count = 0
    noisy_channel = defaultdict(lambda: defaultdict(list))
    for english, chinese, align in zip(english_corpus, chinese_corpus, aligns):
        count += 1
        en_sent = english[0].split()
        ch_sent = chinese.split()
        align = align.split()
        en_ch = OrderedDict()
        index = 0

        try:
            for a in align:
                en_pos, ch_pos = a.split('-')
                en_pos = int(en_pos)
                ch_pos = int(ch_pos)
                en = en_sent[en_pos]
                ch = ch_sent[ch_pos]
                en_ch[index, en_pos, en] = ch
                index += 1

            for _ in english[1:]:
                _, en_grammar, en_pat = _.split('\t')
                start, end = pattern_pos(en_sent, en_pat)
                ch_pat = ""
                for en, ch_term in en_ch.items():
                    _, en_pos, en_term = en
                    if en_pos >= start and en_pos < end:
                        ch_pat += "%s " % ch_term
                    elif en_pos >= end:
                        break
                if 'V' in ch_pat:
                    ch_grammar = extract_ch_grammar(ch_pat)
                    noisy_channel_pattern = "%s | %s" % (en_pat, ch_pat)
                    noisy_channel[en_grammar][ch_grammar].append(noisy_channel_pattern)

        except Exception as e:
            print("line %d: %s" % (count, str(e)))
    return noisy_channel


noisy_channel = extract_pattern()


def get_pattern(input_pat):
    _sum = 0
    stddev = 0.0
    k0 = 0.001

    N = len(noisy_channel[input_pat])
    if N == 0:
        return "NO RESULT"

    for k, v in noisy_channel[input_pat].items():
        _sum += len(v)
    avg = _sum / N

    print("%s (%d)" % (input_pat, _sum))

    for k, v in noisy_channel[input_pat].items():
        stddev += (len(v) - avg) ** 2
    stddev = math.sqrt(stddev / N - 1)

    final_result = {}

    # Filter good grammar
    for grammar, sentences in noisy_channel[input_pat].items():
        best_sentences = [(-999.9, ''), (-999.9, ''), (-999.9, '')]
        freqi = len(sentences)
        strength = (freqi - avg) / stddev
        if not strength > k0:
            continue

        # Find Good Dictionary Example
        for sentence in sentences:
            score = compute_score(input_pat, sentence)
            if score > best_sentences[0][0]:
                best_sentences.pop(0)
                best_sentences.append((score, sentence))
                best_sentences.sort()

        final_result[(grammar, freqi)] = best_sentences

    # Print the result
    for key in sorted(final_result, key=lambda x: x[1], reverse=True):
        values = final_result[key]
        print('-> %s (%d)' % (key[0], key[1]))
        for value in values:
            en, ch = value[1].split(" | ")
            print('     %s %s' % (en, ch))


get_pattern('V n')
