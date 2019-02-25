#!/usr/bin/env python
import fileinput
import re

skip_lines = True
for line in fileinput.input():
        ## LINES FILTERED UNTIL NOT FIRST SEP APPEARS
        line = re.sub('\s+', ' ',line)
        m = re.search(r"\(([A-Za-z0-9_,:/\s]+)\)", line)
        if(m is not None):
                matched = m.group(1)
                pat_list = re.findall("[A-Za-z0-9_,:/]+",matched)
		if len(pat_list) > 1:
		   print line

