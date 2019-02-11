#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys #System functions, such as reading from standard input (usually keyboard) 

from math import exp #Dump everything in module "math" into the local namespace;

from scipy.constants import hbar, pi, k # Get physical constants (e.g. planck h, hbar)

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import numpy as np

import pylab

#Relaxation times in miliseconds:    
T1_branca = 600*10**-3
T2_branca = 80*10**-3

T1_cinzenta = 950*10**-3
T2_cinzenta = 100*10**-3

T1_liquor = 4500*10**-3
T2_liquor = 2200*10**-3

T1_lipid = 250*10**-3
T2_lipid = 60*10**-3


Temp = 300 # in Kelvin
rho = 110.4*6*10**23 / 10**-3  # number of protons per liter in water
gamma = 2.68*10**8 / (2*pi) # proton gyromagnetic ratio in [1/(sec*Tesla)]
B_0 = 1 # in Tesla

print(k)
print(hbar)

#Initial Magnetization
M_0 = rho*(gamma**2)*(hbar**2)*B_0/(4*k*Temp)
print("M_0 = {0:2e}".format(M_0))
M_0=1

#Time array. Values in seconds
t = np.linspace(0,3,100)
   
#Declaring dictionaries for each magnetization (longitudinal and transversal)
Mz = {}
Mxy = {}

#Functions for calculating Mz and Mxy. Each element of the dictionary will be an array corresponding to each relaxation time.
def Longitudinal_magnetization(M_0,relaxation_time,time_array,array_name):
    #array_name should be a string
    x = array_name
    Mz[x] = M_0 * (1 - np.exp(-time_array/relaxation_time))  #    Mz[x] = M_0 * (1 - np.exp(-t/T))    
  
def Transversal_magnetization(M_0,relaxation_time,time_array,array_name):
    x = array_name
    Mxy[x] = M_0 * np.exp(-time_array/relaxation_time)

#Calcuting Mz arrays
Longitudinal_magnetization(M_0,T1_branca,t,"Longitudinal_branca")
Longitudinal_magnetization(M_0,T1_cinzenta,t,"Longitudinal_cinzenta")
Longitudinal_magnetization(M_0,T1_liquor,t,"Longitudinal_liquor")
Longitudinal_magnetization(M_0,T1_lipid,t,"Longitudinal_lipid")

#Plotting Mz curves
fig0, ax0 = plt.subplots()
plt.plot(t,Mz["Longitudinal_branca"],label="Branca")
plt.plot(t,Mz["Longitudinal_cinzenta"],label="Cinzenta")
plt.plot(t,Mz["Longitudinal_liquor"],label="Liquor")
plt.plot(t,Mz["Longitudinal_lipid"],label="Lipídio")
plt.legend()
plt.xlabel("Tempo [segundos]")
plt.ylabel("Magnetização Longitudinal")
ax0.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.1f}'.format(y))) 

pylab.savefig('Longitudinal_Magnetization.png',dpi=600)


#Calcuting Mxy arrays
Transversal_magnetization(M_0,T2_branca,t,"Transversal_branca")
Transversal_magnetization(M_0,T2_cinzenta,t,"Transversal_cinzenta")
Transversal_magnetization(M_0,T2_liquor,t,"Transversal_liquor")
Transversal_magnetization(M_0,T2_lipid,t,"Transversal_lipid")

#Plotting Mxy curves
#plt.figure(2) 
fig, ax = plt.subplots()
plt.plot(t,Mxy["Transversal_branca"],label="Branca")
plt.plot(t,Mxy["Transversal_cinzenta"],label="Cinzenta")
plt.plot(t,Mxy["Transversal_liquor"],label="Liquor")
plt.plot(t,Mxy["Transversal_lipid"],label="Lipídio")
plt.legend()
plt.xlabel("Tempo [segundos]")
plt.ylabel("Magnetização Transversal")

ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.1f}'.format(y))) 
#ax.set_xlim([0,12)

pylab.savefig('Transversal_Magnetization.png',dpi=600)
















