#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
# functions

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
# source /root/venv-py3/bin/activate
# http://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
export TF_CPP_MIN_LOG_LEVEL=3
cd $baseDir/../src
python run.py \
    --train_dir news/ \
    --vocab_size 10000 \
    --size 512 \
    --data_path news/train \
    --dev_data news/dev  \
    --vocab_path news/vocab \
    --attention \
