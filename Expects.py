from typing import List, Optional, Dict, Mapping
import os
import json
from robot.api import logger

class Expects:

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.filename:str
        self.expectations:Dict[str, object] = {}
        self._position:List[str] = []
        self._row_index:int = 0

    def _start_test(self, name:str, attrs:Mapping[str, str]):
        self._position.append(attrs["longname"])

    def _end_test(self, name:str, attributes):
        self._position = self._position[:-1] if len(self._position) > 1 else [attributes["longname"][:-len(name)-1]]

    def _start_keyword(self, name:str, attrs:Mapping[str, str]):
        if not(self._position):
            self._position = ['0', '0.' + str(self._row_index)]
        else:
            self._position.append(self._position[-1] + "." + str(self._row_index))
        self._row_index = 0

    def _end_keyword(self, name:str, attrs:Mapping[str, str]):
        if not(self._position):
            self._row_index = 1
            self._position = ['0']
            return
        splitted = self._position[-1].split(".")
        self._row_index = int(splitted[-1]) if len(splitted) > 1 else 0
        self._row_index += 1
        self._position = self._position[:-1] if len(self._position) > 1 else [str(int(splitted[0])+1)]

    def _start_suite(self, name:str, attrs:Mapping[str, str]):
        filename, _ = os.path.splitext(attrs['source'])
        self.filename = filename + ".json"
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                self.expectations = json.load(f)

    def _end_suite(self, name:str, attrs:Mapping[str, str]):
        with open(self.filename, "w") as f:
            json.dump(self.expectations, f, indent=4)

    def should_be_as_expected(self, value:object):
        if not os.path.isfile(self.filename):
            logger.info(f"Recording expected value {value}")
            self.expectations[self._position[-1]] = value
        else:
            logger.info(f"Validating that value {value} matches expectation")
            if value != self.expectations[self._position[-1]]:
                logger.console(f"\nExecution paused on row {self._position[-1]}")
                logger.console(f"Validation failed replace '{self.expectations[self._position[-1]]}' with new value '{value}'? [y/n]?")
                replace = input()
                if replace == 'y':
                    logger.info(f"Recording expected value {value}")
                    self.expectations[self._position[-1]] = value