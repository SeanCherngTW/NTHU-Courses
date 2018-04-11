# coding: utf-8
def sk_training_all(train_features, train_label, test_features, test_label, test_candidates):
    global sklearn_classifier_all
    print('== SkLearn MaxEnt ==')
    output_candidates = []
    test_set = []
    correct = 0
    N = len(test_label)
    
    for X, y in zip(test_features, test_label):
        test_set.append((X, y))
        
    for i in range(N):
        output_candidates.clear()
        
        feature = test_features[i]
        candidate = test_candidates[i]
        label = test_label[i]
        
        prediction = sklearn_classifier_all.prob_classify(feature)._prob_dict
        sorted_pred = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        
        for result, prob in sorted_pred:
            if result in candidate:
                output_candidates.append((result, prob))
                
        if not output_candidates: 
            continue
            
        top_output_candidate = sorted(output_candidates, key=lambda x: x[1], reverse=True)[0][0]
        
        if top_output_candidate == label:
            correct += 1

    print('hand acc = %.4f' % (correct / N))
    print('nltk acc = %.4f' % nltk.classify.accuracy(sklearn_classifier_all, test_set))
get_ipython().run_cell_magic('time', '', 'train_set = []\nfor X, y in zip(train_features, train_label):\n    train_set.append((X, y))\n    \nsklearn_classifier_all = SklearnClassifier(LogisticRegression(C=10e5)).train(train_set)')
sk_training_all(train_features, train_label, test_features, test_label, test_candidates)
