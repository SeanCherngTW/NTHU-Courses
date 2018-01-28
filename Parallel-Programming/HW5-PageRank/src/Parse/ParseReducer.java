package page_rank;

import java.io.IOException;
import java.util.Iterator;
import java.util.HashSet;
import java.util.Set;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.mapred.OutputCollector;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/* ParseReducer
 * Output: Page <pagerank\t outgoing_link>
 * E.g. B <1    A>
 *      C <1    A,D>
 * Output Format: Text (not Key-value pairs)
 */

/*
    input   page        dangling node
    100M	30727	    27832
    1G	    313500	    246234
    10G	    3133027	    1523520
    50G	    15982471	1030507
*/

public class ParseReducer extends Reducer<Text, Text, Text, Text>
{
    private static Set<String> existPageSet = new HashSet<String>();
    // private static final Log LOG = LogFactory.getLog(ParseReducer.class);
    // int counter = 0;

    public static enum UpdateCounter
    {
        NODECOUNT
    }

    public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException
    {
        String existPage = key.toString();

        if(existPage.startsWith("!"))
        {
            existPageSet.add(existPage.substring(1));
            return;
        }

        long nodeCount = (long) existPageSet.size();
        context.getCounter(UpdateCounter.NODECOUNT).setValue(nodeCount);

        double inverseInitPr = 1 / (double)nodeCount;

        // String NODE_COUNT = context.getConfiguration().get("NODE_COUNT");
        // double inverseN = 1 / Integer.parseInt(NODE_COUNT);
        // String INVERSE_INIT_PR = context.getConfiguration().get("INVERSE_INIT_PR");
        String pagerank = String.valueOf(inverseInitPr) + "\t";

        boolean isFirst = true;

        for (Text value : values)
        {
            String link = value.toString();

            if(!existPageSet.contains(link))
                continue;

            if(!isFirst)
                pagerank += "@-@=@-@@";

            pagerank += link;
            isFirst = false;
        }
        context.write(key, new Text(pagerank));
	}
}
