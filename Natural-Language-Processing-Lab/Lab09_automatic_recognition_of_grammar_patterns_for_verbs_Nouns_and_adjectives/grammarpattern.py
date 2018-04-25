#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter, defaultdict
from itertools import groupby, product
import re
import sys

VOC = []

pgPreps = 'about|after|against|among|as|at|between|behind|by|for|from|in|into|of|on|upon|over|through|to|toward|towards|with'.split(
    '|')
pgVerb = ('V _; V n; V ord; V oneself; V adj; V -ing; V to v; V v; V that; V wh; V wh to v; V quote; ' +
          'V so; V not; V as if; V as though; V someway; V together; V as adj; V as to wh; V by amount; ' +
          'V amount; V by -ing; V in favor of; V n in favor of; V n n; V n adj; V n -ing; V n to v; V n v n; V n that; ' +
          'V n wh; V n wh to v; V n quote; V n v-ed; V n someway; V n with together; ' +
          'V n as adj; V n into -ing; V adv; V and v').split('; ')
pgVerb += ['V %s n' % prep for prep in pgPreps] + ['V n %s n' % prep for prep in pgPreps]
pgVerb = pgVerb + [pat.replace('V ', 'V-ed ') for pat in pgVerb]
pgNoun = ('N for n to v; N from n that; N from n to v; N from n for n; N in favor of; N in favour of; ' +
          'N of amount; N of n as n; N of n to n; N of n with n; N on n for n; N on n to v' +
          'N that; N to v; N to n that; N to n to v; N with n for n; N with n that; N with n to v').split('; ')
pgNoun += pgNoun + ['N %s -ing' % prep for prep in pgPreps]
pgNoun += pgNoun + ['ADJ %s n' % prep for prep in pgPreps if prep != 'of'] + ['N %s -ing' % prep for prep in pgPreps]
pgAdj = ('ADJ adj; ADJ and adj; ADJ as to wh; ' +
         'ADJ enough; ADJ enough for n; ADJ enough for n to v; ADJ enough n; ' +
         'ADJ enough n for n; ADJ enough n for n to v; ADJ enough n that; ADJ enough to v; ' +
         'ADJ for n to v; ADJ from n to n; ADJ in color; ADJ -ing; ' +
         'ADJ in n as n; ADJ in n from n; ADJ in n to n; ADJ in n with n; ADJ in n as n; ADJ n for n' +
         'ADJ n to v; ADJ on n for n; ADJ on n to v; ADJ that; ADJ to v; ADJ to n for n; ADJ n for -ing' +
         'ADJ wh; ADJ on n for n; ADJ on n to v; ADJ that; ADJ to v; ADJ to n for n; ADJ n for -ing').split('; ')
pgAdj += ['ADJ %s n' % prep for prep in pgPreps]
pgPatterns = pgVerb + pgAdj + pgNoun


defaultMap = {'NP': 'n', 'VP': 'v', 'JP': 'adj', 'ADJP': 'adj', 'ADVP': 'adv', 'SBAR': 'that', }
selfWords = ['myself', 'ourselves', 'yourself', 'himself', 'herself', 'themselves']
pronOBJ = ['me', 'us', 'you', 'him', 'them']
ordWords = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'nineth', 'tenth']
reversedWords = ['so', 'not', 'though', 'if', 'someway', 'together', 'way', 'favor', 'favour', 'as if', 'as though']
whWords = ['who', 'what', 'when', 'where', 'whether']


def nChunk_to_pat(nChunk):
    # print 'nChunk_to_pat:::', nChunk
    def doubleN(words, lemmas, tags, chunk):
        lemmaList = lemmas.split('_')
        return (len(lemmaList) > 1 and lemmaList[0] in pronOBJ) or (len(lemmaList) > 1 and 'DT' in lemmaList[1:])
    # if nChunk[0][1].split('_')[0] not in VOC:
    #    return ''
    res = []
    for ichunk, chunkInfo in enumerate(nChunk):
        words, lemmas, tags, chunk = chunkInfo
        tagL, lemmaL = tags.split('_'), lemmas.split('_')
        if ichunk == 0 and chunk == 'VP':
            if 'be' in lemmaL and 'VBN' in tagL:
                res += ['V-ed']
            elif tags == 'VBN':
                res += ['V-ed']
            else:
                res += ['V']
        elif ichunk == 0 and chunk == 'NP':
            res += ['N']
        elif ichunk == 0 and chunk in ['JP', 'ADJP']:
            res += ['ADJ']
        elif chunk == 'VP':
            res += ['-ing' if tags == 'VBG' else 'v']
        elif lemmas in reversedWords:
            res += [lemmas]
        elif chunk == 'NP' and tags == 'VBG':
            res += ['-ing']
        elif chunk == 'NP' and lemmas in selfWords:
            res += ['oneself']
        elif chunk == 'NP' and lemmas in whWords:
            res += ['wh', 'n']
        elif chunk == 'NP' and (tags == 'CD'
                                or lemmas[0] in '0123456789.'):
            res += ['amount']
        elif chunk == 'NP' and doubleN(words, lemmas, tags, chunk):
            res += ['n n']
        elif '"' in lemmas:
            res += ['quote']
        elif chunk == 'ADVP' and lemmas in ordWords:
            res += ['ord']
        elif chunk in ['NP', 'ADJP', 'ADVP', 'VP']:
            res += [defaultMap[chunk]]
        elif chunk == 'PP':
            res += [words]
        elif chunk == 'SBAR' and lemmas == 'that':
            res += ['that']
        elif chunk == 'SBAR':
            res += ['_']
        elif chunk == 'O':
            res += ['_']
        else:
            res += [chunk]
    return ' '.join(res)

# global getpatterns


def getpatterns(nPhrase):

    # print 'getpatterns:::', nPhrase

    def to_ngrams(words, length):
        return zip(*([words[i:] for i in range(length)]))

    def chunk_to_lemma(chunk):
        return chunk[1] if '_' not in chunk[1] else chunk[1][chunk[1].rfind('_') + 1:]

    def chunk_to_head(chunk):
        return chunk[1] if '_' not in chunk[1] else chunk[1][chunk[1].rfind('_') + 1:]

    def nChunk_to_words(nChunk):
        return ' '.join([nChunk[0][0], '['] + [chunk[0] for chunk in nChunk[1:-1]] +
                        [']', nChunk[-1][0]])

    def nChunk_to_collocation(nChunk):
        return ' '.join([chunk_to_lemma(chunk) for chunk in nChunk])

    phrases = [nChunk for n in range(3, 9) for nChunk in to_ngrams(nPhrase, n)]
    # print 'getPatterns:::phrases:', phrases
    phrases = [(nChunk, nChunk_to_pat(nChunk[1:-1])) for nChunk in phrases]
    # print 'getPatterns:::phrases:', '\ngetPatterns:::phrases: '.join( str([ nChunk_to_words(nChunk), pat]) for nChunk, pat in phrases )
    phrases = [(nChunk, 'V' if pat == 'V _' else ('V-ed' if pat == 'V-ed _' else pat))
               for nChunk, pat in phrases if pat in pgPatterns]
    # print 'getPatterns:::phrases:', '\ngetPatterns:::phrases: '.join( str([ nChunk_to_words(ph[0]), ph[1]]) for ph in phrases )

    results = []
    for nChunk, pat in phrases:
        head = chunk_to_head(nChunk[1]).lower()  # .decode('utf-8')
        if VOC and head + '-' + nChunk[1][3][0] not in VOC:
            continue
        ngram, collocation = nChunk_to_words(nChunk), nChunk_to_collocation(nChunk[1:-1])
        try:
            results.append((head + '-' + nChunk[1][3][0], pat, collocation, ngram))  # .decode('utf-8')
        except:
            pass
    # [ (head, pat, col, ngram) for head, pat, col, ngram in results if head not in ['be-V', 'me-N', 'do-V' ] ]
    return results if results else [('_', '_', nChunk_to_collocation(nPhrase[1:-1]), '_')]


if __name__ == '__main__':
    for line in sys.stdin:
        line = line.strip().split('\t')
        print(line)
        getpatterns(line)
        #    parse = eval(line.strip())
        #    parse = [ [y.split() for y in x]  for x in parse ]
        #    print(parse[0])
        #    getpatterns(parse[0])
