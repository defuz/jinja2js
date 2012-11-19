# -*- coding: utf-8 -*-
import sys
import unittest
from os import path

sys.path.append(path.dirname(path.abspath(__file__)))

from jinja2js.testsuite import suite

if __name__ == '__main__':
	unittest.TextTestRunner(descriptions=False, verbosity=3).run(suite())
