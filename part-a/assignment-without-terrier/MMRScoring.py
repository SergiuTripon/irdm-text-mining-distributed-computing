#!/usr/bin/python

########################################################################################################################

# Ref: https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf

########################################################################################################################


# python packages
import argparse
from math import sqrt, log10
from collections import OrderedDict, Counter


########################################################################################################################


# loads docs
def load_docs(input_file):

    # list to hold unique docs
    unique_doc_ids = []
    # list to hold document vector
    doc_vec = []
    # list to hold document term ids
    doc_term_ids = []

    # open file
    with open(input_file) as input_file:
        # for every line in input file
        for line in input_file:
            # if document id is not in unique docs
            if line.split(' ')[0] not in unique_doc_ids:
                # add document id to unique documents list
                unique_doc_ids += [line.split(' ')[0]]
                # split line into tokens
                tokens = line.strip(' \n').split(' ')
                # assign first token to document id
                doc_id = tokens[0]
                # list to hold temporary document vector
                doc_vec_temp = []
                # for every token except the first one
                for token in tokens[1:]:
                    # split token
                    token = token.split(':')
                    # add first token to document term ids
                    doc_term_ids += [int(token[0])]
                    # add first and second token to temporary document vector
                    doc_vec_temp += [(int(token[0]), int(token[1]))]
                # add document id and temporary document vector to document vector list
                doc_vec += [(doc_id, doc_vec_temp)]

    # return document vector and document term ids
    return doc_vec, doc_term_ids


########################################################################################################################


# loads results
def load_results(input_file):

    # list to hold query id document id score
    qid_did_score = []
    # list to hold document ids
    doc_ids = []
    # list to hold document scores
    doc_scores = []

    # open file
    with open(input_file) as input_file:
        # for every line in input file
        for line in input_file:
            # split line into tokens
            tokens = line.strip(' \n').split(' ')
            # assign first token to query id
            query_id = tokens[0]
            # assign third token to document id
            doc_id = tokens[2]
            # assign fifth token to document score
            doc_score = float(tokens[4])
            # concatenate query id and document id and assign to query id document id
            qid_did = ' '.join([query_id, doc_id])
            # add query id document id and document score to query id document id score
            qid_did_score += [(qid_did, doc_score)]
            # add document id to document ids
            doc_ids += [doc_id]
            # add document score to document scores
            doc_scores += [doc_score]

    # return query id document id score, document ids and document scores
    return qid_did_score, doc_ids, doc_scores


########################################################################################################################


# dictionary to hold rq tf-idf memoize
rq_tf_idf_memoize = {}
# dictionary to hold dq tf-idf memoize
dq_tf_idf_memoize = {}

# dictionary to hold rq sum memoize
rq_sum_memoize = {}
# dictionary to hold dq sum memoize
dq_sum_memoize = {}


# calculates cosine similarity between two given documents
def calc_sim(rq_doc_id, dq_doc_id, rq_doc_vec, dq_doc_vec, idf):

    # assign intersection of rq document vector and dq document vector to intersection
    intersection = rq_doc_vec.keys() & dq_doc_vec.keys()
    # sort intersection in ascending order
    intersection = sorted(intersection)

    # if rq document id is not in rq tf-idf memoize or dq document id is not in dq tf-idf memoize
    if rq_doc_id not in rq_tf_idf_memoize or dq_doc_id not in dq_tf_idf_memoize:
        # calculate rq tf-idf and dq tf-idf
        rq_tf_idf_memoize[rq_doc_id] = [idf.get(x) * rq_doc_vec.get(x) for x in intersection]
        dq_tf_idf_memoize[dq_doc_id] = [idf.get(x) * dq_doc_vec.get(x) for x in intersection]

    # get rq and dq tf-idf vector
    rq_tf_idf_vector = rq_tf_idf_memoize.get(rq_doc_id)
    dq_tf_idf_vector = dq_tf_idf_memoize.get(dq_doc_id)
    # calculate dot product of rq and dq tf-idf vector
    rq_dq_dot_product = sum([x * y for x, y in zip(rq_tf_idf_vector, dq_tf_idf_vector)])

    # if rq document id is not in rq sum memoize or dq document id not in dq sum memoize
    if rq_doc_id not in rq_sum_memoize or dq_doc_id not in dq_sum_memoize:
        # assign rq and dq document vector values to rq and dq document term frequencies
        rq_doc_term_freq = rq_doc_vec.values()
        dq_doc_term_freq = dq_doc_vec.values()
        # calculate sum of rq and dq document term frequencies
        rq_sum_memoize[rq_doc_id] = sqrt(sum([(x ** 2) for x in rq_doc_term_freq]))
        dq_sum_memoize[dq_doc_id] = sqrt(sum([(x ** 2) for x in dq_doc_term_freq]))

    # calculate product of rq and dq sum
    rq_dq_product = rq_sum_memoize.get(rq_doc_id) * dq_sum_memoize.get(dq_doc_id)

    # calculate cosine
    cos = float(rq_dq_dot_product) / rq_dq_product

    # return cosine
    return cos


########################################################################################################################


# calculates mmr and ranks 100 given documents based on mmr
def calc_mmr(query_id, qid_did_score, rq, doc_score, doc_vec, idf, lambda_weight):

    # assign first token of document score to max score
    max_score = doc_score[0]
    # assign first token of rq to dq
    dq = [rq[0]]
    # remove first token of dq from rq
    rq.remove(dq[0])

    # open file
    with open('output/temp/mmr_lambda_{:.2f}.txt'.format(lambda_weight), mode='a') as results_file:
        # write results in standard TREC format
        results_file.write('{} Q0 {} 0 {} BM25b0.75\n'.format(query_id, dq[0], max_score, lambda_weight))

    # create dictionary of query id document id score and assign it to query id document id score
    qid_did_score = dict(qid_did_score)
    # create dictionary of document vector and assign it to document vector
    doc_vec = dict(doc_vec)

    # assign length of rq to rq length
    rq_len = len(rq)
    # print progress
    print('query id {} - scored 0 out of {} documents'.format(query_id, rq_len + 1))
    # variable to hold document rank set to 1
    doc_rank = 1
    # variable to hold print progress set to 1
    print_progress = 1
    # loop from 0 to rq length
    for i in range(0, rq_len):
        # variable to hold highest mmr set to 0.0
        high_mmr = 0.0
        # variable to hold highest mmr document
        high_mmr_doc_id = None
        # open file
        with open('output/temp/mmr_lambda_{:.2f}.txt'.format(lambda_weight), mode='a') as results_file:
            # for every rq document id
            for rq_doc_id in rq:
                # for every dq document id
                for dq_doc_id in dq:
                    # assign rq document vector to rq document vector
                    rq_doc_vec = doc_vec.get(rq_doc_id)
                    # assign dq document vector to dq document vector
                    dq_doc_vec = doc_vec.get(dq_doc_id)
                    # concatenate query id and rq document id and assign to query id document id
                    qid_did = ' '.join([str(query_id), rq_doc_id])
                    # assign query id document id score to rq document score
                    rq_doc_score = qid_did_score.get(qid_did)
                    # calculate f1
                    f1 = rq_doc_score / max_score
                    # calculate f2
                    f2 = calc_sim(rq_doc_id, dq_doc_id, OrderedDict(rq_doc_vec), OrderedDict(dq_doc_vec), idf)
                    # calculate mmr
                    # assignment equation
                    # mmr = (lambda_weight * f1) - (1 - lambda_weight) * f2
                    # research paper equation
                    mmr = lambda_weight * (f1 - (1 - lambda_weight) * f2)
                    # if mmr is greater than high mmr:
                    if mmr > high_mmr:
                        # assign mmr to high mmr
                        high_mmr = mmr
                        # assign rq document id to high mmr document id
                        high_mmr_doc_id = rq_doc_id

            # add high mmr document id to dq
            dq += [high_mmr_doc_id]
            # write results in standard TREC format
            results_file.write('{} Q0 {} {} {} mmr_{:.2f}\n'.format(query_id, high_mmr_doc_id, doc_rank, high_mmr,
                                                                    lambda_weight))
            # increment document rank
            doc_rank += 1
            # print progress
            print('query id {} - scored {} out of {} documents'.format(query_id, print_progress, rq_len + 1))
            # increment print progress
            print_progress += 1
            # remove high mmr document id from rq
            rq.remove(high_mmr_doc_id)

    # print progress
    print('\nSaved results to file at path: \'{}\'\n'.format(results_file.name))

    # return
    return


########################################################################################################################


# main function
def main(lambda_weight):

    # load docs
    doc_vec, doc_term_ids = load_docs('input/document_term_vectors.dat')

    # load results
    qid_did_score, doc_ids, doc_score = load_results('output/final/question-1/BM25b0.75_0.res')

    # assign length of document vector to document vector length
    doc_vec_len = len(doc_vec)
    # create a counter of document term ids and assign it to document term ids counter
    doc_term_ids_counter = Counter(doc_term_ids)
    # calculate idf for every term, add it to an ordered dictionary and assign it to idf
    idf = OrderedDict([(x, log10(doc_vec_len / doc_term_ids_counter[x])) for x in doc_term_ids])

    # variable to hold start set to 0
    start = 0
    # variable to hold end set to 100
    end = 100
    # create a list with elements ranging between 201 and 250 and assign it to query ids
    query_ids = list(range(201, 251))
    # for every query id
    for query_id in query_ids:
        # assign document ids ranging between start and end to rq
        rq = doc_ids[start:end]
        # calculate mmr
        calc_mmr(query_id, qid_did_score[start:end], rq, doc_score[start:end], doc_vec, idf, lambda_weight)
        # increment start by 100
        start += 100
        # increment end by 100
        end += 100


########################################################################################################################


# runs main function
if __name__ == '__main__':

    # parse script argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lambda', type=float, dest='lambda_', metavar='lambda weight value',
                        help='lambda weight value', required=True)
    args = parser.parse_args()

    # call main function with the script argument as parameter
    main(args.lambda_)


########################################################################################################################
