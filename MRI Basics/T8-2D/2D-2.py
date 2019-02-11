#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 21:07:03 2017

@author: YuriRT
"""

#import sys
import numpy as np
import cmath
#from math import *
from scipy.constants import hbar, pi, k # Get physical constants (e.g. planck h, hbar)
import matplotlib.pyplot as plt
#import pylab
#import peakutils
from PIL import Image
import matplotlib.image as mplim
import time

start_time = time.time() #Save start time to count program execution time

# --- # --- # --- # --- # --- # --- # --- # --- # --- # --- 
# GENERATE SIGNAL #
def Exp(k,r):
    imaginary_exponential = cmath.exp(-1j*2*pi*k*r)
    return imaginary_exponential

def wExp(f,t):
    imaginary_exponential = np.exp(-1j*2*pi*f*t)
    return imaginary_exponential

def FID(magnetization,t,T,x_exponential,y_exponential):
    Signal = magnetization * np.exp(-t/T) * x_exponential * y_exponential
#    Signal = magnetization * x_exponential * y_exponential
    return Signal
# --- # --- # --- # --- # END # --- # --- # --- # --- # --- 

# --- # --- # --- # --- # DECLARING VARIABLES # --- # --- # --- # --- # --- 

Temp     = 300             # Temperature [Kelvin]
rho      = 110.4*6*10**23  # Number of protons per liter in water
gammaRad = 2.68*10**8      # Proton gyromagnetic ratio [rad/s/Tesla]
gammaHz  = 42.6*10**6      # Proton gyromagnetic ratio [Hz/Tesla]
gamma2pi = (gammaHz/(2*pi))#*10**-4 #Herz/Gauss
B0       = 1               # Static magnetic field in z-direction [Tesla]        
T2       = (100*10**-3)    # Decay time [seconds]
Tau      = 100*10**-3
DX = 0.1 #cm
DY = DX
M = rho*(gammaRad**2)*(hbar**2)*B0/(4*k*Temp) #Initial magnetization

M=1
gamma2pi = 1.0
Tau = 1

n = 100 # Number of points. MUST BE EVEN.
#print('\n Number of points: n = {0:.0f} \n'.format(n))

A = n*DX

G_phase = -5 # Initial phase gradient
#deltaGy =2*np.abs(G_phase)/n #deltaGy will be exact to make Gphase simetric around 0
G_read = -G_phase  # Gradient B-field [Gauss/centimeter] = 0.01*[Tesla/meter]

# Creating time array
total_time = 2*Tau*np.abs(G_phase)/G_read  # Signal acquisition time in [seconds] adjusted so that G[last n] = -G[first n]
dt = total_time/n
time_array = np.empty([n],dtype=float)
for i in range(0,n): time_array[i] = i*dt-(n/2)*dt

# --- # --- # --- # --- # END # --- # --- # --- # --- # --- 

# --- # --- # --- # --- # CREATING REAL AND K SPACE COORDINATE ARRAYS # --- # --- # --- # --- # --- 
x_position_array = np.empty([n],dtype=float)
y_position_array = np.empty([n],dtype=float)

for i in range(0,n):
    x_position_array[i] = i*DX
    y_position_array[i] = i*DY

kspace_y = np.zeros(n)
kspace_x = np.zeros(n)
kspace_x = gamma2pi*G_read*time_array

delta_kx_line = gamma2pi*G_read*dt
delta_ky_line = delta_kx_line
#delta_ky_line = gamma2pi*deltaGy*Tau
deltaGy = delta_ky_line/(gamma2pi*Tau) #deltaGy is such that dkx=dky

if delta_kx_line != DX: print('\nWARNING: dkx and 1/n*dx are different! Adjust DX and G_phase.')

print('\ndX  = {0:.2e}    dY  = {1:.2e}'.format(DX,DY))
print('\ndKX = {0:.2e}    dKY = {1:.2e}'.format(delta_kx_line,delta_ky_line))
print('\ndt  = {2:.2e}    n   = {0:d}    1/n*dX = {1:.2e}'.format(n,1/A,dt))




# --- # --- # --- # --- # END # --- # --- # --- # --- # --- 

# --- # --- # --- # --- # OPENING/CREATING REAL SPACE # --- # --- # --- # --- # --- 
# Opening original image to be transformed
img = Image.open('image100.png').convert('L') #Converting to grayscale
img.save('greyscale.png') #Saving grayscale image
imagem = mplim.imread('greyscale.png')

density_matrix = np.zeros([n,n],dtype=float)
k_space = np.zeros([n,n],dtype=complex)

a=2
for i in range(np.int((n-1)/2)-2*a,np.int((n-1)/2)+2*a):
    for m in range(np.int((n-1)/2)-a,np.int((n-1)/2)+a):
        density_matrix[i][m] = 1.0
        
density_matrix = imagem

#density_matrix[2][10] = 1
#density_matrix[10][2] = 0.5
# --- # --- # --- # --- # END # --- # --- # --- # --- # ---         

# --- # --- # --- # --- # Generate K-Space # --- # --- # --- # --- # --- 
for ky_line in range(0,n):
    
#    if ky_line % 10 == 0: print('ky_line = {0:2d}'.format(ky_line))

    signal = 0.0
    
    G_phase = G_phase + deltaGy

    for y in range(0,n):
        
        for x in range(0,n):
            
            magnetization = M*density_matrix[y][x]
            
#            fx = gamma2pi*G_read*x_position_array[x]
#            fy = gamma2pi*G_phase*y_position_array[y]                   
#            signal = signal + FID(magnetization,0,T2,wExp(fx,time_array),wExp(fy,Tau))

            kx = gamma2pi*G_read*time_array
            ky = gamma2pi*G_phase*Tau
            signal = signal + FID(magnetization,0,T2,wExp(kx,x_position_array[x]),wExp(ky,y_position_array[y]))

    for kx_line in range(0,n): 
        k_space[ky_line][kx_line] = signal[kx_line]
     

#    if ky_line % 10 == 0: # if remainder of k/10 = 0
#        print('ky_line = {0:2d}'.format(ky_line))  
#        fig = plt.figure(figsize=(10,10))
#        plt.subplot(2,2,1)
#        plt.plot(time_array,np.real(signal)), plt.title('Real Part(Signal)'), plt.xlabel('Time [seconds]')
#        plt.subplot(2,2,2)
#        plt.plot(time_array,np.abs(signal)), plt.title('Absolute Value(Signal)'), plt.xlabel('Time [seconds]')
#        plt.show()

k_space_plot = np.log10(1+np.abs(k_space))
# --- # --- # --- # --- # END # --- # --- # --- # --- # --- 


# --- # --- # --- # --- # FOURIER TRANSFORM CALCULATION # --- # --- # --- # --- # --- 
IFT = np.fft.ifft2(k_space)
#IFT = np.fft.fftshift(IFT)
IFTplot = np.log10(1+np.abs(IFT))
#IFTplot = IFTplot/np.amax(IFTplot)

FT = np.fft.fft2(density_matrix)
FT = np.fft.fftshift(FT)
FT_plot = np.log10(1+np.abs(FT))
#FT_plot = FT_plot/np.amax(FT_plot)
# --- # --- # --- # --- # END # --- # --- # --- # --- # --- 


# --- # --- # --- # --- #  SAVING IMAGES  # --- # --- # --- # --- # --- 
fig = plt.figure(figsize=(10,10))
plt.subplot(1,2,1)   
density_plot = plt.imshow(density_matrix,cmap='gray', origin='upper'), plt.axis('off'), plt.title('Real Space')
#plt.savefig('density.png',dpi=500,bbox_inches='tight')
plt.subplot(1,2,2)
kspace_plot = plt.imshow(k_space_plot,cmap='gray', origin='upper'), plt.axis('off'), plt.title('K-Space')
#plt.savefig('k_space.png',dpi=500,bbox_inches='tight')


fig2 = plt.figure(figsize=(10,10))
plt.subplot(2,2,1)
plt.imshow(FT_plot,cmap='gray'), plt.axis('off'), plt.title('2DFT of Real-Space')
#plt.savefig('all_plots.png',dpi=500,bbox_inches='tight')
plt.subplot(2,2,2)
plt.imshow(IFTplot,cmap='gray'), plt.axis('off'), plt.title('IFT of Manual K-Space')
#plt.savefig('IFT.png',dpi=500,bbox_inches='tight')
# --- # --- # --- # --- # --- # --- # --- # --- # --- # --- 

end_time = time.time()

#print('Total time elapsed: {0:.2f} '.format((end_time - start_time)/60))


