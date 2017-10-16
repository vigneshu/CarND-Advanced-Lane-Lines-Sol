import cv2
import numpy as np
from numpy.polynomial import Polynomial as P
import sys
from scipy import misc

class Thresholder:
    def __init__(self):
        self.sobel_kernel = 15

        self.thresh_dir_min = 0.7
        self.thresh_dir_max = 1.2

        self.thresh_mag_min = 50
        self.thresh_mag_max = 255
      
    def threshold(self,img):

        imag = img
        imn=img
		#saturation
        
        #img[0:364,:]=0
        #misc.imsave('output_images/skyskip.jpg', img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype("float32")
        (h, s, v) = cv2.split(img)
        s = s*2.4
        s = np.clip(s,0,255)
        img = cv2.merge([h,s,v])
        img = cv2.cvtColor(img.astype("uint8"), cv2.COLOR_HSV2BGR)
        misc.imsave('output_images/sat.jpg', img)
		#blur
        #img=cv2.bilateralFilter(img,9,75,75)
        img = cv2.GaussianBlur(img, (3,3), 0)

        #img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        #yellow_min = np.array([20, 60, 60], np.uint8)
        #yellow_max = np.array([38, 174, 250], np.uint8)
        #yellow_mask = cv2.inRange(img, yellow_min, yellow_max)
        #yellow_shellr = cv2.blur(yellow_mask,(5,5))
        #misc.imsave('output_images/ymr.jpg', yellow_shellr)

        img = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
        yellow_min = np.array([10, 0, 100], np.uint8)
        yellow_max = np.array([30, 255, 255], np.uint8)
        yellow_mask = cv2.inRange(img, yellow_min, yellow_max)
        yellow_shell = cv2.blur(yellow_mask,(5,5))
        misc.imsave('output_images/ym.jpg', yellow_shell)


        #img = cv2.cvtColor(imag, cv2.COLOR_RGB2HSV)
        #white_min1 = np.array([202,202, 202], np.uint8)#190
        #white_max1 = np.array([255, 255, 255], np.uint8)#255
        #white_mask1 = cv2.inRange(img, white_min1, white_max1)
        #white_shellr = -(cv2.blur(white_mask1,(10,10)))
        #misc.imsave('output_images/wkr.jpg', white_shellr)

        img = cv2.cvtColor(imag, cv2.COLOR_RGB2HLS)
        white_min1 = np.array([0,0, 12], np.uint8)#190
        white_max1 = np.array([255, 255, 255], np.uint8)#255
        white_mask1 = cv2.inRange(img, white_min1, white_max1)
        white_shell1 = -(cv2.blur(white_mask1,(10,10)))
        misc.imsave('output_images/wk1.jpg', white_shell1)

        white_min2 = np.array([0,0, 20], np.uint8)#190
        white_max2 = np.array([255, 255, 255], np.uint8)#255
        white_mask2 = cv2.inRange(img, white_min2, white_max2)
        white_shell2 = -(cv2.blur(white_mask2,(10,10)))
        misc.imsave('output_images/wk2.jpg', white_shell2)

        img = cv2.cvtColor(imag, cv2.COLOR_RGB2HLS)
        white_min3 = np.array([0, 190, 0], np.uint8)
        white_max3 = np.array([255, 255, 255], np.uint8)
        white_mask3 = cv2.inRange(img, white_min3, white_max3)
        white_shell3 = cv2.blur(white_mask3,(10,10))
        misc.imsave('output_images/wk.jpg', white_shell3)
        #edge detection
		#canny
        #img=cv2.bilateralFilter(img,9,75,75)
        img = cv2.GaussianBlur(imn, (1,1), 0)

        # imgc[(white_shell3 != 0) & (final_edge != 0)] = 255
        # imgc[(yellow_shell != 0) & (final_edge != 0)] = 255


        img1=cv2.Canny(img, 50,150)
        edges=img1
        misc.imsave('output_images/canny.jpg', edges)
        imgc_d = np.zeros_like(edges)
        imgc_d[(white_shell3 != 0) | (yellow_shell != 0)] = 255
        img_d_canny=cv2.Canny(imgc_d, 50,150)
        edges_d_canny=img_d_canny
        misc.imsave('output_images/canny_d.jpg', edges_d_canny)

        #sobel
        sobelx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=15)
        sobely = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=15)
        abs_sobelx = np.abs(sobelx)
        abs_sobely = np.abs(sobely)
        scaled_sobel = np.arctan2(abs_sobely, abs_sobelx)
        sxbinary = np.zeros_like(scaled_sobel)
        sxbinary[(scaled_sobel >=0.7) & (scaled_sobel <= 1.2)] = 1
        #misc.imsave('output_images/sx.jpg', sxbinary)

        gradmag = np.sqrt(sobelx ** 2 + sobely ** 2)
        scale_factor = np.max(gradmag) / 255
        gradmag = (gradmag / scale_factor).astype(np.uint8)
        binary_output = np.zeros_like(gradmag)
        binary_output[(gradmag >=50) & (gradmag <= 255)] = 1
        #misc.imsave('output_images/binary.jpg', binary_output)
		#sobel grad and mag
        sobel_combined = np.zeros_like(sxbinary)
        sobel_combined[(binary_output==1) | (sxbinary == 1)] = 1
        sobel_out = np.zeros_like(sxbinary)
        sobel_out[np.abs((sobel_combined==1)-(binary_output==1))]=1
        sobel_out=cv2.cvtColor(sobel_out, cv2.COLOR_HSV2RGB)
        sobel_out=cv2.cvtColor(sobel_out, cv2.COLOR_BGR2GRAY)
        #misc.imsave('output_images/sobel_out.jpg', sobel_out)
        #COMBINE BOTH
        #final_edge=np.zeros_like(edges)
        #final_edge[(img1==1)&(sobel_out==1)]=1
        #misc.imsave('output_images/final_edge.jpg', final_edge)
        final_edge=img1
        #masking with edges

        imga = np.zeros_like(edges)
        imgb = np.zeros_like(edges)
        imgc = np.zeros_like(edges)


        imga[(white_shell1 != 0) & (final_edge != 0)] = 255
        imga[(yellow_shell != 0) & (final_edge != 0)] = 255

        misc.imsave('output_images/colour_masks1.jpg', imga)

        imgb[(white_shell2 != 0) & (final_edge != 0)] = 255
        imgb[(yellow_shell != 0) & (final_edge != 0)] = 255
        misc.imsave('output_images/colour_masks2.jpg', imgb)


        # imgc[(white_shell3 != 0) & (final_edge != 0)] = 255
        # imgc[(yellow_shell != 0) & (final_edge != 0)] = 255
        # imgc[(yellow_shell != 0) & (white_shell3 != 0)] = 255

        # imgc[(white_shell3 != 0) | (yellow_shell != 0)] = 255
        imgc[(white_shell3 != 0) & (img_d_canny != 0)] = 255
        imgc[(yellow_shell != 0) & (img_d_canny != 0)] = 255
        imgc[(yellow_shell != 0) & (white_shell3 != 0)] = 255

        misc.imsave('output_images/colour_masks3.jpg', imgc)

        

        return imgc