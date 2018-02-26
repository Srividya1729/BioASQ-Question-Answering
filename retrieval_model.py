import json
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))


class BM25(object):
    def __init__(self, k1, k3, b, N):
        self.k1 = k1
        self.k3 = k3
        self.b = b
        self.N = N

    def get_score(self, term_dict, common_tokens, N, docId, average_doc_length):
        score = 0
        doc_length = get_doc_length(term_dict, docId)
        for token in common_tokens:
            score += self.get_individual_term_score(term_dict, token, N, doc_length, average_doc_length)
        return score

    def get_individual_term_score(self, term_dict, token, N, doc_length, average_doc_length):
        df_term = len(term_dict[token])
        df_term = (N - df_term + 0.5) / (df_term + 0.5)
        idf = np.log(1 + df_term)

        tf = sum([term_dict[token][x] for x in term_dict[token].keys()])

        tf /= tf + self.k1 * ((1 - self.b) + self.b * (doc_length / average_doc_length))

        return tf * idf


def get_docID(snippet):
    doc_string = snippet['document']
    doc_id = int(doc_string.rstrip().replace('\'', '').split('/')[4])
    return doc_id


def update_dictionary(term_dict, tokens, docId):
    # updates the term dictionary for tokens of docId
    for token in tokens:
        if term_dict.get(token, False):
            if term_dict[token].get(docId, False):
                term_dict[token][docId] += 1
            else:
                term_dict[token][docId] = 1
        else:
            term_dict[token] = {docId: 1}

    return term_dict


def get_doc_length(term_dict, docId):
    count = 0
    for key in term_dict.keys():
        if docId in term_dict[key].keys():
            count += term_dict[key][docId]

    return count


def get_BM25_score(term_dict, question_tokens, docId, tokens, N, avg_doc_length):
    common_tokens = set(question_tokens).intersection(set(tokens))
    bm25_model = BM25(k1=1.2, k3=0, b=0.75, N=N)
    score = bm25_model.get_score(term_dict, common_tokens, N, docId, avg_doc_length)
    return score


def get_score_list(filepath, algo='BM25'):
    fp = open(filepath)
    data = json.load(fp)

    question_score_list = dict()

    for (i, question) in enumerate(data['questions']):
        snippets = question['snippets']
        question_text = question['body']
        question_tokens = get_tokens(question_text)
        term_dict = dict()
        snippet_token_list = []
        total_token_count = 0
        for snippet in snippets:
            docId = get_docID(snippet)
            tokens = get_tokens(snippet['text'])
            total_token_count += len(tokens)
            term_dict = update_dictionary(term_dict, tokens, docId)
            snippet_token_list.append((docId, tokens))

        score_list = dict()
        N = len(snippets)
        avg_doc_length = float(total_token_count) / N
        for item in snippet_token_list:
            docId = item[0]
            tokens = item[1]
            score = get_BM25_score(term_dict, question_tokens, docId, tokens, N, avg_doc_length)
            score_list[docId] = score

        sorted(score_list.iteritems(), key=lambda (k, v): (v, k), reverse=True)
        question_score_list[i] = score_list
        break
    return question_score_list


def get_tokens(text):
    text = text.lower()
    sentences = sent_tokenize(text)
    tokens = []
    for sentence in sentences:
        words = word_tokenize(sentence)
        filtered_words = [w for w in words if not w in stop_words]
        words = [w.lower() for w in filtered_words if w.isalpha()]
        tokens.extend(words)
    return tokens


def main():
    filepath = './input/BioASQ-trainingDataset5b.json'
    score_list = get_score_list(filepath, 'BM25')
    print('retrieved results')


if __name__ == '__main__':
    main()