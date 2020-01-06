*** Settings ***
Library  Expects

*** Test Cases ***
First Test
   Should be as expected   First Test.0
   Should be as expected   First Test.1
   FOR    ${index}    IN RANGE    3
      Should be as expected  First Test.2.${index}.0
      Log  hello
      Should be as expected  First Test.2.${index}.2
   END

Test 2
  Keyword call   bar
  Should be as expected   Test 2.1
  Should be as expected   SomeId  id=SomeId

Test 3
  Should be as expected  Test 3.0

*** Keywords ***
Keyword call
  [Arguments]  ${foo}
  Should be as expected  Keyword call.0
  Log  say something
  Should be as expected  Keyword call.2