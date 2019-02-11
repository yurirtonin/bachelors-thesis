# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 12:27:55 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt

#from matplotlib import rc
#rc('font',**{'family':'sans-serif','serif':['Computer Modern Roman']})
#rc('text', usetex=True) 

"""
This program simulates the Ernst equation (Eq. 18-14 at Haacke). The equation is calculated for "n_points" points, each corresponding to one angle "theta". 
The equation is calculated as "rho" for many angle values (each angle theta being a value of the array "theta_array").
We then use what I call "Ratio Method" (Parker 2001), that divides the signal equation for 2 angle values and then isolates T1 analyticaly. 
We then compared the value of T1 obtained analyticaly through the method with the defined T1 value that generated the simulated curve.  
"""

n_points = 90 # number of angles to be used
theta_array = np.linspace(1,n_points,n_points) #array with angle values. Since array starts at 1 degree, theta_array[1] = 2 degrees

#print(theta_array)

index_0  = 1  #index to select angle0
index_1  = 9 #index to select angle1

TR    = 3.78*10**-3       #Repetition time in milliseconds
TE    = 1.813*10**-3      #Echo time in milliseconds
T2    = 72*10**-3         # T_2 Relaxation time in milliseconds

# Besa values: T1 = 613.9 ms (pre) and T1 = 200.3 ms (post)
#T1 = 613.9*10**-3 
T1 = 200.3*10**-3 
#T1 = 1000*10**-3 
#T1 = 900*10**-3 
        
E1 = np.exp(-TR/T1) #Constant 

thetaErnst = np.arccos(E1)*180/np.pi #Ernst angle


rho0 = 100 # Spin density
rho = rho0 * np.sin(theta_array*np.pi/180)*(1-E1) /(1-E1*np.cos(theta_array*np.pi/180)) #Ernst equation
       
S_0 = rho[index_0] #signal1 at angle index_0-1
S_1 = rho[index_1] #signal2 at angle index_1-1

ideal_ratio = S_1/S_0 # Ideal ratio between signals at the chosen angles
  
gamma = (S_1 * np.sin(theta_array[index_0]*np.pi/180)) / (S_0 * np.sin(theta_array[index_1]*np.pi/180)) #variable used simply to make following T1 calculation less confusing
T1_analytical = -TR/np.log( (gamma-1)/(gamma*np.cos(theta_array[index_1]*np.pi/180) - np.cos(theta_array[index_0]*np.pi/180))) #analytical expression for T1 obtained from "ratio method"

T1_difference = 100*(T1_analytical - T1)/T1 #percentual difference between defined "ideal" T1 and T1 obtained from the analytical expression

print('\n ===== # ===== # RESULTS # ===== # =====')
print('Ernst_angle = {0:.2f}'.format(thetaErnst))
print('Ideal signal ratio = {0:.3f}'.format(ideal_ratio))
print('gamma = {0:.3f}'.format(gamma))
print('TR = {0:.6f}'.format(TR))
print('T1 = {0:.12f}'.format(T1))
print('T1_analytical = {0:.12f}'.format(T1_analytical))
print('T1_percentual_difference = {0:.1f}%'.format(T1_difference))
print('===== # ===== # ===== # ===== # ===== \n')

'''PLOTTING'''
             
plt.figure(1)
graph = plt.plot(theta_array,rho, label='Simulated Equation',linewidth=2)
plt.xlabel('Angulo de flip 'r'$\theta$ [Graus]')
plt.ylabel('Sinal')
plt.title(r"$S_2 = {0:.2f} \quad$  $S_{{10}} = {1:.2f} \quad$ $ S_{{10}}/S_2 =$ {2:.2f}".format(S_0,S_1,ideal_ratio),fontsize=16)
#plt.title(r'$T_R = {0:.2f}$ ms $\quad   T_E = {1:.3f}$ ms $ \quad  T_1 = {2:.0f}$ ms'.format(TR*1000,TE*1000,T1*1000),fontsize=16)
#plt.legend()
plt.savefig('ErnstEquation_simulated.png',dpi=600)
        




