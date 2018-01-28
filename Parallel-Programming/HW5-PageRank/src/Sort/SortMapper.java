package page_rank;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.MapReduceBase;

import java.util.ArrayList;
import java.util.Arrays;
import java.net.URI;
import java.io.*;

public class SortMapper extends Mapper<LongWritable, Text, PagePRPair, NullWritable>
{
	public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException
	{
        StringTokenizer st = new StringTokenizer(value.toString(), "\n");

        while (st.hasMoreTokens())
        {
            String V = st.nextToken();
            int tabPageIndex = V.indexOf("\t");
            int tabRankIndex = V.indexOf("\t", tabPageIndex + 1);

            Text page = new Text(V.substring(0, tabPageIndex));
            double pr = Double.parseDouble(V.substring(tabPageIndex + 1, tabRankIndex));

            context.write(new PagePRPair(page, pr), NullWritable.get());

            // context.write(new DoubleWritable(pr), new Text(page));
        }
	}
}
