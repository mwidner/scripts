#!/bin/sh
#
# This script runs MALLET on a corpus with different numbers of 
# topics and also generates detailed diagnostic output for 
# analysis of the topic quality
#
# It generates however many sub-directories it needs to store
# the different outputs (determined by $n_topics)
#
# Set the variables as needed for your project
#
# Mike Widner <mikewidner@gmail.com>
#
#####


### VARIABLES ###
mallet=/Applications/mallet/bin/mallet
n_topics=(10 20 40 80 100)
project_name=VisualizingLacuna
inputdir=/Users/widner/Projects/DLCL/Lacuna/repos/visualizing_lacuna/documents/*
outputdir=/Users/widner/Projects/DLCL/Lacuna/repos/visualizing_lacuna/mallet_output
extra_stopwords=EXTRA_STOPWORDS	# wherever they live

### IMPORT ###
mallet_import="$mallet import-dir --input $inputdir --output $outputdir/${project_name}.vectors --remove-stopwords --keep-sequence"
# if [ ! -z $extra_stopwords ]; then
# 	mallet_import="$mallet_import --extra-stopwords $extra_stopwords"
# fi

$mallet_import

### TRAIN TOPICS ###
for topics in ${n_topics[@]}
  do
    topics_output="$outputdir/$topics"
    if [ ! -d $topics_output ];
      then
        mkdir -p $topics_output
    fi
	$mallet run cc.mallet.topics.tui.TopicTrainer --input $outputdir/${project_name}.vectors --num-topics $topics --optimize-interval 20 --diagnostics-file $topics_output/diagnostics.xml --output-topic-keys $topics_output/topic-keys.txt --output-doc-topics $topics_output/doc-topics.txt --xml-topic-phrase-report $topics_output/topic-phrase-report.xml --xml-topic-report $topics_output/topic-report.xml --topic-word-weights-file $topics_output/topic-word-weights.txt --word-topic-counts-file $topics_output/word-topic-counts.txt --output-state $topics_output/state.gz
  done
