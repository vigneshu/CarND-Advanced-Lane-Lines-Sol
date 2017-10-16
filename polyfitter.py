import cv2
import numpy as np
from scipy import misc

class Polyfitter:
    def __init__(self):
        self.left_fit = None
        self.right_fit = None
        self.leftx = None
        self.rightx = None

    def polyfit(self, img):
        return self.polyfit_sliding(img)
    def polyfit_sliding(self, img):

               
        
        histogram = np.sum(img[int(img.shape[0] / 2):, :], axis=0)
        out_img = np.dstack((img, img, img)) * 255
        midpoint = np.int(histogram.shape[0] / 2)
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint

        nwindows = 9
        window_height = np.int(img.shape[0]  / nwindows)
        nonzero = img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        leftx_current = leftx_base
        rightx_current = rightx_base
        margin = 100
        margin_l = 50
        margin_r = 150
        minpix = 50
        left_lane_inds = []
        right_lane_inds = []

        for window in range(nwindows - 1):
            win_y_low = img.shape[0] - (window + 1) * window_height
            win_y_high = img.shape[0] - window * window_height
            win_xleft_low = leftx_current - margin_l
            win_xleft_high = leftx_current + margin_r
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            cv2.rectangle(out_img, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), (0, 255, 0), 2)
            cv2.rectangle(out_img, (win_xright_low, win_y_low), (win_xright_high, win_y_high), (0, 255, 0), 2)
            misc.imsave("output_images/rectangles.jpg", out_img)
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (
                nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (
                nonzerox < win_xright_high)).nonzero()[0]
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            if len(good_left_inds) > minpix:
                leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > minpix:
                rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        left_lane_image = np.zeros_like(img)
        # print("left_lane_inds",left_lane_inds)
        # print("left_lane_inds",left_lane_inds.shape)
        # left_lane_image[left_lane_inds]
        self.leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        self.rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        # nonzerotrial0 = img.nonzero()

#        print(self.leftx)
#        print(lefty)
#        print(self.rightx)
#        print(righty)
#        print(((self.leftx==[])|(lefty==[])|(self.rightx==[])|(righty==[])))
#        print(len(self.leftx)==0)

        flag = False
        if ((len(self.leftx)==0)|(len(lefty)==0)|(len(self.rightx)==0)|(len(righty)==0)):
            print("dropping leftx,rightx,lefty,righty zero")
            self.left_fit = [0,0,0]
            self.right_fit = [0,0,0]
            flag = True
        else:
            self.left_fit = np.polyfit(lefty, self.leftx, 2)
            self.right_fit = np.polyfit(righty, self.rightx, 2)
#        self.left_fit=[0,0,0]
#        self.right_fit = [0,0,0]
        ploty = np.linspace(0, 719, num=720)  # to cover same y-range as image
        y_eval = np.max(ploty)
        left_curverad = ((1 + (2 * self.left_fit[0] * y_eval + self.left_fit[1]) ** 2) ** 1.5) / np.absolute(2 * self.left_fit[0])
        right_curverad = ((1 + (2 * self.right_fit[0] * y_eval + self.right_fit[1]) ** 2) ** 1.5) / np.absolute(2 * self.right_fit[0])

        ratio = left_curverad / right_curverad
        # if ratio < 0.66 or ratio > 1.5:
        # if ratio < 0.46 or ratio > 1.5:
        # if ratio < 0.46 or ratio > 1.65:
        if ratio < 0.2 or ratio > 10:
        # if ratio < 0.46 or ratio > 1.8:
        # if ratio < 0.3 or ratio > 2:
            self.left_fit = [0,0,0]
            self.right_fit = [0,0,0]
            print("ratio bad dropping ",ratio) 
            if flag:
                print("leftx,rightx,lefty,righty zero and bad ratio") 
        flagg = False
        if self.left_fit is None:
            flagg = True
        if self.right_fit is None:
            flagg = True
        if np.all(self.left_fit == [0.0,0.0,0.0]):
            flagg = True
        if np.all(self.right_fit == [0.0,0.0,0.0]):
            flagg = True
        if np.all(self.left_fit == [0,0,0]):
            flagg = True
        if np.all(self.right_fit == [0,0,0]):
            flagg = True 
        return self.left_fit, self.right_fit

    def measure_curvature(self, img):
        ploty = np.linspace(0, 719, num=720)  # to cover same y-range as image
        quadratic_coeff = 3e-4  # arbitrary quadratic coefficient
        y_eval = np.max(ploty)
        left_curverad = ((1 + (2 * self.left_fit[0] * y_eval + self.left_fit[1]) ** 2) ** 1.5) / np.absolute(2 * self.left_fit[0])
        right_curverad = ((1 + (2 * self.right_fit[0] * y_eval + self.right_fit[1]) ** 2) ** 1.5) / np.absolute(2 * self.right_fit[0])
        # print(left_curverad, right_curverad)

        ym_per_pix = 30 / 720  # meters per pixel in y dimension
        xm_per_pix = 3.7 / 700  # meters per pixel in x dimension

        ratio = left_curverad / right_curverad
        # if ratio < 0.46 or ratio > 1.65:
        if ratio < 0.66 or ratio > 1.5:
            print('Warning: shitty ratio {}'.format(ratio))

        lane_leftx = self.left_fit[0] * (img.shape[0] - 1) ** 2 + self.left_fit[1] * (img.shape[0] - 1) + self.left_fit[2]
        lane_rightx = self.right_fit[0] * (img.shape[0] - 1) ** 2 + self.right_fit[1] * (img.shape[0] - 1) + self.right_fit[2]

        car_pos = ((img.shape[1] / 2) - ((lane_leftx + lane_rightx) / 2)) * xm_per_pix

        return (left_curverad + right_curverad) / 2,round(car_pos,2)
