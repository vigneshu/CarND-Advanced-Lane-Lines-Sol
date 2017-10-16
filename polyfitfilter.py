import cv2
import numpy as np



class Polyfitfilter:

    def __init__(self):

        # The following variables are for the FIR moving average filter
        self.left_coeff_history=np.zeros((50,3))   # The left coefficients used for the FIR filter
        self.right_coeff_history=np.zeros((50,3))  # The right coefficients used for the FIR filter
        self.weighting_vector1= np.zeros(50) # The confidence 9-10 weighting vector for FIR filter (h)
        self.weighting_vector1[0:10]=np.linspace(1.0,0.1,10)
        self.weighting_vector2= np.zeros(50) # The confidence 7-8 weighting vector for FIR filter (h)
        self.weighting_vector2[0:20]=np.linspace(1.0,0.1,20)                                                       
        self.weighting_vector3= np.zeros(50) # The confidence 5-6 weighting vector for FIR filter (h)
        self.weighting_vector3[0:30]=np.linspace(1.0,0.1,30)                                                       
        self.weighting_vector4= np.zeros(50) # The confidence 3-4 weighting vector for FIR filter (h)
        self.weighting_vector4[0:40]=np.linspace(1.0,0.1,40)                                                       
        self.weighting_vector5= np.zeros(50) # The confidence 0-2 weighting vector for FIR filter (h)
        self.weighting_vector5[0:50]=np.linspace(1.0,0.1,50)                                                       

        self.left_filtered_coeff=[0,0,0]
        self.right_filtered_coeff=[0,0,0]

        # These variables are for low-confidence interpolation
        self.left_coeff_hist_ext=np.zeros((50,3))   # The left coefficients used for low-confidence FIR filter
        self.right_coeff_hist_ext=np.zeros((50,3))  # The right coefficients used for the low-confidence FIR filter
        self.ext_wtg_vctr= np.linspace(1.0,0.1,50) # The weighting vector for the extended time FIR filter (h)
        self.left_ext_filt_coeff=[0,0,300] # These coefficients describe a straight line at approx correct locations
        self.right_ext_filt_coeff=[0,0,980] # So they should be good to start with
        self.left_coeff_hist_ext[:]=[0,0,300] # Fill the history with approx values to start with
        self.right_coeff_hist_ext[:]=[0,0,980]
        # self.max_left_delta_coeff=[5e-4,0.1,200]
        # self.max_right_delta_coeff=[5e-4,0.1,200]
        self.max_left_delta_coeff=[5e-4,1,250]
        self.max_right_delta_coeff=[5e-4,1,250]
        # Initialization state
        self.test=0
        self.confidence=0
        self.acceptable_coeff=True
        self.first_run=True

    def filterLineCoefficients(self,left_fit,right_fit):
        self.updateExtTimeRawDataFilter(left_fit,right_fit)
        left_fit, right_fit = self.lineNotDetected(left_fit,right_fit)
        left_fit, right_fit = self.lineParametersQuestionable(left_fit,right_fit)
        left_fit, right_fit = self.FIR_FilterCoefficients(left_fit,right_fit)
        return left_fit, right_fit

    def FIR_FilterCoefficients(self,left_fit,right_fit):
        if ((self.first_run==True) or (self.confidence==0)):
        # if ((self.first_run==True) or (not self.acceptable_coeff)):
            left_fit=[np.asscalar(left_fit[0]),np.asscalar(left_fit[1]),np.asscalar(left_fit[2])]
            right_fit=[np.asscalar(right_fit[0]),np.asscalar(right_fit[1]),np.asscalar(right_fit[2])]
            print(left_fit)
            print(right_fit)
            self.left_coeff_history[:]=left_fit
            self.right_coeff_history[:]=right_fit
            self.first_run=False
        L_hist=self.left_coeff_history[0:49]
        R_hist=self.right_coeff_history[0:49]
        self.left_coeff_history[1:50]=L_hist
        self.right_coeff_history[1:50]=R_hist
        self.left_coeff_history[0]=left_fit
        self.right_coeff_history[0]=right_fit
        L_response=[0,0,0]
        R_response=[0,0,0]

        # FIR filter parameter selection
        if (self.confidence>=9):
            filter_scaling_factor=1/(np.sum(self.weighting_vector1))
            weighting=filter_scaling_factor*np.array(self.weighting_vector1)
        elif ((self.confidence<=8)&(self.confidence>=7)):
            filter_scaling_factor=1/(np.sum(self.weighting_vector2))
            weighting=filter_scaling_factor*np.array(self.weighting_vector2)
        elif ((self.confidence<=6)&(self.confidence>=5)):
            filter_scaling_factor=1/(np.sum(self.weighting_vector3))
            weighting=filter_scaling_factor*np.array(self.weighting_vector3)
        elif ((self.confidence<=4)&(self.confidence>=3)):
            filter_scaling_factor=1/(np.sum(self.weighting_vector4))
            weighting=filter_scaling_factor*np.array(self.weighting_vector4)
        else:
            filter_scaling_factor=1/(np.sum(self.weighting_vector5))
            weighting=filter_scaling_factor*np.array(self.weighting_vector5)

#        print(self.weighting_vector)
#        print(weighting)

        L_response[0]=np.convolve(self.left_coeff_history[:,0],weighting,'valid')
        L_response[1]=np.convolve(self.left_coeff_history[:,1],weighting,'valid')
        L_response[2]=np.convolve(self.left_coeff_history[:,2],weighting,'valid')
        R_response[0]=np.convolve(self.right_coeff_history[:,0],weighting,'valid')
        R_response[1]=np.convolve(self.right_coeff_history[:,1],weighting,'valid')
        R_response[2]=np.convolve(self.right_coeff_history[:,2],weighting,'valid')

        self.left_filtered_coeff=[(L_response[0]),(L_response[1]),(L_response[2])]        
        self.right_filtered_coeff=[(R_response[0]),(R_response[1]),(R_response[2])]

        # Check to see if the current polyfit values have been rejected.
        # If so, reduce the current confidence level.
        if (self.acceptable_coeff):
            self.confidence=self.confidence+1
            self.confidence=np.clip(self.confidence,0,10) # This is just saturation bounds
        else:
            self.confidence=self.confidence-1
            self.confidence=np.clip(self.confidence,0,10)
        # Then reset the self.acceptable_coeff flag for the next frame processing
        self.acceptable_coeff=True
        return self.left_filtered_coeff, self.right_filtered_coeff

    def lineNotDetected(self,left_fit,right_fit):

        if left_fit is None:
            left_fit=self.left_coeff_history[0]
            self.acceptable_coeff=False
        if right_fit is None:
            right_fit=self.right_coeff_history[0]
            self.acceptable_coeff=False
        if np.all(left_fit == [0.0,0.0,0.0]):
            left_fit=self.left_coeff_history[0]
            self.acceptable_coeff=False
        if np.all(right_fit == [0.0,0.0,0.0]):
            right_fit=self.right_coeff_history[0]
            self.acceptable_coeff=False
        if np.all(left_fit == [0,0,0]):
            left_fit=self.left_coeff_history[0]
            self.acceptable_coeff=False
        if np.all(right_fit == [0,0,0]):
            right_fit=self.right_coeff_history[0]
            self.acceptable_coeff=False
        return left_fit, right_fit

    def lineParametersQuestionable(self,left_fit,right_fit):
        # Check to see if polyline parameters are much different than previous values.
        # If they are, replace last polyline parameters with filtered polyline parameters.

                # self.max_right_delta_coeff=[5e-4,0.1,200]
        if self.first_run:
            return left_fit, right_fit
        if abs(left_fit[0]-self.left_filtered_coeff[0])>self.max_left_delta_coeff[0] :
            print("1 ",abs(left_fit[0]-self.left_filtered_coeff[0]))
            print("self.first_run ",self.first_run)
            self.acceptable_coeff=False
            left_fit=self.left_ext_filt_coeff
        if abs(left_fit[1]-self.left_filtered_coeff[1])>self.max_left_delta_coeff[1]:

            self.acceptable_coeff=False
            print("2 ",abs(left_fit[1]-self.left_filtered_coeff[1]))
            print("2 right side ",self.max_left_delta_coeff[1])
            print("2 bool ",abs(left_fit[1]-self.left_filtered_coeff[1])>self.max_left_delta_coeff[1])
            print("self.first_run ",self.first_run)
            left_fit=self.left_ext_filt_coeff
        if abs(left_fit[2]-self.left_filtered_coeff[2])>self.max_left_delta_coeff[2]:
            self.acceptable_coeff=False
            print("3 ",abs(left_fit[2]-self.left_filtered_coeff[2]))
            print("self.first_run ",self.first_run)
            left_fit=self.left_ext_filt_coeff
        if abs(right_fit[0]-self.right_filtered_coeff[0])>self.max_right_delta_coeff[0]:
            self.acceptable_coeff=False
            print("4 ",abs(right_fit[0]-self.right_filtered_coeff[0]))
            print("self.first_run ",self.first_run)
            right_fit=self.right_ext_filt_coeff
        if abs(right_fit[1]-self.right_filtered_coeff[1])>self.max_right_delta_coeff[1]:
            self.acceptable_coeff=False
            print("5 ",abs(right_fit[1]-self.right_filtered_coeff[1]))
            print("self.first_run ",self.first_run)
            right_fit=self.right_ext_filt_coeff
        if abs(right_fit[2]-self.right_filtered_coeff[2])>self.max_right_delta_coeff[2]:
            self.acceptable_coeff=False
            print("6 ",abs(right_fit[2]-self.right_filtered_coeff[2]))
            print("self.first_run ",self.first_run)
            right_fit=self.right_ext_filt_coeff

        return left_fit, right_fit

    def updateExtTimeRawDataFilter(self,left_fit,right_fit):
        # This function performs filtering of almost raw data over an extended period
        L_hist=self.left_coeff_hist_ext[0:49]
        R_hist=self.right_coeff_hist_ext[0:49]
        self.left_coeff_hist_ext[1:50]=L_hist
        self.right_coeff_hist_ext[1:50]=R_hist
        if np.all(left_fit == [0,0,0]):
            left_fit=[0,0,300]
        if np.all(right_fit == [0,0,0]):
            right_fit=[0,0,980]
        self.left_coeff_hist_ext[0]=left_fit
        self.right_coeff_hist_ext[0]=right_fit
        L_response=[0,0,0]
        R_response=[0,0,0]
        filter_scaling_factor=1/(np.sum(self.ext_wtg_vctr))
        weighting=np.zeros((1,50))
        weighting=filter_scaling_factor*np.array(self.ext_wtg_vctr)
        L_response[0]=np.convolve(self.left_coeff_hist_ext[:,0],weighting,'valid')
        L_response[1]=np.convolve(self.left_coeff_hist_ext[:,1],weighting,'valid')
        L_response[2]=np.convolve(self.left_coeff_hist_ext[:,2],weighting,'valid')
        R_response[0]=np.convolve(self.right_coeff_hist_ext[:,0],weighting,'valid')
        R_response[1]=np.convolve(self.right_coeff_hist_ext[:,1],weighting,'valid')
        R_response[2]=np.convolve(self.right_coeff_hist_ext[:,2],weighting,'valid')
        self.left_ext_filt_coeff=[(L_response[0]),(L_response[1]),(L_response[2])]
        self.right_ext_filt_coeff=[(R_response[0]),(R_response[1]),(R_response[2])]
        return True


