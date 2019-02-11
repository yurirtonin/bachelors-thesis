#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 13:58:51 2017

@author: YuriRT
"""

import sys

from math import *

from scipy.constants import hbar, pi, k # Get physical constants (e.g. planck h, hbar)

from scipy import signal

import numpy as np

import matplotlib.pyplot as plt

import pylab

import peakutils


Temp = 300 # in Kelvin
rho = 110.4*6*10**23  # number of protons per liter in water
gamma = 2.68*10**8 # proton gyromagnetic ratio rad/s/T
gamma2pi = 42.6*10**6 # proton gyromagnetic ratio Hz/T
B_0 = 1 # in Tesla
G = 0.03 # in Tesla/meter


def f(gamma,B0,z,G):
#    frequency = gamma*B0 + gamma*z*G #in Hertz
    frequency = gamma*z*G #in Hertz
    return frequency

def FID(M,T,f,t):
    SIL = M * np.exp(-t/T) * np.exp(1j*2*pi*f*t)
    return SIL
    
##Frequency of particle at z=+5cm
f_pos = f(gamma2pi,B_0,+0.05,G)
#
##Frequency of particle at z=-5cm
f_neg = f(gamma2pi,B_0,-0.05,G)


#    #Initial Magnetization
M_1 = rho*(gamma**2)*(hbar**2)*B_0/(4*k*Temp)
#M_1 = 1.0
M_2 = M_1/2
        
T_2 = 10.0*10**-3
    
a = 0.0
b = 10**-2
steps = 10**(8-np.abs(np.log10(b)))
dt = (b-a)/steps
    
t = np.linspace(a,b,steps)
    
SIL_pos = FID(M_1,T_2,f_pos,t)
    
SIL_neg = FID(M_2,T_2,f_neg,t)
    
SIL_total = SIL_pos + SIL_neg
  

Fourier_transform_SIL3 = np.fft.fft(SIL_total)
Fourier_transform_SIL3 = np.fft.fftshift(Fourier_transform_SIL3)
freq = np.fft.fftfreq(SIL_total.size,dt)
freq = np.fft.fftshift(freq)

Fourier_transform_SIL3 = np.abs(Fourier_transform_SIL3)


def find_peaks(frequency_array,fourier_array,amplitude_threshold,minimum_peak_distance):
    
    peaks = peakutils.peak.indexes(fourier_array,thres=amplitude_threshold,min_dist=minimum_peak_distance)
    
    peaks_number = len(peaks)
    
    peak_frequencies = np.zeros(peaks_number)    
    
    for i in range(0,peaks_number):
        peak_frequencies[i] = frequency_array[peaks[i]]
        print(' f_{0:d} = {1:.4e}'.format(i,peak_frequencies[i]))
    return peak_frequencies

peak_frequencies = find_peaks(freq,Fourier_transform_SIL3,0.1,1)

z0 = (peak_frequencies[0]-gamma2pi*B_0)/(gamma2pi*G)
z1 = (peak_frequencies[1]-gamma2pi*B_0)/(gamma2pi*G)
print(' z_{0:d} = {1:.1e}'.format(0,z0))   
print(' z_{0:d} = {1:.1e}'.format(1,z1))
 
#plt.figure(1)
#plt.plot(t,SIL_pos,label="SIL-1")
#plt.plot(t,SIL_neg,label="SIL-2")
#plt.legend()
#plt.xlabel("Time [seconds]")
#plt.ylabel("SIL")
#pylab.savefig('SIL.png',dpi=600)
#
#plt.figure(2)
#plt.plot(t,SIL_total,label="SIL1 + SIL2")
#plt.legend()
#plt.xlabel("Time [seconds]")
#plt.ylabel("SIL")
#pylab.savefig('SIL1+2.png',dpi=600)



plt.figure(3)
plt.plot(freq,Fourier_transform_SIL3)
#plt.legend()
plt.axis([1.5*peak_frequencies[0],1.5*peak_frequencies[-1],-0.05,2.5])
plt.xlabel("Frequência [Hertz]")
#plt.ylabel("Espaço  peaks")
pylab.savefig('freqspace.png',dpi=600)

#plt.figure(4)
#plt.plot(freq,Fourier_transform_SIL3)
#plt.legend()
##plt.axis([0,400,-0.005,0.3])
#plt.xlabel("Frequency [Hertz]")
#plt.ylabel("SIL Fourier Transform")
#pylab.savefig('SIL4_FT.png',dpi=600)
