#!/usr/bin/env python3

import os
import sys
import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('tests')

    # Suppress any print statements.
    runner = unittest.runner.TextTestRunner(buffer=True)

    if not runner.run(tests).wasSuccessful():
        sys.exit(os.EX_SOFTWARE)

