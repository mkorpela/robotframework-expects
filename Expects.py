from typing import List, Optional, Dict, Mapping
import os
import json
from robot.api import logger # type: ignore

class Expects:

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, interactive:bool=False):
        self.ROBOT_LIBRARY_LISTENER = self
        self.filename:str
        self.expectations:List[Dict[str, object]] = []
        self._position:List[str] = []
        self._row_index:int = 0
        self._interactive = interactive
        self._expectation_index = 0

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
        self.filename = filename + "_expects.json"
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                self.expectations = json.load(f)

    def _end_suite(self, name:str, attrs:Mapping[str, str]):
        with open(self.filename, "w") as f:
            json.dump(self.expectations, f, indent=2, sort_keys=True)

    def should_be_as_expected(self, value:object, id:Optional[str]=None):
        expectation_id:str = id if id else self._position[-1]
        if not os.path.isfile(self.filename) or len(self.expectations) >= self._expectation_index:
            logger.info(f"Recording expected value '{value}' for id '{expectation_id}")
            self.expectations.append({'value':value, 'id':expectation_id})
        else:
            logger.debug(f"Validating that value '{value}' matches expectation")
            expected = self.expectations[self._expectation_index]
            if value != expected['value']:
                if self._interactive:
                    logger.console(f"\nExecution paused on row with id '{expectation_id}'")
                    logger.console(f"Validation failed replace '{expected['value']}' with new value '{value}'? [y/n]?")
                    replace = input()
                    if replace == 'y':
                        logger.info(f"Recording expected value {value}")
                        self.expectations[self._expectation_index] = {'value':value, 'id':expectation_id}
                else:
                    raise AssertionError(f"Unexpected value '{value}'. Expected '{expected['value']}'.")
            else:
                logger.info(f"Value '{value}' is as expected")
            if expected['id'] != expectation_id:
                logger.debug(f"Expectation id mismatch. Expected '{expected['id']}' and was '{expectation_id}'. Updating expectation id.")
                self.expectations[self._expectation_index]['id'] = expectation_id
        self._expectation_index += 1