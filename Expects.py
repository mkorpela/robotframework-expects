from typing import List, Optional, Dict, Mapping, Tuple, cast, Set
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

    def __init__(self, mode:str='NORMAL') -> None:
        '''mode can be NORMAL, INTERACTIVE or AUTOMATIC
        NORMAL = validate results against expectations
        INTERACTIVE = pause execution on validation failure and allow changes to validation criteria
        AUTOMATIC = store all values as expectations
        '''
        self.ROBOT_LIBRARY_LISTENER = self
        self.filename:str
        self.expectations:Dict[str, Dict[str, List[Dict[str, object]]]] = {"Tests":{}, "Keywords":{}}
        self._position:List[str] = []
        self._row_index:int = 0
        self._mode = mode
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
            if not Validator().validate(value, expected):
                if self._mode == 'INTERACTIVE':
                    logger.console(f"\nExecution paused on row with id '{expectation_id}'")
                    NotMatchingValueInspector(value, expectation_id, current_expectations).cmdloop()
                    if not Validator().validate(value, expected):
                        raise AssertionError(f"Unexpected {value}")
                else:
                    raise AssertionError(f"Unexpected {value}")
            if expected['id'] != expectation_id:
                logger.debug(f"Expectation id mismatch. Expected '{expected['id']}' and was '{expectation_id}'. Updating expectation id.")
                expected['id'] = expectation_id

def _is_jsonable(x:object) -> bool:
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class Validator:

    def validate(self, value:object, expected:Dict[str, object]) -> bool:
        isValid = True
        if 'value' in expected:
            isValid &= self._validate_value(value, expected['value'])
        if 'fields' in expected:
            isValid &= self._validate_fields(value, cast(Dict[str, Dict[str, object]], expected['fields']))
        if 'startswith' in expected:
            isValid &= self._validate_startswith(value, cast(str, expected['startswith']))
        if 'regex' in expected:
            isValid &= self._validate_regex(value, cast(str, expected['regex']))
        if 'min' in expected:
            isValid &= self._validate_min(value, cast(float, expected['min']))
        if 'max' in expected:
            isValid &= self._validate_max(value, cast(float, expected['max']))
        return isValid

    def _validate_value(self, value:object, expected:object) -> bool:
        if value != expected:
            logger.console(f"[VALUE]: Validation failed. '{expected}' differs from '{value}'")
            return False
        return True

    def _validate_startswith(self, value:object, expected_start:str) -> bool:
        if not isinstance(value, str):
            logger.console(f"[TYPE]: Value '{value}' is not a string")
            return False
        if not value.startswith(expected_start):
            logger.console(f"[STARTSWITH]: Value '{value}' does not start with '{expected_start}'")
            return False
        return True

    def _validate_regex(self, value:object, expected:str) -> bool:
        if not isinstance(value, str):
            logger.console(f"[TYPE]: Value '{value}' is not a string")
            return False
        if not re.compile(expected).match(value):
            logger.console(f"[REGEX]: Value '{value}' does not match patter")
            return False
        return True

    def _validate_min(self, value:object, expected:float) -> bool:
        if not isinstance(value, Number):
            logger.console(f"[TYPE]: Value '{value}' is not a number")
            return False
        if cast(float, value) < expected:
            logger.console(f"[MIN]: Value {value} is smaller than expected")
            return False
        return True

    def _validate_max(self, value:object, expected:float) -> bool:
        if not isinstance(value, Number):
            logger.console(f"[TYPE]: Value '{value}' is not a number")
            return False
        if cast(float, value) > expected:
            logger.console(f"[MAX]: Value {value} is bigger than expected")
            return False
        return True

    def _validate_fields(self, value:object, fields:Dict[str, Dict[str, object]]) -> bool:
        isValid = True
        matchingFields:Set[str] = set()
        for field, val in inspect.getmembers(value):
            if field in fields:
                matchingFields.add(field)
                if not self.validate(val, fields[field]):
                    logger.console(f"[FIELD]: {field} has unexpected value")
                    isValid = False
        missingFields = set(fields.keys()) - matchingFields
        if missingFields:
            logger.console(f'[FIELD]: Missing expected fields [{", ".join(missingFields)}] in value')
            return False
        return isValid


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
        self._has_old_value = 'value' in self._expected
        self._old_expected_value = self._expected.get('value')
        self._fields:List[Tuple[str, Dict[str, object]]] = []
        for field, val in inspect.getmembers(self._value):
            if not field.startswith('_') and _is_jsonable(val):
                self._fields.append((field, {'value':val}))

    def do_diff(self, attrs) -> None:
        'Show diff to expected value'
        logger.console(f"Expected:{self._old_expected_value}")
        logger.console(f"Actual:{self._value}")

    def do_replace(self, attrs) -> None:
        'Replace expectation with current value'
        logger.console(f"Replaced {self._old_expected_value} with {self._value}")
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

    def do_field(self, line:str) -> None:
        'Set field specific expectation.'
        parts = line.split(None, 2)
        if not parts:
            logger.console("field command needs a field name")
            return
        name:str = parts[0]
        matching = [v for f,v in self._fields if f == name]
        if not matching:
            logger.console("Unknown field name '{name}'")
            return
        if 'fields' not in self._expected:
            self._expected['fields'] = {}
        fields = cast(Dict[str, Dict[str, object]], self._expected['fields'])
        if name not in fields:
            fields[name] = {}
        if len(parts) == 1:
            fields[name] = matching[0]
            logger.console(f"Expecting field: {name} to have value {fields[name]['value']}")
            return
        if parts[1] != 'value' and 'value' in fields[name]:
            del fields[name]['value']
        fields[name][parts[1]] = parts[2]
        logger.console(f"Expecting field: {name} to match {parts[1]} with {parts[2]}")

    def complete_field(self, text:str, line:str, begidx:int, endidx:int) -> List[str]:
        completes:List[str] = []
        for field, _ in self._fields:
            if field.startswith(text):
                completes.append(field)
        a = [s.strip() for s in line.split(None, 2)]
        if len(a) >= 2 and a[1] in [f[0] for f in self._fields]:
            completes.clear()
            for expect in ['max', 'min', 'startswith', 'regex', 'value']:
                if expect.startswith(text):
                    completes.append(expect)
        return completes

    def do_show(self, field:str) -> None:
        'Show value of the current object or a field'
        if field:
            for f, val in self._fields:
                if f == field:
                    logger.console(f"Field:{field}\nvalue:{val['value']}\ntype:{type(val['value'])}")
            return
        logger.console(f"Value:{self._value}\ntype:{type(self._value)}")
        if not self._fields:
            return
        logger.console(f'Fields:')
        for field, _ in self._fields:
            logger.console('  '+field)

    def complete_show(self, text:str, line:str, begidx:int, endidx:int) -> List[str]:
        completes:List[str] = []
        for field, _ in self._fields:
            if field.startswith(text):
                completes.append(field)
        return completes

    def do_test(self, attrs) -> None:
        'Test if values match the constraints'
        logger.console(f"Expecting: {self._expected}")
        if Validator().validate(self._value, self._expected):
            logger.console("PASSED. New value matches constraints")
        else:
            logger.console("FAILED. New value did not match constraints")
        if not self._has_old_value:
            return
        if Validator().validate(self._old_expected_value, self._expected):
            logger.console("PASSED. Old value matches constraints")
        else:
            logger.console("FAILED. Old value did not match constraints")

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