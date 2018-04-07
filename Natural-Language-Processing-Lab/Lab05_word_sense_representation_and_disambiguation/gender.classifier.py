from __future__ import division
import nltk
import random
from nltk.probability import DictionaryProbDist as D


def gender_features(word):
    import string
    features = {char: char in word for char in word.lower()}
    features.update({'count({})'.format(char): word.count(char) for char in word.lower()})
    features.update({'startswith': word[0], 'endswith': word[-1]})
    return features


def LG_gender(train_set, test_set):
    print('== SkLearn MaxEnt ==')
    from nltk.classify import SklearnClassifier
    from sklearn.linear_model import LogisticRegression
    sklearn_classifier = SklearnClassifier(LogisticRegression(C=10e5)).train(train_set)
    print(sklearn_classifier.prob_classify(gender_features('mark'))._prob_dict)
    print(nltk.classify.accuracy(sklearn_classifier, test_set))


def ME_gender(train_set, test_set):
    print('== NLTK MaxEnt ==')
    from nltk.classify import MaxentClassifier
    nltk_classifier = MaxentClassifier.train(train_set, nltk.classify.MaxentClassifier.ALGORITHMS[0])
    print(nltk_classifier.prob_classify(gender_features('mark'))._prob_dict)
    print(nltk.classify.accuracy(nltk_classifier, test_set))


if __name__ == '__main__':
    nltk.download('names')
    names_with_gender = ([(name.lower(), 'male') for name in nltk.corpus.names.words('male.txt')]
                         + [(name.lower(), 'female') for name in nltk.corpus.names.words('female.txt')])
    # print(names_with_gender)
    random.shuffle(names_with_gender)
    featuresets = [(gender_features(name), gender) for name, gender in names_with_gender]
    # print(featuresets)
    split_point = len(featuresets) * 9 // 10
    train_set, test_set = featuresets[:split_point], featuresets[split_point:]
    print(train_set[:2])
    # LG_gender(train_set, test_set)
    ME_gender(train_set, test_set)
