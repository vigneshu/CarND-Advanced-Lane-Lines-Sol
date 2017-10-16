# **Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./output_images/undistorted.jpg "Undistorted"
[image2]: ./output_images/sat.jpg "saturated"
[image8]: ./output_images/warped.jpg "warped"
[image9]: ./output_images/thresholder3.jpg "thresholded images"
[image3]: ./output_images/canny.jpg "canny"
[image4]: ./output_images/ym.jpg "yellow mask"
[image7]: ./output_images/wk.jpg "white mask"
[image11]: ./output_images/final.jpg "output"
[image12]: ./output_images/color_masks3.jpg "color mask with canny edges"
[video1]: ./output_videos/output_video.webm "project__Video"
[white]: ./output_images/white.jpg "White lane lines"
[yellow]: ./output_images/yellow.jpg "Yellow lane lines"
[combined]: ./output_images/combined_binary.jpg "Combining white and Yellow lines"

[image29]: ./output_images/prewarp.jpg "prewarp"





### Pipeline (single images)


### Camera Calibration

#### 1.1 Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.
 

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

I uploaded my camera chessboard images and used the above functions to calculate the object points.

![alt text][image1]

### 1.2  CROP THE SKY AND TUNNELS
edit!: removed from current implementation as pipeline is changed and this is no longer required.
crop the top part of image containing the sky to remove unncessary detections.

I'm pasting the code on how to crop the sky for documentation.
  #img[0:364,:]=0
  #misc.imsave('output_images/skyskip.jpg', img)

### 1.3 saturate image

converted images to HSV from rgb and saturated the 's' by 2.5 times, which accounts for various situations like rain and snow and their galzing on roads.
To demonstrate this step, I will describe how I apply the distortion correction to one of the test images like this one:

![alt text][image2]

### 1.4. perspective transform martrix

THe points for ipm are :

rc = np.float32([
            [570, 450],
            [710, 450],
            [930, 640],
            [350, 640],
        ])

        dst = np.float32([
            [350, 0],
            [930, 0],
            [930, 720],
            [350, 720],
        ])
This resulted in the following source and destination points:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 570, 450      | 350, 0        | 
| 710, 450      | 930, 0        |
| 930, 640      | 930, 720      |
| 350, 640      | 350, 720      |

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

![alt text][image8]

### 1.5 create masks for white color, yellow color

Applied thresholds to detect white and yellow lines. Below are the images obtained from thresholding
![alt text][yellow] 

![alt text][white]  

Then combined the images to form a complete set of lane lines
![alt text][combined]  



#### 4. polyfit and mean averaging filter for convolution


I used poly fit in 2nd degree equation to find the coeff A,B on left side and right side,

whenever I cannot find reasonable points for coe-ffs, I designed a mean averaging convolution filter for the A,B values which consists
of 10 past values , which even predicts the coeffs for unidentified lanes and color of the road changes to red if lane detection is bad
and if detection is good it shows green color.
The mean filter is not being used at the moment as the results were good without it. Improving the mean filter could help solving the harder video challenges

#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

I calculate this based on centre of lanes on image pixels by using measure curvature function.
As per last reviwer recommendation I went through mehdisquali's medium post on advanced lane detection, I sourced this part from his code with slight modification/my touch.  

I have gone through caltech ali paper and an development on this paper another university, ali's paper has a good real time running program.  


#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

used warper function to unwrap to the original mapping.

applied the color path lanes to the original image in the clip using polyfill function.

---
![alt text][image11]
before wrapping back.
!![alt text][image29]
### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's  my output video
project video
![alt text][video1]



### future considerations
1. make it real time
2. may be reduce my mean averaging weight filter and may try use median filtering for faster response based on previous values.


