package page_rank;

import java.io.IOException;
import java.util.StringTokenizer;
import java.util.Iterator;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.MapReduceBase;

import java.util.ArrayList;
import java.util.Arrays;
import java.net.URI;
import java.io.*;

/*
 * sample input: Mapper's output sorted by KEY
 * input format: Iterator<Text> for each KEY
 * ---------------------------------------
 * Page_B |Page_A
 * Page_C |Page_A
 * Page_C |Page_D
 * Page_A Page_B	1.0	1   ----->  PR of Page_B is 1.0
 * Page_A Page_C	1.0	2   ----->  PR of Page_C is 1.0
 * Page_D Page_C	1.0	2   ----->  PR of Page_C is 1.0
*/

/*
    input   page        dangling node
    100M	30727	    27832
    1G	    313500	    246234
    10G	    3133027	    1523520
    50G	    15982471	1030507
*/

public class CalculateReducer extends Reducer<Text, Text, Text, Text>
{
    public static enum UpdateCounter
    {
        SUMOFPAGERANK
    }

    private static Long castValue = 1000000000000000000L;
    public static final double df = 0.85;

    public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException
    {
        // context.getCounter(UpdateCounter.SUMOFPAGERANK).setValue(0);

        boolean isExistingPage = false;
        String links = "";
        double outLinksPRSum = 0.0;
        double currentPagePR = 0.0;

        for (Text value: values)
        {
            String V = value.toString();

            if(V.equals("!"))
                isExistingPage = true;

            else if(V.startsWith("#"))
                currentPagePR = Double.parseDouble(V.substring(1));

            else if(V.startsWith("|"))
                links = links + V.substring(1) + "@-@=@-@@";

            else
            {
                String[] split = V.split("\t");

                double pageRank = Double.parseDouble(split[0]);
                int countOutLinks = Integer.parseInt(split[1]);

                outLinksPRSum += (pageRank / countOutLinks);
            }
        }
        if(!isExistingPage)
            return;

        // String confVariable1 = context.getConfiguration().get("NODE_COUNT");
        // int NODE_COUNT = Integer.parseInt(confVariable1);
        String INVERSE_INIT_PR = context.getConfiguration().get("INVERSE_INIT_PR");
        double inverseN = Double.parseDouble(INVERSE_INIT_PR);
        double danglingNodesPR = context.getConfiguration().getDouble("danglingPR", 0.0);

        links = links.substring(0, links.length() - 8);


        double first = (1 - df) * inverseN;
        double second = df * outLinksPRSum;
        double third = df * danglingNodesPR;

        double newRank = first + second + third;

        // double newRank = ((1 - df) * inverseN) + (df * outLinksPRSum) + (df * danglingNodesPR);

        double currentPageErr = Math.abs(newRank - currentPagePR)  * castValue;
        long result = (long) currentPageErr;

        context.getCounter(UpdateCounter.SUMOFPAGERANK).increment(result);
        context.write(key, new Text(newRank + "\t" + links));
    }
}