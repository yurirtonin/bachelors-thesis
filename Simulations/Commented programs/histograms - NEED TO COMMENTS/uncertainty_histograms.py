# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 12:10:29 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters # lmfit is the package for fitting
from scipy.optimize import curve_fit

#from matplotlib import rc
#rc('font',**{'family':'sans-serif','serif':['Computer Modern Roman']})
#rc('text', usetex=True)

'''
Code description:
    
    
    
'''

class main():
    
    def __init__(self):
        
        self.n_points = 180
        self.theta = np.linspace(1,self.n_points,self.n_points)
        self.sin_theta = np.sin(self.theta*np.pi/180)
        self.tan_theta = np.tan(self.theta*np.pi/180)

        self.index0      = 1 # 1 indicates angle of 2 degrees. Ideal is 15
        self.index1      = 9 # 9 indicates angle of 10 degrees. Ideal is 80

        self.TR = 3.78*10**-3
        self.TE = 1.813*10**-3 
        self.T2 = 72*10**-3
        #self.T1 = 678*10**-3
    
        self.croped_pixel_array = np.loadtxt('croped_pixel_array21.txt')
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
               
        self.rho_at_angle1_distribution = np.empty(0)
        self.rho_at_angle2_distribution = np.empty(0)
        
        self.counter = 0

        for SNR in range(25,30): #vary SNR
            for i in range(0,np.size(self.croped_pixel_array)): #multiple runs with same T1
            
                for j in range(0,1):
                    if j == 0:  
                        T1 = 613.9*10**-3 # pre contrast 
                    else:
                        T1 = 200.3*10**-3 # pro contrast 

                    E1 = np.exp(-self.TR/T1)
                    
                    rho0 = 100
                    rho = rho0 * np.sin(self.theta*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(self.theta*np.pi/180))
                    rho_nonoise = rho

#   Find best angles according to Deoni 2003:
                    maximum = np.amax(rho)
                    rho_at_best_angles = 0.71*maximum
                    
                    SNR_list.append(SNR)
                    StDev = rho[self.index0]/SNR
                    StDev = rho[1]/SNR
                    noise = np.random.normal(0,StDev/3,self.n_points)
                    rho = rho + noise 
                                       
#            Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
                    Y = np.empty(2)
                    X = np.empty(2)
                
                    Y[0] = rho[self.index0]/self.sin_theta[self.index0]
                    Y[1] = rho[self.index1]/self.sin_theta[self.index1]
                    X[0] = rho[self.index0]/self.tan_theta[self.index0]
                    X[1] = rho[self.index1]/self.tan_theta[self.index1]

    
                    coef_angular = (Y[0]-Y[1])/(X[0]-X[1])
                    T1_hand = - self.TR/np.log(coef_angular)                    

                    if (Y[0]-Y[1]) < 0 or (X[0]-X[1]) < 0:
                        self.counter+=1
#                        print('\nA negative angular coefficient was calculated! This indicates noise that is too high!')
#                        print('This (SNR, i) pair will be neglected from the analysis and it will not be saved.')
                        del SNR_list[-1]
                        break
                    else:
                        
#Intensity value given by the Ernst equation for each angle, at each run, is appended to an array:                        
                        self.rho_at_angle1_distribution = np.append(self.rho_at_angle1_distribution,rho[self.index0])
                        self.rho_at_angle2_distribution = np.append(self.rho_at_angle2_distribution,rho[self.index1])

# Linear fitting for obtaining T1
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
                               
#                            plt.figure(1)
#                            graph = plt.plot(self.theta,rho, label='Signal A + noise 'r'$\sigma$',linewidth=2)
#                            graph = plt.plot(self.theta,rho_nonoise,label='Signal A',linewidth=3)
#                            plt.xlabel('Flip angle 'r'$\theta$ [Degrees]')
#                            plt.ylabel('Signal S')                                

        print('# de pontos ignorados = {0:.0f}'.format(self.counter))
        self.difference_list = np.asarray(self.difference_list)
        nBins = 100
        
        def gaus(x,a,x0,sigma):
            return a*np.exp(-(x-x0)**2/(2*sigma**2))
       
#        x = np.linspace(1,100,100)
#        mean = 50
#        sigma = 20
#        amp=100
#        poptdata,pcovdata = curve_fit(gaus,x,np.histogram(self.croped_pixel_array,bins=nBins)[0],p0=[amp,mean,sigma])
#        print(poptdata)
#
#        poptsimulation,pcovsimulation = curve_fit(gaus,x,np.histogram(self.rho_at_angle1_distribution,bins=nBins)[0],p0=[amp,mean,sigma])
#        print(poptsimulation)
        
        
# PLOT OF HISTOGRAMS #        
        def StandardizeAndPlot(distribution,bins,label):
            #This function standardizes a distribution to have mean=0 and stdev=1, i.e., turns it into a standard normal distribution
            newDistribution = (distribution-np.mean(distribution))/np.std(distribution)
            plt.hist(newDistribution,bins=bins,alpha=0.5,label=label)                  
          
        plt.figure(3)
        plt.axvline(x=1, color='r', linestyle='-')
        plt.axvline(x=-1, color='r', linestyle='-')
        StandardizeAndPlot(self.rho_at_angle1_distribution,nBins,'Smaller Angle')
        StandardizeAndPlot(self.rho_at_angle2_distribution,nBins,'Bigger Angle')
        StandardizeAndPlot(self.croped_pixel_array,nBins,'Data')
        plt.title('Standard Normal Distribution (Mean=0 and StdDev=1')
        plt.legend()

        def plotHistogramAsPoints(arrayToPlot,bins,label):
            #This function simply plots the histogram as points
            plt.plot(np.histogram(arrayToPlot,bins=bins)[0],'o',alpha=0.5,label=label)

        plt.figure(4)
        plotHistogramAsPoints(self.rho_at_angle1_distribution,nBins,'Smaller Angle')
        plotHistogramAsPoints(self.rho_at_angle2_distribution,nBins,'Bigger Angle')
        plotHistogramAsPoints(self.croped_pixel_array,nBins,'Data')
        plt.title('Same graph as before, but with points')
        plt.legend()


# NORMAL PLOTS #
        '''
        These plots are used to analyze the distribution in the value of signal intensity points between real data and simulated data with noise. 
        In this way, we can see if simulated is generating a distribution similar to the real data as well. 
        All plots are "standardized", i.e. centered at zero and normalized
        '''                            
        plt.figure(5)
        plt.hist((self.difference_list),bins=nBins,label="Dif",alpha=0.5)
        plt.legend()
        
        plt.figure(6)
        plt.plot((self.croped_pixel_array-np.mean(self.croped_pixel_array))/np.amax(self.croped_pixel_array),'o',alpha=0.2,label="Data")
        plt.legend()
        
        plt.figure(7)
        plt.plot((self.rho_at_angle1_distribution-np.mean(self.rho_at_angle1_distribution))/np.amax(self.rho_at_angle1_distribution),'o',alpha=0.2,label="Simulation Rho(angle2)")
#        plt.plot((self.rho_at_angle2_distribution-np.mean(self.rho_at_angle2_distribution))/np.amax(self.rho_at_angle2_distribution),'o',alpha=0.2,label="Simulation Rho(angle2)")
        plt.legend()

a = main()
a.calculations()















