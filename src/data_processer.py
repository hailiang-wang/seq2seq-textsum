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

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

import unittest
import xml.etree.ElementTree as ET

output_file = os.path.join(curdir, os.path.pardir, "tmp", "business.sohu.com.raw.txt")

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
        if "business.sohu.com" in url and contenttitle is not None and content is not None:
            append_line_to_file("%s ++$++ %s\n" % (contenttitle, content), output_file)
    except ET.ParseError as err:
        pass

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

class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sohu_business(self):
        extract_sohu_business_raw_txt()

def test():
    unittest.main()

if __name__ == '__main__':
    test()
