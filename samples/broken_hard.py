# broken_hard.py
# This file has bugs that only show up at runtime — not obvious from reading.

def get_grade(score):
    grades = {"A": 90, "B": 80, "C": 70}
    for grade, minimum in grades.items()
        if score >= minimum
            return grade
    return "F"

scores = [95, 82, 71, 55]
for s in scores:
    print("Score " + s + " → Grade: " + get_grade(s))
