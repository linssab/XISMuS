import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as imread
import sys
import os

TestList= [
	[0,0,111,111],
	[1,0,111,111],
	[2,0,222,111],
	[3,0,111,222],
	[4,0,111,111],
	[5,0,111,111],
	[0,1,111,111],
	[1,1,111,111],
	[2,1,333,111],
	[3,1,222,111],
	[4,1,444,111],
	[5,1,111,444],
	[0,2,555,111],
	[1,2,666,111],
	[2,2,777,111],
	[3,2,888,111],
	[4,2,888,111],
	[5,2,555,111],
	[0,3,222,111],
	[1,3,111,888],
	[2,3,222,111],
	[3,3,111,888],
	[4,3,111,777],
	[5,3,111,777],
	[0,4,111,222],
	[1,4,111,222],
	[2,4,111,222],
	[3,4,111,222],
	[4,4,111,222],
	[5,4,111,222],
	[0,5,111,444],
	[1,5,111,444],
	[2,5,111,444],
	[3,5,111,444],
	[4,5,111,444],
	[5,5,111,444]]

TestListLen= [ elt[0] for elt in TestList ]
ListDimension=len(TestListLen)

def _Transform(MatrixList):
    iterx=0
    itery=0
    for i in range(len(MatrixList)):
        if len(MatrixList[i]) > 1:
            if MatrixList[i][0] > 0 and MatrixList[i][0] > MatrixList[i-1][0] and MatrixList[i][0] > iterx: iterx=int(MatrixList[i][0])
        if len(MatrixList[i]) > 1:
            if MatrixList[i][1] > 0  and MatrixList[i][1] > MatrixList[i-1][1] and MatrixList[i][1] > itery: itery=int(MatrixList[i][1])

    print("Iter x,y = %d, %d" % (iterx,itery))
    RatesMatrix=np.zeros((iterx+1,itery+1))
    for i in range(len(MatrixList)):
        x=int(MatrixList[i][0])
        y=int(MatrixList[i][1])
        ka=int(MatrixList[i][2])
        kb=int(MatrixList[i][3])
        if kb==0: kb=1
        RatesMatrix[x,y]=ka/kb
    return RatesMatrix

def _ShowMap(input):
    image=input
    plt.imshow(image,cmap='gray')
    plt.show()
    return 0

def _read():
    Matrix=[]
    with open (filename,'rt') as in_file:
        for line in in_file:
            Matrix.append(line.strip("'\n"))
        for i in range(len(Matrix)): 
            Matrix[i]=Matrix[i].split()
        for j in range(len(Matrix)):
            for k in range(len(Matrix[j])):
                if Matrix[j][k].isdigit() == True: Matrix[j][k]=int(Matrix[j][k])
                else: Matrix[j][k]=1
        if len(Matrix[-1]) == 0: Matrix[-1]=[1, 1, 1, 1]
    return Matrix

if __name__ == "__main__":
    filename='ka_kb_test.txt'
    workfile=_read()
    workfile=_Transform(workfile)
    _ShowMap(workfile)
