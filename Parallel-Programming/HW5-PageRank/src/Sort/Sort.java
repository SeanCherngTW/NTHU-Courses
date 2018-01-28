package page_rank;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.KeyValueTextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

public class Sort
{
    public void Sort(String [] args) throws Exception
    {
		Configuration conf = new Configuration();

        Job job = Job.getInstance(conf, "Sort");
		job.setJarByClass(Page_Rank.class);
		// job.setNumReduceTasks(16);

		// Input
		FileInputFormat.setInputPaths(job, new Path(args[1] + "/iter01"));
        job.setInputFormatClass(TextInputFormat.class);

		// Mapper
		job.setMapOutputKeyClass(DoubleWritable.class);
		job.setMapOutputValueClass(Text.class);
		job.setMapperClass(SortMapper.class);

		// Output
		FileOutputFormat.setOutputPath(job, new Path(args[1] + "/result"));
        job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(DoubleWritable.class);
        job.setOutputValueClass(Text.class);

		job.waitForCompletion(true);
    }
}