
from math import sqrt
from collections import OrderedDict

########################################################################################################################


# loads docs
def load_docs(input_file):

    data = []

    with open(input_file) as input_file:
        for line in input_file:
            tokens = line.strip(' \n').split(' ')
            doc_id = tokens[0]
            # doc_vec = tokens[1:]
            doc_vec_temp = []
            for token in tokens[1:]:
                token = token.split(':')
                doc_vec_temp += [(token[0], token[1])]
            data += [(doc_id, doc_vec_temp)]

    return data


########################################################################################################################


# loads results
def load_results(input_file):

    data = []
    doc_ids = []
    doc_ranks = []
    doc_scores = []

    with open(input_file) as input_file:
        for line in input_file:
            tokens = line.strip(' \n').split(' ')
            query_id = tokens[0]
            doc_id = tokens[2]
            doc_rank = tokens[3]
            doc_score = float(tokens[4])
            qid_did = ' '.join([query_id, doc_id])
            data += [(qid_did, doc_score)]
            doc_ids += [doc_id]
            doc_ranks += [(qid_did, doc_rank)]
            doc_scores += [doc_score]

    return data, doc_ids, doc_ranks, doc_scores


########################################################################################################################


def calc_sim(rq_doc_vec, dq_doc_vec):

    rq_doc_vec = OrderedDict(rq_doc_vec)
    dq_doc_vec = OrderedDict(dq_doc_vec)

    rq_vector = [int(rq_doc_vec[x]) for x in rq_doc_vec if x in dq_doc_vec]
    dq_vector = [int(dq_doc_vec[x]) for x in dq_doc_vec if x in rq_doc_vec]

    dot_product = sum([x * y for x, y in zip(rq_vector, dq_vector)])

    d1 = sqrt(sum([(x ** 2) for x in rq_vector]))
    d2 = sqrt(sum([(x ** 2) for x in dq_vector]))
    d1_d2 = d1 * d2

    if d1_d2 != 0.0:
        cos = float(dot_product) / d1_d2
    else:
        cos = 0.0

    return cos


########################################################################################################################


def calc_mmr(query_id, results, rq, doc_ranks, scores, doc_vec, lambda_weight):

    max_score = scores[0]
    dq = [rq[0]]
    rq.remove(dq[0])

    with open('output/mmr_lambda_{}.txt'.format(lambda_weight), mode='a') as results_file:
        results_file.write('{} Q0 {} 0 {} mmr\n'.format(query_id, dq[0], max_score))

    results = dict(results)
    doc_vec = dict(doc_vec)
    doc_ranks = dict(doc_ranks)

    rq_len = len(rq)

    print('query id {} - scored 0 out of {} documents'.format(query_id, rq_len + 1))

    print_progress = 1
    for i in range(0, rq_len):
        high_mmr = 0.0
        high_mmr_doc = ''
        high_mmr_doc_rank = 0
        high_mmr_doc_score = 0.0
        with open('output/mmr_lambda_{}.txt'.format(lambda_weight), mode='a') as results_file:
            for rq_doc in rq:
                for dq_doc in dq:
                    rq_doc_vec = doc_vec.get(rq_doc)
                    dq_doc_vec = doc_vec.get(dq_doc)
                    qid_did = ' '.join([str(query_id), rq_doc])
                    rq_doc_rank = doc_ranks.get(qid_did)
                    rq_doc_score = results.get(qid_did)
                    f1 = rq_doc_score
                    f2 = calc_sim(rq_doc_vec, dq_doc_vec)
                    mmr = (lambda_weight * f1) - ((1 - lambda_weight) * f2)
                    if mmr > high_mmr:
                        high_mmr = mmr
                        high_mmr_doc = rq_doc
                        high_mmr_doc_rank = rq_doc_rank
                        high_mmr_doc_score = rq_doc_score

            dq += [high_mmr_doc]
            results_file.write('{} Q0 {} {} {} mmr\n'.format(query_id, high_mmr_doc, high_mmr_doc_rank,
                                                             high_mmr_doc_score))
            print('query id {} - scored {} out of {} documents'.format(query_id, print_progress, rq_len + 1))
            print_progress += 1
            rq.remove(high_mmr_doc)

    return


########################################################################################################################


# main function
def main():

    # load docs
    doc_vec = load_docs('input/document_term_vectors.dat')

    # load results
    qid_did_score, doc_ids, doc_ranks, doc_scores = load_results('output/BM25b0.75_0.res')

    lambda_weight = 0.5
    # lambda_weight = 0.75

    query_ids = list(range(201, 251))

    start = 0
    end = 100
    for query_id in query_ids:
        results = qid_did_score[start:end]
        scores = doc_scores[start:end]
        rq = doc_ids[start:end]
        calc_mmr(query_id, results, rq, doc_ranks, scores, doc_vec, lambda_weight)
        start += 100
        end += 100

########################################################################################################################


# runs main function
if __name__ == '__main__':
    main()


########################################################################################################################
