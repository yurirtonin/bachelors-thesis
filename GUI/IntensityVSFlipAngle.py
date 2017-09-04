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
    a = 100
    self.n_points = 1000
    self.theta = np.linspace(0,a,n_points)
    self.sin_theta = np.sin(theta*np.pi/180)
    self.tan_theta = np.tan(theta*np.pi/180)
    
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
        b = a*(1-E1)#*np.exp(-TE/T2)
        return E1*x+b
    
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
    
        maximum = np.amax(rho)
        noise = 0.1*maximum*np.random.random_sample(self.n_points)
        rho = rho + noise
        
    #    Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
        Y = np.empty(2)
        X = np.empty(2)
    
        Y[0] = self.rho[2]/self.sin_theta[2]
        Y[1] = self.rho[10]/self.sin_theta[10]
        X[0] = self.rho[2]/self.tan_theta[2]
        X[1] = self.rho[10]/self.tan_theta[10]
    
        beta = rho0*(1-E1)
    
        params = Parameters()
        params.add('amplitude', value=100) #value is the initial value for fitting
        params.add('T1', value = 0.5)
    
        fitting = minimize(residual, params, args=(X, Y))
    #
    #    self.fitted_amplitude = fitting.params['amplitude'].value
    #    self.fitted_T1 = fitting.params['T1'].value
    #    # self.T2 = fitting.params['T2'].value
        
    
        
        
        
        
        
        plt.figure(0)
        graph = plt.plot(theta,rho)#,'bo')
        #graph = plt.plot(theta,rhoapp,'ro')
        plt.show()





















