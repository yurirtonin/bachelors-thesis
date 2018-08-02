# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 12:27:55 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters # lmfit is the package for fitting
import scipy as sp

#from matplotlib import rc
#rc('font',**{'family':'sans-serif','serif':['Computer Modern Roman']})
#rc('text', usetex=True) 

"""
This program simulates the Ernst ratioEquation for different angles (slightly different from each other) and then the average of the signal between the equations from each angle is calculated. 

The average is supposed to represent a small ROI where there was some uncertainty in the flip angle within that ROI.

From the average signal for the ROI, we extract the value of T_1 with the "Ratio method". We want to see how much T_1 changes as a function of small variation of the flip angle within a ROI.


"""


n_points = 90 # number of angles to be used
theta = np.linspace(1,n_points,n_points) #array with angle values

a_0  = 2 #index to select angle0
a_1  = 10 #index to select angle1

train = 43 
TR    = train*3.78*10**-3 #Repetition time
TE    = 1.813*10**-3      #Echo time
T2    = 72*10**-3         # T_2 Relaxation time - where does it come from?
            
T1_difference_list = []     # list to append difference between ideal and simulated T1 values with noise

class ratioEquation():
    
    def __init__(self,S1,S2,a1,a2,TR):
        self.S1 = S1
        self.S2 = S2
        self.a1 = a1 # angle1 in degrees
        self.a2 = a2 # angle2 in degrees
        self.TR = TR
    
    def defineEquation(self,T1):
        E1 = np.exp(-self.TR/T1)
        result = self.S1/self.S2 - np.sin(self.a1*np.pi/180)*(1-E1*np.cos(self.a2*np.pi/180)) / ( np.sin(self.a2*np.pi/180)*(1-E1*np.cos(self.a1*np.pi/180)) )    
        return result


# Besa values: T1 = 613.9 ms (pre) and T1 = 200.3 ms (post)
T1 = 900*10**-3 # pre contrast 
    
E1 = np.exp(-TR/T1)
thetaErnst = np.arccos(E1)*180/np.pi
#            print('Ernst_angle = {0:.2f}'.format(thetaErnst))
            
rho0 = 1
rho = rho0 * np.sin(theta*np.pi/180)*(1-E1) /(1-E1*np.cos(theta*np.pi/180))
            
                   
S_0 = rho[a_0-1] #signal1 at angle index-1
S_1 = rho[a_1-1] #signal2 at angle index-1
  
equation = ratioEquation(S_0,S_1,a_0,a_1,TR) #initiate equation with constants

T1_solved = sp.optimize.fsolve(equation.defineEquation,T1) #solve equation for T1
T1_solved = T1_solved[0]
print('T1_solved = {0:.5f}'.format(T1_solved))
            

difference = (T1_solved - T1)/T1
T1_difference_list.append(difference*100)
print('Difference between fitted and simulated T1 is {0:.5f}%'.format(difference*100)) 


'''PLOTTING'''
            
#plt.figure(4)
#graph = plt.plot(theta,rho, label='Signal A + noise 'r'$\sigma$',linewidth=2)
#plt.xlabel('Flip angle 'r'$\theta$ [Degrees]')
#plt.ylabel('Signal S')
#            plt.legend()
#           plt.savefig('signaltheta.png',dpi=600)
#        
#
#plt.figure(2)
#plt.plot(T1,ratio,'o',c='#ED8F19',markeredgecolor='black',markeredgewidth=0.5)
#plt.xlabel(r'$T_1$',fontsize=16)
#plt.ylabel(r'$S_{10}/S_2$',fontsize=16)
#plt.title(r'$\theta_1 = {0:.0f} \quad   \theta_2 = {1:.0f}  \quad  T_1 = {2:.0f}$ ms'.format(theta[a_0-1],theta[a_1-1],T1*1000),fontsize=16)
#plt.savefig('uncertainty.png',dpi=600)
#
#plt.figure(a)
#plt.axvline(x=15, color='g', linestyle='-')
  



