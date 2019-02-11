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


#T2 = T2*0.5
#Initial magnetization
M = rho*(gamma**2)*(hbar**2)*B0/(4*k*Temp)

conversion_factor = gammaHz*G*10**-4

def f(gamma,B0,z,G):
#    frequency = gamma*B0 + gamma*z*(G*10**-4) #in Hertz; 10**-4 due to unity convertion to Tesla/cm
    frequency = gamma*z*(G*10**-4) #in Hertz
    return frequency

def FID(M,T,f,t):
    SIL = M * np.exp(-t/T) * np.exp(1j*2*pi*f*t)
#    SIL = M * np.exp(1j*2*pi*f*t)
    return SIL

n = 10**5 # Number of points
print('\nNumber of points: n = {0:.0e} \n'.format(n))

# Creating time array
total_time = 1 # Signal acquisition time in [seconds]
dt = total_time/n
time_array = np.empty([n],dtype=float)
for i in range(0,n):
    time_array[i] = i*dt
    
#Defining array with intensities/densities
density_array = np.zeros(n)
for i in range(0,300):
    density_array[np.int(n/2-i)] = 1.0
    density_array[np.int(n/2+i)] = 1.0
slices_positions_array = density_array

deltaX           = 0.01 # [centimeter]
initial_position = -(n/2)*deltaX
position_array = np.empty([n],dtype=float)
for i in range(0,n):
    position_array[i] = initial_position + i*deltaX

# Position and density matrix
space_matrix   = np.empty([n,2],dtype=float)
for i in range(0,n):
        space_matrix[i][0] = position_array[i]
        space_matrix[i][1] = density_array[i]    

# ------ SLICING PARAMETERS ------ #         
half_number_of_slices = 2
interslice = 80
package_center = 1                       # = 1 to center at 0 value of position array
slice_half_width = 5
# ------ ------ ------ ------ ------ # 
if interslice < 2*slice_half_width: print('ATTENTION: Slices are superposing each other! Interslice value should be at greater or equal to 2*slice_half_width value!')

#Generate signals from intensity values
all_SIL = 0.0
peak_center_positions = []
counter = 0 
array_center = np.int((n-1)/2)
for i in range(0,np.int((n-1-interslice)/(2*interslice))): #Last value of loop is chosen so that position_p = n-1 for the last value of i
           
    position_p = np.int(array_center + package_center + interslice/2 + i*interslice)
    position_m = np.int(array_center + package_center - interslice/2 - i*interslice)

    if density_array[position_p] != 0.0 and density_array[position_m] != 0.0:
        
        peak_center_positions.append(position_p)
        peak_center_positions.append(position_m)
        counter = counter + 1
        if counter == half_number_of_slices+1: break
 
        #Generate signal from peak center 
        SIL_p = FID(M*density_array[position_p],T2,f(gammaHz,B0,position_array[position_p],G),time_array)
        SIL_m = FID(M*density_array[position_m],T2,f(gammaHz,B0,position_array[position_m],G),time_array)
        all_SIL = all_SIL + SIL_p + SIL_m

        #Generate signal from peak "bandwidth"         
        for j in range (1,slice_half_width+1):
            if density_array[position_p+j] == 0.0 or density_array[position_m-j] == 0.0: print('ATTENTION: Center of slice is inside the sample, but the some part of the slice width is outside of it!')
            SIL_pp = FID(M*density_array[position_p+j],T2,f(gammaHz,B0,position_array[position_p+j],G),time_array)
            SIL_pm = FID(M*density_array[position_p-j],T2,f(gammaHz,B0,position_array[position_p-j],G),time_array)
            SIL_mp = FID(M*density_array[position_m+j],T2,f(gammaHz,B0,position_array[position_m+j],G),time_array)
            SIL_mm = FID(M*density_array[position_m-j],T2,f(gammaHz,B0,position_array[position_m-j],G),time_array)
            all_SIL = all_SIL + SIL_pp + SIL_pm + SIL_mp + SIL_mm
            
            #Declaring auxiliary array to visualize slices positions at the sample
            value_at_slice = 0
            slices_positions_array[position_p]   = value_at_slice
            slices_positions_array[position_m]   = value_at_slice
            slices_positions_array[position_p+j] = value_at_slice
            slices_positions_array[position_p-j] = value_at_slice
            slices_positions_array[position_m+j] = value_at_slice
            slices_positions_array[position_m-j] = value_at_slice


FT            = np.fft.ifft(all_SIL)
FT            = np.fft.fftshift(FT)
FT            = np.abs(FT)
normalized_FT = FT/np.max(FT)

frequency_array = np.fft.fftfreq(FT.size,dt)
frequency_array = np.fft.fftshift(frequency_array)

peak_positions = np.empty([n])
for i in range(0,n):
    peak_positions[i] = frequency_array[i]/conversion_factor #10**-4 due to unity convertion

#==============================================================================
#  The loop below checks if the number of points 'n' chosen for the calculation
# is enough for generating the necessary resolution and points values for plotting
# the fourier transform in the right position values. This is necessary because:
# the first value generated by the fftfreq function will be f_0 = (-n/2)/(n*dt).
# Since we are using dt inversely proportional to n, say 1/n, f_0 = -n/2
# Hence, we need to guarantee that -n/2 is enough to generate a point that has
# value smaller than the position of the first peak in 'space_matrix' (which 
# depends on 'deltaX'). Program will exit if condition is not satisfied.
#==============================================================================
for i in range(0,n):
    if(density_array[i] != 0):
        if(frequency_array[0]/conversion_factor > position_array[i]):
            print('\n NUMBER OF POINTS IS INSUFICIENT. INCREASE VALUE OF n \n')
            sys.exit('\n NUMBER OF POINTS IS INSUFICIENT. INCREASE VALUE OF n. PROGRAM EXITTED. \n')

# This function return the position of the peaks            
def find_peaks(frequency_array,fourier_array,amplitude_threshold,minimum_peak_distance):
    peaks = peakutils.peak.indexes(fourier_array,thres=amplitude_threshold,min_dist=minimum_peak_distance)
    peaks_number = len(peaks)
    peak_frequencies = np.zeros(peaks_number)    
    for i in range(0,peaks_number):
        peak_frequencies[i] = frequency_array[peaks[i]]
#        print(' f_{0:d} = {1:.4e} --> x_{2:d} = {3:.3f}'.format(i,peak_frequencies[i],i,peak_frequencies[i]/conversion_factor))
    return peak_frequencies

peak_frequencies = find_peaks(frequency_array,FT,0.1,1)

bandwidth = gammaHz*G*(2*slice_half_width*deltaX)
peak_center_positions.sort()
peak_center_frequencies = [gammaHz*G*i for i in peak_center_positions]

print('# slices       = {0:d}'.format(2*half_number_of_slices))
print('Interslice     = {0:.2f} cm'.format(interslice*deltaX))
print('Package center = {0:.2f} cm'.format(position_array[array_center+package_center]))
print('Slice width    = {0:.2f} cm'.format(2*slice_half_width*deltaX))
print('\nBandwidth    = {0:.2e} Hertz\n'.format(bandwidth))

for i in range(0,len(peak_center_frequencies)-1):
    print('Center frequency_{0:d} = {1:.2e}'.format(i,peak_center_frequencies[i]))

plt.figure(2)
plt.plot(position_array,slices_positions_array,label='# slices = {0:d} \n Interslice = {1:.2f} cm \n Package center = {2:.2f} cm \n Slice width = {3:.2f} cm'.format(2*half_number_of_slices,interslice*deltaX,position_array[array_center+package_center],2*slice_half_width*deltaX))
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.3))
plt.xlabel("Position [cm]")
plt.ylabel("Density distribution")
plt.axis([-4,4,-0.1,1.1])
pylab.savefig('Slices.png',dpi=800,bbox_inches='tight')    
 

plt.figure(1)
my_plot = plt.plot(peak_positions,normalized_FT)
plt.axis([-4,4,-0.1,1.1])
plt.xlabel("Position [cm]")
plt.ylabel("Density distribution")
pylab.savefig('density_{0:d}.png'.format(1),dpi=600)    



