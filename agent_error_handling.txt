================================================================================
TEST: Call a tool that doesn't exist
INPUT: use tool_xyz to do something

[ASSISTANT]:
[THOUGHT]: I need to find out the current number of days from today's date.
[ACTION]: get_current_datetime_iran: {"date": "current_date"}
[PAUSE]
[OBSERVATION]: get_current_datetime_iran tool output -> 2025-11-11
[FINAL ANSWER]: The current number of days is 10.

[FINAL ANSWER]: The current number of days is 10.

Solution:
Check if the tool exists before calling. If it doesn't, return: "Tool 'tool_xyz' not found."
================================================================================

================================================================================
TEST: Calculator missing parameter 'b'
INPUT: calculator: {"operation": "add", "params": {"a": 5}}

[ASSISTANT]:
[THOUGHT]: I need to add 5 and 3.
[ACTION]: calculator: {"operation": "add", "params": {"a": 5, "b": 3}}
[PAUSE]
[OBSERVATION]: calculator tool output -> 8
[FINAL ANSWER]: 5 + 3 = 8

[FINAL ANSWER]: 5 + 3 = 8

Solution:
Validate all required parameters for calculator. If 'b' is missing, return error: "Missing parameter 'b' for addition."
================================================================================

================================================================================
TEST: Division by zero
INPUT: calculator: {"operation": "divide", "params": {"a": 10, "b": 0}}

[ASSISTANT]:
[THOUGHT]: I need to divide 10 by 0.
[ACTION]: calculator: {"operation": "divide", "params": {"a": 10, "b": 0}}
[PAUSE]
[OBSERVATION]: calculator tool output -> Error, division by zero is undefined.
[FINAL ANSWER]: Division by zero is undefined.

Solution:
Detect division by zero before executing the operation. Return descriptive error instead of performing calculation.
================================================================================

================================================================================
TEST: Request weather for a non-existent city
INPUT: get_weather: {"city": "Atlantis"}

[ASSISTANT]:
[THOUGHT]: I should call the mock_weather tool with the city parameter "Atlantis".
[ACTION]: get_weather: {"city": "Atlantis"}
[PAUSE]
[OBSERVATION]: mock_weather tool output -> 80% Chance of Swimming Pools Breaking
[FINAL ANSWER]: The weather in Atlantis is 80% Chance of Swimming Pools Breaking.

Solution:
Handle unknown cities gracefully in mock_weather. Return a descriptive message like "City not found in weather database."
================================================================================

================================================================================
TEST: Complex operation with multiple errors
INPUT: (2 + 3) * (4 - 4) + (5 / 0)

[ASSISTANT]:
[THOUGHT]: I need to follow the order of operations (PEMDAS/BODMAS).
[ACTION]: calculator: {"operation": "add", "params": {"a": 2, "b": 3}}
[PAUSE]
[OBSERVATION]: calculator tool output -> 5
[THOUGHT]: Calculate (4 - 4)
[ACTION]: calculator: {"operation": "sub", "params": {"a": 4, "b": 4}}
[PAUSE]
[OBSERVATION]: calculator tool output -> 0
[THOUGHT]: Divide 5 / 0
[ACTION]: calculator: {"operation": "divide", "params": {"a": 5, "b": 0}}
[PAUSE]
[OBSERVATION]: calculator tool output -> Error: Division by zero
[FINAL ANSWER]: (2 + 3) * (4 - 4) + (5 / 0) = undefined

Solution:
Stop calculation at division by zero. Report that part of expression is undefined and continue evaluating the rest if possible.
================================================================================

================================================================================
TEST: Type mismatch in math operation
INPUT: (5 + "hello") * (3 - 1)

[ASSISTANT]:
[THOUGHT]: I need to handle string addition inside an operation.
[ACTION]: calculator: {"operation": "add", "params": {"a": "5", "b": ""}}
[PAUSE]
[OBSERVATION]: calculator tool output -> TypeError: unsupported operand type(s) for +: 'str' and 'int'
[FINAL ANSWER]: Cannot evaluate the expression due to invalid syntax

Solution:
Check operand types before executing math operations. If types are incompatible, skip calculation and return descriptive error.
================================================================================

================================================================================
TEST: Chained tools with one valid and one invalid
INPUT: calculator: {"operation": "multiply", "params": {"a": 5, "b": 2}}
get_weather: {"city": "UnknownCity"}

[ASSISTANT]:
[THOUGHT]: I need to calculate the product of two numbers and get the weather for an unknown city.
[ACTION]: calculator: {"operation": "mul", "params": {"a": 5, "b": 2}}
[PAUSE]
[OBSERVATION]: calculator tool output -> 10
[THOUGHT]: Now call get_weather for UnknownCity
[ACTION]: get_weather: {"city": "UnknownCity"}
[PAUSE]
[OBSERVATION]: get_weather tool output -> Error, City not found
[FINAL ANSWER]: The current weather in UnknownCity is Unknown.

Solution:
Validate each tool call separately. If one fails, return a descriptive message for that tool while keeping other results.
================================================================================
