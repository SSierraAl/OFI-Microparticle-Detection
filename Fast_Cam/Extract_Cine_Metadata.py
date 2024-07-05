
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
#          September 6, 2023
#               Clean Up
#
#*****************************************************************************/

'''This demonstrates how we get metadata from a cine using the cine get properties, also included is a function that is currently not yet in the sdk 
to help get human readable timestamps. '''

from pyphantom import Phantom, cine, utils
import pandas as pd
import time
import numpy as np
from Camera_Selector_Fn import camera_selector
ph = Phantom()
cam = camera_selector(ph)

#making sample recording to save and then look at
def make_simple_test_recording(cam):    
    cam.record()
    time.sleep(.2)
    cam.trigger()
    time.sleep(1)
    return cam

#get cine metadata using gets and sets
def show_cine_metadata(cine):
    print ('{:d} {} {:d} {}'.format(cine.resolution[0],'x',cine.resolution[1],'Resolution'))                                            #cine resolution                                                        
    print("%s post trigger frames" % (cine.post_trigger_frames))                  #cine post_trigger_frames
    print("%s frames per second" % (cine.frame_rate))                             #cine frame_rate
    print("%s exposure" % (cine.exposure))                                        #cine exposure
    print("%s edr exposure" % (cine.edr_exposure))                                #cine edr_exposure
    print("cine number %s" % (cine.cine_number))                                  #cine number    
    print(cine.range)                                                              #cine frame_range                            
    print("first frame at %s" % (cine.get_timestamps(cine.range)[0]))  #timestamp first frame (uses pandas library Timestamp function)
    print("last frame at %s" %  (cine.get_timestamps(cine.range)[1]))  #timestamp last frame 
    print("%s brighness" % (cine.bright)) 
    print("%s contrast" % (cine.contrast)) 
    print("%s gamma" % (cine.gamma)) 
    print("%s bits_per_pixel" % (cine.bits_per_pixel))

    
show_cine_metadata(make_simple_test_recording(cam).Cine(1))                       #note that I'm just taking .Cine(1) here, the first one on the camera's ram, but this would work from a cine file as well
cam.clear_ram()                                                                   #clear camera ram  
cam.close()                                                                       #unregister camera object
ph.close()                                                                        #unregister phantom() object