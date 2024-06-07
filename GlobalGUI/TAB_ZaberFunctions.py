import zaber_motion
from zaber_motion import Units
from zaber_motion.binary import Connection,CommandCode
from random import randint
import numpy as np
import pyqtgraph as pg
import pickle
from PySide6.QtCore import QTimer
import time
from scipy.signal import welch, get_window

COM4="COM4"


#---------- Init --------------#
def InitializeZaber(self):
    self.Zaber_COM="COM4"
    try:
        print("------- Zaber Initialization -------")
        with Connection.open_serial_port(self.Zaber_COM) as connection:
            device_list = connection.detect_devices()
            self.ui.load_pages.z1_slider.setValue(float(device_list[0].get_position())*100/1039370)
            self.ui.load_pages.z1_data.setText(str((float(device_list[0].get_position()))*4.95/1039370))
            self.ui.load_pages.z1_cm.setChecked(True)
            self.ui.load_pages.z1_mm.setChecked(False)
            self.ui.load_pages.z1_um.setChecked(False)
            self.ui.load_pages.z1_Absolute.setChecked(True)
            self.ui.load_pages.z1_Relative.setChecked(False)

            self.ui.load_pages.z2_slider.setValue(float(device_list[2].get_position())*100/1039370)
            self.ui.load_pages.z2_data.setText(str((float(device_list[2].get_position()))*4.95/1039370))
            self.ui.load_pages.z2_cm.setChecked(True)
            self.ui.load_pages.z2_mm.setChecked(False)
            self.ui.load_pages.z2_um.setChecked(False)
            self.ui.load_pages.z2_Absolute.setChecked(True)
            self.ui.load_pages.z2_Relative.setChecked(False)


            self.ui.load_pages.z3_slider.setValue(float(device_list[1].get_position())*100/1039370)
            self.ui.load_pages.z3_data.setText(str((float(device_list[1].get_position()))*4.95/1039370))
            self.ui.load_pages.z3_cm.setChecked(True)
            self.ui.load_pages.z3_mm.setChecked(False)
            self.ui.load_pages.z3_um.setChecked(False)
            self.ui.load_pages.z3_Absolute.setChecked(True)
            self.ui.load_pages.z3_Relative.setChecked(False)

            def seb():
                number=CheckDevices()
                print("tenemos "+ str(number))
                self.ui.load_pages.n_devices_p3.setText(str(number) + " Devices")
            
            def GHome():

                with Connection.open_serial_port(self.Zaber_COM) as connection:
                    device_list = connection.detect_devices()
                    device_list[1].home()
                    device_list[2].home()
                    device_list[0].home()

                #Move Zaber to previous position
                with open('zaberset1.pkl', 'rb') as file:
                    Zab1 = pickle.load(file)
                    SetZaber1(Zab1[0],Zab1[1],Zab1[2],Zab1[3],Zab1[4],Zab1[5])
                with open('zaberset2.pkl', 'rb') as file:
                    Zab2 = pickle.load(file)
                    SetZaber2(Zab2[0],Zab2[1],Zab2[2],Zab2[3],Zab2[4],Zab2[5])
                with open('zaberset3.pkl', 'rb') as file:
                    Zab3 = pickle.load(file)
                    SetZaber3(Zab3[0],Zab3[1],Zab3[2],Zab3[3],Zab3[4],Zab3[5])


                with Connection.open_serial_port(self.Zaber_COM) as connection:
                    device_list = connection.detect_devices()
                    self.ui.load_pages.z1_slider.setValue(float(device_list[0].get_position())*100/1039370)
                    self.ui.load_pages.z1_data.setText(str((float(device_list[0].get_position()))*4.95/1039370))
                    self.ui.load_pages.z1_cm.setChecked(True)
                    self.ui.load_pages.z1_mm.setChecked(False)
                    self.ui.load_pages.z1_um.setChecked(False)
                    self.ui.load_pages.z1_Absolute.setChecked(True)
                    self.ui.load_pages.z1_Relative.setChecked(False)

                    self.ui.load_pages.z2_slider.setValue(float(device_list[2].get_position())*100/1039370)
                    self.ui.load_pages.z2_data.setText(str((float(device_list[2].get_position()))*4.95/1039370))
                    self.ui.load_pages.z2_cm.setChecked(True)
                    self.ui.load_pages.z2_mm.setChecked(False)
                    self.ui.load_pages.z2_um.setChecked(False)
                    self.ui.load_pages.z2_Absolute.setChecked(True)
                    self.ui.load_pages.z2_Relative.setChecked(False)


                    self.ui.load_pages.z3_slider.setValue(float(device_list[1].get_position())*100/1039370)
                    self.ui.load_pages.z3_data.setText(str((float(device_list[1].get_position()))*4.95/1039370))
                    self.ui.load_pages.z3_cm.setChecked(True)
                    self.ui.load_pages.z3_mm.setChecked(False)
                    self.ui.load_pages.z3_um.setChecked(False)
                    self.ui.load_pages.z3_Absolute.setChecked(True)
                    self.ui.load_pages.z3_Relative.setChecked(False)

            def SHome1():
                with Connection.open_serial_port(self.Zaber_COM) as connection:
                    device_list = connection.detect_devices()
                    device_list[0].home()
                    self.ui.load_pages.z1_slider.setValue(float(device_list[0].get_position())*100/1039370)
                    self.ui.load_pages.z1_data.setText(str((float(device_list[0].get_position()))*4.95/1039370))
                    self.ui.load_pages.z1_cm.setChecked(True)
                    self.ui.load_pages.z1_mm.setChecked(False)
                    self.ui.load_pages.z1_um.setChecked(False)
                    self.ui.load_pages.z1_Absolute.setChecked(True)
                    self.ui.load_pages.z1_Relative.setChecked(False)
                
            def SHome2():
                with Connection.open_serial_port(self.Zaber_COM) as connection:
                    device_list = connection.detect_devices()
                    device_list[2].home()
                    self.ui.load_pages.z2_slider.setValue(float(device_list[2].get_position())*100/1039370)
                    self.ui.load_pages.z2_data.setText(str((float(device_list[2].get_position()))*4.95/1039370))
                    self.ui.load_pages.z2_cm.setChecked(True)
                    self.ui.load_pages.z2_mm.setChecked(False)
                    self.ui.load_pages.z2_um.setChecked(False)
                    self.ui.load_pages.z2_Absolute.setChecked(True)
                    self.ui.load_pages.z2_Relative.setChecked(False)

            def SHome3():
                with Connection.open_serial_port(self.Zaber_COM) as connection:
                    device_list = connection.detect_devices()
                    device_list[1].home()
                    self.ui.load_pages.z3_slider.setValue(float(device_list[1].get_position())*100/1039370)
                    self.ui.load_pages.z3_data.setText(str((float(device_list[1].get_position()))*4.95/1039370))
                    self.ui.load_pages.z3_cm.setChecked(True)
                    self.ui.load_pages.z3_mm.setChecked(False)
                    self.ui.load_pages.z3_um.setChecked(False)
                    self.ui.load_pages.z3_Absolute.setChecked(True)
                    self.ui.load_pages.z3_Relative.setChecked(False)

            def Set_z1():
                Abs=self.ui.load_pages.z1_Absolute.isChecked()
                Rel=self.ui.load_pages.z1_Relative.isChecked()
                cm=self.ui.load_pages.z1_cm.isChecked()
                mm=self.ui.load_pages.z1_mm.isChecked()
                um=self.ui.load_pages.z1_um.isChecked()
                dist=self.ui.load_pages.z1_data.text()
                self.ui.load_pages.z1_slider.setValue(50)
                SetZaber1(Abs,Rel,cm,mm,um,dist)
                with Connection.open_serial_port(self.Zaber_COM) as connection:
                    device_list = connection.detect_devices()
                    self.ui.load_pages.z1_slider.setValue(float(device_list[0].get_position())*100/1039370)

            def Set_z2():
                Abs=self.ui.load_pages.z2_Absolute.isChecked()
                Rel=self.ui.load_pages.z2_Relative.isChecked()
                cm=self.ui.load_pages.z2_cm.isChecked()
                mm=self.ui.load_pages.z2_mm.isChecked()
                um=self.ui.load_pages.z2_um.isChecked()
                dist=self.ui.load_pages.z2_data.text()
                SetZaber2(Abs,Rel,cm,mm,um,dist)
                with Connection.open_serial_port(self.Zaber_COM) as connection:
                    device_list = connection.detect_devices()
                    self.ui.load_pages.z2_slider.setValue(float(device_list[2].get_position())*100/1039370)
    
            def Set_z3():
                Abs=self.ui.load_pages.z3_Absolute.isChecked()
                Rel=self.ui.load_pages.z3_Relative.isChecked()
                cm=self.ui.load_pages.z3_cm.isChecked()
                mm=self.ui.load_pages.z3_mm.isChecked()
                um=self.ui.load_pages.z3_um.isChecked()
                dist=self.ui.load_pages.z3_data.text()
                SetZaber3(Abs,Rel,cm,mm,um,dist)
                with Connection.open_serial_port(self.Zaber_COM) as connection:
                    device_list = connection.detect_devices()
                    self.ui.load_pages.z3_slider.setValue(float(device_list[1].get_position())*100/1039370)

            def z1_Slider():
                val=self.ui.load_pages.z1_slider.value()
                SliderZ1(val)
                self.ui.load_pages.z1_data.setText(str((val*5)/100))

            def z2_Slider():
                val=self.ui.load_pages.z2_slider.value()
                SliderZ2(val)
                self.ui.load_pages.z2_data.setText(str((val*5)/100))

            def z3_Slider():
                val=self.ui.load_pages.z3_slider.value()
                SliderZ3(val)
                self.ui.load_pages.z3_data.setText(str((val*5)/100))

            def z1_Slider_Info():
                val=self.ui.load_pages.z1_slider.value()
                self.ui.load_pages.z1_data.setText(str((val*5)/100))
                self.ui.load_pages.z1_cm.setChecked(True)
                self.ui.load_pages.z1_mm.setChecked(False)
                self.ui.load_pages.z1_um.setChecked(False)
                self.ui.load_pages.z1_Absolute.setChecked(True)
                self.ui.load_pages.z1_Relative.setChecked(False)

            def z2_Slider_Info():
                val=self.ui.load_pages.z2_slider.value()
                self.ui.load_pages.z2_data.setText(str((val*5)/100))
                self.ui.load_pages.z2_cm.setChecked(True)
                self.ui.load_pages.z2_mm.setChecked(False)
                self.ui.load_pages.z2_um.setChecked(False)
                self.ui.load_pages.z2_Absolute.setChecked(True)
                self.ui.load_pages.z2_Relative.setChecked(False)

            def z3_Slider_Info():
                val=self.ui.load_pages.z3_slider.value()
                self.ui.load_pages.z3_data.setText(str((val*5)/100))
                self.ui.load_pages.z3_cm.setChecked(True)
                self.ui.load_pages.z3_mm.setChecked(False)
                self.ui.load_pages.z3_um.setChecked(False)
                self.ui.load_pages.z1_Absolute.setChecked(True)
                self.ui.load_pages.z1_Relative.setChecked(False)

            #Constant speed     #######################################################
            def Stop_z1():
                with Connection.open_serial_port("COM4") as connection:
                    response = connection.generic_command(1, CommandCode.STOP, 1)
                    device_list = connection.detect_devices()
                    pos=((float(device_list[0].get_position()))*4.95/1039370)
                    self.ui.load_pages.z1_slider.setValue(float(device_list[0].get_position())*100/1039370)
                    self.ui.load_pages.z1_data.setText(str((float(device_list[0].get_position()))*4.95/1039370))
                
                NewLine=[True, False,True,False,False,pos]
                with open('zaberset1.pkl', 'wb') as file:
                    pickle.dump(NewLine, file)

            def Stop_z2():
                with Connection.open_serial_port("COM4") as connection:
                    response = connection.generic_command(2, CommandCode.STOP, 1)
                    device_list = connection.detect_devices()
                    pos=((float(device_list[2].get_position()))*4.95/1039370)
                    self.ui.load_pages.z2_slider.setValue(float(device_list[2].get_position())*100/1039370)
                    self.ui.load_pages.z2_data.setText(str((float(device_list[2].get_position()))*4.95/1039370))

                NewLine=[True, False,True,False,False,pos]
                with open('zaberset2.pkl', 'wb') as file:
                    pickle.dump(NewLine, file)

            def Stop_z3():
                with Connection.open_serial_port("COM4") as connection:
                    response = connection.generic_command(3, CommandCode.STOP, 1)
                    device_list = connection.detect_devices()
                    pos=((float(device_list[1].get_position()))*4.95/1039370)
                    self.ui.load_pages.z3_slider.setValue(float(device_list[1].get_position())*100/1039370)
                    self.ui.load_pages.z3_data.setText(str((float(device_list[1].get_position()))*4.95/1039370))
                
                NewLine=[True, False,True,False,False,pos]
                with open('zaberset3.pkl', 'wb') as file:
                    pickle.dump(NewLine, file)

            def Left_z1():
                speed=float(self.ui.load_pages.z1speed.text())
                speed=speed*1000*1.6381/1.9843
                with Connection.open_serial_port("COM4") as connection:
                    response = connection.generic_command(1, CommandCode.MOVE_AT_CONSTANT_SPEED, int(-speed))
            
            def Left_z2():
                speed=float(self.ui.load_pages.z2speed.text())
                speed=speed*1000*1.6381/1.9843
                with Connection.open_serial_port("COM4") as connection:
                    response = connection.generic_command(2, CommandCode.MOVE_AT_CONSTANT_SPEED, int(-speed))
            
            def Left_z3():
                speed=float(self.ui.load_pages.z3speed.text())
                speed=speed*1000*1.6381/1.9843
                with Connection.open_serial_port("COM4") as connection:
                    response = connection.generic_command(3, CommandCode.MOVE_AT_CONSTANT_SPEED, int(-speed))
            
            def Right_z1():
                speed=float(self.ui.load_pages.z1speed.text())
                speed=speed*1000*1.6381/1.9843
                with Connection.open_serial_port("COM4") as connection:
                    response = connection.generic_command(1, CommandCode.MOVE_AT_CONSTANT_SPEED, int(speed))
            
            def Right_z2():
                speed=float(self.ui.load_pages.z2speed.text())
                speed=speed*1000*1.6381/1.9843
                with Connection.open_serial_port("COM4") as connection:
                    response = connection.generic_command(2, CommandCode.MOVE_AT_CONSTANT_SPEED, int(speed))
            
            def Right_z3():
                speed=float(self.ui.load_pages.z3speed.text())
                speed=speed*1000*1.6381/1.9843
                with Connection.open_serial_port("COM4") as connection:
                    response = connection.generic_command(3, CommandCode.MOVE_AT_CONSTANT_SPEED, int(speed))

            # Button connections ######################################################
            self.ui.load_pages.z1_slider.sliderMoved.connect(z1_Slider_Info)
            self.ui.load_pages.z2_slider.sliderMoved.connect(z2_Slider_Info)
            self.ui.load_pages.z3_slider.sliderMoved.connect(z3_Slider_Info)

            self.ui.load_pages.z1_slider.sliderReleased.connect(z1_Slider)
            self.ui.load_pages.z2_slider.sliderReleased.connect(z2_Slider)
            self.ui.load_pages.z3_slider.sliderReleased.connect(z3_Slider)

            #Home
            self.ui.load_pages.zabercon_p3.clicked.connect(seb)
            self.ui.load_pages.globalhome_p3.clicked.connect(GHome)
            self.ui.load_pages.home1_p3.clicked.connect(SHome1)
            self.ui.load_pages.home2_p3.clicked.connect(SHome2)
            self.ui.load_pages.home3_p3.clicked.connect(SHome3)

            self.ui.load_pages.z1_set.clicked.connect(Set_z1)
            self.ui.load_pages.z2_Set.clicked.connect(Set_z2)
            self.ui.load_pages.z3_Set.clicked.connect(Set_z3)
            #Stop 
            self.ui.load_pages.z1_Stop.clicked.connect(Stop_z1)
            self.ui.load_pages.z2_Stop.clicked.connect(Stop_z2)
            self.ui.load_pages.z3_Stop.clicked.connect(Stop_z3)
            #Constant Speed
            self.ui.load_pages.z1_left.clicked.connect(Left_z1)
            self.ui.load_pages.z1_right.clicked.connect(Right_z1)
            self.ui.load_pages.z2_left.clicked.connect(Left_z2)
            self.ui.load_pages.z2_right.clicked.connect(Right_z2)
            self.ui.load_pages.z3_left.clicked.connect(Left_z3)
            self.ui.load_pages.z3_right.clicked.connect(Right_z3)
        print("------- Zaber Ready -------")
    except:
        print('------- Error Zaber Connection -------')
        self.ui.load_pages.n_devices_p3.setText("0 Devices")

    #def RequestUpdateGraph():
    #    self.data_line_Vol.setData(self.DAQ_X_Axis, self.DAQ_Data)
    #    #self.data_line_Freq.setData(self.dataFreq,self.dataFreqY)

    #Timer Adquisition
    #self.timerZaberPlot = QTimer()
    #self.timerZaberPlot.setInterval(1/10)
    #self.timerZaberPlot.timeout.connect(RequestUpdateGraph)


def CheckDevices():
    with Connection.open_serial_port(COM4) as connection:
        device_list = connection.detect_devices()
        return len(device_list)

#---------- Zaber 1 --------------#
def SetZaber1(Abs,Rel,cm,mm,um,dist):
    with Connection.open_serial_port(COM4) as connection:
        device_list = connection.detect_devices()
        if Abs:
            if cm:
                device_list[0].move_absolute(float(dist), Units.LENGTH_CENTIMETRES)
            elif mm:
                device_list[0].move_absolute(float(dist), Units.LENGTH_MILLIMETRES)
            elif um:
                device_list[0].move_absolute(float(dist), Units.LENGTH_MICROMETRES)
        if Rel:
            if cm:
                device_list[0].move_relative(float(dist), Units.LENGTH_CENTIMETRES)
            elif mm:
                device_list[0].move_relative(float(dist), Units.LENGTH_MILLIMETRES)
            elif um:
                device_list[0].move_relative(float(dist), Units.LENGTH_MICROMETRES)

        pos=((float(device_list[0].get_position()))*4.95/1039370)
    
    NewLine=[True, False,cm,mm,um,pos]
    with open('zaberset1.pkl', 'wb') as file:
        pickle.dump(NewLine, file)


def SliderZ1(val):    
    with Connection.open_serial_port(COM4) as connection:
        device_list = connection.detect_devices()
        device_list[0].move_absolute(float((val*5)/100), Units.LENGTH_CENTIMETRES)
        pos=((float(device_list[0].get_position()))*4.95/1039370)
    NewLine=[True, False,True,False,False,pos]
    with open('zaberset1.pkl', 'wb') as file:
        pickle.dump(NewLine, file)

#---------- Zaber 2 --------------#
def SetZaber2(Abs,Rel,cm,mm,um,dist):
    with Connection.open_serial_port(COM4) as connection:
        device_list = connection.detect_devices()
        if Abs:
            if cm:
                device_list[2].move_absolute(float(dist), Units.LENGTH_CENTIMETRES)
            elif mm:
                device_list[2].move_absolute(float(dist), Units.LENGTH_MILLIMETRES)
            elif um:
                device_list[2].move_absolute(float(dist), Units.LENGTH_MICROMETRES)
        if Rel:
            if cm:
                device_list[2].move_relative(float(dist), Units.LENGTH_CENTIMETRES)
            elif mm:
                device_list[2].move_relative(float(dist), Units.LENGTH_MILLIMETRES)
            elif um:
                device_list[2].move_relative(float(dist), Units.LENGTH_MICROMETRES)
        pos=((float(device_list[2].get_position()))*4.95/1039370)
    NewLine=[True, False,cm,mm,um,pos]
    with open('zaberset2.pkl', 'wb') as file:
        pickle.dump(NewLine, file)


def SliderZ2(val):
    
    with Connection.open_serial_port(COM4) as connection:
        device_list = connection.detect_devices()
        device_list[2].move_absolute(float((val*5)/100), Units.LENGTH_CENTIMETRES)
        pos=((float(device_list[2].get_position()))*4.95/1039370)
    NewLine=[True, False,True,False,False,pos]
    with open('zaberset2.pkl', 'wb') as file:
        pickle.dump(NewLine, file)


#---------- Zaber 3 --------------#
def SetZaber3(Abs,Rel,cm,mm,um,dist):
    with Connection.open_serial_port(COM4) as connection:
        device_list = connection.detect_devices()
        if Abs:
            if cm:
                device_list[1].move_absolute(float(dist), Units.LENGTH_CENTIMETRES)
            elif mm:
                device_list[1].move_absolute(float(dist), Units.LENGTH_MILLIMETRES)
            elif um:
                device_list[1].move_absolute(float(dist), Units.LENGTH_MICROMETRES)
        if Rel:
            if cm:
                device_list[1].move_relative(float(dist), Units.LENGTH_CENTIMETRES)
            elif mm:
                device_list[1].move_relative(float(dist), Units.LENGTH_MILLIMETRES)
            elif um:
                device_list[1].move_relative(float(dist), Units.LENGTH_MICROMETRES)
        pos=((float(device_list[1].get_position()))*4.95/1039370)
    
    NewLine=[True, False,cm,mm,um,pos]
    with open('zaberset3.pkl', 'wb') as file:
        pickle.dump(NewLine, file)

def SliderZ3(val):
    
    with Connection.open_serial_port(COM4) as connection:
        device_list = connection.detect_devices()
        device_list[1].move_absolute(float((val*5)/100), Units.LENGTH_CENTIMETRES)
        pos=((float(device_list[1].get_position()))*4.95/1039370)
    NewLine=[True, False,True,False,False,pos]
    with open('zaberset3.pkl', 'wb') as file:
        pickle.dump(NewLine, file)