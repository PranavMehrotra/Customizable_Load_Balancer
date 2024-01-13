import bisect

# Create a sorted list
nums = [(1,0), (2,0), (5,0), (7,0), (9,1), (10, 1)]

# Find the index where to insert 2
index = bisect.bisect_left(nums, (20,))

print(nums)

# Print the index
print(index)