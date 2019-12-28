*** Settings ***
Library  Expects.py

*** Test Cases ***
Test 1
   Should be as expected   foo
   Should be as expected   ${1}
   Should be as expected   ${null}
   FOR    ${index}    IN RANGE    42
        Should be as expected    ${index}
        Log  hello
        Should be as expected    ${2*${index}-3}
   END
