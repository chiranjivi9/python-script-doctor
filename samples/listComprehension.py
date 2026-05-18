a = [1, 3, 5, 6, 12, 11, 10]
# desired output
# [2, 6, 10, 12, 24, 22, 20]
d = []
for x in a:
    d.append(x * 2)
print d

# alternatively : Simpler Syntax
c = [x*2 for x in a]
print c

# Print squares of the number in the list
squaredList = []
for num in range(2, 8):
    squaredList.append(num**2)
print squaredList

# [49, 36, 25, 16, 9, 4]
revSqrList = []
for num in range(6, 1, -1):
    revSqrList.append(num**2)
print revSqrList

revListComprehension = [num**2 for num in range(6, 1, -1)]
print revListComprehension
