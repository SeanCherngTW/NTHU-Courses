package page_rank;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;

import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.mapred.OutputCollector;

import java.util.ArrayList;
import java.util.Arrays;
import java.net.URI;
import java.io.*;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/* ParseMapper Output: Page <Outgoing_page>
 * E.g. B <A>
 *      C <A>
 *      C <D>
 */
public class ParseMapper extends Mapper<LongWritable, Text, Text, Text> {

	public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException
	{
		boolean isDanglingNode = true;

		String currentPage = unescapeXML(value.toString());
		String title = "";

		/*  Match title pattern */
		Pattern titlePattern = Pattern.compile("<title>(.+?)</title>");
		Matcher titleMatcher = titlePattern.matcher(currentPage);

		while (titleMatcher.find())
		{
			title = titleMatcher.group();
			title = title.substring(7, title.length() - 8);
		}

		/*  Match link pattern */
		Pattern linkPattern = Pattern.compile("\\[\\[(.+?)([\\|#]|\\]\\])");
		Matcher linkMatcher = linkPattern.matcher(currentPage);

		context.write(new Text("!" + title), new Text("Exist"));

		while (linkMatcher.find())
		{
			isDanglingNode = false;

			String link = linkMatcher.group();

			if (link.endsWith("]]"))
				link = capitalizeFirstLetter(link.substring(2, link.length() - 2));
			else // link.endsWith("#" OR "|")
				link = capitalizeFirstLetter(link.substring(2, link.length() - 1));

			context.write(new Text(title), new Text(link));
		}

		if (isDanglingNode)
			context.write(new Text(title), new Text(""));

	}


	private String unescapeXML(String input)
	{
		return input.replaceAll("&lt;", "<").replaceAll("&gt;", ">").replaceAll("&amp;", "&").replaceAll("&quot;", "\"").replaceAll("&apos;", "\'");
    }

	private String capitalizeFirstLetter(String input)
	{
    	char firstChar = input.charAt(0);
		if ( firstChar >= 'a' && firstChar <='z')
		{
			if ( input.length() == 1 )
				return input.toUpperCase();
            else
                return input.substring(0, 1).toUpperCase() + input.substring(1);
        }
        else
        	return input;
    }
}
