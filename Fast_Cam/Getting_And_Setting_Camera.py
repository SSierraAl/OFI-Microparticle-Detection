
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
#          August 25, 2023
#
#*****************************************************************************/


'''Connecting to a camera, and then getting and setting the most obvious features, like partition count, resolution, frame rate, exposure, etc.'''

from pyphantom import Phantom, phantom, utils, cine 
from Camera_Selector_Fn import camera_selector
import time

#camera selector function
ph = Phantom()
ph.add_simulated_camera()                                           #add simulated camera to pool
#cam = ph.Camera(ph.camera_count-1)                                 #connecting to that simulated camera
cam = ph.Camera(0)                                                  #connecting to real camera
#cam = camera_selector(ph)                                          #can use this function instead to connect to specific camera if you have multiple connected
#get and set some basic settings

def getting_and_setting_test(cam):
    cam.partition_count = 1                                         #partition count set
    cam.resolution = (9999, 9999)                                   #resolution set
    cam.frame_rate = 100                                            #frame rate set
    cam.exposure = 100                                              #exposure set
    cam.edr_exposure = 0                                            #edr exposure set
    cam.quiet = 0                                                   #quiet mode set (1 = quiet mode on)
    #cam.record(cine = 1, delete_all = False)                       #capture mode (parameters optional, defaults shown)                                                    

    print("%s partition(s)" % (cam.partition_count))                #partition count get
    print("%s fps" % (cam.frame_rate))                              #frame rate get    
    print(cam.resolution)                                           #resolution get
    print("Exposure is %s" % (cam.exposure))                        #exposure get
    print("Edr exposure is %s" % (cam.edr_exposure))                #edr exposure get
    print(cam.quiet)                                                #quiet mode get (True = quiet)

    print("Camera sensor Temperature: %s" %(cam.get_selector_uint (utils.CamSelector.gsSensorTemperature)))  #get using selector
    print("Camera cameraTemperature: %s" %(cam.get_selector_int (utils.CamSelector.gsCameraTemperature)))    #get using selector
    print("Camera Model: %s" %(cam.get_selector_string (utils.CamSelector.gsModel)))                         #get using selector
    print("Camera Ip Address: %s" %(cam.get_selector_string (utils.CamSelector.gsIPAddress)))                #get using selector
   
    print("Camera Quiet Fan: %s" %(cam.get_selector_int (utils.CamSelector.gsQuiet)))                       #get using selector
    cam.set_selector_int (utils.SetSelector(utils.CamSelector.gsQuiet,1))                                   #set quiet fan using selector
    print("Camera Quiet Fan On: %s" %(cam.get_selector_int (utils.CamSelector.gsQuiet)))
    time.sleep(3)                                                                                           #wait time

    cam.set_selector_int (utils.SetSelector(utils.CamSelector.gsQuiet,0))
    print("Camera Quiet Fan off: %s" %(cam.get_selector_int (utils.CamSelector.gsQuiet)))
    
    #
    # this is valid for cameras that support programmable I/O 
    # sim cameras DONOT fully support PIO
    #
    print("Camera pio_signal_name: %s" %(cam.pio_signal_name(utils.PioSignal(3,2))))
    print("Camera pio_signal_count: %s" %(cam.pio_signal_count(3)))
    print("Camera pio_get_signal: %s" %(cam.pio_get_signal(3)))
    cam.pio_set_pulse_proc(utils.PulseProcParam(3, 0, 0, 33, 23, 11))
    print("Camera pio_get_pulse_proc: %s" %(cam.pio_get_pulse_proc(3)))

getting_and_setting_test(cam)
cam.clear_ram()                                                     #clear camera ram
cam.close()                                                         #unregister camera object
ph.close()     

