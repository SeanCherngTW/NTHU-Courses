package page_rank;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.MapReduceBase;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import org.apache.log4j.Logger;

import java.net.URI;
import java.io.*;

/*
	 * KEY is a Text (ONE) sent from Map.
	 *
	 * VALUE is a Iterator of Double writable.
	 *
     * */

public class DanglingNodesReducer extends Reducer<Text, DoubleWritable, NullWritable, DoubleWritable>
{
    private static Long castValue = 1000000000000000000L;
    int counter = 0;
    final static Logger logger = Logger.getLogger(DanglingNodesReducer.class);
    // private int danglingNodeCount = 0;
    private static final Log LOG = LogFactory.getLog(DanglingNodesReducer.class);

    public static enum UpdateCounter
    {
        SUMOFNODES
    }

    // Total number of nodes in the data set

    public void reduce(Text key, Iterable<DoubleWritable> values, Context context) throws IOException, InterruptedException
    {

        double s = 0.0;

        for (DoubleWritable value : values)
            s += value.get();

        // if(key.toString().equals("HI")){
        //     counter++;
        //     logger.error("MUST BE 27832: " + String.valueOf(counter));
        // }

        // logger.error("MUST BE 27832: " + String.valueOf(counter));

        // String confVariable1 = context.getConfiguration().get("NODE_COUNT");
        // Integer NODE_COUNT = Integer.parseInt(confVariable1);
        // long result = (long) (s * castValue / NODE_COUNT);
        String INVERSE_INIT_PR = context.getConfiguration().get("INVERSE_INIT_PR");
        double inverseN = Double.parseDouble(INVERSE_INIT_PR);
        double resultDouble = s * inverseN * castValue;
        long result = (long) resultDouble;

        // Update the value in the counter.
        // context.getCounter(UpdateCounter.SUMOFNODES).setValue(result);
        context.getCounter(UpdateCounter.SUMOFNODES).increment(result);
        // context.getCounter(CalculateReducer.UpdateCounter.SUMOFPAGERANK).setValue(0L);
    }
}