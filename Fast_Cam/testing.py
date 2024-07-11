###########################################################################################################################
################################################# Libraries ###############################################################
###########################################################################################################################
from PyQt6.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot, QTimer, QMetaObject, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from pyphantom import Phantom, utils
import time
import numpy as np
import os
import cv2
from threading import Lock
from Camera_Selector_Fn import camera_selector

############################################################################################################################
######################################## Thread for Frame Capture ##########################################################
############################################################################################################################

class WorkerCapture(QObject):
    # Signal to emit captured frames
    frames_captured = Signal(np.ndarray)
    capture_finished = Signal(list)

    def __init__(self, cam, capture_duration):
        super().__init__()
        self.cam = cam
        self.capture_duration = capture_duration
        self.running = True
        self.frames = []
        self.particle_signal = False
        self.frame_count = 0

    @Slot()
    def capture_frame(self):
        if not self.running:
            self.capture_finished.emit(self.frames)
            return

        live_image = self.cam.get_live_image()
        img = np.array(live_image, dtype=np.uint8)
        self.frames_captured.emit(live_image)  # Emit each captured frame for live image
        self.frame_count += 1

        if self.particle_signal and self.frame_count < 20:
            self.frames.append(img)

        print(f"WorkerCapture: Captured frame {self.frame_count}")

    def signal_P(self):
        self.particle_signal = True
        self.frame_count = 0

    def stop(self):
        self.running = False

############################################################################################################################
######################################## Class for Managing Frame Capture ##################################################
############################################################################################################################

class FrameCapture(QObject):
    def __init__(self, cam, capture_duration):
        super().__init__()

        # Path to save the snapshots
        self.snapshots_folder = os.path.expanduser('~/Desktop/Test/Snapshots')
        self.cam = cam
        self.capture_duration = capture_duration
        self.frames = []
        self.worker_capture = WorkerCapture(self.cam, self.capture_duration)
        self.worker_capture.frames_captured.connect(self.store_frame)
        self.worker_capture.capture_finished.connect(self.capture_finished)
        self.thread_capture = QThread()
        self.worker_capture.moveToThread(self.thread_capture)
        self.thread_capture.start()
        print("FrameCapture: Initialized and thread started")

        self.initUI()  # Initialize the user interface

        self.timer = QTimer()
        self.timer.timeout.connect(self.worker_capture.capture_frame)
        self.timer.start(30)  # Capture frame every 5 ms

    def initUI(self):
        self.window = QWidget()
        self.window.setWindowTitle('Frame Capture Control')
        layout = QVBoxLayout()

        self.stop_button = QPushButton('Stop Capture')
        self.stop_button.clicked.connect(self.stop_capture)
        layout.addWidget(self.stop_button)

        self.particle_button = QPushButton('Trigger Particle Signal')
        self.particle_button.clicked.connect(self.trigger_particle_signal)
        layout.addWidget(self.particle_button)

        self.window.setLayout(layout)
        self.window.show()

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
        print(f"FrameCapture: Saved {len(frames)} frames to {self.snapshots_folder}")
        print("FrameCapture: Capture finished")
        QApplication.quit()  # Quit the application event loop

    def stop_capture(self):
        self.timer.stop()
        
        QMetaObject.invokeMethod(self.worker_capture, "stop", Qt.ConnectionType.QueuedConnection)

    def trigger_particle_signal(self):
        self.worker_capture.signal_P()
        #QMetaObject.invokeMethod(self.worker_capture, "signal_P", Qt.ConnectionType.QueuedConnection)

    def get_frames(self):
        print(f"FrameCapture: Returning {len(self.frames)} captured frames")
        return self.frames

############################################################################################################################
################################################# Main Script ##############################################################
############################################################################################################################

if __name__ == "__main__":
    import sys

    # Create a QApplication instance
    app = QApplication(sys.argv)

    # Initialize Phantom object and connect to the camera
    ph = Phantom()                                       # Make a Phantom object
    cam_count = ph.camera_count                          # Check for connected cameras
    cam = camera_selector(ph)                            # Connect to the specific camera
    print("Connected to the existing camera")
    cam = ph.Camera(0)

    # Now we have at least one camera connected   
    ph.discover(print_list=True)  #[name, serial number, model, camera number]

    # Get parameters
    res = cam.resolution                                 # Getting resolution
    print('{:d} x {:d} Resolution'.format(res[0], res[1]))
    frame_rate = cam.frame_rate                          # Getting frame rate
    print("%s Framerate(fps)" % (frame_rate))
    part_count = cam.partition_count                     # Get partition count 
    print("%s Partition_count" % (part_count))
    exposure = cam.exposure                              # Get exposure time
    print("%s exposure(us)" % (exposure))

    # Set parameters
    cam.resolution = (500, 500)                          # Setting resolution
    cam.frame_rate = 5500                                # Setting framerate
    cam.post_trigger_frames = 30                         # Setting post trigger frames
    cam.partition_count = 1                              # Setting partition count 

    # Start recording
    cam.record()                                         # Start recording
    time.sleep(3)                                        # Wait for the recording to stabilize
    cam.trigger()                                        # Trigger 

    # Start the frame capture
    capture_duration = 3  # Duration for which to capture frames (useless)
    frame_capture = FrameCapture(cam, capture_duration)

    # Run the application event loop
    app.exec()

    # Clean up
    cam.close()                                          # Unregister camera objects
    ph.close()                                           # Unregister Phantom() objects
