# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:46:59 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt

'''
In this program we fix the number of images we want, an then calculate how many
 pulses and how much time is necessary for the longitudinal magnetization to 
 reach the steady state after appling a pulse that flips the spin by an angle "theta". 
'''

images = 80 #number of images (1 image for each cut)

M0 = 100 # initial magnetzation

TR = 3.78*10**-3 # repetition time in seconds
    
T1 = 700*10**-3 # longitudinal relaxation time

E1 = np.exp(-TR/T1)

thetaErnst = int(np.floor(np.arccos(E1)*180/np.pi))

print('theta_Ernst = {0:d}'.format(thetaErnst))

n_list = [] #list to save numbers later.
theta_list = []


N = 1000
initial_angle=1
#for theta in range(initial_angle,thetaErnst):
for theta in range(initial_angle,90):

#    theta is flip angle in degrees

    print('Angle = {0:d}'.format(theta))

    Mz_array = np.empty(N)
    n_array  = np.empty(N)
    Mz = M0
    for n in range(0,N):
        
        Mz = Mz*np.cos(theta*np.pi/180)*E1+ M0*(1-E1) #when TR=0, Mz = Mz*cos(), that means, it has the value immediately after the flip
                                                      #when TR=infinity, Mz=M0  
    
        Mz_array[n] = Mz
        n_array[n]  = n
        
    plt.figure(1)    
    plt.plot(n_array,Mz_array)
    
    distance_between_elements = 100 #how many pulses ahead you want to use to check if steady state was reached
    
    for n in range(0,N-distance_between_elements): #loop to compare Mz between to points in the array
        
        difference = np.abs(Mz_array[n]-Mz_array[n+distance_between_elements])/Mz_array[n]
#        print(difference)
        
        if difference < 0.01: #if difference is less than 1% between a certain Mz and another Mz ahead, then we have reached steady state
            n_stable = n
            Mz_stable = Mz_array[n]
            break
    
    n_list.append(n) #saving number of pulses that were required to reach steady_state
    theta_list.append(theta)    #saving corresponding angle values
    

    
    print('Estabilidade atingida após {0:d} pulsos. Mz_steady = {1:.2e}.'.format(n,Mz_stable))
    
    total_time = TR*n_stable*images #calculates total time necessary to obtain the fixed number of images
    
    print('Tempo total para aquisição: Ttotal = {0:.2f} segundos'.format(total_time))
    
#    if total_time >= Texame: print('Ângulo = {0:.0f} graus requer Texame > {1:f}'.format(theta,Texame))
    
    print('=== # === # === # === # === # === # === # === # === # ')

plt.figure(2)
plt.plot(theta_list,n_list,'o') #plot number of pulses required to reach steady state for each angle

