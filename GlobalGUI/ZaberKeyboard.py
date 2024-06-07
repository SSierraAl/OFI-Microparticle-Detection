import time
import keyboard
import zaber_motion
from zaber_motion import Units
from zaber_motion.binary import Connection,CommandCode


COM_4="COM4"
step=0.1

global posX
global posY
global posZ


def movIncrease(pos,stp):
    output=0
    if pos+stp>4.95:
        output=4.95
    else:
        output=pos+stp
    return output
def movDecrease(pos,stp):
    output=0
    if pos-stp<0.05:
        output=0.05
    else:
        output=pos-stp
    return output
    


with Connection.open_serial_port(COM_4) as connection:
    device_list = connection.detect_devices()
    posX=float(device_list[0].get_position())*4.95/1039370
    posY=float(device_list[2].get_position())*4.95/1039370
    posZ=float(device_list[1].get_position())*4.95/1039370




while True:

    if keyboard.is_pressed('w'):
        with Connection.open_serial_port(COM_4) as connection:
            device_list = connection.detect_devices()
            print('mov X')
            movement= movIncrease(posX,step)
            posX=movement
            print(movement)
            device_list[0].move_absolute(posX, Units.LENGTH_CENTIMETRES)
            time.sleep(0.2) 
    if keyboard.is_pressed('s'):
        with Connection.open_serial_port(COM_4) as connection:
            device_list = connection.detect_devices()
            print('mov X')
            movement= movDecrease(posX,step)
            posX=movement
            print(movement)
            device_list[0].move_absolute(posX, Units.LENGTH_CENTIMETRES)
            time.sleep(0.2) 


    if keyboard.is_pressed('a'):
        with Connection.open_serial_port(COM_4) as connection:
            device_list = connection.detect_devices()
            print('mov Y')
            movement= movIncrease(posY,step)
            posY=movement
            print(movement)
            device_list[2].move_absolute(posY, Units.LENGTH_CENTIMETRES)
            time.sleep(0.2) 
    if keyboard.is_pressed('d'):
        with Connection.open_serial_port(COM_4) as connection:
            device_list = connection.detect_devices()
            movement= movDecrease(posY,step)
            posY=movement
            print('mov Y')
            print(movement)
            device_list[2].move_absolute(posY, Units.LENGTH_CENTIMETRES)
            time.sleep(0.2) 


    if keyboard.is_pressed('t'):
        with Connection.open_serial_port(COM_4) as connection:
            device_list = connection.detect_devices()
            print('mov Z')
            movement= movIncrease(posZ,step)
            posZ=movement
            print(movement)
            device_list[1].move_absolute(posZ, Units.LENGTH_CENTIMETRES)
            time.sleep(0.2)
    if keyboard.is_pressed('g'):
        with Connection.open_serial_port(COM_4) as connection:
            device_list = connection.detect_devices()
            print('mov Z')
            movement= movDecrease(posZ,step)
            posZ=movement
            print(movement)
            device_list[1].move_absolute(posZ, Units.LENGTH_CENTIMETRES)
            time.sleep(0.2) 

        
        




