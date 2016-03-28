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

import java.io.IOException;

import java.util.Iterator;
import java.util.StringTokenizer;
//added Collections package
import java.util.Collections;

//added PairOfInts package
import edu.umd.cloud9.io.PairOfInts;
//added PairOfWritables package
import edu.umd.cloud9.io.PairOfWritables;
//added ArrayListWritable package
import edu.umd.cloud9.io.ArrayListWritable;

//added EntryObject2IntFrequencyDistribution package
import edu.umd.cloud9.util.EntryObject2IntFrequencyDistribution;
//added Object2IntFrequencyDistribution package
import edu.umd.cloud9.util.Object2IntFrequencyDistribution;
//added PairOfObjectInt package
import edu.umd.cloud9.util.PairOfObjectInt;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;

import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobClient;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;

import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

import org.apache.log4j.Logger;

/**
 * <p>
 * Simple inverted index. This Hadoop Tool builds an inverted index in flat text file, and
 * takes the following command-line arguments:
 * </p>
 * 
 * <ul>
 * <li>[input-path] input path</li>
 * <li>[output-path] output path</li>
 * <li>[num-mappers] number of mappers</li>
 * <li>[num-reducers] number of reducers</li>
 * </ul>
 * 
 * @author Jimmy Lin
 * @author Marc Sloan
 */
public class BuildInvertedIndex extends Configured implements Tool {
	private static final Logger sLogger = Logger.getLogger(BuildInvertedIndex.class);

	/**
	 *  Mapper: emits (term, term_freq) for every word occurrence
	 *
	 */
	private static class MyMapper extends MapReduceBase implements
			Mapper<LongWritable, Text, Text, PairOfInts> {

		/**
		 *  Store an Object2IntFrequencyDistribution, which will be mapped 
		 *  to each word found in the test
		 */
		//variable to hold counts
		private final static Object2IntFrequencyDistribution<String> counts = new EntryObject2IntFrequencyDistribution<String>();
		
		/**
		 * reuse objects to save overhead of object creation
		 */
		//variable to hold term
		private Text term = new Text();

		/**
		 * Mapping function. This takes the text input, converts it into a String which is split into 
		 * words, then each of the terms is mapped to the OutputCollector with a term frequency. 
		 * 
		 * @param docno Input key, not used in this example
		 * @param doc A line of input Text taken from the data
		 * @param output Map from each term (Text) to its term_freq (PairOfInts)
		 */
		public void map(LongWritable docno, Text doc, OutputCollector<Text, PairOfInts> output,
				Reporter reporter) throws IOException {
			
			//Convert input word into String and tokenize to find words
			String line = ((Text) doc).toString();
			StringTokenizer itr = new StringTokenizer(line);
			
			//clear counts
			counts.clear();
			
			//variable to hold term
			String word = null;
			
			//For each bigram, map it to a count of one. Duplicate bigrams will be counted 
			//in the reduce phase.
			while (itr.hasMoreTokens()) {
				
				//update the word as the next token/word
				word = itr.nextToken();
				
				//if word exists
				if (word != null) {
					
					//increment frequency of word
					counts.increment(word);
				}
			}
			
			//for every count in counts
			for (PairOfObjectInt<String> count : counts) {
				
				//set term as left element of count
				term.set(count.getLeftElement());
				
				//set term frequency as the document number + the right element of count
				PairOfInts term_freq = new PairOfInts((int) docno.get(), count.getRightElement());
				
				//output term and its frequency
				output.collect(term, term_freq);
			}
		}
	}

	/**
	 * Reducer: sums up all the counts
	 *
	 */
	private static class MyReducer extends MapReduceBase implements
			Reducer<Text, PairOfInts, Text, PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>>> {

		/**
		 *  Stores the sum of counts for a term
		 */
		//variable to hold document frequency
		private final static IntWritable doc_freq = new IntWritable();

		/**
		 *  @param docno The Text term 
		 *  @param values An iterator over the values associated with this term
		 *  @param output Map from each docno (Text) to its inverted_index (PairOfWritables)
		 *  @param reporter Used to report progress
		 */
		public void reduce(Text docno, Iterator<PairOfInts> doc,
				OutputCollector<Text, PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>>> output,
				Reporter reporter) throws IOException {
			
			//sum up values
			//variable to hold frequency
			int freq = 0;
			
			//variable to hold postings
			ArrayListWritable<PairOfInts> postings = new ArrayListWritable<PairOfInts>();
			
			//until there are values left
			while (doc.hasNext()) {
				
				//add each value to the postings array by cloning it
				postings.add(doc.next().clone());
				
				//increment frequency
				freq++;
			}
			
			//sort postings array in ascending order
			Collections.sort(postings);
			
			//set document frequency
			doc_freq.set(freq);
			
			//form the inverted index: document frequency + postings
			PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>> inverted_index = new PairOfWritables<IntWritable, ArrayListWritable<PairOfInts>>(doc_freq, postings);
			
			//output document number + inverted index = docno, doc freq, postings
			output.collect(docno, inverted_index);
		}
	}

	/**
	 * Creates an instance of this tool.
	 */
	public BuildInvertedIndex() {
	}

	/**
	 *  Prints argument options
	 * @return
	 */
	private static int printUsage() {
		System.out.println("usage: [input-path] [output-path] [num-mappers] [num-reducers]");
		ToolRunner.printGenericCommandUsage(System.out);
		return -1;
	}

	/**
	 * Runs this tool.
	 */
	public int run(String[] args) throws Exception {
		if (args.length != 4) {
			printUsage();
			return -1;
		}

		String inputPath = args[0];
		String outputPath = args[1];

		int mapTasks = Integer.parseInt(args[2]);
		int reduceTasks = Integer.parseInt(args[3]);

		sLogger.info("Tool: BuildInvertedIndex");
		sLogger.info(" - input path: " + inputPath);
		sLogger.info(" - output path: " + outputPath);
		sLogger.info(" - number of mappers: " + mapTasks);
		sLogger.info(" - number of reducers: " + reduceTasks);

		JobConf conf = new JobConf(BuildInvertedIndex.class);
		conf.setJobName("BuildInvertedIndex");

		conf.setNumMapTasks(mapTasks);
		conf.setNumReduceTasks(reduceTasks);

		FileInputFormat.setInputPaths(conf, new Path(inputPath));
		FileOutputFormat.setOutputPath(conf, new Path(outputPath));
		FileOutputFormat.setCompressOutput(conf, false);

		/**
		 *  Note that these must match the Class arguments given in the mapper 
		 */
		conf.setOutputKeyClass(Text.class);
		conf.setOutputValueClass(PairOfInts.class);

		conf.setMapperClass(MyMapper.class);
		conf.setReducerClass(MyReducer.class);

		// Delete the output directory if it exists already
		Path outputDir = new Path(outputPath);
		FileSystem.get(outputDir.toUri(), conf).delete(outputDir, true);

		long startTime = System.currentTimeMillis();
		JobClient.runJob(conf);
		sLogger.info("Job Finished in " + (System.currentTimeMillis() - startTime) / 1000.0
				+ " seconds");

		return 0;
	}

	/**
	 * Dispatches command-line arguments to the tool via the
	 * <code>ToolRunner</code>.
	 */
	public static void main(String[] args) throws Exception {
		int res = ToolRunner.run(new Configuration(), new BuildInvertedIndex(), args);
		System.exit(res);
	}
}