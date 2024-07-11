
###########################################################################################################################
################################################# Libraries ###############################################################
###########################################################################################################################
from PyQt6.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot, QTimer
from Camera_Selector_Fn import camera_selector
from pyphantom import Phantom, utils
import time
import numpy as np
import os
import cv2
import keyboard
from threading import Thread

#TO DO: 
# ----- Comment all the functions that you create and try to parametrize everything

# -----(0) Understand the impact of the different parameters of the camera (to find the best configuration)
# -----(2) Function to trigger and capture the next or previous frames
# -----(1) Find one lamp that could help us for our experiments (check the lumens) could be the ring of leds and order it (could be the ring of leds or something like this one https://fr.rs-online.com/web/p/lampes-pour-machines-outils/2121679?cm_mmc=FR-PLA-DS3A-_-google-_-CSS_FR_FR_ePMax_Prio1-_--_-2121679&matchtype=&&gad_source=1&gclid=CjwKCAjwnK60BhA9EiwAmpHZw9NaNhuPyE_6Dn3sZRkUbXiPlQdIWDbpzl2Y7rCb7k0ze0_DYp9TSBoCD0gQAvD_BwE&gclsrc=aw.ds)

#Experiments
# ----- Trigger the camera with the amplitud signal
# ----- Test with real particles to set the maximum speed permited for the experiments# ----- Think that at the end we need to correlate the signal of the laser and the camera in the same time for the particle
# ----- Additional just if possible: (check how to trigger the camera just with the image of the particles!)



class WorkerCapture(QObject):
    # Signal to emit captured frames
    #frames_captured = Signal(np.ndarray)
    capture_finished = Signal(list)

    def __init__(self, cam):
        super().__init__()
        self.cam = cam
        self.running = False
        self.frames = []
        self.particle_signal = False
        self.frame_count = 0

    @Slot()
    def capture_frame(self):
        
        while self.running == True:

            live_image = self.cam.get_live_image()
            #img = np.array(live_image, dtype=np.uint8)
            #self.frames_captured.emit(live_image)  # Emit each captured frame for live image
            if bool(self.cam._live_cine.is_color.value):    
                frame = cv2.cvtColor(live_image, cv2.COLOR_RGB2BGR)          
            cv2.imshow('live', frame)  # Use cv2 library to show the image you saved
            cv2.waitKey(100)
            #self.frame_count += 1
            if keyboard.is_pressed('space') or keyboard.is_pressed('esc') or keyboard.is_pressed('enter'):    #close window and break out of loop by pressing space, esc, or enter 
                cv2.destroyAllWindows
                break
        #if self.particle_signal and self.frame_count < 20:
        #    self.frames.append(img)


    def signal_P(self):
        self.particle_signal = True
        self.frame_count = 0

    def stop(self):
        self.running = False
        #cv2.destroyAllWindows

    def startstart(self):
        self.running=True

############################################################################################################################
######################################## Class for Managing Frame Capture ##################################################
############################################################################################################################

class FrameCapture(QObject):
    workCAM_requested = Signal(int)
    def __init__(self,main_window):
        super().__init__()

        self.main_window=main_window
        # Initialize Phantom object and connect to the camera
        self.ph = Phantom()                                       # Make a Phantom object
        self.cam_count = self.ph.camera_count                          # Check for connected cameras
        self.cam = camera_selector(self.ph)                            # Connect to the specific camera
        print("Connected to the existing camera")
        self.cam = self.ph.Camera(0)

        # Now we have at least one camera connected   
        self.ph.discover(print_list=True)  #[name, serial number, model, camera number]

        # Get parameters INIT
        res = self.cam.resolution                                 # Getting resolution
        print('{:d} x {:d} Resolution'.format(res[0], res[1]))
        frame_rate = self.cam.frame_rate                          # Getting frame rate
        print("%s Framerate(fps)" % (frame_rate))
        part_count = self.cam.partition_count                     # Get partition count 
        print("%s Partition_count" % (part_count))
        exposure = self.cam.exposure                              # Get exposure time
        print("%s exposure(us)" % (exposure))

        # Path to save the snapshots
        self.frames = []
        self.worker_capture = WorkerCapture(self.cam)
        #self.worker_capture.frames_captured.connect(self.store_frame)
        #self.worker_capture.capture_finished.connect(self.capture_finished)
        self.workCAM_requested.connect(self.worker_capture.capture_frame)
        self.thread_capture = QThread()
        self.worker_capture.moveToThread(self.thread_capture)
        #self.thread_capture.start()
        print("FrameCapture: Initialized and thread started")

        #I dont remember... What is the pourpose of that?
        #self.timer_CAM = QTimer()
        #self.timer_CAM.timeout.connect(self.worker_capture.capture_frame)
        #self.timer_CAM.setInterval(30)

        #Interfaz buttons connections #######################################
        #Start all the process
        self.main_window.ui.load_pages.but_start_cam.clicked.connect(self.but_start_cam)
        #Stop all the process and kill the thread
        self.main_window.ui.load_pages.but_stop_cam.clicked.connect(self.but_stop_capture_cam)
        #Capture the next X frames
        self.main_window.ui.load_pages.but_trigger_next_cam.clicked.connect(self.trigger_particle_signal)
        #Capture the previous X frames
        self.main_window.ui.load_pages.but_trigger_previous_cam.clicked.connect(self.trigger_particle_signal)
        #Additional buttons if needed
        #self.main_window.ui.load_pages.but_additional_1_cam.clicked.connect(self. )
        #self.main_window.ui.load_pages.but_additional_2_cam.clicked.connect(self. )

        # Start recording
        self.cam.record()                                    # Start recording
        time.sleep(2)                                        # Wait for the recording to stabilize
        self.cam.trigger()                                   # Trigger 


    #Start all the process, and read the parameters, be carefull after we need to be able to stop everything
    def but_start_cam(self):
        #Read all the parameters

        self.cam = self.ph.Camera(0) # Not sure

        #Update parameters each time you press start
        self.cam.frame_rate = int(self.main_window.ui.load_pages.line_frame_rate_cam.text())
        self.post_trigger_frames = int(self.main_window.ui.load_pages.line_trigger_frame_cam.text())
        self.cam.partition_count  = int(self.main_window.ui.load_pages.line_partition_count_cam.text())
        self.snapshots_folder = self.main_window.ui.load_pages.line_directory_cam.text()
        self.cam.resolution = (500,500)
        
        #Start thread (init)
        self.thread_capture.start()
        #Set running variable in True
        self.worker_capture.startstart()
        # Call the infinit loop to request the camera
        self.workCAM_requested.emit(0)


    #Stop timmer
    def but_stop_capture_cam(self):
        self.worker_capture.stop()


    @Slot(np.ndarray)
    def store_frame(self, frame):
        if bool(self.cam._live_cine.is_color.value):    
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)          
        cv2.imshow('live', frame)  # Use cv2 library to show the image you saved
        cv2.waitKey(1)

    @Slot(list)
    def capture_finished(self, frames):
        os.makedirs(self.snapshots_folder, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        for i, frame in enumerate(frames):
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            filename = f'Snapshot_{timestamp}_{i+1}.png'
            cv2.imwrite(os.path.join(self.snapshots_folder, filename), frame)
        #print(f"FrameCapture: Saved {len(frames)} frames to {self.snapshots_folder}")
        #print("FrameCapture: Capture finished")



    def trigger_particle_signal(self):
        self.worker_capture.signal_P()
        #QMetaObject.invokeMethod(self.worker_capture, "signal_P", Qt.ConnectionType.QueuedConnection)

    def get_frames(self):
        #print(f"FrameCapture: Returning {len(self.frames)} captured frames")
        return self.frames
    


