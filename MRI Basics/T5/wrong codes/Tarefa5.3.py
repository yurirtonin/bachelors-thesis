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
G        = 0.03            # Gradient B-field [Tesla/meter]
T2       = 10.0*10**-3     # Decay time [seconds]

#Initial magnetization
M = rho*(gamma**2)*(hbar**2)*B0/(4*k*Temp)

#Defining array with intensities/densities
array_size = 51
box_size   = (array_size-1)/5
A = np.int((array_size-1)/2-box_size)
B = np.int((array_size-1)/2+box_size)
density_array = np.zeros(array_size)
for i in range(A,B):
        density_array[i] = 1.0

#plt.plot(density_array)

deltaX           = 0.01 # [centimeter]
initial_position = -0.1

position_array = np.zeros(len(density_array))
space_matrix   = np.zeros((len(density_array),2))

for i in range(0,len(density_array)-1):
    position_array[i] = initial_position + i*deltaX

for i in range(0,len(density_array)-1):
        space_matrix[i][0] = position_array[i]
        space_matrix[i][1] = density_array[i]
    
def frequency(gamma,B0,z,G):
    freq = gamma*B0 + gamma*z*G 
    return freq

def FID(M,T2,f,t):
    SIL = M * np.exp(-t/T2) * np.exp(1j*2*pi*f*t)
    return SIL

# Generate time array
a     = 0.0                         # Initial time-value
b     = 10**-2                      # Final time-value
steps = 10**(8-np.abs(np.log10(b))) # Number of time-step
dt    = (b-a)/steps                 # Time-step
t = np.linspace(a,b,steps)          # Time array
    
#Generate signals from intensity values
all_SIL = 0.0
for i in range(0,len(density_array)-1):
    f = frequency(gamma2pi,B0,position_array[i],G)
    SIL = FID(M*density_array[i],T2,f,t)
    all_SIL = all_SIL + SIL
    
FT            = np.fft.fft(all_SIL)
#FT    = np.fft.fftshift(FT)
FT            = np.abs(FT)
normalized_FT = FT/np.max(FT)

frequency_FT = np.fft.fftfreq(FT.size,dt)

def find_peaks(frequency_array,fourier_array,amplitude_threshold,minimum_peak_distance):
    peaks = peakutils.peak.indexes(fourier_array,thres=amplitude_threshold,min_dist=minimum_peak_distance)
    peaks_number = len(peaks)
    peak_frequencies = np.zeros(peaks_number)    
    for i in range(0,peaks_number):
        peak_frequencies[i] = frequency_array[peaks[i]]
#        print(' f_{0:d} = {1:.4e}'.format(i,peak_frequencies[i]))
    return peak_frequencies

peak_frequencies = find_peaks(frequency_FT,FT,0.1,1)

plt.figure(3)
plt.plot(frequency_FT,normalized_FT)
#plt.legend()
plt.axis([0.995*peak_frequencies[0],1.005*peak_frequencies[-1],-0.05,1.1])
plt.xlabel("Frequency [Hertz]")
plt.ylabel("k Space peaks")
pylab.savefig('SIL3_FT-2.png',dpi=600)    
    