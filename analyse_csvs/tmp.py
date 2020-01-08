
import numpy as np
import matplotlib.pyplot as plt  # To visualize
import pandas as pd  # To read data
from sklearn.linear_model import LinearRegression
from pylab import *

Y = np.array([22, 28, 27, 28, 31, 30, 31, 30, 31, 36, 32, 32], ndmin =2)
X = np.array([1,2,3,4,5,6,7,8,9,10,11,12], ndmin = 2)
Y = [22, 28, 27, 28, 31, 30, 31, 30, 31, 36, 32, 32]
X = [1,2,3,4,5,6,7,8,9,10,11,12]

m,b = np.polyfit(X, Y, 1)
print(m)
print(b)
#X = X1.values.reshape(-1, 1)  # values converts it into a numpy array
#Y = Y1.values.reshape(-1, 1)
# linear_regressor = LinearRegression()  # create object for the class
# linear_regressor.fit(X, Y)  # perform linear regression
# Y_pred = linear_regressor.predict(Y)  # make predictions
# print(Y_pred)
# plt.scatter(X, Y)
# plt.plot(X, Y_pred, color='red')
# plt.show()
