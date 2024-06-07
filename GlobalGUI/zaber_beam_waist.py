    
import zaber_motion
from zaber_motion import Units
from zaber_motion.binary import Connection,CommandCode

with Connection.open_serial_port("COM4") as connection:
        device_list = connection.detect_devices()
        #print(len(device_list))
        device_list[2].home()
#        device_list[0].move_absolute((2.25-(3.008-2)), Units.LENGTH_CENTIMETRES)
        

        connection.generic_command(3, CommandCode.MOVE_AT_CONSTANT_SPEED, int(  (((500/1.45)/10)*1.6384/0.047625))   )#/0.047625)) #speed in um/s
    

        
#        with Connection.open_serial_port(self.Zaber_COM) as connection:
#            connection.generic_command(3, CommandCode.MOVE_AT_CONSTANT_SPEED, int(((self.speed/1000)*1.6384/1.9843)))#/0.047625)) #speed in um/s
    