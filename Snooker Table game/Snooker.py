import numpy as np
import cv2
import math


def detect_stick(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #masking pink colour in stick
    lower_stick = np.array([150,200,200])
    upper_stick = np.array([200,255,255])
    mask = cv2.inRange(hsv, lower_stick, upper_stick)
    res = cv2.bitwise_and(img,img, mask= mask)

    contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    cnt = contours[0]
    approx = cv2.approxPolyDP(cnt,0.1*cv2.arcLength(cnt,True),True)
    cv2.drawContours(img,contours,-1,(255,0,0),1)

    #centroid of pink contour
    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    centroid = [cx, cy]
    return centroid

def find_intersection( p0, p1, p2, p3 ):
    s10_x = p1[0] - p0[0]
    s10_y = p1[1] - p0[1]
    s32_x = p3[0] - p2[0]
    s32_y = p3[1] - p2[1]
    denom = s10_x * s32_y - s32_x * s10_y

    if denom == 0 : return None # collinear

    denom_is_positive = denom > 0

    s02_x = p0[0] - p2[0]
    s02_y = p0[1] - p2[1]
    s_numer = s10_x * s02_y - s10_y * s02_x

    if (s_numer < 0) == denom_is_positive : return None # no collision

    t_numer = s32_x * s02_y - s32_y * s02_x

    if (t_numer < 0) == denom_is_positive : return None # no collision

    if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive : return None # no collision
    
    # collision detected
    t = float(t_numer) / denom
    intersection_point = [ int(round(p0[0] + (t * s10_x))), int(round(p0[1] + (t * s10_y))) ]
    
    return intersection_point

def play(img,file_number):
    cimg = cv2.medianBlur(img,5)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #hough transform for detecting balls
    circles = cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1,20,param1=40,param2=35,minRadius=20,maxRadius=100)
    circles = np.uint16(np.around(circles))
    rmin=circles[0][0][2]
    x=circles[0][0][0]
    y=circles[0][0][1]
    for i in circles[0,:]:
        
        # draw the outer circle
        cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle   
        cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
        #detecting the white ball
        if i[2] < rmin:
            rmin=i[2]
            x=i[0]
            y=i[1]

    #line tangent to the 7 stacked balls
    cv2.line(cimg,(570,0),(570,420),(225,0,0),3)

    #line from stick to balls
    cx=detect_stick(cimg)[0]
    cy=detect_stick(cimg)[1]
    lengthAB = math.sqrt(abs(x - cx)^2 + abs(y - cy)^2) 
    a = int(round(x + (x - cx)*300 / lengthAB))
    b = int(round(y + (y - cy)*300 / lengthAB))
    cv2.line(cimg,(x,y),(a,b),(225,0,0),3)
    
    #intersection point of two lines
    p = find_intersection([570,0],[570,420],[x,y],[a,b])
    cv2.circle(cimg,(p[0],p[1]),5,(0,0,255),2)

    #assuming 7 balls are evenly stacked from top to bottom
    resolution = img.shape
    h = round(float(resolution[0])/7)
    if p[1] < h:
        ball_number = 8
    elif p[1] < 2*h and p[1] >= h:
        ball_number = 9
    elif p[1] < 3*h and p[1] >= 2*h:
        ball_number = 10
    elif p[1] < 4*h and p[1] >= 3*h:
        ball_number = 11
    elif p[1] < 5*h and p[1] >= 4*h:
        ball_number = 12
    elif p[1] < 6*h and p[1] >= 5*h:
        ball_number = 13
    elif p[1] < 7*h and p[1] >= 6*h:
        ball_number = 14

    #display image and exit
    cv2.imshow('Collision detection '+str(file_number),cimg)

    return ball_number

if __name__ == "__main__":
    #checking output for single image
    img = cv2.imread('test_images/1.jpg')
    ball_number = play(img,1)
    print ball_number, " number ball at target range"
    #checking output for all images
    num_list = []
    for file_number in range(1,11):
        file_name = "test_images/"+str(file_number)+".jpg"
        pic = cv2.imread(file_name)
        ball_number = play(pic,file_number)
        num_list.append(ball_number)
    print num_list

cv2.waitKey(0)
cv2.destroyAllWindows()
