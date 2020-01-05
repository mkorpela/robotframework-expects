from typing import List, Optional, Dict, Mapping, Tuple, cast, Set, Callable
import os
import re
import json
import inspect
import difflib
from cmd import Cmd
import sys
from numbers import Number
import substrings
from robot.api import logger # type: ignore

class Expects:

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, mode:str='NORMAL') -> None:
        '''mode can be NORMAL, INTERACTIVE or TRAINING
        NORMAL = validate results against expectations
        INTERACTIVE = pause execution on validation failure and allow changes to validation criteria.
        TRAINING = store all values as expectations
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
            if self._mode == 'NORMAL':
                raise AssertionError(f"Unexpected {value}")
            expected = {'id':expectation_id}
            current_expectations.append(expected)
            ExpectationResolver(value, expected).resolve()
        else:
            logger.debug(f"Validating that value '{value}' matches expectation")
            if not Validator(logger.info).validate(value, expected):
                if self._mode == 'INTERACTIVE':
                    logger.console(f"\nExecution paused on row with id '{expectation_id}'")
                    NotMatchingValueInspector(value, expectation_id, current_expectations).cmdloop()
                    if not Validator(logger.console).validate(value, expected):
                        raise AssertionError(f"Unexpected {value}")
                elif self._mode == 'TRAINING':
                    logger.console(f"\nUnexpected {value} - updating expectations")
                    ExpectationResolver(value, expected).resolve()
                    if not Validator(logger.console).validate(value, expected):
                        raise AssertionError(f"Unexpected {value}")
                    else:
                        logger.console(f"resolved expectations")
                else:
                    raise AssertionError(f"Unexpected {value}")
            logger.info(f"Value '{value}' matches expectations")
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

    def __init__(self, log:Callable[[str], None]) -> None:
        self._log = log

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
            self._log(f"[VALUE]: Validation failed. '{expected}' differs from '{value}'")
            return False
        self._log("Matches expected value")
        return True

    def _validate_startswith(self, value:object, expected_start:str) -> bool:
        if not isinstance(value, str):
            self._log(f"[TYPE]: Value '{value}' is not a string")
            return False
        if not value.startswith(expected_start):
            self._log(f"[STARTSWITH]: Value '{value}' does not start with '{expected_start}'")
            return False
        self._log("Matches startswith")
        return True

    def _validate_regex(self, value:object, expected:str) -> bool:
        if not isinstance(value, str):
            self._log(f"[TYPE]: Value '{value}' is not a string")
            return False
        if not re.compile(expected).match(value):
            self._log(f"[REGEX]: Value '{value}' does not match patter")
            return False
        self._log("Matches regex")
        return True

    def _validate_min(self, value:object, expected:float) -> bool:
        if not isinstance(value, Number):
            self._log(f"[TYPE]: Value '{value}' is not a number")
            return False
        if cast(float, value) < expected:
            self._log(f"[MIN]: Value {value} is smaller than expected")
            return False
        self._log("Matches min constraint")
        return True

    def _validate_max(self, value:object, expected:float) -> bool:
        if not isinstance(value, Number):
            self._log(f"[TYPE]: Value '{value}' is not a number")
            return False
        if cast(float, value) > expected:
            self._log(f"[MAX]: Value {value} is bigger than expected")
            return False
        self._log("Matches max constraint")
        return True

    def _validate_fields(self, value:object, fields:Dict[str, Dict[str, object]]) -> bool:
        isValid = True
        matchingFields:Set[str] = set()
        for field, val in inspect.getmembers(value):
            if field in fields:
                matchingFields.add(field)
                if not self.validate(val, fields[field]):
                    self._log(f"[FIELD]: {field} has unexpected value")
                    isValid = False
        missingFields = set(fields.keys()) - matchingFields
        if missingFields:
            self._log(f'[FIELD]: Missing expected fields [{", ".join(missingFields)}] in value')
            return False
        if isValid:
            self._log("Matching fields")
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
        if Validator(logger.console).validate(self._value, self._expected):
            logger.console("PASSED. New value matches constraints")
        else:
            logger.console("FAILED. New value did not match constraints")
        if not self._has_old_value:
            return
        if Validator(logger.console).validate(self._old_expected_value, self._expected):
            logger.console("PASSED. Old value matches constraints")
        else:
            logger.console("FAILED. Old value did not match constraints")

    def do_quit(self, args) -> bool:
        'Quit Value Inspector and store new expectations'
        return True


class ExpectationResolver:

    def __init__(self, value:object, expected:Dict[str, object]) -> None:
        self._value = value
        self._expected = expected
        self._has_old_value = 'value' in self._expected
        self._old_expected_value = self._expected.get('value')
        self._fields:List[Tuple[str, Dict[str, object]]] = []
        for field, val in inspect.getmembers(self._value):
            if not field.startswith('_') and _is_jsonable(val):
                self._fields.append((field, {'value':val}))

    def resolve(self):
        if self._has_old_value and self._old_expected_value == self._value:
            return
        if isinstance(self._value, str):
            return self._resolve_str()
        if isinstance(self._value, Number):
            return self._resolve_number()
        if _is_jsonable(self._value) and not self._has_old_value:
            self._expected['value'] = self._value
            return
        if not _is_jsonable(self._value) and self._fields:
            return self._resolve_complex_object()
        raise AssertionError(f"No strategy for type {type(self._value)}")

    def _resolve_str(self):
        if self._has_old_value:
            parts = substrings.find_matching_parts(self._value, self._old_expected_value)
            if parts != [] and parts != [""]:
                del self._expected['value']
                self._expected['regex'] = substrings.regexpify(parts).pattern
                self._expected['examples'] = [self._value, self._old_expected_value]
                logger.console(f"Resolved with regex")
                return
            raise AssertionError("Could not resolve with a meaninful regex")
        elif 'regex' in self._expected and 'examples' in self._expected:
            combined = substrings.find_matching_parts(self._value, self._expected['examples'][0])
            for example in self._expected['examples'][1:]:
                combined = substrings.combine(combined, example)
            if combined != [] and combined != [""]:
                self._expected['regex'] = substrings.regexpify(combined).pattern
                self._expected['examples'].append(self._value)
                logger.console(f"Resolved with regex")
                return
            raise AssertionError("Could not resolve with a meaninful regex")
        else:
            self._expected['value'] = self._value

    def _resolve_number(self):
        assert 'value' not in self._expected or 'min' not in self._expected
        if self._has_old_value:
            del self._expected['value']
            self._expected['min'] = min(self._value, self._old_expected_value)
            self._expected['max'] = max(self._value, self._old_expected_value)
            logger.console(f"Resolved with min {self._expected['min']} and max {self._expected['max']}")
            return
        if 'min' in self._expected and 'max' in self._expected:
            self._expected['min'] = min(self._value, self._expected['min'])
            self._expected['max'] = max(self._value, self._expected['max'])
            assert 'value' not in self._expected
            logger.console(f"Resolved with min {self._expected['min']} and max {self._expected['max']}")
            return
        self._expected['value'] = self._value

    def _resolve_complex_object(self):
        if self._has_old_value:
            raise AssertionError(f"No startegy for complex object with already expected value")
        if 'fields' in self._expected:
            for field, val in self._fields:
                if field in self._expected['fields']:
                    ExpectationResolver(val['value'], self._expected['fields'][field]).resolve()
            logger.console("Resolved by updating field expectations")
            return
        self._expected['fields'] = dict(self._fields)
        logger.console("Resolved by expecting all fields")
