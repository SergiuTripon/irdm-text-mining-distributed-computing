#### IRDM - Assignment 1 - Part A & B

This is an assigment I completed as part of the [COMPGI15 - Information Retrieval & Data Mining](http://www.cs.ucl.ac.uk/teaching_learning/syllabus/mscml/gi15_information_retrieval_data_mining/) module (MSc Web Science and Big Data Analytics) which I undertook at UCL.

Repository contents:

* Part A source code in Python
* Part B source code in Java
* Report source code in LaTeX

---

##### Assignment Brief

The aim of this assignment was to experiment with:

* Text Mining
* Distributed Computing

###### Part A: Text Mining

This part of the assignment contained six questions. It required two models to be implemented and their effectiveness was evaluated by implementing widely used evaluation metrics. The task was to carry out retrieval on a standard TREC document test collection using a number of different models and analyze the results.

###### Part B: Distributed Computing

The primary objective of this part of the assignment was to introduce Hadoop and MapReduce framework and to gain practical experience using Amazon’s cloud computing platform AWS. The task was to program Hadoop algorithms for different types of indexing on a data set and run them using AWS, which were then used to answer some IR questions.

---

##### Instructions

To run the source code, follow the steps below:

###### Part A: Text Mining

```bash
# running BM25 Model
python BM25Model.py

# running NDCG
python NDCG.py

# running MMR Scoring
python MMRScoring.py --lambda 0.25
python MMRScoring.py --lambda 0.50

# running Portfolio Scoring
python PortfolioScoring.py --b_param -4
python PortfolioScoring.py --b_param 4

# running alpha-NDCG
python alpha-NDCG.py -mv mmr_0.25
python alpha-NDCG.py -mv mmr_0.50
python alpha-NDCG.py -mv portfolio_-4
python alpha-NDCG.py -mv portfolio_4

```

---

###### Part B: Distributed Computing

To run the source code, you have to manually set up a project in an IDE that supports Scala. For this assignment, IntelliJ IDEA IDE was used.
