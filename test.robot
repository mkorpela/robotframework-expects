*** Settings ***
Library  Expects.py
Library  RequestsLibrary

*** Test Cases ***
Test 1
   Should be as expected   foo
   Should be as expected   ${1}
   Log   Hello World
   Should be as expected   ${null}
   FOR    ${index}    IN RANGE    42
        Should be as expected    ${index}
        Log  hello
        Should be as expected    ${2*${index}-3}
   END

Test 2
  Keyword call   bar
  Keyword call   bar

Test 3
  Create Session  google  http://www.google.com
  ${resp}=	Get Request	google  /
  Should be as expected  ${resp}

*** Keywords ***
Keyword call
  [Arguments]  ${foo}
  Should be as expected  ${foo}