# -*- coding: utf-8 -*-

# Copyright © 2009 Alessandro Morandi (email : webmaster@simbul.net)
#
# This file is part of pymeo.
# 
# pymeo is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pymeo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with pymeo.  If not, see <http://www.gnu.org/licenses/>.

import sys
sys.path.append('.')
sys.path.append('..')

import unittest

from pymeo import pymeo
from tests import mocks
from tests import test_advanced, test_simple, test_consistency

# Comment the following line to run the test against the remote server
pymeo.urllib2.urlopen = mocks.dummy_urlopen

def main():
    cases = []
    
    for module in [test_advanced, test_simple, test_consistency]:
        cases.append(unittest.TestLoader().loadTestsFromModule(module))
    
    suite = unittest.TestSuite(cases)
    
    unittest.TextTestRunner(verbosity=1).run(suite)

if __name__ == '__main__':
    if pymeo.urllib2.urlopen == mocks.dummy_urlopen:
        print "Running tests against mock Vimeo server"
    main()