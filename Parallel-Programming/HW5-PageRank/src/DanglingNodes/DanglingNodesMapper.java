package page_rank;

import java.io.IOException;
import java.util.StringTokenizer;

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

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/*
 * sample input:
 * input format: Text (not key-value pairs)
 * ---------------------------------------
 * Page_A\t1.0
 * Page_B\t1.0\tPage_A
 * Page_C\t1.0\tPage_A,Page_D
*/

public class DanglingNodesMapper extends Mapper<LongWritable, Text, Text, DoubleWritable>
{
    private Text ONE = new Text("1");
    private double danglingNodesPR = 0.0;
    private DoubleWritable PAGERANK = new DoubleWritable();
    // private static final Log LOG = LogFactory.getLog(DanglingNodesMapper.class);

	public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException
	{
        // String page = value.toString();

        // int pageTabIndex = page.indexOf("\t");
        // int rankTabIndex = page.indexOf("\t", pageTabIndex + 1);

        // String outGoingLinks = page.substring(rankTabIndex + 1);
        // String currnetPagePR = page.substring(pageTabIndex + 1, rankTabIndex);

        // if(outGoingLinks.equals(""))
        //     danglingNodesPR += Double.parseDouble(currnetPagePR);

        int pageTabIndex = value.find("\t");
        int rankTabIndex = value.find("\t", pageTabIndex + 1);
        String currentPagePR = Text.decode(value.getBytes(), pageTabIndex + 1, rankTabIndex - (pageTabIndex + 1));
        String outGoingLinks = Text.decode(value.getBytes(), rankTabIndex + 1, value.getLength() - (rankTabIndex + 1));

        if(outGoingLinks.equals(""))
        {
            // context.write(new Text("HI"), new DoubleWritable(0));
            danglingNodesPR += Double.parseDouble(currentPagePR);
        }
    }

    protected void cleanup(Context context) throws IOException, InterruptedException
    {
		PAGERANK.set(danglingNodesPR);
		context.write(ONE, PAGERANK);
		// danglingNodesPR = 0.0;
	}
}
