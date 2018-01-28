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

/*
 * sample input:
 * input format: Text (not key-value pairs)
 * ---------------------------------------
 * Page_A\t1.0
 * Page_B\t1.0\tPage_A
 * Page_C\t1.0\tPage_A,Page_D
*/

public class CalculateMapper extends Mapper<LongWritable, Text, Text, Text>
{
	public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException
	{
        // String page = value.toString();

        // int pageTabIndex = page.indexOf("\t");
        // int rankTabIndex = page.indexOf("\t", pageTabIndex + 1);

        // String currentPage = page.substring(0, pageTabIndex);
        // String currentPagePR = page.substring(pageTabIndex + 1, rankTabIndex);
        // String outGoingLinks = page.substring(rankTabIndex + 1);

        // if(outGoingLinks.equals(""))
        //     return;

        int pageTabIndex = value.find("\t");
        int rankTabIndex = value.find("\t", pageTabIndex + 1);

        // Skip pages with no links. (dangling nodes)
        if(rankTabIndex == -1)
        {
            String page = value.toString();
            String currentPage = page.substring(0, pageTabIndex);
            String currentPagePR = page.substring(pageTabIndex + 1);
            // String currentPage = Text.decode(value.getBytes(), 0, pageTabIndex);
            // String currentPagePR = Text.decode(value.getBytes(), pageTabIndex + 1, value.getLength() - (pageTabIndex + 1));
            // context.write(new Text(currentPage), new Text("|"));
            context.write(new Text(currentPage), new Text("!"));
            context.write(new Text(currentPage), new Text("#" + currentPagePR));
            return;
        }

        String currentPage = Text.decode(value.getBytes(), 0, pageTabIndex);
        String currentPagePR = Text.decode(value.getBytes(), pageTabIndex + 1, rankTabIndex - (pageTabIndex + 1));
        String outGoingLinks = Text.decode(value.getBytes(), rankTabIndex + 1, value.getLength() - (rankTabIndex + 1));

        context.write(new Text(currentPage), new Text("!"));

        String[] outGoingLinksArray = outGoingLinks.split("@-@=@-@@");

        for (String outGoingLink : outGoingLinksArray)
        {
            Text pageRankTotalLinks = new Text(currentPagePR + "\t" + outGoingLinksArray.length);
            context.write(new Text(outGoingLink), pageRankTotalLinks);
            context.write(new Text(currentPage), new Text("|" + outGoingLink));
        }

        // context.write(new Text(currentPage), new Text("|" + outGoingLinks));
        context.write(new Text(currentPage), new Text("#" + currentPagePR));
    }
}
