import cv2
import numpy as np
from scipy import misc


class Polydrawer:
    def draw(self, img, left_fit, right_fit, Minv, confidence):
        color_warp = np.zeros_like(img).astype(np.uint8)

        fity = np.linspace(0, img.shape[0] - 1, img.shape[0])
        left_fitx = left_fit[0] * fity ** 2 + left_fit[1] * fity + left_fit[2]
        right_fitx = right_fit[0] * fity ** 2 + right_fit[1] * fity + right_fit[2]

        # Recast the x and y points into usable format for cv2.fillPoly()
        pts_left = np.array([np.transpose(np.vstack([left_fitx, fity]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, fity])))])
        pts = np.hstack((pts_left, pts_right))
        pts = np.array(pts, dtype=np.int32)
        
       # print(confidence)
        b, g, r = self.adjustConfidenceColor(confidence)
        cv2.fillPoly(color_warp, pts, (r, g, b))
        misc.imsave('output_images/prewarp.jpg',color_warp)
        newwarp = cv2.warpPerspective(color_warp, Minv, (img.shape[1], img.shape[0]))
        # Combine the result with the original image
        result = cv2.addWeighted(img, 1, newwarp, 0.3, 0)

        return result

    def adjustConfidenceColor(self,confidence):

        #color_angle=(confidence/10.0)*60
        color_angle=80
        hsv_color = np.uint8([[[color_angle,255,255]]])
        bgr_color = cv2.cvtColor(hsv_color,cv2.COLOR_HSV2BGR)
        b = np.asscalar(bgr_color[0,0,0])
        g = np.asscalar(bgr_color[0,0,1])
        r = np.asscalar(bgr_color[0,0,2])
        return b, g, r
