#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 21:07:03 2017

@author: YuriRT
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 13:58:51 2017

@author: YuriRT
"""

import sys
import numpy as np
from math import *
from scipy.constants import hbar, pi, k # Get physical constants (e.g. planck h, hbar)
import matplotlib.pyplot as plt
import pylab
import peakutils


Temp     = 300             # Temperature [Kelvin]
rho      = 110.4*6*10**23  # Number of protons per liter in water
gamma    = 2.68*10**8      # Proton gyromagnetic ratio [rad/s/Tesla]
gamma2pi = 42.6*10**6      # Proton gyromagnetic ratio [Hz/Tesla]
B0       = 1               # Static magnetic field in z-direction [Tesla]
G        = 0.03            # Gradient B-field [Tesla/meter] = *100*3 G/cm
T2       = 100.0*10**-3     # Decay time [seconds]

#Initial magnetization
M = rho*(gamma**2)*(hbar**2)*B0/(4*k*Temp)

n = 1000 # Array size. Must be EVEN !

#Defining array with intensities/densities
density_array = np.zeros(n)
for i in range(0,3):
    density_array[np.int(n/2-i)] = 1.0
    density_array[np.int(n/2+i)] = 1.0
#density_array[np.int(n/2-1)] = 1.0
#density_array[np.int(n/2+1)] = 1.0

deltaX           = 0.01 # [centimeter]
initial_position = -(n/2)*deltaX

position_array = np.zeros(n)
for i in range(0,len(density_array)):
    position_array[i] = initial_position + i*deltaX

space_matrix   = np.zeros((n,2))
for i in range(0,n):
        space_matrix[i][0] = position_array[i]
        space_matrix[i][1] = density_array[i]
    
def frequency(gamma,B0,z,G):
    freq = gamma*z*G 
#    freq = gamma*B0 + gamma*z*G 
    return freq

# Generate time array
#t = np.zeros(n)
#dt = 10**-3
#for i in range(0,n):
#    t[i] = i*dt
a     = 0.0                         # Initial time-value
b     = 10*10**-3                   # Final time-value
steps = 10**(7-np.abs(np.log10(b))) # Number of time-step
dt    = (b-a)/steps                 # Time-step
t     = np.linspace(a,b,steps)      # Time array

def k_value(gamma,G,t):
    k = (gamma/(2*pi))*G*t 
    return k

def FID(M,T2,k,z):
    SIL = M * np.exp(-t/T2) * np.exp(1j*2*pi*k*z)
#    SIL = M * np.exp(-1j*2*pi*k*z)
    return SIL
    
#Generate signals from intensity values
all_SIL = 0.0 
k = k_value(gamma2pi,G,t)
dk = k_value(gamma2pi,G,dt)
for i in range(0,n):
    SIL = FID(M*density_array[i],T2,k,position_array[i])
    all_SIL = all_SIL + SIL
    
FT            = np.fft.ifft(all_SIL)
FT            = np.fft.fftshift(FT)
#FT            = np.abs(FT)
normalized_FT = FT/np.max(FT)

frequency_FT = np.fft.fftfreq(FT.size)
frequency_FT = np.fft.fftshift(frequency_FT)
#frequency_FT = position_array

def find_peaks(frequency_array,fourier_array,amplitude_threshold,minimum_peak_distance):
    peaks = peakutils.peak.indexes(fourier_array,thres=amplitude_threshold,min_dist=minimum_peak_distance)
    peaks_number = len(peaks)
    peak_frequencies = np.zeros(peaks_number)    
    for i in range(0,peaks_number):
        peak_frequencies[i] = frequency_array[peaks[i]]
#        print(' z_{0:d} = {1:.4e}'.format(i,peak_frequencies[i]))
    return peak_frequencies

peak_frequencies = find_peaks(frequency_FT,FT,0.1,1)

plt.figure(3)
plt.plot(frequency_FT,normalized_FT)
plt.axis([-0.01,0.01,-1.1,1.1])
plt.figure(4)
plt.plot(position_array,density_array)
plt.axis([-0.1,0.1,-1.1,1.1])

#plt.legend()
#plt.axis([0.9*peak_frequencies[0],1.1*peak_frequencies[-1],-1.1,1.1])
#plt.axis([-0.02,0.02,-1.1,1.1])
#plt.xlabel("Frequency [Hertz]")
#plt.ylabel("k Space peaks")
#pylab.savefig('SIL3_FT-2.png',dpi=600)    
