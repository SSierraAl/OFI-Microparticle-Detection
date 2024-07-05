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
#          September 13, 2023

#          09/19/2023  
#          written with cv2_color
#
#*****************************************************************************/
# -*- coding: utf-8 -*-
"""
"""

'''
This script is a simple Cine MP4 converter for a color camera
input : cinefile
output : a saved mp4 in C:/Users/Desktop/OUTPUT.mp4', change the directory accordingly

'''
#############################
import keyboard 
import cv2      
import os, os.path
import numpy as np
from pyphantom import cine, Phantom, utils  #this is the phantom sdk
import copy

ph = Phantom()

# ------------------------------------
our_matrix = []
file_path = ph.file_select_dialog()   #put your cine path here, os.path.expanduser skips C:\users\username for you                                                            
our_cine = cine.Cine.from_filepath(file_path)        #make a cine object from our cine file

#loop through cine 1 frame at a time to create matrix, 
for i in range(our_cine.range[0], our_cine.range[1]+1):                               #range is [first, last+1) so we get the whole range                               
    our_matrix.append(our_cine.get_images(utils.FrameRange(i,i)))                     #append get_images() of a frame range 1 image long to our matrix
our_matrix = np.squeeze(our_matrix)      

# Cine Image Parameters / Lengths
print("Cine Image Size: " + str(our_matrix.shape))  
print("Number of images: " + str(len(our_matrix)))                           #number of images
print("Cine Image height " + str(len(our_matrix[0])) )                      #image height
print("Image widths " + str(len(our_matrix[0][0])))                          #image width

#getting size of frames:
frameSize2 = ( len(our_matrix[0][0]), len(our_matrix[0]) )
#creating object out2 that serves to be used later to write frames to mp4 file

MP4out = cv2.VideoWriter('C:/Users/Desktop/OUTPUT.mp4',cv2.VideoWriter_fourcc(*'X264'), 15, frameSize2)

#initializing 8-bit array with the proper frame size
array = np.zeros([len(our_matrix[0]), len(our_matrix[0][0]), 3], dtype=np.uint8)
new_matrix=[]

for i in range(0,len(our_matrix)):

        new_matrix = our_matrix[i,:,:] 
        MP4out.write(cv2.cvtColor(new_matrix, cv2.COLOR_RGB2BGR))
  
MP4out.release()
ph.close()
print("Number of images: " + str(frameSize2))  
