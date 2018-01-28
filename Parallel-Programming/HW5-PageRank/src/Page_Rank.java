package page_rank;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

import java.io.IOException;
import java.text.DecimalFormat;
import java.text.NumberFormat;

public class Page_Rank extends Configured implements Tool
{
	private static ArrayList<Double> errList = new ArrayList<Double>();

	private static Long castValue = 1000000000000000000L;

	private static int nodeCount = 0;
	private static Double inverseN = 0.0;
	private static Long nodeCountLong = 0L;

	private static Long danglingNodesPRLong = 0L;
	private static Double danglingNodesPR = 0.0;

	private static Long sumOfPRLong = 0L;
	private static Double sumOfPR = 0.0;

	private double curSumOfPR = 0.0;
	private double newSumOfPR = 0.0;

	private static int NODE_COUNT = 0;
	private static double INVERSE_INIT_PR = 0.0;
	private static NumberFormat nf = new DecimalFormat("00");

    public static void main(String[] args) throws Exception
    {
		/*
		 * args[0] = Input path
		 * args[1] = Output path
		 * args[2] = num of iter
		 */
		System.exit(ToolRunner.run(new Configuration(), new Page_Rank(), args));
	}

	@Override
	public int run(String[] args) throws Exception
	{
		boolean isUntilConvergence = true;
		int iterTimes = 100;
		if(args.length == 3)
		{
			iterTimes = Integer.parseInt(args[2]);
			isUntilConvergence = false;
		}

		String inputPath = args[0];
		String outputPath = args[1];
		if(!outputPath.endsWith("/"))
			outputPath += "/";

		String tmpPath = outputPath + "tmp/iter";
		String dnPath = outputPath + "tmp/danglingnodes";
		String outPath = outputPath + "result";

		// String dataSize = "";

		// if(inputPath.contains("input-100M"))
		// {
		// 	dataSize = "100M";
		// 	NODE_COUNT = 30727;
		// 	INVERSE_INIT_PR = 0.00003254466;
		// }
		// else if (inputPath.contains("input-1G"))
		// {
		// 	dataSize = "1G";
		// 	NODE_COUNT = 313500;
		// 	INVERSE_INIT_PR = 0.00000318979;
		// }
		// else if (inputPath.contains("input-10G"))
		// {
		// 	dataSize = "10G";
		// 	NODE_COUNT = 3133027;
		// 	INVERSE_INIT_PR = 0.000000319180141;
		// }
		// else // (inputPath.contains("input-50G"))
		// {
		// 	dataSize = "50G";
		// 	NODE_COUNT = 15982471;
		// 	INVERSE_INIT_PR = 0.0000000625685478;
		// }

		System.out.println("----------Job1 is started----------");
		nodeCount = Parse(inputPath, tmpPath + nf.format(00));
		inverseN = 1 / (double)nodeCount;

		System.out.println("----------Job1 is finished----------");

		String inPath = null;
		String lastDanglingNodesPath = null;
		String lastResultPath = null;
		// String lastConvergencePath = null;
		double _err = 0.0;

		System.out.println("----------Job2 is started----------");

		for (int runs = 0; runs < iterTimes; runs++)
		{
            inPath = tmpPath + nf.format(runs);
			lastResultPath = tmpPath + nf.format(runs + 1);
			lastDanglingNodesPath = dnPath + nf.format(runs + 1);
			// lastConvergencePath = "/Page_Rank/tmp/convergence" + nf.format(runs + 1);

			System.out.println("----------Job2 danglingnodes" + nf.format(runs + 1) + " is started----------");
			danglingNodesPR = DanglingNodes(inPath, lastDanglingNodesPath, inverseN);
			System.out.println("----------Job2 danglingnodes" + nf.format(runs + 1) +  " is finished----------");

			System.out.println("----------Job2 iter" + nf.format(runs + 1) + " is started----------");
			newSumOfPR = Calculate(inPath, lastResultPath, danglingNodesPR, inverseN);
			System.out.println("----------Job2 iter" + nf.format(runs + 1) + " is finished----------");

			// System.out.println("----------Job2 errcount" + nf.format(runs + 1) + " is started----------");
			// newSumOfPR = Convergence(lastResultPath, lastConvergencePath);
			// System.out.println("----------Job2 errcount" + nf.format(runs + 1) + " is finished----------");

			_err = Math.abs(newSumOfPR - curSumOfPR);
			System.out.println("curSumOfPR = " + curSumOfPR);
			System.out.println("newSumOfPR = " + newSumOfPR);
			System.out.println("danglingNodesPR = " + danglingNodesPR);
			System.out.println("err of iter " + nf.format(runs + 1) + " = " + _err);
			errList.add(_err);

			if (isUntilConvergence && _err < 0.001)
				break;

			curSumOfPR = newSumOfPR;
		}
		System.out.println("Job2 is finished");

		System.out.println("Job3 is started");
		Sort(lastResultPath, outPath);
		System.out.println("Job3 is finished");

		int i = 1;
		for(Double err : errList)
		{
			System.out.println("iter " + i + ", err = " + err);
			i++;
		}

        return 0;
    }

	public int Parse(String inPath, String outPath) throws Exception
    {
		Configuration conf = new Configuration();
		// conf.set("NODE_COUNT", String.valueOf(NODE_COUNT));
		// conf.set("INVERSE_INIT_PR", String.valueOf(INVERSE_INIT_PR));
		Job job = Job.getInstance(conf, "Parse");
		job.setJarByClass(Page_Rank.class);
		// job.setNumReduceTasks(16);

		// Input
		FileInputFormat.addInputPath(job, new Path(inPath));
		job.setInputFormatClass(TextInputFormat.class);

		// Mapper
		job.setMapOutputKeyClass(Text.class);
		job.setMapOutputValueClass(Text.class);
		job.setMapperClass(ParseMapper.class);

		// Reducer
		job.setReducerClass(ParseReducer.class);

		// Output
		FileOutputFormat.setOutputPath(job, new Path(outPath));
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);

		job.waitForCompletion(true);

		nodeCountLong = job.getCounters()
				.findCounter(ParseReducer.UpdateCounter.NODECOUNT)
				.getValue();

		nodeCount = nodeCountLong.intValue();

		// Conf supports long data type, convert it back to float.
		// danglingNodesPR = ((double) danglingNodesPRLong) / castValue;


		return nodeCount;
	}

	public double DanglingNodes(String inPath, String outPath, double inverseN) throws Exception
	{
		Configuration conf = new Configuration();
		conf.set("INVERSE_INIT_PR", String.valueOf(inverseN));
		// conf.set("INVERSE_INIT_PR", String.valueOf(INVERSE_INIT_PR));

		Job job = Job.getInstance(conf, "DanglingNodes");
		job.setJarByClass(Page_Rank.class);
		// job.setNumReduceTasks(16);

		// Input
		FileInputFormat.addInputPath(job, new Path(inPath));

		// Mapper
		job.setMapperClass(DanglingNodesMapper.class);

		// Reducer
		job.setReducerClass(DanglingNodesReducer.class);
		job.setNumReduceTasks(1);

		// Output
		FileOutputFormat.setOutputPath(job, new Path(outPath));
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(DoubleWritable.class);

		job.waitForCompletion(true);

		danglingNodesPRLong = job.getCounters()
				.findCounter(DanglingNodesReducer.UpdateCounter.SUMOFNODES)
				.getValue();

		// Conf supports long data type, convert it back to float.
		danglingNodesPR = ((double) danglingNodesPRLong) / castValue;

		// job.getCounters().findCounter(DanglingNodesReducer.UpdateCounter.SUMOFNODES).setValue(0L);
		return danglingNodesPR;
	}

	public double Calculate(String inPath, String outPath, double danglingNodesPR, double inverseN) throws Exception
    {
		Configuration conf = new Configuration();
		// conf.set("NODE_COUNT", String.valueOf(NODE_COUNT));
		conf.set("INVERSE_INIT_PR", String.valueOf(inverseN));
		conf.setDouble("danglingPR", danglingNodesPR);

        Job job = Job.getInstance(conf, "Calculate");
		job.setJarByClass(Page_Rank.class);
		// job.setNumReduceTasks(16);

		// Input
		FileInputFormat.setInputPaths(job, new Path(inPath));
        job.setInputFormatClass(TextInputFormat.class);

		// Mapper
		job.setMapOutputKeyClass(Text.class);
		job.setMapOutputValueClass(Text.class);
		job.setMapperClass(CalculateMapper.class);

		// Output
		FileOutputFormat.setOutputPath(job, new Path(outPath));
        job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

		// Reducer
		job.setReducerClass(CalculateReducer.class);
		job.setNumReduceTasks(1);

		job.waitForCompletion(true);
		sumOfPRLong = job.getCounters()
				.findCounter(CalculateReducer.UpdateCounter.SUMOFPAGERANK)
				.getValue();

		// Conf supports long data type, convert it back to float.
		sumOfPR = ((double) sumOfPRLong) / castValue;

		// job.getCounters().findCounter(CalculateReducer.UpdateCounter.SUMOFPAGERANK).setValue(0L);

		return sumOfPR;
	}

	// public double Convergence(String inPath, String outPath) throws Exception
	// {
	// 	Configuration conf = new Configuration();
	// 	Job job = Job.getInstance(conf, "Convergence");
	// 	job.setJarByClass(Page_Rank.class);
	// 	// job.setNumReduceTasks(16);

	// 	// Input
	// 	FileInputFormat.addInputPath(job, new Path(inPath));

	// 	// Mapper
	// 	job.setMapperClass(ConvergenceMapper.class);

	// 	// Reducer
	// 	job.setReducerClass(ConvergenceReducer.class);

	// 	// Output
	// 	FileOutputFormat.setOutputPath(job, new Path(outPath));
	// 	job.setOutputKeyClass(Text.class);
	// 	job.setOutputValueClass(DoubleWritable.class);

	// 	job.waitForCompletion(true);
	// 	sumOfPRLong = job.getCounters()
	// 			.findCounter(ConvergenceReducer.UpdateCounter.SUMOFPAGERANK)
	// 			.getValue();

	// 	// Conf supports long data type, convert it back to float.
	// 	sumOfPR = ((double) sumOfPRLong) / castValue;

	// 	return sumOfPR;
	// }

	public boolean Sort(String inPath, String outPath) throws Exception
    {
		Configuration conf = new Configuration();

        Job job = Job.getInstance(conf, "Sort");
		job.setJarByClass(Page_Rank.class);
		// job.setNumReduceTasks(16);

		// Input
		FileInputFormat.setInputPaths(job, new Path(inPath));
        job.setInputFormatClass(TextInputFormat.class);

		// Mapper
		job.setMapOutputKeyClass(PagePRPair.class);
		job.setMapOutputValueClass(NullWritable.class);
		job.setMapperClass(SortMapper.class);

		// job.setSortComparatorClass(SortDoubleComparator.class);

		// Output
		FileOutputFormat.setOutputPath(job, new Path(outPath));
        job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);

		// Reducer
		job.setReducerClass(SortReducer.class);
		job.setNumReduceTasks(1);

		return job.waitForCompletion(true);
    }
}