package page_rank;

import java.io.IOException;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.io.NullWritable;

public class SortReducer extends Reducer<PagePRPair, NullWritable, Text, Text> {

    public void reduce(PagePRPair key, Iterable<NullWritable> values, Context context) throws IOException, InterruptedException
    {
        Text K = key.getPage();
        Text V = new Text(Double.toString(key.getPR()));

        context.write(K, V);

        // context.write(values, new Text(key.toString()));
    }
}