#!/bin/sh

# Folder structure to run this script successfully
# terrier-core-4.1
# clueweb
# scripts
#    index_clueweb.sh
#    bm25_terrier.sh

# delete collection.spec file if exists
rm -rf ../terrier-core-4.1/etc/collection.spec

# delete terrier.properties file if exists
rm -rf ../terrier-core-4.1/etc/terrier.properties

# delete index folder if exists
rm -rf ../terrier-core-4.1/var/index/*

# generate collection
sh ../terrier-core-4.1/bin/trec_setup.sh ../clueweb12/

echo '###### Beginning of properties added by Sergiu Tripon ######' >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# path to index folder' >> ../terrier-core-4.1/etc/terrier.properties
echo terrier.index.path=index/ >> ../terrier-core-4.1/etc/terrier.properties
echo '# path to etc folder' >> ../terrier-core-4.1/etc/terrier.properties
echo terrier.etc=../terrier-core-4.1/etc/ >> ../terrier-core-4.1/etc/terrier.properties
echo '# path to share folder' >> ../terrier-core-4.1/etc/terrier.properties
echo terrier.share=../terrier-core-4.1/share/ >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# path to collection' >> ../terrier-core-4.1/etc/terrier.properties
echo collection.spec=collection.spec >> ../terrier-core-4.1/etc/terrier.properties
echo '# specify tags to index content from' >> ../terrier-core-4.1/etc/terrier.properties
echo FieldTags.process=TITLE,H1,H2,H3,H4,H5,H6,ELSE >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# collection type' >> ../terrier-core-4.1/etc/terrier.properties
echo trec.collection.class=SimpleFileCollection >> ../terrier-core-4.1/etc/terrier.properties
echo '# document type' >> ../terrier-core-4.1/etc/terrier.properties
echo indexing.simplefilecollection.extensionsparsers=txt:TaggedDocument >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# words to be ignored' >> ../terrier-core-4.1/etc/terrier.properties
echo stopwords.filename=stopword-list.txt >> ../terrier-core-4.1/etc/terrier.properties
echo '# how documents need to be tokenized' >> ../terrier-core-4.1/etc/terrier.properties
echo termpipelines=Stopwords,PorterStemmer >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# index information other than document text' >> ../terrier-core-4.1/etc/terrier.properties
echo indexer.meta.forward.keys=filename >> ../terrier-core-4.1/etc/terrier.properties
echo indexer.meta.reverse.keys=filename >> ../terrier-core-4.1/etc/terrier.properties
echo '# specify character length' >> ../terrier-core-4.1/etc/terrier.properties
echo indexer.meta.forward.keylens=64 >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '### Question 1 ###' >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# convert document text to lower case' >> ../terrier-core-4.1/etc/terrier.properties
echo lowercase=TRUE >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# tokenize document text by splitting at all non-alphanumeric characters' >> ../terrier-core-4.1/etc/terrier.properties
echo tokeniser=EnglishTokeniser >> ../terrier-core-4.1/etc/terrier.properties
echo >> ../terrier-core-4.1/etc/terrier.properties
echo '# set index name' >> ../terrier-core-4.1/etc/terrier.properties
echo terrier.index.prefix=terrier_clueweb_index >> ../terrier-core-4.1/etc/terrier.properties

# generate index
../terrier-core-4.1/bin/trec_terrier.sh -i -j
