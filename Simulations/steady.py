# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:46:59 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt


M0 = 1 # initial magnetzation

theta = 5 # flip angle in degrees

TR = 10*10**-3 # repetition time in seconds

T1 = 700*10**-3 # longitudinal relaxation time




N = 1000
Mz_array = np.empty(N)
n_array  = np.empty(N)
Mz = M0
for n in range(0,N):
    
    E1 = np.exp(-n*TR/T1)
    Mz = Mz*np.cos(theta*np.pi/180)*E1+ M0*(1-E1)

    Mz_array[n] = Mz
    n_array[n]  = n
    
plt.plot(n_array,Mz_array)












