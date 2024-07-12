
###########################################################################################################################
################################################# Libraries ###############################################################
###########################################################################################################################
from PyQt6.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

from Camera_Selector_Fn import camera_selector
from pyphantom import Phantom
from collections import deque

import time
import numpy as np
import os
import cv2
import keyboard

#TO DO: 
# ----- Comment all the functions that you create and try to parametrize everything

# -----(0) Understand the impact of the different parameters of the camera (to find the best configuration)
# -----(2) Function to trigger and capture the next or previous frames
# -----(1) Find one lamp that could help us for our experiments (check the lumens) could be the ring of leds and order it (could be the ring of leds or something like this one https://fr.rs-online.com/web/p/lampes-pour-machines-outils/2121679?cm_mmc=FR-PLA-DS3A-_-google-_-CSS_FR_FR_ePMax_Prio1-_--_-2121679&matchtype=&&gad_source=1&gclid=CjwKCAjwnK60BhA9EiwAmpHZw9NaNhuPyE_6Dn3sZRkUbXiPlQdIWDbpzl2Y7rCb7k0ze0_DYp9TSBoCD0gQAvD_BwE&gclsrc=aw.ds)

#Experiments
# ----- Trigger the camera with the amplitud signal
# ----- Test with real particles to set the maximum speed permited for the experiments# ----- Think that at the end we need to correlate the signal of the laser and the camera in the same time for the particle
# ----- Additional just if possible: (check how to trigger the camera just with the image of the particles!)

#different parameters of the camera 

#1) Resolution: This determines the detail captured in the image. Higher resolutions capture more detail but can reduce the frame rate and increase data storage requirements.

#2) Frame Rate: This is the number of frames captured per second. Higher frame rates are crucial for capturing fast-moving objects but can reduce the resolution and increase data storage requirements.

#3) Exposure Time: This is the duration the sensor is exposed to light for each frame. Shorter exposure times are better for reducing motion blur but require more light. Longer exposure times can introduce motion blur but work better in low-light conditions.

#4) Partition Count: This refers to the ability to divide the camera's memory into multiple segments or partitions. Each partition acts as a separate storage area where different sequences of captured frames can be saved independently. This feature is particularly useful for various applications and scenarios in high-speed photography.

#This feature allows:
#Multiple Takes Without Downloading: Capture several high-speed events successively without needing immediate data downloads.
#Event Segmentation: Store different events in separate memory areas for easier analysis.
#Efficient Memory Use: Manage memory better by selectively clearing and reusing specific partitions.
#Avoiding Overwrites: Reduce the risk of overwriting important footage.




class WorkerCapture(QObject):
    # Signal to emit captured frames
    #frames_captured = Signal(np.ndarray)
    capture_finished = Signal(list)

    def __init__(self, cam,resolution,trigger_frames,snapshots_folder,image_label,global_counter_cam):
        super().__init__()
        self.cam = cam
        
        self.global_counter_cam=global_counter_cam
        self.resolution =resolution
        self.snapshots_folder=snapshots_folder
        self.image_label=image_label
        self.trigger_frames=trigger_frames
        self.image_queue = deque(maxlen=self.trigger_frames) 
        self.running = False
        self.frames = []
        self.particle_signal = False
        self.particle_signal_prev = False
        self.frame_count = 0
        #rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        self.h=self.resolution[1]
        self.w=self.resolution[0]
        self.ch=3
        self.bytes_per_line = self.ch * self.w

    @Slot()
    def capture_frame(self):
        while self.running == True:
            live_image = self.cam.get_live_image()
            
            self.image_queue.append(live_image)
            if self.particle_signal_prev==True:
                self.save_img(list(self.image_queue))
                self.particle_signal_prev=False

            if self.particle_signal==True:
                self.frame_count=self.frame_count+1
                self.frames.append(live_image)
                if self.frame_count>= self.trigger_frames:
                    self.particle_signal = False
                    self.save_img(self.frames)

            live_image = (live_image / 256).astype(np.uint8)
            #print("Live Image Data Type:", live_image.dtype)
            qt_img = self.convert_cv_qt(live_image)
            self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, rgb_image):
        """Convert image to QPixmap"""
        convert_to_Qt_format = QImage(rgb_image.data, self.w, self.h, self.bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.resolution[0], self.resolution[1], Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)


    #Consider do it in other Thread !!!!! 
    def save_img(self,Group_Images):
        os.makedirs(self.snapshots_folder, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M")
        for i, frame in enumerate(Group_Images):
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            filename = f'Snapshot_{timestamp}_{self.global_counter_cam}_{i+1}.png'
            cv2.imwrite(os.path.join(self.snapshots_folder, filename), frame)
            print(i)
        print(f"FrameCapture: Saved {len(Group_Images)} frames to {self.snapshots_folder}")
        print("FrameCapture: Capture finished")


    # Control Signals ############################################


    # To triggger the camera to capture the events
    def signal_P(self):
        self.particle_signal = True
        self.frames = []
        self.frame_count = 0
        self.global_counter_cam=self.global_counter_cam+1
    #Trigger for previous frames
    def signal_P_Prev(self):
        self.global_counter_cam=self.global_counter_cam+1
        self.particle_signal_prev=True

    def stop(self):
        self.running = False
        #cv2.destroyAllWindows

    def startstart(self):
        self.running=True

    #Just to store the image with an increasing number
    def Update_counter(self):
        return self.global_counter_cam

############################################################################################################################
######################################## Class for Managing Frame Capture ##################################################
############################################################################################################################

class FrameCapture(QObject):
    workCAM_requested = Signal(int)
    def __init__(self,main_window):
        super().__init__()

        self.global_counter_cam=0
        self.main_window=main_window
        # Initialize Phantom object and connect to the camera
        self.ph = Phantom()                                       # Make a Phantom object
        self.cam_count = self.ph.camera_count                     # Check for connected cameras


        #Interfaz buttons connections #######################################
        #Start all the process
        self.main_window.ui.load_pages.but_start_cam.clicked.connect(self.but_start_cam)
        #Stop all the process and kill the thread
        self.main_window.ui.load_pages.but_stop_cam.clicked.connect(self.but_stop_capture_cam)
        #Capture the next X frames
        self.main_window.ui.load_pages.but_trigger_next_cam.clicked.connect(self.trigger_particle_signal)
        #Capture the previous X frames
        self.main_window.ui.load_pages.but_trigger_previous_cam.clicked.connect(self.trigger_particle_signal_prev)


    #Start all the process, and read the parameters, be carefull after we need to be able to stop everything
    def but_start_cam(self):

        self.cam = camera_selector(self.ph)                            # Connect to the specific camera
        self.cam = self.ph.Camera(0)
        # Now we have at least one camera connected   
        self.ph.discover(print_list=True)  #[name, serial number, model, camera number]

        #Update parameters based on the GUI
        self.cam.partition_count  = 1
        self.cam.frame_rate = int(self.main_window.ui.load_pages.line_frame_rate_cam.text())
        #Number of images to save
        self.trigger_frames = int(self.main_window.ui.load_pages.line_trigger_frame_cam.text())
        self.snapshots_folder = self.main_window.ui.load_pages.line_directory_cam.text()
        self.cam.resolution = (int(self.main_window.ui.load_pages.line_resolution_cam_w.text()),int(self.main_window.ui.load_pages.line_resolution_cam_h.text()))
        self.cam.exposure =int(self.main_window.ui.load_pages.line_exposure_cam.text())
        
        #Resize display widget
        self.main_window.ui.load_pages.image_label.resize(self.cam.resolution[0],self.cam.resolution[1])


        # Check parameters ###################################################################
        res = self.cam.resolution                                 # Getting resolution
        self.main_window.ui.load_pages.line_resolution_cam_w.setText(str(res[0])) 
        self.main_window.ui.load_pages.line_resolution_cam_h.setText(str(res[1])) 
        frame_rate = self.cam.frame_rate   
        self.main_window.ui.load_pages.line_frame_rate_cam.setText(str(frame_rate))                       
        exposure = self.cam.exposure    
        self.main_window.ui.load_pages.line_exposure_cam.setText(str(exposure))

        # Start recording
        self.cam.record()                                    # Start recording
        time.sleep(2)                                        # Wait for the recording to stabilize
        self.cam.trigger()                                   # Trigger 

        #Initialize Class
        self.frames = []
        self.worker_capture = WorkerCapture(self.cam,self.cam.resolution,self.trigger_frames,self.snapshots_folder,self.main_window.ui.load_pages.image_label,self.global_counter_cam)
        self.workCAM_requested.connect(self.worker_capture.capture_frame)
        self.thread_capture = QThread()
        self.worker_capture.moveToThread(self.thread_capture)

        #Start thread (init)
        self.thread_capture.start()
        #Set running variable in True
        self.worker_capture.startstart()
        # Call the infinit loop to request the camera
        self.workCAM_requested.emit(0)



    #Stop the infinity loop
    def but_stop_capture_cam(self):
        self.global_counter_cam=self.worker_capture.Update_counter()
        self.worker_capture.stop()  
        self.thread_capture.terminate() 
        self.cam.close()

    #Stop timmer and terminate the thread whtn the app is closed
    def close_capture_cam(self):
        self.worker_capture.stop()        
        self.thread_capture.terminate()
        self.cam.close()


    def trigger_particle_signal(self):
        self.worker_capture.signal_P()

    def trigger_particle_signal_prev(self):
        self.worker_capture.signal_P_Prev()

