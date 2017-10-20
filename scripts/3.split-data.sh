#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
# functions
function display_lines(){
    cat $1 |wc -l
}


# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $baseDir/../tmp
T_FILE=$baseDir/../tmp/business.sohu.com.title.txt
C_FILE=$baseDir/../tmp/business.sohu.com.content.txt
TRAIN_T_FILE=$baseDir/../tmp/title-train.txt
TRAIN_C_FILE=$baseDir/../tmp/content-train.txt
DEV_T_FILE=$baseDir/../tmp/title-dev.txt
DEV_C_FILE=$baseDir/../tmp/content-dev.txt

awk 'NR<3000' $T_FILE  > $DEV_T_FILE
awk 'NR<3000' $C_FILE  > $DEV_C_FILE
awk 'NR>=3000' $T_FILE > $TRAIN_T_FILE
awk 'NR>=3000' $C_FILE > $TRAIN_C_FILE

display_lines $DEV_T_FILE
display_lines $DEV_C_FILE
display_lines $TRAIN_T_FILE
display_lines $TRAIN_C_FILE

