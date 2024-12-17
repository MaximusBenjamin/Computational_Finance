import random
import math
from collections import Counter
import matplotlib.pyplot as plt

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

"""
def function_fibonacci(count):
    fibonacci_sequence = [1,1]

    for i in range(2,count): 
        next_number = fibonacci_sequence[-1] + fibonacci_sequence[-2]
        fibonacci_sequence.append(next_number)

    return fibonacci_sequence

fibonacci_numbers = function_fibonacci(10000)
print(fibonacci_numbers)

fibonacci_numbers.count([1])

def extract_leading_digits(numbers):
    leading_digits = [int(str(num)[0] for num in numbers)]
    return leading_digits
def benford_probabilities():
    return {d:math.log10(1 + 1 / d) for d in range (1,10)}

def analyze_fibonacci_benford(count):
    fibonacci_numbers = function_fibonacci(count)

    leading_digits = extract_leading_digits(fibonacci_numbers)

    counts = Counter(leading_digits)

    total = len(leading_digits) 
    observed_frequencies = """


x = [i+1 for i in range(10)]
y = [(i+1)**2 for i in range(10)]
fig=plt.figure()
ax=fig.add_subplot(111)
ax.bar(x, y, color='red', alpha=0.2)
ax.scatter(x, y, color='red')
ax.plot(x, y, color='blue')

plt.show()