import sys
k = min(int(sys.argv[1]), 10)
print(round((2**k-1) * float(sys.argv[2])))