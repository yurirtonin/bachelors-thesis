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

class main():
    
    def __init__(self):
        
        self.n_points = 180
        self.theta = np.linspace(1,self.n_points,self.n_points)
        self.sin_theta = np.sin(self.theta*np.pi/180)
        self.tan_theta = np.tan(self.theta*np.pi/180)

        self.index0      = 1 # 1 indicates angle of 2 degrees. Ideal is 15
        self.index1      = 9 # 9 indicates angle of 10 degrees. Ideal is 80
#        self.index0      = 15 # 1 indicates angle of 2 degrees. Ideal is 15
#        self.index1      = 80 # 9 indicates angle of 10 degrees. Ideal is 80

        train = 43
        self.TR = 3.78*10**-3*train
        self.TE = 1.813*10**-3 
        self.T2 = 72*10**-3
        #self.T1 = 678*10**-3
    
        self.croped_pixel_array = np.loadtxt('croped_pixel_array.txt')
        self.croped_pixel_array = np.ravel(self.croped_pixel_array) #transform 2D to 1D array
    
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
        self.difference_list = []
        
        
        self.angle1_distribution = np.empty(0)
        self.angle2_distribution = np.empty(0)
        
        self.counter = 0

        for SNR in range(9,10): #vary SNR
            for i in range(0,np.size(self.croped_pixel_array)): #multiple runs with same T1
            
                for j in range(0,1):
                    if j == 0:  
                        T1 = 613.9*10**-3 # pre contrast 
                    else:
                        T1 = 200.3*10**-3 # pro contrast 

                    E1 = np.exp(-self.TR/T1)
                    
                    thetaErnst = np.arccos(E1)*180/np.pi
#                    print('Ernst_angle = {0:.2f}'.format(thetaErnst))
                    
#     Why did I use 3 as the amplitude below? I think I got this value from the data. 
                    ampIdeal = 3 / (np.sin(2*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(2*np.pi/180))) 
                    rho0 = ampIdeal
#                    rho0 = 1

                    rho = rho0 * np.sin(self.theta*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(self.theta*np.pi/180))
                    rho_nonoise = rho

#   Find best angles according to Deoni 2003:
                    maximum = np.amax(rho)
                    rho_at_best_angles = 0.71*maximum
                    
                    SNR_list.append(SNR)
                    StDev = rho[self.index0]/SNR
                    StDev = rho[1]/SNR
                    noise = np.random.normal(0,StDev,self.n_points)
                    rho = rho + noise 
                                       
#            Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
                    Y = np.empty(2)
                    X = np.empty(2)
                
                    Y[0] = rho[self.index0]/self.sin_theta[self.index0]
                    Y[1] = rho[self.index1]/self.sin_theta[self.index1]
                    X[0] = rho[self.index0]/self.tan_theta[self.index0]
                    X[1] = rho[self.index1]/self.tan_theta[self.index1]

    
                    coef_angular = (Y[0]-Y[1])/(X[0]-X[1])
    #                print('\nHand angular coef = {0:.6e}'.format(coef_angular))

#                    if coef_angular < 0:
#                    if (Y[0]-Y[1]) < 0 or (X[0]-X[1]) < 0:
                    if 1 > 2:    
                        self.counter+=1
#                        print('\nA negative angular coefficient was calculated! This indicates noise that is too high!')
#                        print('This (SNR, i) pair will be neglected from the analysis and it will not be saved.')
                        del SNR_list[-1]
                        break
                    else:
                        
                        self.angle1_distribution = np.append(self.angle1_distribution,rho[self.index0])
                        self.angle2_distribution = np.append(self.angle2_distribution,rho[self.index1])

                        T1_hand = - self.TR/np.log(coef_angular)

                        params = Parameters()
                        params.add('amplitude', value=100) #value is the initial value for fitting
                        params.add('T1', value = 0.05, min = 0, max=2)
                    
                        fitting = minimize(self.residual, params, args=(X, Y))
                            
                        if fitting.success == False:# or fitting.params['T1'].value > 1.95: 
                            print('\nFitting was NOT successful or too close to the limit')
                        else:
                            self.fitted_amplitude = fitting.params['amplitude'].value
                            self.fitted_T1 = fitting.params['T1'].value
#                            print('    Fitted Amplitude = {0:.2e}'.format(self.fitted_amplitude))
#                            print('    Fitted T1        = {0:.2e}'.format(self.fitted_T1))
#                            print('    Hand T1          = {0:.2e}'.format(T1_hand))
            
        
                            difference = (self.fitted_T1 - T1)/T1
                            self.difference_list.append(difference*100)
         
#                                self.fit_x_points = np.linspace(X[0],X[1],1000)
#                                self.fitted_plot = self.model_equation(self.fitted_amplitude,self.TE,self.TR,self.fitted_T1,self.T2,self.fit_x_points)
                               
                            plt.figure(1)
#                            graph = plt.plot(self.theta,rho, label='Signal A + noise 'r'$\sigma$',linewidth=2)
                            graph = plt.plot(self.theta,rho_nonoise,label='Signal A',linewidth=3)
                            plt.xlabel('Flip angle 'r'$\theta$ [Degrees]')
                            plt.ylabel('Signal S')
                                
#                            plt.figure(2)
#                            graph1 = plt.plot(X,Y,'o')
#                            plt.xlabel('Sinal / tangente')
#                            plt.ylabel('Sinal / seno')


        print('# de pontos ignorados = {0:.0f}'.format(self.counter))
        self.difference_list = np.asarray(self.difference_list)
        nBins = 100

        def StandardizeAndPlot(distribution,bins,label):
            newDistribution = (distribution-np.mean(distribution))/np.std(distribution)
            plt.hist(newDistribution,bins=bins,alpha=0.5,label=label)                  
          
        plt.figure(3)
        plt.axvline(x=1, color='r', linestyle='-')
        plt.axvline(x=-1, color='r', linestyle='-')
        StandardizeAndPlot(self.croped_pixel_array,nBins,'Data')
        StandardizeAndPlot(self.angle1_distribution,nBins,'Smaller Angle')
        StandardizeAndPlot(self.angle2_distribution,nBins,'Bigger Angle')
        plt.legend()

        def plotHistogramAsPoints(arrayToPlot,bins,label):
            plt.plot(np.histogram(arrayToPlot,bins=bins)[0],'o',alpha=0.5,label=label)

        plt.figure(4)
        plotHistogramAsPoints(self.croped_pixel_array,nBins,'Data')
        plotHistogramAsPoints(self.angle1_distribution,nBins,'Smaller Angle')
        plotHistogramAsPoints(self.angle2_distribution,nBins,'Bigger Angle')
        plt.legend()
                            
        plt.figure(5)
        plt.hist((self.difference_list),bins=nBins,label="Dif",alpha=0.5)
        plt.legend()


a = main()
a.calculations()















