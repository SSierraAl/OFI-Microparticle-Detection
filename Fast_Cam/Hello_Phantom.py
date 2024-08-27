
#*****************************************************************************/
#                                                                   
#  Copyright (C) 1992-2023 Vision Research Inc. All Rights Reserved.
#                                                                   
#  The licensed information contained herein is the property of     
#  Vision Research Inc., Wayne, NJ, USA  and is subject to change   
#  without notice.                                                  
#                                                                   
#  No part of this information may be reproduced, modified or       
#  transmitted in any form or by any means, electronic or           
#  mechanical, for any purpose, without the express written         
#  permission of Vision Research Inc.                               
#                                        
#   Version                            
#           August 4, 2023
#
#           August 24, 2023
#               added small delay after trigger command
#
#*****************************************************************************/

# -*- coding: utf-8 -*-

"""
Created on Fri Aug  4 12:47:48 2023

Hello Phantom, lets get camera connected 

"""

#________Load phantom libraies and related/needed modules_____________
from pyphantom import Phantom, utils, cine
import time
import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
from Camera_Selector_Fn import camera_selector

#_____________CONNECT______________

ph = Phantom()                                       #make a phantom object
cam_count = ph.camera_count                          #lets see if a camera is around
# if cam_count == 0:                                  #if no camera is connected, makes simulated camera
#      print("No cameras connected, making simulated camera")
#      ph.add_simulated_camera(sensor_type=utils.SensorTypeEnum.MONO)
#      cam = ph.Camera(0)
cam = camera_selector(ph)                             #to connect to specific camera
print("Connected to the existing camera")
cam = ph.Camera(0)    
#____now we have atleast one camera connected   
                                         
ph.discover(print_list = True)  #[name, serial number, model, camera number]

# #Get parameters
res=cam.resolution                                 #geting resolution
print ('{:d} {} {:d} {}'.format(res[0],'x',res[1],'Resolution'))
frame_rate = cam.frame_rate                         #geting frame rate
print("%s Framerate(fps)" % (frame_rate))
part_count = cam.partition_count                    #get partition count 
print("%s Partition_count" % (part_count))
exposure = cam.exposure                             #get exposure time
print("%s exposure(us)" % (exposure))


#Set parameters
cam.resolution = (640, 128)                        #setting resolution
cam.frame_rate = 8000                                #setting framerate
cam.post_trigger_frames = 100                         #setting post trigger frames
cam.partition_count = 1                             #setting partition count 

#Record 
cam.record()                                        #start recording
time.sleep(3)                                       #wait recording time
cam.trigger()                                       #trigger 
time.sleep(2)                                       #wait recording result
cine1 = cam.Cine(1)                                 #make cine object for cine in ram we just recorded

#----------Task 1: read and display an image from the recorded cine------------

image1 = [] #initilize 
test_range = utils.FrameRange(cine1.range.last_image-50, cine1.range.last_image)  #set range, utils.FrameRange(int, int), this is how we create a FrameRange
image1 = cine1.get_images(test_range)         #get_images(Framerange), return 3d array for monochrome
img = np.squeeze(image1)
#plt.imshow(img[0])
#plt.show()

#----------Task 2: save the recording in a raw cine file. It can be played in PCC application-------- 

#cine1.save_dialog()
#use cine1.save() and give the path, format, and range we want to save.
cine1.save(filename = os.path.expanduser('~')+'\Desktop\Test\TestFile', format = utils.FileTypeEnum(0), range = utils.FrameRange(cine1.range.last_image-50, cine1.range.last_image)) 

#---------Task 3: save the recording as a group of tif image files. 
#cine1.save_dialog()

cine1.save(filename = os.path.expanduser('~')+'\Desktop\Test\TestFile', format = utils.FileTypeEnum(-8), range = utils.FrameRange(cine1.range.last_image-50, cine1.range.last_image)) 

cam.close()                                    #unregister camera objects
ph.close()                                     #unregister phantom() objects