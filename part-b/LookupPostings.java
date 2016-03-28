/*
 * Cloud9: A MapReduce Library for Hadoop
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you
 * may not use this file except in compliance with the License. You may
 * obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
 * implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */

package edu.umd.cloud9.examples;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;

//added HashMap package
import java.util.HashMap;
//added Map package
import java.util.Map;
//added Set package
import java.util.Set;
import java.util.List;
import java.util.StringTokenizer;

import org.apache.hadoop.fs.Path;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;

//added ArrayListWritable package
import edu.umd.cloud9.io.ArrayListWritable;
//added PairOfInts package
import edu.umd.cloud9.io.PairOfInts;
//added PairOfWritables package
import edu.umd.cloud9.io.PairOfWritables;

public class LookupPostings {
	public static void main(String[] args) throws IOException {
		
		//hard coded path to avoid setting arguments
		String[] fixed_path = {"output/build-inverted-index"};
		args = fixed_path;
		
		if (args.length != 1) {
			System.out.println("usage: [input-path]");
			System.exit(-1);
		}
		
		System.out.println("input path: " + args[0]);
		
		//calls to lookupPosting function
		lookupPosting("king", args[0].toString());
		lookupPosting("macbeth", args[0].toString());
		lookupPosting("juliet", args[0].toString());
		lookupPosting("martino", args[0].toString());

		//List<PairOfWritables<PairOfStrings, FloatWritable>> pairs =
		//SequenceFileUtils.readDirectory(new Path(args[0]));
	}

	/**
	 * Reads in the inverted index file
	 * 
	 * @param path
	 * @return
	 * @throws IOException
	 */
	private static List<PairOfWritables<Text, PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>>>> readDirectory(Path path)
			throws IOException {
		
		File dir = new File(path.toString());
		
		//variable to hold the final inverted index
        ArrayListWritable<PairOfWritables<Text, PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>>>> inverted_index_final = new ArrayListWritable<PairOfWritables<Text, PairOfWritables<IntWritable,ArrayListWritable<PairOfInts>>>>();
        
        for (File child : dir.listFiles()) {
			if (".".equals(child.getName()) || "..".equals(child.getName())) {
				continue; // Ignore the self and parent aliases.
			}
			
			FileInputStream buildInvertedIndexFile = null;
			buildInvertedIndexFile = new FileInputStream(child.toString());
			
			//Read in the file
			DataInputStream resultsStream = new DataInputStream(buildInvertedIndexFile);
			BufferedReader results = new BufferedReader(new InputStreamReader(resultsStream));
			
			StringTokenizer rToken;
			String rLine;
			
			//variable to hold inverted index
			String invertedindex;
			
			//variable to hold document frequency
            String document_frequency;
            
            //variable to hold posting
            String posting;
			
            // iterate through every line in the file
			while ((rLine = results.readLine()) != null) {
				//variable to hold postings
                ArrayListWritable<PairOfInts> postings = new ArrayListWritable<PairOfInts>();
                
                //split rLine on "\t"/tab
				rToken = new StringTokenizer(rLine, "	");
				
				//extract the meaningful information
				//extract the term
				Text term = new Text(rToken.nextToken());
				
				//extract inverted index >> (document frequency, [(docno, term_frequency)])
				invertedindex = rToken.nextToken();
				
				//split inverted index on "["
                rToken = new StringTokenizer(invertedindex, "[");
                
                //take the next token >> (int,
                document_frequency = rToken.nextToken();
                
                //extract document frequency >> int 
                document_frequency = document_frequency.substring(1, document_frequency.length() - 2);
                
                //take the next token >> (int, int)
                posting = rToken.nextToken();
                
                //extract posting >> (docno, term_frequency)
                posting = posting.substring(0, posting.length() - 2);
                
                //split posting on "(" to extract separate values: docno, term_frequency
                rToken = new StringTokenizer(posting, "(");
                
                //until there are tokens left
                while (rToken.hasMoreTokens()) {
                	
                	//split rToken on "," to extract separate values: docno, term_frequency
                    StringTokenizer pToken = new StringTokenizer(rToken.nextToken(), ",");
                    
                    //extract docno >> int
                    String docno = pToken.nextToken();
                    
                    //take the next token >> int)
                    String term_frequency = pToken.nextToken();
                    
                    //extract term_frequency >> int
                    term_frequency = term_frequency.substring(1, term_frequency.length() - 1);
                    
                    //add docno and term_frequency values to the postings array, need to be wrapped using Integer
                    postings.add(new PairOfInts(Integer.valueOf(docno), Integer.valueOf(term_frequency)));
                }
                
                //assign document_frequency value to doc_freq
                IntWritable doc_freq = new IntWritable(Integer.valueOf(document_frequency));
                
                //form inverted_index >> (doc freq, [(docno, term_frequency)])
                PairOfWritables inverted_index = new PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>>(doc_freq, postings);
                
                //add term to inverted_index >> (term, (doc_freq, [(docno, term_frequency)]))
                PairOfWritables<Text, PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>>> term_inverted_index = new PairOfWritables(term, inverted_index);
                
                //add term and inverted index to array >> [(term, (doc_freq, [(docno, term_frequency)]))]
                inverted_index_final.add(term_inverted_index);
			}
			
			if (buildInvertedIndexFile != null)
				buildInvertedIndexFile.close();
		}
        
        //return final inverted index array
		return inverted_index_final;
	}
	
	public static void lookupPosting(String term, String args) throws IOException {
		
		//variable to hold pairs of inverted index >> [(term, (doc_freq, [(docno, term_frequency)]))]
		List<PairOfWritables<Text, PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>>>> pairs;
		
		//assign read output to pairs
		pairs = readDirectory(new Path(args));
		
		//hashmap variable to hold histogram
		HashMap<String, HashMap<Integer, Integer>> histogram = new HashMap<String, HashMap<Integer, Integer>>();
		
		//variable to hold line_number for "martino"
		int line_number = 0;
        
		//for every pair in pairs
		for (PairOfWritables<Text, PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>>> pair : pairs) {
			
			//variable to hold current term, used to compare to term supplied as argument
			String term_to_compare = pair.getLeftElement().toString();
			
			//variable to hold inverted index
			PairOfWritables inverted_index = pair.getRightElement();
			
			//if current term equals to term supplied as argument
			if (term_to_compare.equals(term)) {
				
				//variable to hold entries array
				ArrayListWritable<PairOfInts> elements = (ArrayListWritable) inverted_index.getRightElement();
				
				//for every entry in entries
				for (PairOfInts element : elements) {
					
					//variable to hold term frequency
					int term_frequency = element.getRightElement();
					
					//if current term hasn't already been added to hashmap
					if (histogram.get(term) == null) {
						
						//variable to hold term frequency
						HashMap term_freq = new HashMap();
						
						//add term_frequency to term_freq and start the count with 1
						term_freq.put(term_frequency, 1);
						
						//add the term and its frequency to the histogram
						histogram.put(term, term_freq);
					
					//if current term has already been added to hashmap
					} else {
						
						//set count to 0
						int count = 0;
						
						//if current term's term frequency hasn't already been added to hashmap
						if (histogram.get(term).get(term_frequency) == null) {
						
							//start count
							count = 0;
						
						//if current term's term frequency has already been added to hashmap
						} else {
							
							//update count
							count = histogram.get(term).get(term_frequency);
						}
						
						//variable to hold term frequency
						HashMap term_freq = new HashMap(histogram.get(term));
						
						//add term_frequency to term_freq and increment the count
						term_freq.put(term_frequency, count + 1);
						
						//add the term and its frequency to the histogram
						histogram.put(term, term_freq);
					}
				}
				
			//if current term equals martino, get the line_number
			} else if (term.equals("martino")) {
				
				//variable to hold entries array
				ArrayListWritable<PairOfInts> elements = (ArrayListWritable<PairOfInts>) inverted_index.getRightElement();
				
				//variable to hold line number (docno)
				line_number = elements.get(0).getLeftElement();
			}
		}
		
		//print term supplied as argument
		System.out.println("histogram for term: " + '\"' + term + '\"');
		
		//get entries for term argument
		Set<Map.Entry<String, HashMap<Integer, Integer>>> elements = histogram.entrySet();
		
		//for every entry of the term argument
		for (Map.Entry<String, HashMap<Integer, Integer>> element : elements) {
			
			//get entry value (right element)
			Set<Map.Entry<Integer, Integer>> frequencies = element.getValue().entrySet();
			
			//for every frequency of the term argument
			for (Map.Entry<Integer, Integer> frequency : frequencies) {
				//variable to hold time/times label for keys
				String key_times;
				
				//variable to hold time/times label for labels
				String val_times;
				
				//if frequency key equals to 1 (left element)
				if (frequency.getKey() == 1) {
				
					//singular
					key_times = " time in ";
				
				//if frequency key doesn't equal to 1 (left element)
				} else {
					
					//plural
					key_times = " times in ";
				}
				
				//if frequency key equals to 1 (right element)
				if (frequency.getValue() == 1) {
				
					//singular
					val_times = " line";
				
				//if frequency key doesn't equal to 1 (right element)
				} else {
					
					//plural
					val_times = " lines";
				}
				
				//variable to hold line number of "martino" occurence
				String martino = "";
				
				//if term supplied as argument equal to "martino"
				if (term.equals("martino")) {
					
					//variable to hold line number of "martino" occurence
					martino = " with line number: " + line_number;
				}
				
				//print frequencies >> "how many times" term appears in "how many lines"
				System.out.println(frequency.getKey() + key_times + frequency.getValue() + val_times + martino);
			}
			
			//print empty line, used as separator
			System.out.println();
		}
	}
}