#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/seq2seq-textsum/src/data_processer.py
# Author: Hai Liang Wang
# Date: 2017-10-18:19:33:36
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-10-18:19:33:36"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

PLT = 2
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"
else:
    PLT = 3

import unittest
import xml.etree.ElementTree as ET
import re
import requests
import json

def resolve_utf8(word):
    if PLT == 2:
        return word.encode("utf8")
    else:
        return word

output_file = os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.raw.txt")

def append_line_to_file(line, file_path):
    with open(file_path, "a") as fout:
        fout.write(line)

def parse_xml(raw_string):
    try:
        root = ET.fromstring(raw_string)
        vals = []
        for child in root:
            vals.append(child.text)
        assert len(vals) == 4, "packed values length should be 4"
        [url, docno, contenttitle, content] = vals
        if contenttitle is not None and content is not None:
            append_line_to_file("%s ++$++ %s\n" % (contenttitle, content), output_file)
    except ET.ParseError as err:
        pass

'''
分词
'''
import jieba
import jieba.posseg as tokenizer
COMPANY_DICT_PATH = os.path.join(curdir, "resources", "vocab.company.utf8")
SOUGOU_DICT_PATH = os.path.join(curdir, "resources", "vocab.sougou.utf8")
STOPWORD_DICT_PATH = os.path.join(curdir, "resources", "stopwords.utf8")
jieba.load_userdict(COMPANY_DICT_PATH)
jieba.load_userdict(SOUGOU_DICT_PATH)
jieba_stopwords = set()

def load_stop_words():
    if len(jieba_stopwords) > 0:
        return True
    if not os.path.exists(STOPWORD_DICT_PATH):
        return None
    with open(STOPWORD_DICT_PATH, "r") as fin:
        for x in fin:
            x = x.strip()
            if not x.startswith("#"): jieba_stopwords.add(x)
    print("jieba stopwords loaded, len %d." % len(jieba_stopwords))
    return True
load_stop_words()

def seg_jieba(body):
    '''
    Jieba tokenizer
    '''
    y = tokenizer.cut(body["content"], HMM=True)
    words, tags = [], []
    for o in y:
        w = resolve_utf8(o.word)
        t = o.flag
        if "type" in body and body["type"] == "nostopword":
            if w in jieba_stopwords: continue
        if "punct" in body and body["punct"] == False:
            if t.startswith("x"): continue
        words.append(w)
        tags.append(t)
    assert len(words) == len(tags), "words and tags should be the same length with jieba tokenizer."
    return words, tags

def word_segment(utterance, vendor = "jieba"):
    '''
    segment words
    '''
    words, tags = [], []
    try:
        if vendor == "jieba":
            words, tags = seg_jieba({
                                "content": utterance,
                                "punct": False
                                })
        else:
            raise Exception("None tokenizer.")
    except Exception as e:
        print("seg error\n", utterance, e)
    return words, tags

'''
load punct
'''
punct = []
with open(os.path.join(curdir, "resources", "punctuation.utf8"), "r") as fin:
    [ punct.append(x.strip()) for x in fin.readlines()]
assert len(punct) > 0, "punct set should not be empty."

def filter_special_punct(utterance):
    '''
    remove special punct
    '''
    for o in punct:
        utterance = utterance.replace(o, " ")
    return utterance

emoji = []
with open(os.path.join(curdir, "resources", "emoji.utf8"), "r") as fin:
    [ emoji.append(x.strip()) for x in fin.readlines()]
assert len(emoji) > 0, "emoji set should not be empty."

def filter_emoji(utterance):
    '''
    remove 【emoji】
    '''
    for o in emoji:
        utterance = utterance.replace(o, "")
    return utterance

def filter_date(utterance):
    '''
    replace date with TAG_DATE
    '''
    utterance = re.sub(u"\d{1,}\s*年\d{1,}\s*月\d{1,}\s*日", "TDATE", utterance)
    utterance = re.sub(u"\d{1,}\s*月\d{1,}\s*日", "TDATE", utterance)
    utterance = re.sub(u"\d{1,}\s*月\d{1,}\s*日", "TDATE", utterance)
    utterance = re.sub(u"\d{2,}\s*年\d{1,}月", "TDATE", utterance)
    utterance = re.sub("\d{4}-\d{1,2}-\d{1,2}", "TDATE", utterance)
    return utterance

def filter_full_to_half(utterance):
    '''
    全角转换为半角: http://www.qingpingshan.com/jb/python/118505.html
    '''
    n = []
    utterance = utterance.decode('utf-8')
    for char in utterance:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        num = unichr(num)
        n.append(num)

    return ''.join(n)


def filter_eng_to_tag(utterance):
    '''
    TODO 删除全角的英文: 替换为标签TAG_NAME_EN
    由数字、26个英文字母或者下划线组成的字符串
    '''
    utterance = re.sub("[A-Za-z]+", "TENGLISH", utterance)
    return utterance

'''
load names
'''
person_names = []
with open(os.path.join(curdir, "resources", "names.utf8"), "r") as fin:
    [ person_names.append(x.strip()) for x in fin.readlines()]
assert len(person_names) > 0, "person names set should not be empty."

def filter_name(utterance):
    '''
    将人名替换成 TAG_PERSON_NAME
    '''
    result = []
    for o in utterance:
        if not o in person_names:
            result.append(o)
        else:
            result.append("TPERSON")
    return result

def filter_url(utterance):
    '''
    超链接URL：替换为标签TAG_URL
    '''
    # utterance = re.sub("[a-zA-z]+://[^\s]*", "TAG_URL", utterance)
    utterance = re.sub("http[s]?://[^\s]*", "TURL", utterance)
    return utterance

def filter_number(utterance):
    utterance = re.sub("[^a-zA-Z0-9_]+[0-9.]+", " TNUMBER", utterance)
    return utterance

def extract_sohu_full_raw_txt():
    data_path = os.path.join(curdir, os.path.pardir, "tmp", "news_sohusite_xml.uft8")
    with open(data_path, "r") as m:
        t = []
        for x in m.readlines():
            x = x.strip()
            if x == "<doc>":
                t = []
                t.append(x)
            elif x == "</doc>":
                t.append(x)
                parse_xml("".join(t))
            else:
                t.append(x)

def extract_sohu_business_raw_txt():
    resource_list = os.path.join(curdir, "resources", "news.data_list.txt")
    root_dir = os.path.join(curdir, os.path.pardir)
    data_xmls = []
    with open(resource_list, "r") as rin:
        [data_xmls.append(os.path.join(root_dir, x).strip()) for x in rin.readlines()]

    for o in data_xmls:
        with open(o, "r") as m:
            t = []
            for x in m.readlines():
                x = x.strip()
                if x == "<doc>":
                    t = []
                    t.append(x)
                elif x == "</doc>":
                    t.append(x)
                    parse_xml("".join(t))
                else:
                    t.append(x)

def solo_tnumber_utterance(utterance):
    '''
    replace multiple TNUMBER with one TNUMBER
    '''
    tokens = utterance.split()
    result = []
    pre = None
    for o in tokens:
        if pre == "TNUMBER" and o == "TNUMBER":
            pass
        elif pre == "TNUMBER" and o != "TNUMBER":
            result.append(o)
        elif pre != "TNUMBER" and o == "TNUMBER":
            result.append(o)
            pre = "TNUMBER"
        elif pre != "TNUMBER" and o != "TNUMBER":
            result.append(o)
            pre = o
    return " ".join(result)

def solo_space_utterance(utterance):
    '''
    replace multiple spaces with one space
    '''
    return re.sub(' +',' ', utterance).strip()

def preprocess_sohu_full_raw_txt():
    '''
    •   特殊字符：去除特殊字符，如：“「，」,￥,…”；
    •   括号内的内容：如表情符，【嘻嘻】，【哈哈】
    •   日期：替换日期标签为TAG_DATE，如：***年*月*日，****年*月，等等
    •   超链接URL：替换为标签TAG_URL；
    •   删除全角的英文：替换为标签TAG_NAME_EN；
    •   替换数字：TAG_NUMBER；
    '''
    file_path = os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.raw.txt")
    with open(file_path, "r") as fin:
        for x in fin.readlines():
            x = x.split(" ++$++ ")
            assert len(x) == 2, "business news should be in 2"
            title = x[0].strip()
            content = x[1].strip()
            # filters
            content = filter_full_to_half(content)
            content = filter_date(content)
            content = filter_number(content)
            content = filter_special_punct(content)
            content = filter_emoji(content)
            content = filter_url(content)
            c, _ = word_segment(content)
            c = filter_name(c)

            title = filter_full_to_half(title)
            title = filter_date(title)
            title = filter_number(title)
            title = filter_special_punct(title)
            title = filter_emoji(title)
            title = filter_url(title)
            t, _ = word_segment(title)
            t = filter_name(t)

            c = solo_tnumber_utterance(solo_space_utterance(" ".join(c))) 
            t = solo_tnumber_utterance(solo_space_utterance(" ".join(t)))

            # write line to files
            if len(c.split(" ")) > 3 and len(t.split(" ")) > 3:
                append_line_to_file(c + "\n", os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.content.txt"))
                append_line_to_file(t + "\n", os.path.join(curdir, os.path.pardir, "tmp", "full.sohu.com.title.txt"))

class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filter_url(self):
        print(filter_url("fp http://www.deepnlp.org/blog/textsum-seq2seq-attention/ 天气不错中"))

    def test_filter_date(self):
        content = "６月２０日：粮油、肉类、禽蛋、奶类价格稳定"
        content = filter_full_to_half(content)
        content = filter_special_punct(content)
        content = filter_emoji(content)
        content = filter_url(content)
        content = filter_date(content)
        content = filter_number(content)  
        print("result:", content)

    def test_filter_number(self):
        content = "G20"
        content = filter_number(content)
        print(content)

    def test_filter_special_punct(self):
        pass

    def test_extract_sohu_business_raw_txt(self):
        extract_sohu_business_raw_txt()

    def test_extract_sohu_full_raw_txt(self):
        extract_sohu_full_raw_txt()

    def test_preprocess_sohu_business_raw_txt(self):
        preprocess_sohu_business_raw_txt()

    def test_preprocess_sohu_full_raw_txt(self):
        preprocess_sohu_full_raw_txt()

def test():
    unittest.main()

if __name__ == '__main__':
    test()
