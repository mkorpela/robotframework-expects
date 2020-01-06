*************************
Robot Framework - Expects
*************************

Library to train computer to validate expected results based on examples. Make your testing smarter with applying machine learning!

This library exposes one robot framework keyword: ``Should be as expected  ${VALUE}``.
It checks expectations of what a ``${VALUE}`` should be against generated expectations json file.
Expectation file is in human readable format and can be edited manually. System will generate expectations automatically.

How to use this:
================

1. Install from PyPI ``pip install robotframework-expects``
2. Add library to RF test suite in training mode ``Library  Expects  TRAINING``
3. Catch a value  ``${VALUE}= ..`` from your SUT in your test
4. Add expect block to the test ``Should be as expected  ${VALUE}``
5. Run your test ``robot yoursuite.robot`` -> generates a file ``yoursuite_expects.json``
6. Change library to normal mode ``Library  Expects`` (remove ``TRAINING``)
7. Run your tests

Improving expectations
======================

There are three ways to improve expectations:

1. Run test multiple times in ``TRAINING`` mode to gain better validation model from multiple example runs.
2. Run test in ``INTERACTIVE`` mode to stop execution on failing ``Should be as expected`` and exploring and making a better validation model.
3. Modifying ``_expects.json`` by hand.

When expectations change
========================

If your system changes in a way that old expectations should not be used, just remove ``_expects.json`` file and switch library to ``TRAINING`` mode. Then run your test to record new expectations.
