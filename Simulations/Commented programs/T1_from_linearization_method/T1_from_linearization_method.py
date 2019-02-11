# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 12:10:29 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters # lmfit is the package for fitting

#from matplotlib import rc
#rc('font',**{'family':'sans-serif','serif':['Computer Modern Roman']})
#rc('text', usetex=True)

"""
This program simulates the Ernst equation (Eq. 18-14 at Haacke). The equation is calculated for "n_points" points, each corresponding to one angle "theta". 
The equation is calculated as "rho" for many angle values (each angle theta being a value of the array "theta_array").
We then use the "linearization" of the Ernst equation to obtain T1. To do that we plot values of Signal/sin(theta) vs. Signal/tan(theta).
We then compared the value of T1 obtained from the "linearization" method with the defined T1 value that generated the simulated curve.  
"""

class main():
    
    def __init__(self):
        
        self.n_points = 180 #number of angles to be used in the simulated
        self.theta = np.linspace(1,self.n_points,self.n_points) #array with values of angles from 1 to n_points
        self.sin_theta = np.sin(self.theta*np.pi/180) #array with the sine of the angles
        self.tan_theta = np.tan(self.theta*np.pi/180) #array with the tan of the angles

        self.index0      = 1 #index0 = 1 will select angle theta=2, since theta array starts at 1 degree.
        self.index1      = 9

        self.TR = 3.78*10**-3
        self.TE = 1.813*10**-3 
        self.T2 = 72*10**-3
        self.T1 = 613.9*10**-3 # pre contrast        
#       Besa paper values: T1 = 613.9 ms (pre) and T1 = 200.3 ms (post)

    def residual(self,params, x, data):
        # Parameters to be fitted must be declared below
        amplitude = params['amplitude']
        T1 = params['T1']
        # T2 = params['T2']
        model = self.model_equation(amplitude,self.TE,self.TR,T1,self.T2,x)
        return (data - model)
        
    def model_equation(self,a,TE,TR,T1,T2,x): # x is the flip angle
        E1 = np.exp(-TR/T1)
        b = a*(1-E1)#*np.exp(-TE/T2)
        return E1*x+b
    
    def calculations(self):
                
        E1 = np.exp(-self.TR/self.T1) #Constant term to make calculations simpler.
        thetaErnst = np.arccos(E1)*180/np.pi #Ernst angle
        
        # Calculation of Ernst equation
        rho0 = 100     
        rho = rho0 * np.sin(self.theta*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(self.theta*np.pi/180))
        
        ideal_ratio = rho[self.index1]/rho[self.index0] # Ideal ratio between signals at the chosen angles
   
        #Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
        Y = np.empty(2)
        X = np.empty(2)
    
        # Calculating x and y values of each of the two data points
        Y[0] = rho[self.index0]/self.sin_theta[self.index0]
        Y[1] = rho[self.index1]/self.sin_theta[self.index1] 
        X[0] = rho[self.index0]/self.tan_theta[self.index0]
        X[1] = rho[self.index1]/self.tan_theta[self.index1]
  
        #Manual calculation of angular coefficient
        coef_angular = (Y[0]-Y[1])/(X[0]-X[1])
        T1_hand = - self.TR/np.log(coef_angular)
        
        params = Parameters()
        params.add('amplitude', value=100) #value is the initial value for fitting
        params.add('T1', value = 0.05, min = 0, max=2)
    
        fitting = minimize(self.residual, params, args=(X, Y))
        if fitting.success: 
            print('\nFitting was successful! Continue calculation...')
        
            self.fitted_amplitude = fitting.params['amplitude'].value #Amplitude obtained from linear fitting of two data points
            self.fitted_T1 = fitting.params['T1'].value #T1 obtained from linear fitting of two data points

            T1_difference = np.abs(self.fitted_T1 - self.T1)/self.T1 #percentual difference between fitted and correct T1
 
            self.fit_x_points = np.linspace(X[0],X[1],1000) # x values to plot fitted line between data points
            self.fitted_plot = self.model_equation(self.fitted_amplitude,self.TE,self.TR,self.fitted_T1,self.T2,self.fit_x_points) #y values to plot fitted line                         

            plt.figure(1)
            graph = plt.plot(self.theta,rho, label='Signal A + noise 'r'$\sigma$',linewidth=2)
            plt.xlabel('Ângulo de flip 'r'$\theta$ [Graus]')
            plt.ylabel('Sinal')
#           plt.legend()
            plt.savefig('ernstSimulated.png',dpi=600)
                
            plt.figure(2)
            graph1 = plt.plot(X,Y,'o',label='Pontos p/ 'r'$\theta_1 = 2$ e $\theta_2 = 10$')
            graph1 = plt.plot(self.fit_x_points,self.fitted_plot, label ='Reta de ajuste')
            plt.xlabel('Sinal / tangente')
            plt.ylabel('Sinal / seno')
            plt.legend()
            plt.savefig('linearizationsimulation.png',dpi=600)

            print('\n ===== # ===== # RESULTS # ===== # =====')
            print('Ernst_angle = {0:.2f}'.format(thetaErnst))
            print('Ideal signal ratio = {0:.5f}'.format(ideal_ratio))
            print('TR = {0:.3e}'.format(self.TR))
            print('T1 = {0:.3e}'.format(self.T1))
            print('Hand T1 = {0:.3e}'.format(T1_hand))
            print('Fitted T1 = {0:.3e}'.format(self.fitted_T1))
            print('Fitted Amplitude = {0:.2e}'.format(self.fitted_amplitude))
            print('T1_percentual_difference = {0:.1f}%'.format(T1_difference))
            print('===== # ===== # ===== # ===== # ===== \n')        

a = main()
a.calculations()
















