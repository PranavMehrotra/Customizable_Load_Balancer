import random

# function to generate a new random hostname for a server
def generate_new_hostname():
        new_hostname = "S_"
        for i in range(6):
            new_hostname += str(random.randint(0, 9))