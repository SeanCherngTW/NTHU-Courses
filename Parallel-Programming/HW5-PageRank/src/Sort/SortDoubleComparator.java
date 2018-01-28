package page_rank;

import java.io.*;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.WritableComparable;
import org.apache.hadoop.io.WritableComparator;

public class SortDoubleComparator extends WritableComparator
{
    protected SortDoubleComparator()
    {
		super(DoubleWritable.class, true);
	}

	@SuppressWarnings("rawtypes")

	@Override
    public int compare(WritableComparable w1, WritableComparable w2)
    {
		DoubleWritable k1 = (DoubleWritable) w1;
		DoubleWritable k2 = (DoubleWritable) w2;

		return -1 * k1.compareTo(k2);
	}
}