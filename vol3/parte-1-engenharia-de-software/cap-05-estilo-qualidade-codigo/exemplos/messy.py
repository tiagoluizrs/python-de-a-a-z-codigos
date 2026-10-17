import os, sys
from typing import List, Optional
import json
def Process(data = [], flag=False ):
    result=[]
    for i in range(len(data)):
        if data[i] == None:
            continue
        if flag == True:
            result.append(data[i]*2)
        else :
            result.append(data[i])
    try:
        x = json.loads("{}")
    except:
        pass
    unused = 1
    return result
class my_class:
    def method(self,a,b):
        l = [x for x in a if x]
        if len(l) > 0:
            return "%s-%s" % (a, b)
        return f"{a}"
def long_function_with_a_very_long_name_that_goes_on(argument_one, argument_two, argument_three, argument_four):
    return argument_one
