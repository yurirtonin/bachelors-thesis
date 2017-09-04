# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:46:59 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters # lmfit is the package for fitting


class main():
    
    def __init__(self):
        
        #rho0 = 8.14
        a = 89
        self.n_points = 1000
        self.theta = np.linspace(1,a,self.n_points)
        self.sin_theta = np.sin(self.theta*np.pi/180)
        self.tan_theta = np.tan(self.theta*np.pi/180)

        train = 43
        self.TR = 3.78*10**-3*train
        self.TE = 1.813*10**-3 
        self.T2 = 72*10**-3
        #self.T1 = 678*10**-3
    
    def residual(self,params, x, data):
        # Parameters to be fitted must be declared below
        amplitude = params['amplitude']
        T1 = params['T1']
        # T2 = params['T2']
    
        model = self.model_equation(amplitude,self.TE,self.TR,T1,self.T2,x)
    
        return (data - model)
    
    def model_equation(self,a,TE,TR,T1,T2,x): # x is the flip angle
        E1 = np.exp(-TR/T1)
        b = a*(1-E1)*np.exp(-TE/T2)
        return E1*x+b
    
    def calculations(self):
            
        delta = 100
        for i in range(100,100+delta,delta):
            T1 = i*10**-3
         
            print('TR = {0:.2e}'.format(self.TR))
            print('T1 = {0:.2e}'.format(T1))
        
            E1 = np.exp(-self.TR/T1)
            
            thetaErnst = np.arccos(E1)*180/np.pi
            print('thetaErnst = {0:.2f}'.format(thetaErnst))
            
            
            ampIdeal = 3 / (np.sin(2*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(2*np.pi/180))) 
            rho0 = ampIdeal
                
            rho = rho0 * np.sin(self.theta*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(self.theta*np.pi/180)) 
            #    rhoapp = rho0 * theta / (1+0.5*E1*theta**2/(1-E1))
            rho_sin = rho / self.sin_theta
            rho_tan = rho / self.tan_theta
            maximum = np.amax(rho)
            noise = 0.1*maximum*np.random.random_sample(self.n_points)
            rho = rho + noise
                    
            print(len(rho_tan))
            print(rho_tan)
            
#    Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
            Y = np.empty(2)
            X = np.empty(2)
        
            Y[0] = rho[3]/self.sin_theta[3]
            Y[1] = rho[11]/self.sin_theta[11]
            X[0] = rho[3]/self.tan_theta[3]
            X[1] = rho[11]/self.tan_theta[11]
               
            params = Parameters()
            params.add('amplitude', value=100) #value is the initial value for fitting
            params.add('T1', value = 0.5)
        
            fitting = minimize(self.residual, params, args=(X, Y))
            if fitting.success: print('Fitting was successful')
            
            self.fitted_amplitude = fitting.params['amplitude'].value
            self.fitted_T1 = fitting.params['T1'].value
            print('Fitted Amplitude = {0:.2e}'.format(self.fitted_amplitude))
            print('Fitted T1 = {0:.2e}'.format(self.fitted_T1))
            
            self.fitted_plot = self.model_equation(self.fitted_amplitude,self.TE,self.TR,self.fitted_T1,self.T2,rho_tan)
           
            plt.figure(0)
            graph = plt.plot(self.theta,rho)#,'bo')
            #graph = plt.plot(theta,rhoapp,'ro')
            plt.show()

            plt.figure(1)
            graph1 = plt.plot(rho_tan,self.fitted_plot)
            graph1 = plt.plot(X,Y,'ro')
            plt.show()


a = main()
a.calculations()

















