from typing import List, Optional, Dict, Mapping, Tuple, cast
import os
import re
import json
import inspect
import difflib
from cmd import Cmd
import sys
from numbers import Number
from robot.api import logger # type: ignore

class Expects:

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, interactive:bool=False) -> None:
        self.ROBOT_LIBRARY_LISTENER = self
        self.filename:str
        self.expectations:Dict[str, Dict[str, List[Dict[str, object]]]] = {"Tests":{}, "Keywords":{}}
        self._position:List[str] = []
        self._row_index:int = 0
        self._interactive = interactive
        self._expectation_index = 0
        self._current_test:str = "UNKNOWN"
        self._current_keyword:str = "UNKNOWN"

    def _start_test(self, name:str, attrs:Mapping[str, str]) -> None:
        self._position.append(name)
        self._current_test = name
        self._expectation_index = 0

    def _end_test(self, name:str, attributes) -> None:
        self._position = self._position[:-1] if len(self._position) > 1 else [attributes["longname"][:-len(name)-1]]
        self._current_test = "UNKNOWN"

    def _start_keyword(self, name:str, attrs:Mapping[str, str]) -> None:
        if attrs['libname'] == '' and attrs['type'] == 'Keyword':
            self._current_keyword = name
            self._position.append(name)
        elif not(self._position):
            self._position = ['0', '0.' + str(self._row_index)]
        else:
            self._position.append(self._position[-1] + "." + str(self._row_index))
        self._row_index = 0

    def _end_keyword(self, name:str, attrs:Mapping[str, str]) -> None:
        if attrs['libname'] == '':
            self._current_keyword = "UNKNOWN"
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

    def _store_new_expected_value(self, value:object, expectation_id:str) -> None:
        if self._current_keyword == "UNKNOWN":
            expectations = self.expectations["Tests"][self._current_test]
        else:
            expectations = self.expectations["Keywords"][self._current_keyword]
        if _is_jsonable(value):
            logger.console(f"\nRecording expected value '{value}' for id '{expectation_id}'")
            expectations.append({'value':value, 'id':expectation_id})
        else:
            logger.console(f"\nGiven object '{value}' is of type '{type(value)}' and can not be stored. Falling back to Value Inspector.")
            ComplexObjectValueInspector(value, expectation_id, expectations).cmdloop()

    def _report_unexpected(self, actual:object, expected:object) -> str:
        if isinstance(actual, str) and isinstance(expected, str):
            index = 0
            for i in (i for i, (a, e) in enumerate(zip(actual, expected)) if a != e):
                index = i
                break
            diff = "\n".join(difflib.ndiff(actual.splitlines(keepends=True), expected.splitlines(keepends=True)))
            return f"Strings differ after {index} characters:\n{diff}"
        return f"Unexpected {actual}. Expected it to be {expected}"

    def _validate_value(self, value:object, expected:object, expectation_id:str) -> None:
        if value != expected:
            if self._interactive:
                logger.console(f"\nExecution paused on row with id '{expectation_id}'")
                logger.console(f"Validation failed. '{expected}' differs from '{value}'")
                if self._current_keyword == "UNKNOWN":
                    expectations = self.expectations["Tests"][self._current_test]
                else:
                    expectations = self.expectations["Keywords"][self._current_keyword]
                NotMatchingValueInspector(value, expectation_id, expectations).cmdloop()
            else:
                raise AssertionError(self._report_unexpected(value, expected))
        else:
            logger.info(f"Value '{value}' is as expected")

    def _validate_startswith(self, value:object, expected_start:str, expectation_id:str) -> None:
        if not isinstance(value, str):
            raise AssertionError(f"Value '{value}' is not a string")
        if not value.startswith(expected_start):
            raise AssertionError(f"Value '{value}' does not start with '{expected_start}'")
        logger.info(f"Value startswith is as expected")

    def _validate_regex(self, value:object, expected:str, expectation_id:str) -> None:
        if not isinstance(value, str):
            raise AssertionError(f"Value '{value}' is not a string")
        matcher = re.compile(expected)
        if not matcher.match(value):
            raise AssertionError(f"Value '{value}' does not match")
        logger.info(f"Value matches expected")

    def _validate_min(self, value:object, expected:float, expectation_id:str) -> None:
        if not isinstance(value, Number):
            raise AssertionError(f"Value {value} is not of numeric type")
        if cast(float, value) < expected:
            raise AssertionError(f"Value {value} is smaller than {expected}")
        logger.info(f"Value is bigger than minimum expected")

    def _validate_max(self, value:object, expected:float, expectation_id:str) -> None:
        if not isinstance(value, Number):
            raise AssertionError(f"Value {value} is not of numeric type")
        if cast(float, value) > expected:
            raise AssertionError(f"Value {value} is bigger than {expected}")
        logger.info(f"Value is smaller than maximum expected")

    def _validate_fields(self, value:object, fields:Dict[str, Dict[str, object]], expectation_id:str) -> None:
        logger.info("Checking object")
        for field, val in inspect.getmembers(value):
            if field in fields:
                self._validate(val, fields[field], expectation_id)
                logger.info(f"Field '{field}' is as expected")

    def _validate(self, value:object, expected:Dict[str, object], expectation_id:str) -> None:
        if 'value' in expected:
            self._validate_value(value, expected['value'], expectation_id)
        if 'fields' in expected:
            self._validate_fields(value, cast(Dict[str, Dict[str, object]], expected['fields']), expectation_id)
        if 'startswith' in expected:
            self._validate_startswith(value, cast(str, expected['startswith']), expectation_id)
        if 'regex' in expected:
            self._validate_regex(value, cast(str, expected['regex']), expectation_id)
        if 'min' in expected:
            self._validate_min(value, cast(float, expected['min']), expectation_id)
        if 'max' in expected:
            self._validate_max(value, cast(float, expected['max']), expectation_id)

    def _find_expected(self, expectation_id:str, current_expectations:List[Dict[str, object]]) -> Optional[Dict[str, object]]:
        for exp in current_expectations:
            if exp['id'] == expectation_id:
                return exp
        if len(current_expectations) < self._expectation_index:
            return None
        return current_expectations[self._expectation_index-1]

    def should_be_as_expected(self, value:object, id:Optional[str]=None) -> None:
        expectation_id:str = id if id else self._position[-1]
        if self._current_keyword == "UNKNOWN":
            expectations = self.expectations["Tests"]
            if self._current_test not in expectations:
                expectations[self._current_test] = []
        else:
            expectations = self.expectations["Keywords"]
            if self._current_keyword not in expectations:
                expectations[self._current_keyword] = []
        current_expectations = expectations[self._current_keyword if self._current_keyword != "UNKNOWN" else self._current_test]
        self._expectation_index += 1
        expected = self._find_expected(expectation_id, current_expectations)
        if expected is None:
            self._store_new_expected_value(value, expectation_id)
        else:
            logger.debug(f"Validating that value '{value}' matches expectation")
            self._validate(value, expected, expectation_id)
            if expected['id'] != expectation_id:
                logger.debug(f"Expectation id mismatch. Expected '{expected['id']}' and was '{expectation_id}'. Updating expectation id.")
                expected['id'] = expectation_id

def _is_jsonable(x:object) -> bool:
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class _ValueInspector(Cmd):
    intro = '\n## Value inspector shell. Type help or ? to list commands. ##\n'
    prompt = 'inspector >> '

    def __init__(self, value:object, expectation_id:str, expectations:List[Dict[str, object]]) -> None:
        # Robot Framework mangles outputs and inputs
        self._oldstdin = sys.stdin
        self._oldstdout = sys.stdout
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        Cmd.__init__(self)
        self._value = value
        self._id = expectation_id
        self._expectations = expectations

    def postloop(self):
        sys.stdin = self._oldstdin
        sys.stdout = self._oldstdout


class NotMatchingValueInspector(_ValueInspector):

    def __init__(self, value:object, expectation_id:str, expectations:List[Dict[str, object]]) -> None:
        _ValueInspector.__init__(self, value, expectation_id, expectations)
        self._expected = [e for e in expectations if e["id"] == expectation_id][0]

    def do_diff(self, attrs) -> None:
        'Show diff to expected value'
        logger.console(f"Expected:{self._expected['value']}")
        logger.console(f"Actual:{self._value}")

    def do_replace(self, attrs) -> None:
        'Replace expectation with current value'
        logger.console(f"Replaced {self._expected['value']} with {self._value}")
        self._expected['value'] = self._value

    def do_min(self, minvalue:str) -> None:
        'Set min constraint. Removes value constraint.'
        min_val = float(minvalue)
        logger.console(f"Setting min value constraint to {min_val}")
        if 'value' in self._expected:
            del self._expected['value']
        self._expected['min'] = min_val

    def do_max(self, maxvalue:str) -> None:
        'Set max constraint. Removes value constraint.'
        max_val = float(maxvalue)
        logger.console(f"Setting max value constraint to {max_val}")
        if 'value' in self._expected:
            del self._expected['value']
        self._expected['max'] = max_val

    def do_startswith(self, value:str) -> None:
        'Set startswith constraint. Removes value constraint.'
        logger.console(f"Setting startswith constraint to '{value}'")
        if 'value' in self._expected:
            del self._expected['value']
        self._expected['startswith'] = value

    def do_regex(self, value:str) -> None:
        'Set regex match constraint. Removes value constraint.'
        logger.console(f"Setting regex constraint to '{value}'")
        if 'value' in self._expected:
            del self._expected['value']
        self._expected['regex'] = value

    def do_quit(self, args) -> bool:
        'Quit Value Inspector and store new expectations'
        return True


class ComplexObjectValueInspector(_ValueInspector):

    def __init__(self, value:object, expectation_id:str, expectations:List[Dict[str, object]]) -> None:
        _ValueInspector.__init__(self, value, expectation_id, expectations)
        self._fields:List[Tuple[str, Dict[str, object]]] = []
        for field, val in inspect.getmembers(self._value):
            if not field.startswith('_') and _is_jsonable(val):
                self._fields.append((field, {'value':val}))
        self._selected_fields:Dict[str, object] = {}

    def do_show(self, field:str) -> None:
        'Show value of the current object or a field'
        if field:
            for f, val in self._fields:
                if f == field:
                    logger.console(f"Field:{field}\nvalue:{val['value']}\ntype:{type(val['value'])}")
            return
        logger.console(f"\nValue: '{self._value}'")

    def complete_show(self, text:str, line:str, begidx:int, endidx:int) -> List[str]:
        completes:List[str] = []
        for field, _ in self._fields:
            if field.startswith(text):
                completes.append(field)
        return completes

    def do_expect(self, field:str) -> None:
        'Set expectation for field to contain current value'
        for f, val in self._fields:
            if f == field:
                self._selected_fields[field] = val
                logger.console(f"Set expectation for field {field}")
                return
        logger.console(f"Could not find field {field}")

    def complete_expect(self, text:str, line:str, begidx:int, endidx:int) -> List[str]:
        completes:List[str] = []
        for field, _ in self._fields:
            if field.startswith(text):
                completes.append(field)
        return completes

    def do_quit(self, args) -> bool:
        'Quit Value Inspector and store selected expectations'
        self._expectations.append({'fields':self._selected_fields, 'id':self._id})
        return True

    def do_fields(self, args) -> None:
        'Show fields with storable values'
        logger.console(f'== Fields for {self._value} ==')
        for field, _ in self._fields:
            logger.console(field)