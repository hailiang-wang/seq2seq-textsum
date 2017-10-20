#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
# functions

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $baseDir/..
T_FILE=$baseDir/../tmp/business.sohu.com.content.txt
C_FILE=$baseDir/../tmp/business.sohu.com.title.txt
if [ -f $T_FILE ]; then
    rm $T_FILE
fi
if [ -f $C_FILE ]; then
    rm $C_FILE
fi
cd src
python data_processer.py Test.test_preprocess_sohu_business_raw_txt
set -x
cat $C_FILE|wc -l
cat $T_FILE|wc -l
