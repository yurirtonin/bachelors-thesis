#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 13:58:51 2017

@author: YuriRT
"""

import sys

from math import *

from scipy.constants import hbar, pi, k # Get physical constants (e.g. planck h, hbar)

import numpy as np

import matplotlib.pyplot as plt

import pylab


Temp = 300 # in Kelvin
rho = 110.4*6*10**23  # number of protons per liter in water
gamma = 2.68*10**8 # proton gyromagnetic ratio
B_0 = 1 # in Tesla

m = 1
for n in range(0,3):
    m = 2*m 
    #Initial Magnetization
    M_1 = rho*(gamma**2)*(hbar**2)*B_0/(4*k*Temp)
    M_2 = m*M_1/4
    
    omega_1 = 2*pi*10.0*10**1
    omega_2 = 2*pi*30.0*10**1
    
    T_1 = m*10.0*10**-3
    T_2 = 50.0*10**-3
    
    a = 0
    b = 0.1
    steps = 1000000
    dt = (b-a)/steps
    
    t = np.linspace(a,b,steps)
    
    SIL_1 = M_1 * (np.cos(omega_1 * t) + 1j*np.sin(omega_1 * t)) * np.exp(-t/T_1)
    
    SIL_2 = M_2 * (np.cos(omega_2 * t) + 1j*np.sin(omega_2 * t)) * np.exp(-t/T_2)
    
    SIL_3 = SIL_2 + SIL_1
    
    #plt.figure(1)
    #plt.plot(t,SIL_1,label="SIL-1")
    #plt.plot(t,SIL_2,label="SIL-2")
    #plt.legend()
    #plt.xlabel("Time [seconds]")
    #plt.ylabel("SIL")
    #pylab.savefig('SIL.png',dpi=600)
    #
    #plt.figure(2)
    #plt.plot(t,SIL_3,label="SIL1 + SIL2")
    #plt.legend()
    #plt.xlabel("Time [seconds]")
    #plt.ylabel("SIL")
    #pylab.savefig('SIL1+2.png',dpi=600)
    
    freq = np.fft.fftfreq(t.size,dt)
    Fourier_transform_SIL3 = np.fft.fft(SIL_3)
    
    plt.figure(3)
    plt.plot(freq,Fourier_transform_SIL3)
    plt.legend()
    plt.axis([0,400,-0.005,2])
    plt.xlabel("Frequency [Hertz]")
    plt.ylabel("SIL Fourier Transform")
    pylab.savefig('SIL3_FT.png',dpi=600)
    
    plt.figure(4)
    plt.plot(freq,Fourier_transform_SIL3)
    plt.legend()
    plt.axis([0,400,-0.005,0.3])
    plt.xlabel("Frequency [Hertz]")
    plt.ylabel("SIL Fourier Transform")
    pylab.savefig('SIL4_FT.png',dpi=600)
