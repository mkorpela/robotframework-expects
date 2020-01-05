*** Settings ***
Library  expects.Expects  TRAINING
Library  RequestsLibrary

*** Test Cases ***
Test 1
   Should be as expected   foobarzoo
   Should be as expected   ${1}
   Log   Hello World
   Should be as expected   ${null}
   FOR    ${index}    IN RANGE    42
        Should be as expected    ${index}   id=myIndexExpectation
        Log  hello
        Should be as expected    ${2*${index}-3}
   END

Test 2
  Should be as expected   first
  Keyword call   bar
  Should be as expected   third
  Run Keyword And Expect Error  *  Keyword call   zoo
  Should be as expected   fifth

Test 3
  Create Session  google  http://www.google.com
  ${resp}=	Get Request	google  /
  Should be as expected  ${resp}

*** Keywords ***
Keyword call
  [Arguments]  ${foo}
  Should be as expected  ${foo}
  Log  say something
  Should be as expected  ${2}
