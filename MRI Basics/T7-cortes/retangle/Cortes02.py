#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 21:07:03 2017

@author: YuriRT
"""

import sys
import numpy as np
from math import *
from scipy.constants import hbar, pi, k # Get physical constants (e.g. planck h, hbar)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import peakutils
import pylab

Temp     = 300             # Temperature [Kelvin]
rho      = 110.4*6*10**23  # Number of protons per liter in water
gamma    = 2.68*10**8      # Proton gyromagnetic ratio [rad/s/Tesla]
gammaHz  = 42.6*10**6      # Proton gyromagnetic ratio [Hz/Tesla]
gamma2pi = gammaHz/(2*pi)
B0       = 1               # Static magnetic field in z-direction [Tesla]
G        = 3               # Gradient B-field [Gauss/centimeter] = 0.01*[Tesla/meter]
T2       = (100*10**-3)    # Decay time [seconds]


n = 10**5 # Number of points
print('\n Number of points: n = {0:.0e} '.format(n))

deltaX           = 0.01 # [centimeter]
print('\n Space resolution: dX = {0:.2f} cm '.format(deltaX))
         
        
# -- Fixed Parameter -- # 
dF = 40.68*10**6  # "delta F" RF bandwidth [Hz] - Calculated as if we were to have a 2 cm thich slice with a G = 3 G/cm gradient.

# -- Input Parameters -- # 
z0 = 0  # Slice central position [cm]. WE ASSUME SAMPLE IS CENTERED. POSITION z0 = 0 CORRESPONDS TO THE CENTER OF THE SAMPLE.
dZ = 1  # "delta Z" - Slice thickness [cm]
number_of_slices = 2
interslice_cm = 15 # Interslice (distance between slices center) [cm] 

# TO GENERATE A SINGLE SLICE IN THE CENTER, dZ and interslice_cm must be the same and number_of_slices must equal 2.

# -- Remaining parameters -- #
Gz = dF / (gamma2pi*dZ)
f0 = gamma2pi*Gz*z0

print('\n Input parameters: \n z0 = {0:.0f} cm \n dZ = {1:.0f} cm '.format(z0,dZ))
print('\n Output parameters: \n f0 = {1:.2e} Hz \n Gz = {0:.2e} G/cm '.format(Gz,f0))
        

# ------ SLICING PARAMETERS - indexes ------ #   
      
package_center = z0 / deltaX + 1             # = 1 to center at 0 value of position array
if package_center.is_integer() == False: 
    print('\n ERROR: Your slice central position z0 = {0:.2f} is invalid. System resolution is dX = {1:.2f}. z0 should be an integer number of dX = {1:.2f}. \n'.format(z0,deltaX))
    sys.exit('\n SEE ERROR MESSAGE ABOVE. PROGRAM EXITTED. \n')
else: package_center = np.int(package_center) #Transforming to integer so it can be used as index
   
slice_half_width = dZ / (2*deltaX)
if slice_half_width.is_integer() == False: 
    print('\n ERROR: slice_half_width dZ = {0:.2f} is invalid. System resolution is dX = {1:.2f}. dZ should be an integer number of dX = {1:.2f}. \n'.format(z0,deltaX))
    sys.exit('\n SEE ERROR MESSAGE ABOVE. PROGRAM EXITTED. \n')
else: slice_half_width = np.int(slice_half_width) #Transforming to integer so it can be used as index

half_number_of_slices = number_of_slices/2
half_number_of_slices = np.int(half_number_of_slices)

interslice = interslice_cm / deltaX
if interslice.is_integer() == False: 
    print('\n ERROR: Your interslice = {0:.2f} is invalid. System resolution is dX = {1:.2f}. Interslice should be an integer number of dX = {1:.2f}. \n'.format(z0,deltaX))
    sys.exit('\n SEE ERROR MESSAGE ABOVE. PROGRAM EXITTED. \n')
else: interslice = np.int(interslice) #Transforming to integer so it can be used as index
if interslice < 2*slice_half_width: print('\n ATTENTION: Slices are superposing each other! Interslice value should be at greater or equal to 2*slice_half_width value!')
# ------ ------ ------ ------ ------ # 



#Defining array with intensities/densities
density_array = np.zeros(n)
sample_size = 60 # cm
points_n = np.int(sample_size/(2*deltaX))
for i in range(0,points_n):
    density_array[np.int(n/2-i)] = 1.0
    density_array[np.int(n/2+i)] = 1.0
slices_positions_array = density_array

initial_position = -(n/2)*deltaX
position_array = np.empty([n],dtype=float)
for i in range(0,n):
    position_array[i] = initial_position + i*deltaX

# Position and density matrix
space_matrix   = np.empty([n,2],dtype=float)
for i in range(0,n):
        space_matrix[i][0] = position_array[i]
        space_matrix[i][1] = density_array[i]   



peak_center_positions = []
counter = 0 
array_center = np.int((n-1)/2)
for i in range(0,np.int((n-1-interslice)/(2*interslice)-(package_center/interslice))): #Last value of loop is chosen so that position_r = n-1 for the last value of i. In other words: array_center + package_center + interslice/2 + i*interslice = n-1
    
    # r and l subscripts stand for right and left       
    position_r = np.int(array_center + package_center + interslice/2 + i*interslice) # The presence of + interslice/2 at position_r and -interslice/2 at position_l indicate that the first two peaks will be separated by 2*interslice/2, each separated by interslice/2 from the package_center 
    position_l = np.int(array_center + package_center - interslice/2 - i*interslice)

    if density_array[position_r] != 0.0 and density_array[position_l] != 0.0:

        counter = counter + 1
        if counter == half_number_of_slices+1: break
        
        peak_center_positions.append(position_r)
        peak_center_positions.append(position_l)
        peak_center_positions.sort()


        #Generate signal from peak "bandwidth"         
        for j in range (1,slice_half_width+1):
            
            #Declaring auxiliary array to visualize slices positions at the sample
            value_at_slice = 0
            slices_positions_array[position_r]   = value_at_slice
            slices_positions_array[position_l]   = value_at_slice
            slices_positions_array[position_r+j] = value_at_slice
            slices_positions_array[position_r-j] = value_at_slice
            slices_positions_array[position_l+j] = value_at_slice
            slices_positions_array[position_l-j] = value_at_slice

mylabel = ' N = {0:d} \n Interslice = {1:.2f} cm \n Centro do pacote = {2:.2f} cm \n Largura do corte = {3:.2f} cm'.format(2*half_number_of_slices,interslice*deltaX,position_array[array_center+package_center],2*slice_half_width*deltaX)
  

figura = plt.figure(2)
#plt.plot(position_array,density_array,'yo')
plt.plot(position_array,slices_positions_array,label=mylabel)
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.3))
plt.xlabel("Posição [cm]")
#plt.ylabel("Density distribution")
plt.axis([-50,50,-0.1,1.1])
pylab.savefig('Slices.png',dpi=800,bbox_inches='tight')    

 





