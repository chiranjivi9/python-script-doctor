# broken_example.py
# This file has 4 intentional bugs for testing the Script Doctor agent.
# DO NOT fix these manually — let the agent do it.

def calculate_average(numbers)       # Bug 1: missing colon
    total = 0
    for num in numbers               # Bug 2: missing colon
        total = total + num
    return total / len(numbers       # Bug 3: missing closing parenthesis

scores = [85, 90, 78, 92, 88]
avg = calculate_average(scores)
print("Class average: " + avg)       # Bug 4: can't add str + float, needs str(avg)
