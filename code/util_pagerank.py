#-*- coding:utf-8 -*-
import numpy as np

def graphMove(a):
	b = np.transpose(a) 
	c = np.zeros((a.shape), dtype = float)
	for i in range(a.shape[0]):
		for j in range(a.shape[1]):
			if b[j].sum() == 0:
				c[i][j] = 1.0 / (len(b[j]) * 1.0)
			else:
				c[i][j] = (a[i][j] * 1.0) / (b[j].sum() * 1.0)
	return c

def firstPr(c):
	pr = np.zeros((c.shape[0],1),dtype = float) 
	for i in range(c.shape[0]):
		pr[i] = float(1)/c.shape[0]
	return pr

def pageRank(p,m,v):
	flag = 1000
	while((v == p*dot(m,v) + (1-p)*v).all()==False):
		v = p*dot(m,v) + (1-p)*v
		flag = flag - 1
		if flag == 0 and max(abs(v - (p*dot(m,v) + (1-p)*v))) < 0.0001:
			break
	return v