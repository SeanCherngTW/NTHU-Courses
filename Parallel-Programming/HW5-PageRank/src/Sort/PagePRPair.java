package page_rank;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

import org.apache.hadoop.io.Writable;
import org.apache.hadoop.io.WritableComparable;
import org.apache.hadoop.io.Text;

public class PagePRPair implements WritableComparable
{
	private Text page;
    private double pr;

    public PagePRPair()
    {
		page = new Text();
		pr = 0.0;
	}

    public PagePRPair(Text page, double pr)
    {
		this.page = page;
		this.pr = pr;
	}

	@Override
    public void write(DataOutput out) throws IOException
    {
		page.write(out);
		out.writeDouble(pr);
	}

	@Override
    public void readFields(DataInput in) throws IOException
    {
		page.readFields(in);
		pr = in.readDouble();
	}

    public Text getPage()
    {
		return page;
	}

    public double getPR()
    {
		return pr;
	}

	@Override
    public int compareTo(Object o)
    {
		double PR1 = this.getPR();
		double PR2 = ((PagePRPair)o).getPR();

		Text Page1 = this.getPage();
		Text Page2 = ((PagePRPair)o).getPage();

		// Compare between two objects
		// First order by average, and then sort them lexicographically in ascending order

		if(PR1 > PR2)
			return -1;
		else if(PR1 < PR2)
			return 1;
        else
        {
			if(strCompare(Page1.toString(), Page2.toString()) < 0)
				return -1;
			else
				return 1;
		}
	}

	private int strCompare(String s1, String s2){
		return s1.compareTo(s2);
	}
}
