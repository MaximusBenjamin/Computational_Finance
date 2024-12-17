import random

# 100 = Integer
# 100.0 = Float
# 'hiking' = String
# True = boolean 
# e,f,g = 1,2.0,"hiking" multiple assignment 

# Type casting: Swapping data types

# ** = power 
# // = floar division e.g. 11//3 = 3 (how many times it fits) 
# $ = remainder e.g. 11%3==2 

# s.replace('rocks', 'sucks') 
# s.find('c') searches for first c
# s.rfind('c') searches for reverse c 
# s.find('c', 7) starts search at 7 
# s.find('Park') -1 == not found
"""
s='Olympic national park rocks!' 

a = s[1] 
print(a)
"""
"""
stocks=1000
loans=1000
deposits=1800
capital=200
x=-0.3

if stocks*(1+x)+loans-deposits < 0: 
    print('The bank is bankrupt') 
elif stocks*(1+x)+loans-deposits==0: 
    print('The bank has zero capital') 
else:
    print('The bank still has capital') 
"""

"""N=int(input("Please input a number: "))
list_of_numbers = [] 
for i in range(1,N+1,1):
    list_of_numbers.append(i)  
    
print(list_of_numbers)

sum_number = 0 
for i in list_of_numbers:
    sum_number += i

print(f"The sum of the number is: {sum_number}")
"""


