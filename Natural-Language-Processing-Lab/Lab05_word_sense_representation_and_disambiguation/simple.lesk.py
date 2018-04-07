# from nltk.corpus import wordnet as wn
import re
from collections import defaultdict, Counter
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
import random

lmtzr = WordNetLemmatizer()


def words(text):
    return re.findall(r'\w+', text.lower())


TF = defaultdict(lambda: defaultdict(lambda: 0))
DF = defaultdict(lambda: [])


def wnTag(pos):
    return {'noun': 'n', 'verb': 'v', 'adjective': 'a', 'adverb': 'r'}[pos]


def trainLesk():
    training = [line.strip().split('\t') for line in open('wn.in.evp.cat.txt', 'r') if line.strip() != '']

    def isHead(head, word, tag):
        try:
            return lmtzr.lemmatize(word, tag) == head
        except:
            return False

    # zucchini-n-2	vegetable.n.01	zucchini courgette||small cucumber-shaped vegetable marrow; typically dark green||
    # {'zucchini-n-1': 'vine.n.01', 'zucchini-n-2': 'vegetable.n.01'}
    for wnid, wncat, senseDef, target in training:
        # head = word, pos = postag
        head, pos = wnid.split('-')[:2]
        # split senseDef into words
        for word in words(senseDef):
            # We only need to update TF & DF once for each word which represents the features of each word
            if word != head and not isHead(head, word, pos):
                TF[word][wncat] += 1
                DF[word] += [] if wncat in DF[word] else [wncat]


def testLesk():
    testdata = [line.strip().split('\t') for line in open('evp.in.wn.cat.txt', 'r') if line.strip() != '']

    def df(word):
        return len(DF[word])

    def leskOverlap(senseDef, target):
        wnidCount = [(wncat, tf, word, len(DF[word]) + 1) for word in senseDef
                     for wncat, tf in TF[word].items()
                     if wncat in target.values()]
        res = sorted([(wnid, tf * int(1000 / df)) for wnid, tf, word, df in wnidCount], key=lambda x: -x[1])[:7]
        if not res:
            return 'Not found'
        counter = Counter()
        for wnid, tfidf in res:
            counter[wnid] += tfidf
        return counter.most_common(1)[0]

    for evpid, wncat, senseDef, target in testdata:
        # head, pos = evpid.split('-')[:2]
        print('%s\t%s\t%s' % (evpid, leskOverlap(words(senseDef), eval(target)), senseDef.split('||')[0]))


if __name__ == '__main__':
    trainLesk()
    testLesk()
