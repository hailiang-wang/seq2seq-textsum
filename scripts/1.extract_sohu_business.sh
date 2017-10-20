#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
# functions

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $baseDir/../src
if [ -f $baseDir/../tmp/business.sohu.com.raw.txt ]; then
    rm $baseDir/../tmp/business.sohu.com.raw.txt
fi
python data_processer.py Test.test_extract_sohu_business_raw_txt
