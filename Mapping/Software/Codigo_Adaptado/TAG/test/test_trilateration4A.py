import numpy as np
import math

Anchor_matrix = np.array([[0,0],[10,0],[0,10],[10,10]])

# d = [1.5, 8.5, 7.8, 6]

"""
Obterner distancias a partir de un punto r
"""
r = np.array([5,5])

d = []
for Anchor in Anchor_matrix:
    vector = Anchor-r
    d.append(math.sqrt(np.sum(vector**2)))

x = Anchor_matrix[:,0]
y = Anchor_matrix[:,1]
k = x**2 + y**2

A = []
b = []

for i in range(1,len(d)):
    A.append(np.array([x[i], y[i]]) - np.array([x[0], y[0]]))
    b.append(d[0]**2 - d[i]**2 + k[i]-k[0])

A = np.array(A)
b = np.array(b)[np.newaxis]

R = (np.dot(np.linalg.pinv(A),b.T)/2)
print(R)

