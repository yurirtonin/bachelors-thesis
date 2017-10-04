# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:46:59 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt

images = 80 #number of images (1 image for each cut)

M0 = 100 # initial magnetzation

TR = 162*10**-3 # repetition time in seconds
    
T1 = 700*10**-3 # longitudinal relaxation time

E1 = np.exp(-TR/T1)

thetaErnst = int(np.floor(np.arccos(E1)*180/np.pi))

#print('theta_Ernst = {0:d}'.format(thetaErnst))
    
for theta in range(1,thetaErnst):

#    theta is flip angle in degrees

    print('Angle = {0:d}'.format(theta))

    N = 1000
    Mz_array = np.empty(N)
    n_array  = np.empty(N)
    Mz = M0
    for n in range(0,N):
        
        Mz = Mz*np.cos(theta*np.pi/180)*E1+ M0*(1-E1)
    
        Mz_array[n] = Mz
        n_array[n]  = n
        
    plt.plot(n_array,Mz_array)
    
    distance_between_elements = 100
    
    for n in range(0,N-distance_between_elements):
        
        difference = np.abs(Mz_array[n]-Mz_array[n+distance_between_elements])/Mz_array[n]
#        print(difference)
        
        if difference < 0.01:
            n_stable = n
            Mz_stable = Mz_array[n]
            break

    print('Estabilidade atingida após {0:d} pulsos. Mz_steady = {1:.2e}.'.format(n,Mz_stable))
    
    total_time = TR*n_stable*images
    
    print('Tempo total para aquisição: Ttotal = {0:.2f} segundos'.format(total_time))
    
    if total_time >= Texame: print('Ângulo = {0:.0f} graus requer Texame > {1:f}'.format(theta,Texame))
    
    print('=== # === # === # === # === # === # === # === # === # ')



