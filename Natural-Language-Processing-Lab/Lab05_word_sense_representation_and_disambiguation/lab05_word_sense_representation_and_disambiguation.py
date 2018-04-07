# coding: utf-8
from __future__ import division
import nltk
import random
import re
import string
import operator
import time
from pprint import pprint
from collections import defaultdict, Counter
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.probability import DictionaryProbDist as D
from nltk.classify import SklearnClassifier
from sklearn.linear_model import LogisticRegression
with open('stopwords.txt', 'r') as f:
    stopwords = [line.strip() for line in f]
lmtzr = WordNetLemmatizer()


def words(text):
    return re.findall(r'\w+', text.lower())


wordnet_data = [line.strip().split('\t') for line in open('wn.in.evp.cat.txt', 'r') if line.strip() != '']


def split_train_test(data):
    random.shuffle(data)
    split_point = len(data) * 9 // 10
    train_set, test_set = data[:split_point], data[split_point:]
    return train_set, test_set


train_set, test_set = split_train_test(wordnet_data)


def wordnet_features(sentence):
    sentence = sentence.replace('||', ' ').replace('; ', ' ')
    features = {}
    for word in sentence.lower().split():
        if word not in stopwords:
            if word not in features:
                features[word] = 1
            else:
                features[word] += 1
    return features


def feature_engineering(train_set):
    org_word = []
    label = []
    features = []
    candidates = []
    for train in train_set:
        c = []
        org_word += [''.join(train[:][0])]
        label += [''.join(train[:][1])]
        features += [wordnet_features(''.join(train[:][2]))]
        for candidate in eval(train[:][3]).values():
            c += [candidate]
        candidates += [c]
    return org_word, label, features, candidates


train_org_word, train_label, train_features, train_candidates = feature_engineering(train_set)
test_org_word, test_label, test_features, test_candidates = feature_engineering(test_set)


def sk_training_all(train_features, train_label, test_features, test_label, test_candidates):
    print('== SkLearn MaxEnt ==')
    final_result = []
    train_set = []
    test_set = []
    correct = 0
    total = 0
    for X, y in zip(train_features, train_label):
        train_set.append((X, y))

    for X, y in zip(test_features, test_label):
        test_set.append((X, y))

    sklearn_classifier = SklearnClassifier(LogisticRegression(C=10e5)).train(train_set)

    for feature, candidate in zip(test_features, test_candidates):
        prediction = sklearn_classifier.prob_classify(wordnet_features(''.join(feature)))._prob_dict
        sorted_pred = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        for label, prob in sorted_pred:
            if label in candidate:
                final_result.append(label)
                has_ans = True
                break
        if not has_ans:
            final_result.append(sorted_pred[0][0])
        has_ans = False
        total += 1

    for i in range(len(final_result)):
        if test_label[i] == final_result[i]:
            correct += 1

    print('correct = %d, total = %d' % (correct, total))
    print(nltk.classify.accuracy(sklearn_classifier, test_set))

    return final_result


final_r_all = sk_training_all(train_features, train_label, test_features, test_label, test_candidates)

"""
== SkLearn MaxEnt ==
correct = 825, total = 2320
0.49267241379310345
"""
