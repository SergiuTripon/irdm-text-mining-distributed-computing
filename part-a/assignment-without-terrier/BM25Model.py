
# Ref: https://en.wikipedia.org/wiki/Okapi_BM25

########################################################################################################################


# python packages
from math import log2
from operator import attrgetter


########################################################################################################################


# doc object
class Doc(object):

    def __init__(self, doc_id, doc_vec, doc_term_id, doc_term_freq, doc_len):

        # document id
        self.doc_id = doc_id
        # document vector
        self.doc_vec = doc_vec
        # document term id
        self.doc_term_id = doc_term_id
        # document term frequency
        self.doc_term_freq = doc_term_freq
        # document length
        self.doc_len = doc_len


########################################################################################################################


# query object
class Query(object):

    def __init__(self, query_id, query_vec, query_term_id, query_term_freq):

        # query id
        self.query_id = query_id
        # query vector
        self.query_vec = query_vec
        # query term id
        self.query_term_id = query_term_id
        # query term frequency
        self.query_term_freq = query_term_freq


########################################################################################################################


# result object
class Result(object):

    def __init__(self, query_id, doc_id, doc_score):

        # query id
        self.query_id = query_id
        # document id
        self.doc_id = doc_id
        # document score
        self.doc_score = doc_score


########################################################################################################################


# loads documents
def load_docs(input_file):

    # list to hold unique docs
    unique_docs = []
    # list to hold data
    data = []
    # variable to hold documents length
    docs_len = 0

    # open file
    with open(input_file) as input_file:
        # for every line in input file
        for line in input_file:
            # if document id is not in unique docs
            if line.split(' ')[0] not in unique_docs:
                # add document id to unique documents list
                unique_docs += [line.split(' ')[0]]
                # split line into tokens
                tokens = line.strip(' \n').split(' ')
                # assign first token to document id
                doc_id = tokens[0]
                # assign all tokens except the first one to document vector
                doc_vec = tokens[1:]
                # list to hold document term id
                doc_term_id = []
                # list to hold document term frequency
                doc_term_freq = []
                # variable to hold document length
                doc_len = 0
                # for every token except the first one
                for token in tokens[1:]:
                    # split token
                    token = token.split(':')
                    # add first token to document term id
                    doc_term_id += [token[0]]
                    # add second token to document term frequency
                    doc_term_freq += [token[1]]
                    # add second token to document length
                    doc_len += int(token[1])
                # add document length to documents length
                docs_len += doc_len
                """ add document id, document vector, document term id, document term
                    frequency and document length as attributes of the Doc object """
                data += [Doc(doc_id, doc_vec, doc_term_id, doc_term_freq, doc_len)]

    # return data and documents length
    return data, docs_len


########################################################################################################################


# loads queries
def load_queries(input_file):

    # list to hold data
    data = []

    # open file
    with open(input_file) as input_file:
        # for every line in input file
        for line in input_file:
            # split line into tokens
            tokens = line.strip(' \n').split(' ')
            # assign first token to query id
            query_id = tokens[0]
            # assign all tokens except the first one to query vector
            query_vec = tokens[1:]
            # list to hold query term id
            query_term_id = []
            # list to hold query term frequency
            query_term_freq = []
            # for every token except the first one
            for token in tokens[1:]:
                # split token
                token = token.split(':')
                # add first token to query term id
                query_term_id += [token[0]]
                # add second token to query term frequency
                query_term_freq += [token[1]]
            """ add query id, query vector, query term id and query term frequency
                as attributes of the Query object """
            data += [Query(query_id, query_vec, query_term_id, query_term_freq)]

    # return data
    return data


########################################################################################################################


# finds and retrieves frequency of a given query term, from document vector
def get_fqid(query_term_id, doc_vec):

    # fqid - current query term qi's term frequency in document D
    # iterate through document vector and retrieve fqid
    fqid = [x for x in doc_vec if query_term_id in x]
    # if fqid exists in document vector
    if fqid:
        # split fqid
        fqid = fqid[0].split(':')
        # update fqid as the second token
        fqid = int(fqid[1])
    # if fqid does not exist in document vector
    else:
        # set fqid to 0
        fqid = 0

    # return fqid
    return fqid


########################################################################################################################


# calculates bm25 score
def calc_bm25(docs, doc_term_ids, docs_len, N, query_id, query_term_ids, k1, b):

    # list to hold data
    data = []

    # calculate average document length
    avg_doc_len = docs_len / N

    # variable to hold print progress set to 0
    print_progress = 0
    # for every document
    for doc in docs:
        # variable to hold document id
        doc_id = doc.doc_id
        # variable to hold document vector
        doc_vec = doc.doc_vec
        # variable to hold document length
        doc_len = doc.doc_len

        # variable to hold document score
        doc_score = 0.0
        # for every query term id
        for query_term_id in query_term_ids:

            # k1, b - free parameters
            # doc_len - current document's length
            # avg_doc_len - average document length
            # N - total number of documents in the collection
            # nqi - number of documents containing current query term qi
            # fqid - current query term qi's term frequency in document D
            # idfqi - inverse document frequency weight of the current query term qi

            # calculate nqi
            nqi = doc_term_ids.count(query_term_id)
            # get fqid
            fqid = get_fqid(query_term_id, doc_vec)

            # calculate idfqi
            idfqi = log2((N - nqi + 0.5) / (nqi + 0.5))
            # calculate fraction part
            fraction = (fqid * (k1 + 1)) / (fqid + k1 * (1 - b + b * doc_len / avg_doc_len))

            # calculate bm25 score for current document and current query term qi
            bm25_score = idfqi * fraction

            # add current query term qi's bm25 score to overall document score
            doc_score += bm25_score

        """ add query id, document id and document score as attributes of
            the Result object """
        data += [Result(query_id, doc_id, doc_score)]
        # print progress
        print('query id {} - scored {} out of {} documents'.format(query_id, print_progress, N))
        # increment print progress
        print_progress += 1

    # sort data in reverse order
    data = sorted(data, reverse=True, key=attrgetter('doc_score'))

    # return data
    return data


########################################################################################################################


# main function
def main():

    # load docs
    docs, docs_len = load_docs('input/document_term_vectors.dat')
    # load queries
    queries = load_queries('input/query_term_vectors.dat')

    # variable to hold free parameter b
    b = 0.75
    # variable to hold free parameter k1
    k1 = 1.5

    # variable to hold number of documents in the collection
    N = len(docs)
    # for every document in collection, retrieve its term ids
    doc_term_ids = [doc_term_id for doc in docs for doc_term_id in doc.doc_term_id]

    # for every query
    for query in queries:
        # variable to hold query id
        query_id = query.query_id
        # variable to hold query term id
        query_term_id = query.query_term_id
        # calculate bm25 score and return output in results
        results = calc_bm25(docs, doc_term_ids, docs_len, N, query_id, query_term_id, k1, b)
        # open file
        with open('output/question-1/BM25b0.75_0.res', mode='a') as results_file:
            # variable to hold document rank
            doc_rank = 0
            # for every result
            for result in results:
                # if document rank is less than 100
                if doc_rank < 100:
                    # write results in standard TREC format
                    results_file.write('{} Q0 {} {} {} BM25b0.75\n'.
                                       format(result.query_id, result.doc_id, doc_rank, result.doc_score))
                # increment document rank
                doc_rank += 1
        # print progress
        print('\nSaved results to file at path: \'{}\'\n'.format(results_file.name))


########################################################################################################################


# runs main function
if __name__ == '__main__':
    main()
