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

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.StringTokenizer;

import org.apache.hadoop.fs.Path;

import org.apache.hadoop.io.FloatWritable;

import edu.umd.cloud9.io.PairOfStrings;
import edu.umd.cloud9.io.PairOfWritables;

public class AnalyzeBigramRelativeFrequency {
	public static void main(String[] args) {
		
		//hard coded path to avoid setting arguments
		String[] fixed_path = {"output/bigram-relative-frequency"};
		args = fixed_path;
		
		if (args.length != 1) {
			System.out.println("usage: [input-path]");
			System.exit(-1);
		}

		System.out.println("input path: " + args[0]);

		//List<PairOfWritables<PairOfStrings, FloatWritable>> pairs =
		//SequenceFileUtils.readDirectory(new Path(args[0]));
		
		List<PairOfWritables<PairOfStrings, FloatWritable>> pairs;
		
		try {
			pairs = readDirectory(new Path(args[0]));

			List<PairOfWritables<PairOfStrings, FloatWritable>> list1 = new ArrayList<PairOfWritables<PairOfStrings, FloatWritable>>();

			for (PairOfWritables<PairOfStrings, FloatWritable> p : pairs) {
				PairOfStrings bigram = p.getLeftElement();

				//add romeo to list1
				if (bigram.getLeftElement().equals("romeo")) {
					list1.add(p);
				}
			}
			
			//p of is given romeo
			Collections.sort(list1,
					new Comparator<PairOfWritables<PairOfStrings, FloatWritable>>() {
						public int compare(PairOfWritables<PairOfStrings, FloatWritable> e1,
								PairOfWritables<PairOfStrings, FloatWritable> e2) {
							if (e1.getRightElement().compareTo(e2.getRightElement()) == 0) {
								return e1.getLeftElement().compareTo(e2.getLeftElement());
							}

							return e2.getRightElement().compareTo(e1.getRightElement());
						}
					});

			int i = 0;
			Boolean loop = true;
			for (PairOfWritables<PairOfStrings, FloatWritable> p : list1) {
				
				PairOfStrings bigram = p.getLeftElement();
				System.out.println(bigram + "\t" + p.getRightElement());
				i++;
				
				if (i > 5) {
					break;
				}
			}
			
			//variable to hold list2
			List<PairOfWritables<PairOfStrings, FloatWritable>> list2 = new ArrayList<PairOfWritables<PairOfStrings, FloatWritable>>();
			
			//variable to hold list3
			List<PairOfWritables<PairOfStrings, FloatWritable>> list3 = new ArrayList<PairOfWritables<PairOfStrings, FloatWritable>>();
			
			//variable to hold list4
			List<PairOfWritables<PairOfStrings, FloatWritable>> list4 = new ArrayList<PairOfWritables<PairOfStrings, FloatWritable>>();
			
			//value provided in the assignment paper
			float romeo = 0.0032f;
			
			//holds p(is) - probability of is
			float is = 0.0f;
			
			//holds p(the) - probability of the
			float the = 0.0f;
			
			//holds p(king) - probability of king
			float king = 0.0f;
			
			for (PairOfWritables<PairOfStrings, FloatWritable> p : pairs) {
				PairOfStrings bigram = p.getLeftElement();

				//add romeo to list1
				if (bigram.getLeftElement().equals("romeo")) {
					list2.add(p);
				}
				
				//add is to list2
				if (bigram.getLeftElement().equals("is")) {
					list3.add(p);
				}
				
				//add the to list3
				if (bigram.getLeftElement().equals("the")) {
					list4.add(p);
				}
			}

			//p of is given romeo
			Collections.sort(list2,
					new Comparator<PairOfWritables<PairOfStrings, FloatWritable>>() {
						public int compare(PairOfWritables<PairOfStrings, FloatWritable> e1,
								PairOfWritables<PairOfStrings, FloatWritable> e2) {
							if (e1.getRightElement().compareTo(e2.getRightElement()) == 0) {
								return e1.getLeftElement().compareTo(e2.getLeftElement());
							}

							return e2.getRightElement().compareTo(e1.getRightElement());
						}
					});

			i = 0;
			loop = true;
			for (PairOfWritables<PairOfStrings, FloatWritable> p : list2) {
				
				PairOfStrings bigram = p.getLeftElement();
				i++;
				
				//if loop is false
				if (loop == false) {
				
					//stop looping
					break;
				
				//if the word to the right of the left word is "is"
				} else if (bigram.getRightElement().equals("is")) {
				
					//get right element
					String right_element = p.getRightElement().toString();
					
					//assign value of right element to variable
					is = Float.valueOf(right_element); 
					
					//stop the loop
					loop = false;
				}
			}

			//p of the given is
			Collections.sort(list3,
					new Comparator<PairOfWritables<PairOfStrings, FloatWritable>>() {
						public int compare(PairOfWritables<PairOfStrings, FloatWritable> e1,
								PairOfWritables<PairOfStrings, FloatWritable> e2) {
							if (e1.getRightElement().compareTo(e2.getRightElement()) == 0) {
								return e1.getLeftElement().compareTo(e2.getLeftElement());
							}

							return e2.getRightElement().compareTo(e1.getRightElement());
						}
					});

			i = 0;
			loop = true;
			for (PairOfWritables<PairOfStrings, FloatWritable> p : list3) {
				
				PairOfStrings bigram = p.getLeftElement();
				i++;

				//if loop is false
				if (loop == false) {
				
					//stop looping
					break;
				
				//if the word to the right of the left word is "the"
				} else if (bigram.getRightElement().equals("the")) {
					
					//get right element
					String right_element = p.getRightElement().toString();
					
					//assign value of right element to variable
					the = Float.valueOf(right_element);
					
					//stop the loop
					loop = false;
				}
			}
			
			//p of king given the
			Collections.sort(list4,
					new Comparator<PairOfWritables<PairOfStrings, FloatWritable>>() {
						public int compare(PairOfWritables<PairOfStrings, FloatWritable> e1,
								PairOfWritables<PairOfStrings, FloatWritable> e2) {
							if (e1.getRightElement().compareTo(e2.getRightElement()) == 0) {
								return e1.getLeftElement().compareTo(e2.getLeftElement());
							}

							return e2.getRightElement().compareTo(e1.getRightElement());
						}
					});

			i = 0;
			loop = true;
			for (PairOfWritables<PairOfStrings, FloatWritable> p : list4) {
				
				PairOfStrings bigram = p.getLeftElement();
				i++;
				
				//if loop is false
				if (loop == false) {
					
					//stop looping
					break;
				
				//if the word to the right of the left word is "king"
				} else if (bigram.getRightElement().equals("king")) {
					
					//get right element
					String right_element = p.getRightElement().toString();
					
					//assign value of right element to variable
					king = Float.valueOf(right_element); 
					
					//stop the loop
					loop = false;
				}
			}
			
			//print p(romeo)
			System.out.println("The given probability of \"romeo\": " + romeo);
			
			//print p(is|romeo)
			System.out.println("The probability of \"is\" given \"romeo\": " + is);
			
			//print p(the|is)
			System.out.println("The probability of \"the\" given \"is\": " + the);
			
			//print p(king|the)
			System.out.println("The probability of \"king\" given \"the\": " + king);
			
			//calculate combined frequency of "romeo is the king"
			float romeo_is_the_king = romeo * is * the * king;
			
			//print p(romeo is the king)
			System.out.println("The probability of \"romeo is the king\": " + romeo_is_the_king);
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	/**
	 * Reads in the bigram relative frequency count file
	 * 
	 * @param path
	 * @return
	 * @throws IOException
	 */
	private static List<PairOfWritables<PairOfStrings, FloatWritable>> readDirectory(Path path)
			throws IOException {

		File dir = new File(path.toString());
		ArrayList<PairOfWritables<PairOfStrings, FloatWritable>> relativeFrequencies = new ArrayList<PairOfWritables<PairOfStrings, FloatWritable>>();
		for (File child : dir.listFiles()) {
			if (".".equals(child.getName()) || "..".equals(child.getName())) {
				continue; // Ignore the self and parent aliases.
			}
			FileInputStream bigramFile = null;

			bigramFile = new FileInputStream(child.toString());

			// Read in the file
			DataInputStream resultsStream = new DataInputStream(bigramFile);
			BufferedReader results = new BufferedReader(new InputStreamReader(resultsStream));

			StringTokenizer rToken;
			String rLine;
			String firstWord;
			String secondWord;
			String frequency;

			// iterate through every line in the file
			while ((rLine = results.readLine()) != null) {
				rToken = new StringTokenizer(rLine);
				// extract the meaningful information
				firstWord = rToken.nextToken();
				//remove leading ( and trailing ,
				firstWord = firstWord.substring(1, firstWord.length() - 1);
				secondWord = rToken.nextToken();
				//remove trailing )
				secondWord = secondWord.substring(0, secondWord.length() - 1);
				frequency = rToken.nextToken();

				relativeFrequencies.add(new PairOfWritables<PairOfStrings, FloatWritable>(
						new PairOfStrings(firstWord, secondWord), new FloatWritable(Float
								.parseFloat(frequency))));

			}
			if (bigramFile != null)
				bigramFile.close();
		}

		return relativeFrequencies;
	}
}