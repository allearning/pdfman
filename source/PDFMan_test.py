import re
import app_conf
import logging
from PDFMan import PDFManipulator


man = PDFManipulator(app_conf.read_config())
tests = [   "1, 2, 3, 6, 15-5-5-1, 19",
            "1,5,2,1",
            "1,2,5,1",
            "55",
            "1-11",
            "1,0,2-4",
            "100-4, 1",
            "1,,7, 3",
            "5,8,",
            "    ",
            "a"]


for test in tests:
    print(man.decode_pagenum(test))