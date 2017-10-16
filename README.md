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
[video1]: ./output_videos/project_video_20170924-224845.webm "project__Video"
[video2]: ./output_videos/harder_challenge_video_20170924-224331.webm "harder_challenge"
[video3]: ./output_videos/challenge_video_20170924-223723.webm "challenge_video"
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
### 1.4 Apply gaussian blur
 I applied gaussian blur on window size of 3x3 to smoothen the image.

#### 1.5. perspective transform martrix

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
    
### 1.6 canny edge detector

Apply cv canny edge detector to find edges in the images and save it under a different name.
![alt text][image3]

### 1.7 create masks for white color, yellow color

Created three kinds of white masks to suits various terrain and weather conditions and have one yellow mask.


all color masks are created in HSL COLOR SPACE for better results.


![yellow mask][image4] 

![white mask][image7]  



### 1.7 bitwise canny and color masks

do bitwise && operator on color mask of yellow and canny and store as img1

do bitwise && operator on color mask of white and img1 , the end result is an image containing strips of lanes.


![alt text][image12]

recommended color masks




#### 4. polyfit and mean averaging filter for convolution

I used poly fit in 2nd degree equation to find the coeff A,B on left side and right side,

whenever I cannot find reasonable points for coe-ffs, I designed a mean averaging convolution filter for the A,B values which consists
of 10 past values , which even predicts the coeffs for unidentified lanes and color of the road changes to red if lane detection is bad
and if detection is good it shows green color.

I even show value of confidence on prediction of lanes for safety in the console.



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
link is ./output_videos/project_video_20170924-224845.webm


harder challenge

![alt text][video2]

link is ./output_videos/harder_challenge_video_20170924-224331.webm

challenge video
![alt text][video3] link is ./output_videos/challenge_video_20170924-223723.webm


### future considerations
1. make it real time
2. may be reduce my mean averaging weight filter and may try use median filtering for faster response based on previous values.

###for reviewers

Thanks for wonderful review 
Followed last review and 

changed my pipeline order and 

IMproved thresholding a lot to improve detection, which is almost in all frames.

Read the papers and mehdi squali's medium post, actually I tried building my pipeline intially based on his and drifted a 
lot to build my own and if run my code vs his code on various datasets, you can see the code never breaks, detection is lot effective and gives a weighted fir filter to smoothen out the detection over 10 frames, my code works under tunnels, bridges, overhead lighting in tunnels, most of the shadows from overhead passes in flyover.

I have tried collecting my own data and analyse the code and compared it with squali's code, I got better run results as mentioned above. I tried all above scenarios.

regarding futurisitc improvements,

I saw ice/ snow data online and I think we need to ahve adaptive switching program with different thresholders for snow/ normal days, same thresholders cannot vbe applied to both. and main thing we observe in snow is tracks of vehicles which are partly dirt/ not so white tracks left by previous vehicles vs lanes in normal days. 

about mud tracks with no roadas or an single road with no lanes, we need to determine in the first place whether it is a single way or doubline line way, which can be from user input/ maps/ even by tracking vehicles in oppositedirection, which is not hte ideal case.

I have seen rain and snow data, during a day with both snow and rain, the road becomes so glossy and shinning, that's the reason I used sautrate in my thresholding to accounting for rain days, lighting conditions and road lane marker wear out causing low color intensities. I tried my code on rain data and it works good.

I have learned a lot on this project, I tried various data sets involving rain, rain with light snow, lane wear out, urban roads, highways, underpasses, bridges. thanks again.



Thanks a lot.
