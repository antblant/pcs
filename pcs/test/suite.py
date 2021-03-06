#!/usr/bin/env python

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
import sys
import os.path

PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))
sys.path.insert(0, PACKAGE_DIR)

from pcs.test.tools import pcs_unittest as unittest

def prepare_test_name(test_name):
    """
    Sometimes we have test easy accessible with fs path format like:
    "pcs/test/test_node"
    but loader need it in module path format like:
    "pcs.test.test_node"
    so is practical accept fs path format and prepare it for loader
    """
    return test_name.replace("/", ".")

def tests_from_suite(test_candidate):
    if isinstance(test_candidate, unittest.TestCase):
        return [test_candidate.id()]
    test_id_list = []
    for test in test_candidate:
        test_id_list.extend(tests_from_suite(test))
    return test_id_list

def autodiscover_tests():
    #...Find all the test modules by recursing into subdirectories from the
    #specified start directory...
    #...All test modules must be importable from the top level of the project.
    #If the start directory is not the top level directory then the top level
    #directory must be specified separately...
    #So test are loaded from PACKAGE_DIR/pcs but their names starts with "pcs."
    return unittest.TestLoader().discover(
        start_dir=os.path.join(PACKAGE_DIR, "pcs"),
        pattern='test_*.py',
        top_level_dir=PACKAGE_DIR,
    )

def discover_tests(explicitly_enumerated_tests, exclude_enumerated_tests=False):
    if not explicitly_enumerated_tests:
        return autodiscover_tests()
    if exclude_enumerated_tests:
        return unittest.TestLoader().loadTestsFromNames([
            test_name for test_name in tests_from_suite(autodiscover_tests())
            if test_name not in explicitly_enumerated_tests
        ])
    return unittest.TestLoader().loadTestsFromNames(explicitly_enumerated_tests)

def run_tests(tests, verbose=False, color=False):
    resultclass = unittest.TextTestResult
    if color:
        from pcs.test.tools.color_text_runner import ColorTextTestResult
        resultclass = ColorTextTestResult

    testRunner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        resultclass=resultclass
    )
    return testRunner.run(tests)

explicitly_enumerated_tests = [
    prepare_test_name(arg) for arg in sys.argv[1:] if arg not in (
        "-v",
        "--color",
        "--no-color",
        "--all-but",
    )
]
test_result = run_tests(
    discover_tests(explicitly_enumerated_tests, "--all-but" in sys.argv),
    verbose="-v" in sys.argv,
    color=(
        "--color" in sys.argv
        or
        (
            sys.stdout.isatty()
            and
            sys.stderr.isatty()
            and "--no-color" not in sys.argv
        )
    ),
)
if not test_result.wasSuccessful():
    sys.exit(1)

# assume that we are in pcs root dir
#
# run all tests:
# ./pcs/test/suite.py
#
# run with printing name of runned test:
# pcs/test/suite.py -v
#
# run specific test:
# IMPORTANT: in 2.6 module.class.method doesn't work but module.class works fine
# pcs/test/suite.py pcs.test.test_acl.ACLTest -v
# pcs/test/suite.py pcs.test.test_acl.ACLTest.testAutoUpgradeofCIB
#
# run all test except some:
# pcs/test/suite.py pcs.test_acl.ACLTest --all-but
#
# for colored test report
# pcs/test/suite.py --color
