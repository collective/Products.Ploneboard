# where is 'pot'?, add your path here

import os

bin_search_path = [
    '/usr/bin',
    '/usr/local/bin',

    # for windows, the dos path needs double backslahes , e.g.
    'c:\\programme\\att\\graphviz\\bin\\',
    ]
DOT_EXE = 'dot'

if os.name == 'nt':
    DOT_EXE = 'dot.exe'
