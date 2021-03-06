from svm.rank import SVMRank
from dataLoader import DataLoader
import constants as C
import factoid_letor_features
import numpy as np
import json
from sklearn.metrics import classification_report
from tqdm import tqdm

from nltk.tokenize import RegexpTokenizer

from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

def overlap_score(entity1, entity2):
    if entity1 == '':
        return 0.0

    words1 = entity1.split(' ')
    words2 = entity2.split(' ')
    size1 = float(len(set(words1)))
    size2 = float(len(set(words2)))

    if size1 * size2 == 0:
        return 0.0

    overlap = float(len(set(words1).intersection(set(words2))))
    return (overlap * overlap) / (size1 * size2)

def get_scores(res):

    prediction = []
    ground_truth = []
    for r in res:
        pred, ground = r
        prediction.append(pred)
        ground_truth.append(ground)

    return classification_report(prediction, prediction)


def gold_candidate_rank(candidates, gold_answers):
    scores = []
    candidates = [candidate[C.ENTITY] for candidate in candidates]
    for candidate in candidates:
        score = np.array([overlap_score(candidate, answer) for answer in gold_answers]).max()
        scores.append((score, candidate))
    ranks = {}
    scores = sorted(scores, reverse=True)
    for rank, (score, candidate) in enumerate(scores):
        ranks[candidate] = rank
    return [ranks[candidate] for candidate in candidates]

def get_features(question, ranked_sentences):
    candidates = question.snippet_ner_entities
    X = np.array([factoid_letor_features.all_features(question.question, ranked_sentences, candidate) for candidate in candidates])
    y = gold_candidate_rank(candidates, question.exact_answer_ref)
    return X.tolist(), candidates

def get_only_features(question, ranked_sentences):
    candidates = question.snippet_ner_entities
    # candidates = [{
    #     C.ENTITY: candidate,
    #     C.TYPE: '',
    #     C.SOURCE: '',
    # } for candidate in candidates]
    X = np.array([factoid_letor_features.all_features(question.question, ranked_sentences, candidate) for candidate in candidates])
    candidates = [candidate[C.ENTITY] for candidate in candidates]
    return X.tolist(), candidates

def finder_n(words, w_dict):
    words = [a for a in words if a not in stop_words]
    size = len(words)
    for k in range(1, 5):
        for i in range(size):
            w_dict[' '.join(words[i:i+k])] += 1
    return []

def get_top_entities(sentences):
    w_dict = dd(int)
    tokenizer = RegexpTokenizer(r'\w+')
    for sentence in sentences:
        finder_n(tokenizer.tokenize(sentence.lower()), w_dict)
    n_relevant = [(k,v) for k,v in dict(w_dict).iteritems()]
    n_relevant.sort(key=lambda x: x[1], reverse=True)
    return n_relevant

def main():
    file_name = 'input/BioASQ-task6bPhaseB-testset3.json'
    file_name = 'input/BioASQ-trainingDataset6b.json'
    file_name = 'input/BioASQ-trainingDataset5b.json'
    file_name = 'input/phaseB_5b_05.json'
    save_model_file_name = 'weights_2'
    ranker = SVMRank(save_model_file_name)
    data = DataLoader(file_name)
    data.load_ner_entities()
    ans_file = 'output/factoid_list_%s.json' % data.name

    questions = data.get_questions_of_type(C.FACTOID_TYPE)
    for i, question in enumerate(tqdm(questions)):
        ranked_sentences = question.ranked_sentences()
        X, candidates = get_only_features(question, ranked_sentences)
        top_answers = ranker.classify_from_feed(X, candidates, i)
        question.exact_answer = [[answer] for answer in top_answers[:5]]
        # question.exact_answer = [answer for answer in top_answers]
        # print question.exact_answer_ref
        # print '\n'
        # print top5
        # print '\n'
        # print '\n\n\n'
    questions = data.get_questions_of_type(C.LIST_TYPE)
    for i, question in enumerate(tqdm(questions)):
        ranked_sentences = question.ranked_sentences()
        X, candidates = get_only_features(question, ranked_sentences)
        top_answers = ranker.classify_from_feed(X, candidates, i)
        question.exact_answer = [[answer] for answer in top_answers[:10]]

    data.save_factoid_list_answers(ans_file)
    # data.eval_factoid()

if __name__ == '__main__':
    main()