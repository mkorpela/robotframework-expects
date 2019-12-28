import os
import json
from typing import List

class Expects:

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.filename = None
        self.expectations = {}
        self._position:List[str] = []
        self._row_index = 0

    def _start_test(self, name, attributes):
        self._position.append(attributes["longname"])

    def _end_test(self, name, attributes):
        self._position = self._position[:-1] if len(self._position) > 1 else [attributes["longname"][:-len(name)-1]]

    def _start_keyword(self, name, attributes):
        if not(self._position):
            self._position = ['0', '0.' + str(self._row_index)]
        else:
            self._position.append(self._position[-1] + "." + str(self._row_index))
        self._row_index = 0

    def _end_keyword(self, name, attributes):
        if not(self._position):
            self._row_index = 1
            self._position = ['0']
            return
        splitted = self._position[-1].split(".")
        self._row_index = int(splitted[-1]) if len(splitted) > 1 else 0
        self._row_index += 1
        self._position = self._position[:-1] if len(self._position) > 1 else [str(int(splitted[0])+1)]

    def _start_suite(self, name, attrs):
        filename, _ = os.path.splitext(attrs['source'])
        self.filename = filename + ".json"
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                self.expectations = json.load(f)

    def _end_suite(self, name, attrs):
        if not os.path.isfile(self.filename):
            with open(self.filename, "w") as f:
                json.dump(self.expectations, f, indent=4)

    def should_be_as_expected(self, value):
        if not os.path.isfile(self.filename):
            print(f"Recording expected value {value}")
            self.expectations[self._position[-1]] = value
        else:
            print(f"Validating that value {value} matches expectation")
            assert value == self.expectations[self._position[-1]]