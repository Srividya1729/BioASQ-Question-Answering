from svm.rank import SVMRank
from dataLoader import DataLoader
import constants as C
import factoid_letor_features
import numpy as np
import json

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

def gold_candidate_rank(candidates, gold_answers):
    scores = []
    candidates = [candidate[C.ENTITY] for candidate in candidates]
    for candidate in candidates:
        score = np.array([overlap_score(candidate, answer) for answer in gold_answers]).max()
        scores.append((score, candidate))
    ranks = {}
    scores = sorted(scores, reverse=True)
    for rank, (score, candidate) in enumerate(scores):
        ranks[candidate] = rank + 1
    return [ranks[candidate] for candidate in candidates]

def get_features(question, ranked_sentences):
    candidates = question.snippet_ner_entities
    X = np.array([factoid_letor_features.all_features(question.question, ranked_sentences, candidate) for candidate in candidates])
    y = gold_candidate_rank(candidates, question.exact_answer_ref)
    return X.tolist(), y

def main():
    ranker = SVMRank()
    file_name = 'input/BioASQ-trainingDataset6b.json'
    data = DataLoader(file_name)
    data.load_ner_entities()
    questions = data.get_questions_of_type(C.FACTOID_TYPE)[:419]

    for i, question in enumerate(questions):
        ranked_sentences = question.ranked_sentences()
        X, y = get_features(question, ranked_sentences)
        ranker.feed(X, y, i)

    ranker.train_from_feed()
    ranker.save('weights_2')

if __name__ == "__main__":
    main()
