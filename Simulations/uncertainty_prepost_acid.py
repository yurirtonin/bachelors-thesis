# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 12:10:29 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters # lmfit is the package for fitting

from matplotlib import rc
rc('font',**{'family':'sans-serif','serif':['Computer Modern Roman']})
rc('text', usetex=True)

class main():
    
    def __init__(self):
        
        self.n_points = 180
        self.theta = np.linspace(1,self.n_points,self.n_points)
        self.sin_theta = np.sin(self.theta*np.pi/180)
        self.tan_theta = np.tan(self.theta*np.pi/180)

        self.index0      = 15
        self.index1      = 80
        self.index2      = 4
        self.index3      = 11
        self.index4      = 14

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
    
    def calculations(self):
            
        SNR_list = []
        difference_list = []
        
        delta = 100
#        for i in range(700,700+delta,delta):
        
        X0_array = np.empty(0)
        X1_array = np.empty(0)
        Y0_array = np.empty(0)
        Y1_array = np.empty(0)

        for a in range(0,1):  
            if a == 0: 
                T1 = 613.9*10**-3 # pre contrast 
            else:
                T1 = 200.3*10**-3 # pro contrast           
            
#                Besa values: T1 = 613.9 ms (pre) and T1 = 200.3 ms (post)

            for j in range(4,30): #vary SNR
                for i in range(1,30): #multiple runs with same T1
#                        T1 = 700*10**-3
                    
    #                print('\n===== // ===== // ===== // ===== // ===== // =====')
    #                print('\nT1 = {0:.2e}'.format(T1))
    #                print('TR = {0:.2e}'.format(self.TR))
                
                    E1 = np.exp(-self.TR/T1)
                    
                    thetaErnst = np.arccos(E1)*180/np.pi
    #                print('Ernst_angle = {0:.2f}'.format(thetaErnst))
                    
                    ampIdeal = 3 / (np.sin(2*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(2*np.pi/180))) 
                    rho0 = ampIdeal
                    rho0 = 1
                    
                    rho = rho0 * np.sin(self.theta*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(self.theta*np.pi/180))
                    rho_nonoise = rho
#                   rhoapp = rho0 * theta / (1+0.5*E1*theta**2/(1-E1))
        
                    maximum = np.amax(rho)
                    rho_at_best_angles = 0.71*maximum
                    find_rho = rho
                    best_angle = (np.abs(find_rho-rho_at_best_angles)).argmin()
                    find_rho = np.delete(find_rho,best_angle)
                    for i in range(1,10): 
                        find_rho = np.delete(find_rho,best_angle+i)
                        find_rho = np.delete(find_rho,best_angle-i)
                    best_angle2 = (np.abs(find_rho-rho_at_best_angles)).argmin()
                    print(best_angle)
                    print(best_angle2)

                    
                    SNR = j
                    SNR_list.append(SNR)
                    StDev = rho[self.index0]/SNR
                    noise = StDev*np.random.random_sample(self.n_points)*1
                    rho = rho + noise 
    #                print('\nNoise is at most the Standard Deviation = {0:.5f}'.format(StDev))
                    
                    rho_sin = np.divide(rho,self.sin_theta)
                    rho_tan = np.divide(rho,self.tan_theta)
                    
        #    Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
                    Y = np.empty(2)
                    X = np.empty(2)
                
                    Y[0] = rho[self.index0]/self.sin_theta[self.index0]
                    Y[1] = rho[self.index1]/self.sin_theta[self.index1]
                    X[0] = rho[self.index0]/self.tan_theta[self.index0]
                    X[1] = rho[self.index1]/self.tan_theta[self.index1]
#                        Y[2] = rho[self.index2]/self.sin_theta[self.index2]
#                        X[2] = rho[self.index2]/self.tan_theta[self.index2] 
#                        Y[3] = rho[self.index3]/self.sin_theta[self.index3]
#                        X[3] = rho[self.index3]/self.tan_theta[self.index3] 
#                        Y[4] = rho[self.index4]/self.sin_theta[self.index4]
#                        X[4] = rho[self.index4]/self.tan_theta[self.index4]  
    
                    X0_array = np.append(X0_array,X[0])
                    X1_array = np.append(X1_array,X[1])
                    Y0_array = np.append(Y0_array,Y[0])
                    Y1_array = np.append(Y1_array,Y[1])
      
                    coef_angular = (Y[0]-Y[1])/(X[0]-X[1])
    #                print('\nHand angular coef = {0:.6e}'.format(coef_angular))
                    T1_hand = - self.TR/np.log(coef_angular)
                    
                    params = Parameters()
                    params.add('amplitude', value=100) #value is the initial value for fitting
                    params.add('T1', value = 0.05)
                
                    fitting = minimize(self.residual, params, args=(X, Y))
                    if fitting.success: 
    #                    print('\nFitting was successful:')
                    
                        self.fitted_amplitude = fitting.params['amplitude'].value
                        self.fitted_T1 = fitting.params['T1'].value
    #                    print('    Fitted Amplitude = {0:.2e}'.format(self.fitted_amplitude))
#                        print('    Fitted T1        = {0:.2e}'.format(self.fitted_T1))
    #                    print('    Hand T1          = {0:.2e}'.format(T1_hand))
        
                        if np.abs(self.fitted_T1) > 100: 
                        #Fitting does not converge sometimes. It gives |T1| > 1000. We are desconsidering these points in this conditional.
                            del SNR_list[-1] #removes last element of list
                            continue         #skips current iteration
    
                        difference = np.abs(self.fitted_T1 - T1)/T1
                        difference_list.append(difference*100)
#                        print('    Difference between fitted and simulated T1 is {0:.5f}%'.format(difference*100))
     
#                            self.fit_x_points = np.linspace(X[0],X[1],1000)
#                            self.fitted_plot = self.model_equation(self.fitted_amplitude,self.TE,self.TR,self.fitted_T1,self.T2,self.fit_x_points)
#                           
                        plt.figure(4)
                        graph = plt.plot(self.theta,rho_nonoise,'o')#,label='Sinal',linewidth=3)
#                        graph = plt.plot(self.theta,rho)#,label='Sinal com ruído 'r'$\sigma$',linewidth=2)
#                        graph = plt.plot(theta,rhoapp,'ro')
#                        plt.xlabel('Ângulo de flip 'r'$\theta$ [Graus]')
#                        plt.ylabel('Sinal S')
#                        plt.legend()
#                        plt.savefig('signaltheta.png')
#                            
#                            plt.figure(5)
#        #                    graph1 = plt.plot(rho_tan,self.fitted_plot)
#        #                    graph1 = plt.plot(X,Y,'o')                    
#                            graph1 = plt.plot(X,Y,'o')#,label='Pontos p/ 'r'$\theta_1 = 2$ e $\theta_2 = 10$')
#        #                    graph1 = plt.plot(self.fit_x_points,self.fitted_plot)#, label ='Reta de ajuste')
#                            plt.xlabel('Sinal / tangente')
#                            plt.ylabel('Sinal / seno')
#        #                    plt.legend()
#            #                plt.show()
#                            plt.savefig('linear2.png')
        
                        plt.figure(a)
                        plt.axvline(x=15, color='g', linestyle='-')
                        plt.plot(SNR_list,difference_list,'ro')
                        plt.xlabel('SNR',fontsize=16)
                        plt.ylabel(r'$\Delta \% T_1$',fontsize=16)
                        plt.title(r'$\theta_1 = {0:.0f}  \quad   \theta_2 = {1:.0f}  \quad  T_1 = {2:.0f}$ ms'.format(self.theta[self.index0],self.theta[self.index1],T1*1000),fontsize=16)
        
            


a = main()
a.calculations()

















