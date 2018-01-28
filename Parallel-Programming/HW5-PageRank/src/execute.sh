#!/bin/bash
# Do not uncomment these lines to directly execute the script
# Modify the path to fit your need before using this script
# INPUT_FILE=hdfs:///user/ta/PageRank/Input/input-100M
# OUTPUT_FILE=output-100M
# JAR=Page_Rank.jar
# INPUT_FILE=/user/ta/PageRank/Input/input-100M
# OUTPUT_FILE=Page_Rank/Output
# RESULT_FILE=Page_Rank/Output/result
# JAR=Page_Rank.jar
hdfs dfs -rm -r Page_Rank/Output
hdfs dfs -rm -r Page_Rank/tmp
hadoop jar Page_Rank.jar page_rank.Page_Rank Page_Rank/Input Page_Rank/Output
# hdfs dfs -getmerge Page_Rank/tmp/result page_rank.txt