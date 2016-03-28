# Folder structure to run this script successfully
# terrier-core-4.1
# topics
# qrels
# scripts
#    index_clueweb.sh
#    bm25_terrier.sh

# delete results folder if exists
rm -rf ../terrier-core-4.1/var/results/*

echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# Question 2' >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# path to topics file' >> ../terrier-core-4.1/etc/terrier.properties
echo trec.topics=../topics/trec2013-topics.txt >> ../terrier-core-4.1/etc/terrier.properties
echo '# set topics parser' >> ../terrier-core-4.1/etc/terrier.properties
echo trec.topics.parser=TRECQuery >> ../terrier-core-4.1/etc/terrier.properties
echo '# set query tags' >> ../terrier-core-4.1/etc/terrier.properties
echo TrecQueryTags.doctag=TOP >> ../terrier-core-4.1/etc/terrier.properties
echo TrecQueryTags.idtag=NUM >> ../terrier-core-4.1/etc/terrier.properties
echo TrecQueryTags.process=TOP,NUM,TITLE >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties

echo '# set ranking model' >> ../terrier-core-4.1/etc/terrier.properties
echo trec.model=org.terrier.matching.models.BM25 >> ../terrier-core-4.1/etc/terrier.properties
echo 'print filename' >> ../terrier-core-4.1/etc/terrier.properties
echo trec.querying.outputformat.docno.meta.key=filename >> ../terrier-core-4.1/etc/terrier.properties
echo '# path to results' >> ../terrier-core-4.1/etc/terrier.properties
echo trec.results=results >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# path to qrels file' >> ../terrier-core-4.1/etc/terrier.properties
echo trec.qrels=../qrels/qrels.adhoc.txt >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '### End of properties added by Sergiu Tripon ###' >> ../terrier-core-4.1/etc/terrier.properties

# perform batch retrieval
../terrier-core-4.1/bin/trec_terrier.sh -r

# remove path part before filename and ".txt" extension from the results file
sed -i 's/..\/clueweb12\///' ../terrier-core-4.1/var/results/BM25b0.75_0.res
sed -i 's/.txt//' ../terrier-core-4.1/var/results/BM25b0.75_0.res
