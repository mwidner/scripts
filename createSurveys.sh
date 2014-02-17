#!/bin/sh
s2g=./survey2graph.py
input=DLCLFacultySurvey.csv
config=DLCLFacultySurvey.ini
rm -rf unimodal
rm -rf loose_ends
rm -rf bimodal
$s2g --input $input --config $config --output unimodal
$s2g --input $input --config $config --output loose --loose_ends
$s2g --input $input --config $config --output bimodal --bimodal
