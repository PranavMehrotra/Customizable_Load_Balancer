#plot for part 2 of analysis

import matplotlib.pyplot as plt
import numpy as np

# Simulated data (replace this with your actual data)
num_servers = [2, 3, 4, 5, 6]
# average_load = [5000,3333.3333333 ,2500, 2000, 1666.66667]
# std_deviation_load = [771, 44.49968788, 692.3998, 796.5940161, 700.905763201]

average_load = [5000,3333.3333333 ,2500, 2000, 1666.66667]
std_deviation_load = [1098, 320.264820, 451.886047, 513.2928988, 468.46866]

# Plotting
plt.figure(figsize=(10, 6))

# Line plot for average load
plt.plot(num_servers, average_load, label='Average Load', marker='o')

# Line plot for standard deviation of load
plt.plot(num_servers, std_deviation_load, label='Std Deviation Load', marker='o')

# Adding labels and title
plt.xlabel('Number of Servers')
plt.ylabel('Load')
plt.title('Average Load and Standard Deviation vs. Number of Servers')
plt.legend()

# Display the plot
plt.grid(True)
plt.show()
