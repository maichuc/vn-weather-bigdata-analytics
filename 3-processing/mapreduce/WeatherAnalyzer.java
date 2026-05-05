// =============================================================================
// TIER 3: PROCESSING LAYER - MapReduce Weather Analyzer
// File: WeatherAnalyzer.java
// Purpose: Calculate average temperature per province from JSON data on HDFS.
// =============================================================================

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;
import org.apache.hadoop.conf.Configured;

import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class WeatherAnalyzer extends Configured implements Tool {

    public static class WeatherMapper extends Mapper<LongWritable, Text, Text, DoubleWritable> {
        private final Text provinceKey = new Text();
        private final DoubleWritable tempValue = new DoubleWritable();
        
        private static final Pattern PROVINCE_PATTERN = Pattern.compile("\"province\":\\s*\"([^\"]+)\"");
        private static final Pattern TEMP_PATTERN = Pattern.compile("\"temp\":\\s*([\\d\\.-]+)");

        @Override
        protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            String line = value.toString();
            Matcher mProvince = PROVINCE_PATTERN.matcher(line);
            Matcher mTemp = TEMP_PATTERN.matcher(line);
            
            if (mProvince.find() && mTemp.find()) {
                provinceKey.set(mProvince.group(1));
                tempValue.set(Double.parseDouble(mTemp.group(1)));
                context.write(provinceKey, tempValue);
            }
        }
    }

    public static class WeatherReducer extends Reducer<Text, DoubleWritable, Text, Text> {
        @Override
        protected void reduce(Text key, Iterable<DoubleWritable> values, Context context) throws IOException, InterruptedException {
            double sum = 0;
            int count = 0;
            for (DoubleWritable val : values) {
                sum += val.get();
                count++;
            }
            double avg = sum / count;
            context.write(key, new Text(String.format("%.2f,%d", avg, count)));
        }
    }

    @Override
    public int run(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: WeatherAnalyzer <input> <output>");
            return -1;
        }

        Configuration conf = getConf();
        Job job = Job.getInstance(conf, "Weather Analyzer (MapReduce)");
        job.setJarByClass(WeatherAnalyzer.class);

        job.setMapperClass(WeatherMapper.class);
        job.setReducerClass(WeatherReducer.class);

        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(DoubleWritable.class);
        
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        job.setInputFormatClass(TextInputFormat.class);
        job.setOutputFormatClass(TextOutputFormat.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        return job.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        int exitCode = ToolRunner.run(new Configuration(), new WeatherAnalyzer(), args);
        System.exit(exitCode);
    }
}
