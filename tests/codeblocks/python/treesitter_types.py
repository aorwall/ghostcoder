from __future__ import print_function
import os as operating_system
from . import my_module
from math import *

# print_statement
print("Hello, World!")

# assert_statement
assert 1 == 1, "This should not fail"

# expression_statement
# named_expression
x = (y := 20)

# return_statement
def func():
    return x

# delete_statement
del x

# raise_statement
raise Exception("An error occurred")

# pass_statement
pass

# break_statement
for i in range(10):
    if i == 5:
        break

# continue_statement
for i in range(10):
    if i == 5:
        continue

# _compound_statement
# if_statement
# elif_clause
# else_clause
if x > 10:
    print("x is greater than 10")
elif x == 10:
    print("x is 10")
else:
    print("x is less than 10")

# for_statement
for i in range(10):
    print(i)

# while_statement
while x > 0:
    x -= 1

# try_statement
# except_clause
# except_group_clause
# finally_clause
try:
    x = 1 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
finally:
    print("End of try block")

# with_statement
# with_clause
# with_item
with open('file.txt', 'r') as file:
    content = file.read()

# function_definition
# parameters
# lambda_parameters
# list_splat
# dictionary_splat
def func(x, *args, **kwargs):
    print(x, args, kwargs)

# global_statement
global x

# nonlocal_statement
def outer():
    x = 10
    def inner():
        nonlocal x
        x = 20
    inner()
    print(x)

# exec_statement
exec('print("Hello, World!")')

# type_alias_statement
Url = str

# class_definition
# type_parameter
class MyClass:
    pass

# argument_list
func(10, 20, 30, a=1, b=2, c=3)

# decorated_definition
# decorator
@staticmethod
def my_func():
    pass

# block
{
    "key": "value"
}

# expression_list
1, 2, 3, 4, 5

# dotted_name
os.path.join