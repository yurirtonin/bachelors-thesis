# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:46:59 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt


#rho0 = 8.14
a = 10
theta = np.linspace(0,a,1000)

train = 43
TR = 1.62*10**-3
TR = TR*train
TE = 1.78*10**-3 
T1 = 678*10**-3
E1 = np.exp(-TR/T1)

thetaErnst = np.arccos(E1)*180/np.pi
print('thetaErnst = {0:.2f}'.format(thetaErnst))

T2 = 72*10**-3

ampIdeal = 7 / np.sin(2*np.pi/180)*(1-E1)*np.exp(-TE/T2)/(1-E1*np.cos(2*np.pi/180))
print(ampIdeal)

rho0 = ampIdeal
rho = rho0 * np.sin(theta*np.pi/180)*(1-E1)*np.exp(-TE/T2)/(1-E1*np.cos(theta*np.pi/180))
rhoapp = rho0 * theta / (1+0.5*E1*theta**2/(1-E1))

plt.figure(0)
graph = plt.plot(theta,rho,'bo')
graph = plt.plot(theta,rhoapp,'ro')

plt.show()