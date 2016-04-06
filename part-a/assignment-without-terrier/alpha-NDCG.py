#!/usr/bin/python

########################################################################################################################

# Ref: https://en.wikipedia.org/wiki/Discounted_cumulative_gain#Normalized_DCG

########################################################################################################################


# python packages
import argparse
from math import log2
from collections import OrderedDict


########################################################################################################################


# loads results
def load_results(input_file):

    # list to hold data
    qid_did = []
    # list to hold query ids
    query_ids = []

    # open file
    with open(input_file) as input_file:
        # for every line in input file
        for line in input_file:
            # split line into tokens
            tokens = line.strip(' \n').split(' ')
            # assign first token to query id
            query_id = tokens[0]
            # if query id is not in query ids list
            if query_id not in query_ids:
                # add query id to query ids list
                query_ids += [query_id]
            # convert to int and assign fourth token to document rank
            doc_rank = int(tokens[3])
            # if document rank is less than 50
            if doc_rank < 50:
                # assign third token to document id
                doc_id = tokens[2]
                # concatenate query id and document id and assign to query id document id
                qid_did_temp = ' '.join([query_id, doc_id])
                # add temporary query id document id to query id document id list
                qid_did += [qid_did_temp]

    # return query id document id and query ids lists
    return qid_did, query_ids


########################################################################################################################


# loads qrels
def load_qrels(input_file):

    # list to hold document intent
    doc_int = OrderedDict({})
    # list to hold document relevance
    doc_rel = OrderedDict({})

    # open file
    with open(input_file) as input_file:
        # for every line in input file
        for line in input_file:
            # split line into tokens
            tokens = line.strip(' \n').split(' ')
            # assign first token to query id
            query_id = tokens[0]
            # assign second token to temporary document intent
            doc_int_temp = int(tokens[1])
            # assign third token to document id
            doc_id = tokens[2]
            # assign fourth token to temporary document relevance
            doc_rel_temp = int(tokens[3])
            # concatenate query id and document id and assign to query id document id
            qid_did = ' '.join([query_id, doc_id])
            # add temporary document intent to document intent dictionary
            doc_int[qid_did] = doc_int_temp
            # add temporary document relevance to document relevance dictionary
            doc_rel[qid_did] = doc_rel_temp

    # return document intent and document relevance
    return doc_int, doc_rel


########################################################################################################################


# calculate alpha ndcg
def calc_alpha_ndcg(results, doc_int, doc_rel, k, alpha, start, end):

    # get document relevance scores for document ids between start and end
    rels = [doc_int.get(results[i]) * ((1 - alpha) ** doc_rel.get(results[i]))
            if doc_rel.get(results[i]) is not None else 0 for i in range(start, end)]

    # sort relevance scores in descending order and assign to sorted relevance scores
    sorted_rels = sorted(rels, reverse=True)

    # assign first relevance score to relevance score 1
    rel1 = rels[0]
    # assign first sorted relevance score to sorted relevance score 1
    sorted_rel1 = sorted_rels[0]

    # calculate dcg fraction
    dcg_fraction = sum([(rels[i] / log2(i + 1)) for i in range(1, k)])
    # calculate idcg fraction
    idcg_fraction = sum([(sorted_rels[i] / log2(i + 1)) for i in range(1, k)])

    # calculate dcg
    dcg = rel1 + dcg_fraction
    # calculate idcg
    idcg = sorted_rel1 + idcg_fraction

    # set alpha ndcg to 0.0
    alpha_ndcg = 0.0

    # if dcg and idcg are not equal to 0 or 0.0
    if dcg and idcg != 0 or 0.0:
        # calculate alpha-ndcg
        alpha_ndcg = dcg / idcg

    # return alpha ndcg
    return alpha_ndcg


########################################################################################################################


# main function
def main(model_value):

    # split parameter on '_'
    tokens = model_value.split('_')
    # assign first token to model
    model = tokens[0]
    # assign second token to value
    value = tokens[1]

    # variable to hold param set to null
    param = None
    # variable to hold results set to null
    results = None
    # variable to hold query ids set to null
    query_ids = None

    # if model is equal to mmr
    if model == 'mmr':
        # set param to 'lambda'
        param = 'lambda'
        # if value is equal to '0.25'
        if value == '0.25':
            # load corresponding results
            results, query_ids = load_results('output/final/question-3/mmr_lambda_0.25.txt')
        # if value is equal to '0.50'
        elif value == '0.50':
            # load corresponding results
            results, query_ids = load_results('output/final/question-3/mmr_lambda_0.50.txt')
    # if model is equal to portfolio
    elif model == 'portfolio':
        # set param to 'b'
        param = 'b'
        # if value is equal to '-4'
        if value == '-4':
            # load corresponding results
            results, query_ids = load_results('output/final/question-4/portfolio_b_-4.txt')
        # if value is equal to '4'
        elif value == '4':
            # load corresponding results
            results, query_ids = load_results('output/final/question-4/portfolio_b_4.txt')

    # load qrels
    doc_int, doc_rel = load_qrels('input/qrels.ndeval.txt')

    # assign length of query ids to query ids length
    query_ids_len = len(query_ids)
    # list to hold alpha-ndcg at k in (1, 5, 10, 20, 30, 40, 50)
    all_alpha_ndcg = [0.0 for _ in range(7)]

    # variable to hold file path set to null
    file_path = None

    # loop for alpha in (0.1, 0.5, 0.9)
    for alpha in (0.1, 0.5, 0.9):
        # for every query id
        for query_id in query_ids:
            # convert query id to int and assign to query id
            query_id = int(query_id)
            # convert first query id to int and assign to query id 1
            query_id1 = int(query_ids[0])

            # loop from 0 to 1, 5, 10, 20, 30, 40, 50
            for k in (1, 5, 10, 20, 30, 40, 50):
                # set i to 0
                i = 0
                # if k equals 1, i equals 0
                if k == 1:
                    i = 0
                # else if k equals 5, i equals 1
                elif k == 5:
                    i = 1
                # else if k equals 10, i equals 2
                elif k == 10:
                    i = 2
                # else if k equals 20, i equals 3
                elif k == 20:
                    i = 3
                # else if k equals 30, i equals 4
                elif k == 30:
                    i = 4
                # else if k equals 40, i equals 5
                elif k == 40:
                    i = 5
                # else if k equals 50, i equals 6
                elif k == 50:
                    i = 6

                # set start value
                start = 50 * (query_id - query_id1)
                # set end value
                end = start + k

                # calculate alpha-ndcg and return output in alpha ndcg
                alpha_ndcg = calc_alpha_ndcg(results, doc_int, doc_rel, k, alpha, start, end)
                # add alpha ndcg to all alpha ndcg
                all_alpha_ndcg[i] += alpha_ndcg

        # calculate average alpha-ndcg @ k = 1
        avg_alpha_ndcg_k1 = all_alpha_ndcg[0] / query_ids_len
        # calculate average alpha-ndcg @ k = 5
        avg_alpha_ndcg_k5 = all_alpha_ndcg[1] / query_ids_len
        # calculate average alpha-ndcg @ k = 10
        avg_alpha_ndcg_k10 = all_alpha_ndcg[2] / query_ids_len
        # calculate average alpha-ndcg @ k = 20
        avg_alpha_ndcg_k20 = all_alpha_ndcg[3] / query_ids_len
        # calculate average alpha-ndcg @ k = 30
        avg_alpha_ndcg_k30 = all_alpha_ndcg[4] / query_ids_len
        # calculate average alpha-ndcg @ k = 40
        avg_alpha_ndcg_k40 = all_alpha_ndcg[5] / query_ids_len
        # calculate average alpha-ndcg @ k = 50
        avg_alpha_ndcg_k50 = all_alpha_ndcg[6] / query_ids_len

        # write alpha ndcg @ k in (1, 5, 10, 20, 30, 40, 50) to file
        with open('output/temp/{}_{}_{}_ndcg.txt'.format(model, param, value), mode='a') as results_file:
            results_file.write('{}\n'.format(model))
            results_file.write('{} = {}\n'.format(param, value))
            results_file.write('alpha\t|\tK\t|\talpha-NDCG@K\n')
            results_file.write('{:.1f}\t|\t1\t|\t{:.3f}\n'.format(alpha, avg_alpha_ndcg_k1))
            results_file.write('{:.1f}\t|\t5\t|\t{:.3f}\n'.format(alpha, avg_alpha_ndcg_k5))
            results_file.write('{:.1f}\t|\t10\t|\t{:.3f}\n'.format(alpha, avg_alpha_ndcg_k10))
            results_file.write('{:.1f}\t|\t20\t|\t{:.3f}\n'.format(alpha, avg_alpha_ndcg_k20))
            results_file.write('{:.1f}\t|\t30\t|\t{:.3f}\n'.format(alpha, avg_alpha_ndcg_k30))
            results_file.write('{:.1f}\t|\t40\t|\t{:.3f}\n'.format(alpha, avg_alpha_ndcg_k40))
            results_file.write('{:.1f}\t|\t50\t|\t{:.3f}\n\n'.format(alpha, avg_alpha_ndcg_k50))

            # assign results file name to file path
            file_path = results_file.name

    # print progress
    print('\nSaved results to file at path: \'{}\'\n'.format(file_path))


########################################################################################################################


# runs main function
if __name__ == '__main__':

    # parse script argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-mv', '--model_value', type=str, dest='model_value', metavar='model value',
                        help='model value', required=True)
    args = parser.parse_args()

    # call main function with the script argument as parameter
    main(args.model_value)


########################################################################################################################
