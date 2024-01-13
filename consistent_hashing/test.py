import bisect
import numpy as np
# Create a sorted list
# nums = [(1,0), (2,0), (5,0), (7,0), (9,1), (10, 1)]

# Find the index where to insert 2
# index = bisect.bisect_left(nums, (20,))

# nums.insert(index, (20, 1))

# Print the index
# print(index)

a = np.zeros((5,2), dtype=int)
a[1] = 1,2
a[3] = 3,42
print(a)