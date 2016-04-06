#!/usr/bin/python

########################################################################################################################

# Ref 1: http://www.efalken.com/LowVolClassics/markowitz_JF1952.pdf
# Ref 2: http://web4.cs.ucl.ac.uk/staff/jun.wang/papers/2009-sigir09-portfoliotheory.pdf
# Ref 3: https://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient

########################################################################################################################


# python packages
import argparse
from numpy import cov, std
from collections import OrderedDict


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


# dictionary to hold rq dq term frequency memoize
rq_dq_term_freq_memoize = {}


# calculates pearson's correlation coefficient between two given documents
def calc_pxy(rq_doc_id, dq_doc_id, rq_doc_vec, dq_doc_vec):

    # assign union of rq document vector and dq document vector to union
    union = rq_doc_vec.keys() | dq_doc_vec.keys()
    # sort union in ascending order
    union = sorted(union)

    # concatenate rq and dq document id and assign to rq dq document id
    rq_dq_doc_id = ' '.join([rq_doc_id, dq_doc_id])

    # if rq dq document id is not in rq dq term frequency memoize
    if rq_dq_doc_id not in rq_dq_term_freq_memoize:
        # assign rq and dq document vector values to rq and dq document term frequency
        rq_doc_term_freq = [rq_doc_vec.get(x) if rq_doc_vec.get(x) is not None else 0 for x in union]
        dq_doc_term_freq = [dq_doc_vec.get(x) if dq_doc_vec.get(x) is not None else 0 for x in union]
        # add rq and dq document term frequency to rq dq term frequency memoize
        rq_dq_term_freq_memoize[rq_dq_doc_id] = (rq_doc_term_freq, dq_doc_term_freq)

    # get rq and dq term frequency vector
    rq_term_freq_vector = rq_dq_term_freq_memoize.get(rq_dq_doc_id)[0]
    dq_term_freq_vector = rq_dq_term_freq_memoize.get(rq_dq_doc_id)[1]

    # calculate covariance
    covariance = cov(rq_term_freq_vector, dq_term_freq_vector)[0][1]

    # calculate standard deviation
    standard_deviation = (std(rq_term_freq_vector) * std(dq_term_freq_vector))

    # calculate pearson's correlation coefficient
    pxy = covariance / standard_deviation

    # return pearson's correlation coefficient
    return pxy


########################################################################################################################


# calculates mva and ranks 100 given documents at a time
def calc_mva(query_id, qid_did_score, rq, doc_score, doc_vec, b):

    # assign first token of document score to max score
    max_score = max(doc_score)
    # assign first token of rq to dq
    dq = [rq[0]]
    # remove first token of dq from rq
    rq.remove(dq[0])

    # open file
    with open('output/temp/portfolio_b_{}.txt'.format(b), mode='a') as results_file:
        # write results in standard TREC format
        results_file.write('{} Q0 {} 0 {} bm25_b_0.75\n'.format(query_id, dq[0], max_score, b))

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
        # variable to hold highest mva set to null
        high_mva = None
        # variable to hold highest mva document set to null
        high_mva_doc_id = None
        # open file
        with open('output/temp/portfolio_b_{}.txt'.format(b), mode='a') as results_file:
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
                    # normalize bm25 score
                    norm_bm25_score = rq_doc_score / max_score
                    # calculate pearson's correlation coefficient
                    p_x_y = calc_pxy(rq_doc_id, dq_doc_id, OrderedDict(rq_doc_vec), OrderedDict(dq_doc_vec))
                    # calculate mva
                    mva = norm_bm25_score - (b * i) - 2 * b * p_x_y
                    # if high mva is null:
                    if high_mva is None:
                        # assign mva to high mva
                        high_mva = mva
                        # assign rq document id to high mva document id
                        high_mva_doc_id = rq_doc_id
                    # if mva is greater than high mva:
                    if mva > high_mva:
                        # assign mva to high mva
                        high_mva = mva
                        # assign rq document id to high mva document id
                        high_mva_doc_id = rq_doc_id

            # add high mva document id to dq
            dq += [high_mva_doc_id]
            # write results in standard TREC format
            results_file.write('{} Q0 {} {} {} portfolio_b_{}\n'.format(query_id, high_mva_doc_id, doc_rank, high_mva, b))
            # increment document rank
            doc_rank += 1
            # print progress
            print('query id {} - scored {} out of {} documents'.format(query_id, print_progress, rq_len + 1))
            # increment print progress
            print_progress += 1
            # remove high mva document id from rq
            rq.remove(high_mva_doc_id)

    # print progress
    print('\nSaved results to file at path: \'{}\'\n'.format(results_file.name))

    # return
    return


########################################################################################################################


# main function
def main(b):

    # load docs
    doc_vec, doc_term_ids = load_docs('input/document_term_vectors.dat')

    # load results
    qid_did_score, doc_ids, doc_score = load_results('output/final/question-1/bm25_b_0.75.txt')

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
        # calculate mva
        calc_mva(query_id, qid_did_score[start:end], rq, doc_score[start:end], doc_vec, b)
        # increment start by 100
        start += 100
        # increment end by 100
        end += 100


########################################################################################################################


# runs main function
if __name__ == '__main__':

    # parse script argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--b_param', type=int, dest='b_param_', metavar='b param value',
                        help='b param value', required=True)
    args = parser.parse_args()

    # call main function with the script argument as parameter
    main(args.b_param_)


########################################################################################################################
