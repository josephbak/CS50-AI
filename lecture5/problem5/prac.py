import sys
import os

print(f"this is the name of the program: {sys.argv[0]}")

for filename in os.listdir(os.getcwd()):
    print(filename)
    print(type(filename))
