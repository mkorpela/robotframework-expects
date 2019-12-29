from typing import List, Optional, Dict, Mapping, Tuple
import os
import json
import inspect
import difflib
from robot.api import logger # type: ignore

class Expects:

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, interactive:bool=False) -> None:
        self.ROBOT_LIBRARY_LISTENER = self
        self.filename:str
        self.expectations:List[Dict[str, object]] = []
        self._position:List[str] = []
        self._row_index:int = 0
        self._interactive = interactive
        self._expectation_index = 0

    def _start_test(self, name:str, attrs:Mapping[str, str]) -> None:
        self._position.append(attrs["longname"])

    def _end_test(self, name:str, attributes) -> None:
        self._position = self._position[:-1] if len(self._position) > 1 else [attributes["longname"][:-len(name)-1]]

    def _start_keyword(self, name:str, attrs:Mapping[str, str]) -> None:
        if not(self._position):
            self._position = ['0', '0.' + str(self._row_index)]
        else:
            self._position.append(self._position[-1] + "." + str(self._row_index))
        self._row_index = 0

    def _end_keyword(self, name:str, attrs:Mapping[str, str]) -> None:
        if not(self._position):
            self._row_index = 1
            self._position = ['0']
            return
        splitted = self._position[-1].split(".")
        self._row_index = int(splitted[-1]) if len(splitted) > 1 else 0
        self._row_index += 1
        self._position = self._position[:-1] if len(self._position) > 1 else [str(int(splitted[0])+1)]

    def _start_suite(self, name:str, attrs:Mapping[str, str]) -> None:
        filename, _ = os.path.splitext(attrs['source'])
        self.filename = filename + "_expects.json"
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                self.expectations = json.load(f)

    def _end_suite(self, name:str, attrs:Mapping[str, str]) -> None:
        with open(self.filename, "w") as f:
            json.dump(self.expectations, f, indent=2, sort_keys=True)

    def _is_jsonable(self, x:object) -> bool:
        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False

    def _store_new_expected_value(self, value:object, expectation_id:str) -> None:
        if self._is_jsonable(value):
            logger.console(f"Recording expected value '{value}' for id '{expectation_id}")
            self.expectations.append({'value':value, 'id':expectation_id})
        else:
            logger.console(f"\nGiven object '{value}' is of type '{type(value)}' and can not be stored")
            logger.console(f"Would you like to explore possible fields for validateable data in '{value}' [y/n]?")
            explore = input()
            if explore == 'y':
                fields:List[Tuple[str, object]] = []
                for field, val in inspect.getmembers(value):
                    if not field.startswith('_') and self._is_jsonable(val):
                        logger.console(f"{len(fields)+1}. Field '{field}' has a storable value")
                        fields.append((field, val))
                if not fields:
                    logger.console(f"No storable fields found", stream='stderr')
                    raise AssertionError("Could not expect this")
                else:
                    logger.console(f"Select fields by typing their indexes separated with a comma to store values from:")
                    field_indexes = input()
                    selected_fields = dict([fields[int(i)-1] for i in field_indexes.split(',')])
                    if not selected_fields:
                        logger.console(f"No fields selected", stream='stderr')
                        raise AssertionError("Could not expect this")
                    for f in selected_fields:
                        logger.console(f"Recording expected value for field '{f}' for id '{expectation_id}'")
                    self.expectations.append({'fields':selected_fields, 'id':expectation_id})

    def _report_unexpected(self, actual:object, expected:object) -> str:
        if isinstance(actual, str) and isinstance(expected, str):
            diff = difflib.ndiff(actual.splitlines(keepends=True), expected.splitlines(keepends=True))
            return "Strings differ:\n"+'\n'.join(diff)
        return f"Unexpected {actual}. Expected it to be {expected}"

    def _validate_value(self, value:object, expected:object, expectation_id:str) -> None:
        if value != expected:
            if self._interactive:
                logger.console(f"\nExecution paused on row with id '{expectation_id}'")
                logger.console(f"Validation failed replace '{expected}' with new value '{value}'? [y/n]?")
                replace = input()
                if replace == 'y':
                    logger.info(f"Recording expected value {value}")
                    self.expectations[self._expectation_index] = {'value':value, 'id':expectation_id}
            else:
                raise AssertionError(self._report_unexpected(value, expected))
        else:
            logger.info(f"Value '{value}' is as expected")

    def _validate_fields(self, value:object, fields:Dict[str, object], expectation_id:str) -> None:
        logger.info("Checking object")
        for field, val in inspect.getmembers(value):
            if field in fields:
                if val != fields[field]:
                    raise AssertionError(f"On field '{field}': {self._report_unexpected(val, fields[field])}")
                logger.info(f"Field '{field}' is as expected")

    def should_be_as_expected(self, value:object, id:Optional[str]=None) -> None:
        expectation_id:str = id if id else self._position[-1]
        if not os.path.isfile(self.filename) or len(self.expectations) <= self._expectation_index:
            self._store_new_expected_value(value, expectation_id)
        else:
            logger.debug(f"Validating that value '{value}' matches expectation")
            expected = self.expectations[self._expectation_index]
            if 'value' in expected:
                self._validate_value(value, expected['value'], expectation_id)
            if 'fields' in expected:
                self._validate_fields(value, expected['fields'], expectation_id)
            if expected['id'] != expectation_id:
                logger.debug(f"Expectation id mismatch. Expected '{expected['id']}' and was '{expectation_id}'. Updating expectation id.")
                self.expectations[self._expectation_index]['id'] = expectation_id
        self._expectation_index += 1