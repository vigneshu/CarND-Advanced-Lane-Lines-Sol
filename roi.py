import cv2
import numpy as np

class ROI:
    def __init__(self):
        self.left_mask_start=0
        self.left_mask_end=150
        self.middle_mask_start=450
        self.middle_mask_end=1279-self.middle_mask_start
        self.right_mask_start=1279-self.left_mask_end
        self.right_mask_end=1279

    def maskImage(self, img):
#        img[:,self.left_mask_start:self.left_mask_end]=[0,0,0]
#        img[:,self.middle_mask_start:self.middle_mask_end]=[0,0,0]
#        img[:,self.right_mask_start:self.right_mask_end]=[0,0,0]       
        img[:,self.left_mask_start:self.left_mask_end]=0
        img[:,self.middle_mask_start:self.middle_mask_end]=0
        img[:,self.right_mask_start:self.right_mask_end]=0
        return img
