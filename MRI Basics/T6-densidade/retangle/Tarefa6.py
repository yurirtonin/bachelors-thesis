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
import pylab
import peakutils

Temp     = 300             # Temperature [Kelvin]
rho      = 110.4*6*10**23  # Number of protons per liter in water
gamma    = 2.68*10**8      # Proton gyromagnetic ratio [rad/s/Tesla]
gamma2pi = 42.6*10**6      # Proton gyromagnetic ratio [Hz/Tesla]
B0       = 1               # Static magnetic field in z-direction [Tesla]
G        = 3               # Gradient B-field [Gauss/centimeter] = 0.01*[Tesla/meter]
T2       = (200*10**-3)    # Decay time [seconds]

for m in range(0,13):
    T2 = T2*0.5
    #Initial magnetization
    M = rho*(gamma**2)*(hbar**2)*B0/(4*k*Temp)
    
    conversion_factor = gamma2pi*G*10**-4
    
    def f(gamma,B0,z,G):
    #    frequency = gamma*B0 + gamma*z*(G*10**-4) #in Hertz; 10**-4 due to unity convertion to Tesla/cm
        frequency = gamma*z*(G*10**-4) #in Hertz
        return frequency
    
    def FID(M,T,f,t):
        SIL = M * np.exp(-t/T) * np.exp(1j*2*pi*f*t)
    #    SIL = M * np.exp(1j*2*pi*f*t)
        return SIL
    
    n = 10**5 # Number of points
    print('\n Number of points: n = {0:.0e} \n'.format(n))
    
    # Creating time array
    total_time = 1 # Signal acquisition time in [seconds]
    dt = total_time/n
    time_array = np.empty([n],dtype=float)
    for i in range(0,n):
        time_array[i] = i*dt
        
    #Defining array with intensities/densities
    density_array = np.zeros(n)
    for i in range(0,200):
        density_array[np.int(n/2-i)] = 0.5
        density_array[np.int(n/2+i)] = 1.0
    #density_array[np.int(n/2-1)] = 1.0
    #density_array[np.int(n/2+1)] = 1.0
    
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
    
    #Generate signals from intensity values
    all_SIL = 0.0
    for i in range(0,n):
        if density_array[i] != 0.0:
            SIL = FID(M*density_array[i],T2,f(gamma2pi,B0,position_array[i],G),time_array)
            all_SIL = all_SIL + SIL
        
    FT            = np.fft.ifft(all_SIL)
    FT            = np.fft.fftshift(FT)
    FT            = np.abs(FT)
#    normalized_FT = FT/np.max(FT)
    normalized_FT = FT
    
    frequency_array = np.fft.fftfreq(FT.size,dt)
    frequency_array = np.fft.fftshift(frequency_array)
    
    peak_positions = np.empty([n])
    for i in range(0,n):
        peak_positions[i] = frequency_array[i]/conversion_factor #10**-4 due to unity convertion
    
    #==============================================================================
    #  The loop below checks if the number of points 'n' chosen for the calculation
    # is enough for generating the necessary resolution and points values for plotting
    # the fourier transform in the right position values. This is necessary because:
    # the first value generate by the fftfreq function will be f_0 = (-n/2)/(n*dt).
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
                
    def find_peaks(frequency_array,fourier_array,amplitude_threshold,minimum_peak_distance):
        peaks = peakutils.peak.indexes(fourier_array,thres=amplitude_threshold,min_dist=minimum_peak_distance)
        peaks_number = len(peaks)
        peak_frequencies = np.zeros(peaks_number)    
        for i in range(0,peaks_number):
            peak_frequencies[i] = frequency_array[peaks[i]]
    #        print(' f_{0:d} = {1:.4e} --> x_{2:d} = {3:.3f}'.format(i,peak_frequencies[i],i,peak_frequencies[i]/conversion_factor))
        return peak_frequencies
    
    peak_frequencies = find_peaks(frequency_array,FT,0.1,1)
    
    #plt.figure(1)
    #plt.plot(time_array,np.real(SIL),'r--',linewidth=1)
    #plt.axis([0,1/1000,-0.000004,0.000004])
    
    plt.figure(m)
    my_plot = plt.plot(peak_positions,normalized_FT,label='T2 = {0:.5f}'.format(T2))#,'bo')
    #plt.axis([-0.1,0.1,-0.05,1.1])
    plt.legend()
#    plt.axis([1.2*peak_positions[0],1.2*peak_positions[-1],-0.05,1.1])
#    plt.axis([-5,5,-0.05,1.1])
#    plt.axis([-.5,.5,-0.05,1.1])
    plt.xlabel("Posição [cm]")
    plt.ylabel("Distribuição de Densidade")
    pylab.savefig('density_{0:d}.png'.format(m),dpi=600)    
