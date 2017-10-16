import cv2
from matplotlib import pyplot as plt
from moviepy.video.io.VideoFileClip import VideoFileClip
from scipy import misc
import os,sys,time
from polyfitfilter import Polyfitfilter
from polydrawer import Polydrawer
from polyfitter import Polyfitter
from thresholder import Thresholder
from warper import Warper
from roi import ROI
from Undistorter import Undistorter
import numpy as np


polyfitfilter = Polyfitfilter()
thresholder = Thresholder()
warper = Warper()
polyfitter = Polyfitter()
polydrawer = Polydrawer()
roi=ROI()
undistorter = Undistorter()


def main():
    #input file name without extension type
    
    video ='project_video'
    
    path='./inputvideos/'
    video_in=path+video
    time_name= time.strftime("%Y%m%d-%H%M%S")
    white_output = 'output_videos/{}_{}.webm'.format(video,time_name)
    #change the subclip size
    # clip1 = VideoFileClip('{}.mp4'.format(video_in)).subclip(13, 15)
    clip1 = VideoFileClip('{}.mp4'.format(video_in)).subclip(1, 50)
    # clip1 = VideoFileClip('{}.mp4'.format(video_in)).subclip(24, 25)
    # clip1 = VideoFileClip('{}.mp4'.format(video_in)).subclip(21, 25)
    # clip1 = VideoFileClip('{}.mp4'.format(video_in)).subclip(38, 42)
    # clip1 = VideoFileClip('{}.mp4'.format(video_in)).subclip(1, 3)
    
    white_clip = clip1.fl_image(process_image)  # NOTE: this function expects color images!!
    white_clip.write_videofile(white_output, audio=False, codec='libvpx')
    #white_clip.write_videofile(white_output, audio=False)
def region_of_interest(img, vertices):
    """
    Applies an image mask.
    
    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    """
    #defining a blank mask to start with
    mask = np.zeros_like(img)   
    
    #defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255
        
    #filling pixels inside the polygon defined by "vertices" with the fill color    
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    
    #returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def process_image(base):

    fig = plt.figure(figsize=(10,8))
    i = 1
    imgpoly=base
    imgu= undistorter.undistort(base)
    misc.imsave('output_images/undistorted.jpg', imgu)



    #z='undistorted_{}.jpg'.format(time_name)
    #z1="./output_images/"+z
    imgw = warper.warp(imgu)
    misc.imsave('output_images/warped.jpg', imgw)


    imshape = imgw.shape
    vertices = np.array([[(200,imshape[0]),(200, 0), (imshape[1], 0), (imshape[1],imshape[0])]], dtype=np.int32)    
    imgw = region_of_interest(imgw, vertices) 

    imgt = thresholder.threshold(imgw)
    misc.imsave('output_images/thresholded.jpg', imgt)
    img=imgt
    
 
    #img=roi.maskImage(img)
    #misc.imsave('output_images/roi.jpg',img)

    
    # i = show_image(fig, i, img, 'Thresholded', 'gray')

    
    # i = show_image(fig, i, img, 'Warped', 'gray')

    left_fit, right_fit = polyfitter.polyfit(img)

    lane_curve, car_pos = polyfitter.measure_curvature(img)
    # Linear filtering and rejection of bogus data for line coefficients
    left_fit, right_fit = polyfitfilter.filterLineCoefficients(left_fit,right_fit)
    # print(polyfitfilter.confidence)
    img = polydrawer.draw(imgpoly, left_fit, right_fit, warper.Minv, polyfitfilter.confidence)
    misc.imsave('output_images/final.jpg', img)

   

    if car_pos > 0:
        car_pos_text = '{}m right of center'.format(car_pos)
    else:
        car_pos_text = '{}m left of center'.format(abs(car_pos))

    # if polyfitfilter.confidence>0:
    cv2.putText(img, "Lane curve: {}m".format(lane_curve.round()), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,color=(255, 255, 255), thickness=2)
    cv2.putText(img, "Car is {}".format(car_pos_text), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color=(255, 255, 255),thickness=2)    

    # show_image(fig, i, img, 'Final')
    # plt.imshow(img)
    # plt.show()
    return img


def show_image(fig, i, img, title, cmap=None):
    a = fig.add_subplot(2, 2, i)
    plt.imshow(img, cmap)
    a.set_title(title)
    return i + 1


if __name__ == '__main__':
   main()
