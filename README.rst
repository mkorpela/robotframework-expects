*************************
Robot Framework - Expects
*************************

*NOTE: This is currently an alpha version! Use with CURIOSITY and caution :D*

Library to train computers to validate expected results based on examples. Validate something big and volatile with ease. Make your testing smarter with applying machine learning.

This library exposes only one robot framework keyword: ``Should be as expected  ${VALUE}``.
It checks expectations of what a ``${VALUE}`` should be against generated expectations json file.
Expectation file is in human readable format and can be edited manually. System will generate expectations automatically.

``Should be as expected  value  id=<str>  training=<boolean>``
If you define an id, then the system more easily detects the same expectation when your test structure changes. Otherwise it uses a generated id and this breaks very easily.
Training can be set on library level, but individual expectations can be trained with the training flag without training all expectations.

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

1. Run a test multiple times in ``TRAINING`` mode to gain better validation model from multiple example runs.
2. Run a test in ``INTERACTIVE`` mode to stop execution on failing ``Should be as expected``. Then explore and make a better validation model.
3. Modifying ``_expects.json`` by hand.

When expectations change
========================

If your system changes in a way that old expectations should not be used, just remove ``_expects.json`` file and switch library to ``TRAINING`` mode. Then run your test to record new expectations.
