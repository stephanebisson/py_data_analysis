#!/bin/bash
clear

START=$(date +%s)

# python dataAnalysis_SB.py < r.txt
python dataAnalysis_original_ish.py < r.txt

END=$(date +%s)
DIFF=$(( $END - $START ))
echo "Duration: $DIFF seconds"

# echo "Difference:"
# diff -i 1_readyForAvg_noS_RWFixLAT.xls 1_expected.xls > diff.txt
# head -n 3 diff.txt
