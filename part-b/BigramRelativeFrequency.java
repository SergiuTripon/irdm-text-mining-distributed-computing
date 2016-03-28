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

//added PairOfStrings package
import edu.umd.cloud9.io.PairOfStrings;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
//added FloatWritable package
import org.apache.hadoop.io.FloatWritable;

import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobClient;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Partitioner;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;

import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

import org.apache.log4j.Logger;

/**
 * <p>
 * Simple bigram relative frequency. This Hadoop Tool counts bigram relative frequency in flat text file, and
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
public class BigramRelativeFrequency extends Configured implements Tool {
	private static final Logger sLogger = Logger.getLogger(BigramRelativeFrequency.class);

	/**
	 *  Mapper: emits (token + " " + token, 1) for every bigram occurrence
	 *
	 */
	
	private static class MyMapper extends MapReduceBase implements
			Mapper<LongWritable, Text, PairOfStrings, FloatWritable> {

		/**
		 *  Store an IntWritable with a value of 1, which will be mapped 
		 *  to each bigram found in the test
		 */
		private final static FloatWritable one = new FloatWritable(1);
		
		/**
		 * reuse objects to save overhead of object creation
		 */
		//variable to hold bigram
		private final static PairOfStrings bigram = new PairOfStrings();

		/**
		 * Mapping function. This takes the text input, converts it into a String which is split into 
		 * words, then each of the bigrams is mapped to the OutputCollector with a count of 
		 * one. 
		 * 
		 * @param key Input key, not used in this example
		 * @param value A line of input Text taken from the data
		 * @param output Map from each bigram (PairOfStrings) to its count (IntWritable)
		 */
		public void map(LongWritable key, Text value, OutputCollector<PairOfStrings, FloatWritable> output,
				Reporter reporter) throws IOException {
			
			//Convert input word into String and tokenize to find words
			String line = ((Text) value).toString();
			StringTokenizer itr = new StringTokenizer(line);
			
			//variable to hold previous word
			String previous_word = null;
			
			//variable to hold current word
			String current_word;
			
			//For each bigram, map it to a count of one. Duplicate bigrams will be counted 
			//in the reduce phase.
			while (itr.hasMoreTokens()) {
				
				//update the current word as the next word
				current_word = itr.nextToken();
				
				//if there is a previous word before the current word
				if (previous_word != null) {
					
					//form bigram of previous word and current word
					bigram.set(previous_word, current_word);
					
					//output the bigram
					output.collect(bigram, one);
					
					//form bigram of previous word and current word
					bigram.set(previous_word, "***");
					
					//output the bigram
					output.collect(bigram, one);
				}
				
				//update the previous word as the current word
				previous_word = current_word;
			}
		}
	}
	
	/**
	 * Combiner: sums up all the counts
	 *
	 */
	private static class MyCombiner extends MapReduceBase implements
			Reducer<PairOfStrings, FloatWritable, PairOfStrings, FloatWritable> {

		/**
		 *  Stores the sum of counts for a bigram
		 */
		private final static FloatWritable SumValue = new FloatWritable();

		/**
		 *  @param key The Text bigram 
		 *  @param values An iterator over the values associated with this word
		 *  @param output Map from each bigram (PairOfStrings) to its sum (FloatWritable)
		 *  @param reporter Used to report progress
		 */
		@Override
		public void reduce(PairOfStrings key, Iterator<FloatWritable> values,
				OutputCollector<PairOfStrings, FloatWritable> output, Reporter reporter) throws IOException {
			
			//sum up values
			int sum = 0;
			while (values.hasNext()) {
				
				sum += values.next().get();
			}
			
			SumValue.set(sum);
			output.collect(key, SumValue);
		}
	}

	/**
	 * Reducer: sums up all the counts
	 *
	 */
	private static class MyReducer extends MapReduceBase implements
			Reducer<PairOfStrings, FloatWritable, PairOfStrings, FloatWritable> {

		/**
		 *  Stores the sum of counts for a bigram
		 */
		private final static FloatWritable SumValue = new FloatWritable();
		private float each_frequency = 0.0f;

		/**
		 *  @param key The Text bigram 
		 *  @param values An iterator over the values associated with this word
		 *  @param output Map from each bigram (PairOfStrings) to its sum (FloatWritable)
		 *  @param reporter Used to report progress
		 */
		public void reduce(PairOfStrings key, Iterator<FloatWritable> values,
				OutputCollector<PairOfStrings, FloatWritable> output, Reporter reporter) throws IOException {
			
			//sum up values
			float sum = 0.0f;
			while (values.hasNext()) {
				
				sum += values.next().get();
			}
			
			//if the right element of the bigram equals to "***"
			//this will output the frequency of any word followed by the word supplied as argument
			if (key.getRightElement().equals("***")) {
				
				//update sum
				SumValue.set(sum);
				
				//output bigram and its sum
				output.collect(key, SumValue);
				
				//update each_frequency as the sum 
				each_frequency = sum;
			
			//if the right element of the bigram doesn't equal to "***"
			//this will output frequencies for every bigram that contains the word supplied as argument
			} else {
				
				//set sum as the sum divided by each_frequency
				SumValue.set(sum / each_frequency);
				
				//output bigram and its sum
				output.collect(key, SumValue);
			}
		}
	}
	
	/**
	 * Partitioner controls the partitioning of the keys of the intermediate map-outputs.
	 * The key (or a subset of the key) is used to derive the partition, typically by a
	 * hash function. The total number of partitions is the same as the number of reduce
	 * tasks for the job. Hence this controls which of the m reduce tasks the intermediate
	 * key (and hence the record) is sent for reduction.
	 */
	protected static class MyPartitioner extends MapReduceBase implements
			Partitioner<PairOfStrings, FloatWritable> {
		@Override
		public int getPartition(PairOfStrings key, FloatWritable value, int numReduceTasks) {
			return (key.getLeftElement().hashCode() & Integer.MAX_VALUE) % numReduceTasks;
		}
	}

	/**
	 * Creates an instance of this tool.
	 */
	public BigramRelativeFrequency() {
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

		sLogger.info("Tool: BigramRelativeFrequency");
		sLogger.info(" - input path: " + inputPath);
		sLogger.info(" - output path: " + outputPath);
		sLogger.info(" - number of mappers: " + mapTasks);
		sLogger.info(" - number of reducers: " + reduceTasks);

		JobConf conf = new JobConf(BigramRelativeFrequency.class);
		conf.setJobName("BigramRelativeFrequency");

		conf.setNumMapTasks(mapTasks);
		conf.setNumReduceTasks(reduceTasks);

		FileInputFormat.setInputPaths(conf, new Path(inputPath));
		FileOutputFormat.setOutputPath(conf, new Path(outputPath));
		FileOutputFormat.setCompressOutput(conf, false);

		/**
		 *  Note that these must match the Class arguments given in the mapper 
		 */
		conf.setOutputKeyClass(PairOfStrings.class);
		conf.setOutputValueClass(FloatWritable.class);

		conf.setMapperClass(MyMapper.class);
		conf.setCombinerClass(MyCombiner.class);
		conf.setReducerClass(MyReducer.class);
		conf.setPartitionerClass(MyPartitioner.class);

		//Delete the output directory if it exists already
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
		int res = ToolRunner.run(new Configuration(), new BigramRelativeFrequency(), args);
		System.exit(res);
	}
}