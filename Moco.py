import sys
import serial
import PyTango

class MocoClass(PyTango.DeviceClass):

    cmd_list = { 'RestoreSoftInBeam' : [ [ PyTango.ArgType.DevVoid, "" ],
                                         [ PyTango.ArgType.DevVoid, "" ] ],
                 'Tune' : [ [ PyTango.ArgType.DevVoid, "" ],
                            [ PyTango.ArgType.DevVoid, "" ] ],
                  'TunePeak' : [ [ PyTango.ArgType.DevVoid, "" ],
                            [ PyTango.ArgType.DevVoid, "" ] ],
                  'Go' : [ [ PyTango.ArgType.DevVoid, "" ],
                            [ PyTango.ArgType.DevVoid, "" ] ],
                  'Stop' : [ [ PyTango.ArgType.DevVoid, "" ],
                            [ PyTango.ArgType.DevVoid, "" ] ],
                  'Pause' : [ [ PyTango.ArgType.DevString, "" ],
                            [ PyTango.ArgType.DevVoid, "" ] ],
                  'SetOperationFlags' : [ [ PyTango.ArgType.DevVarStringArray, "" ],
                                        [ PyTango.ArgType.DevVoid, "" ] ],
                  'ClearOperationFlags' : [ [ PyTango.ArgType.DevVarStringArray, "" ],
                                        [ PyTango.ArgType.DevVoid, "" ] ],
                  'GetInfo' : [ [ PyTango.ArgType.DevVoid, "" ],
                            [ PyTango.ArgType.DevVarStringArray, "" ] ],
                  'Reset' : [ [ PyTango.ArgType.DevVoid, "" ],
                            [ PyTango.ArgType.DevVoid, "" ] ],
                  'OnlineCmd' : [ [ PyTango.ArgType.DevString, "" ],
                            [ PyTango.ArgType.DevVarStringArray, "" ] ],
                  'OscilOn' : [ [ PyTango.ArgType.DevVoid, "" ],
                            [ PyTango.ArgType.DevVoid, "" ] ],
                  'OscilOff' : [ [ PyTango.ArgType.DevVoid, "" ],
                            [ PyTango.ArgType.DevVoid, "" ] ],
    }

    attr_list = { 'InBeamConf' : [ [ PyTango.ArgType.DevString ,
                                    PyTango.AttrDataFormat.SCALAR ,
                                    PyTango.AttrWriteType.READ_WRITE] ],
                  'OutBeamConf' : [ [ PyTango.ArgType.DevString ,
                                    PyTango.AttrDataFormat.SCALAR ,
                                    PyTango.AttrWriteType.READ_WRITE] ],
                  'SetPoint' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ],
                  'Mode' : [ [ PyTango.ArgType.DevString ,
                                    PyTango.AttrDataFormat.SCALAR ,
                                    PyTango.AttrWriteType.READ_WRITE] ],
                  'Tau' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ],
                  'SoftBeam' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ ] ],
                  'OperationFlags' : [ [ PyTango.ArgType.DevString,
                                  PyTango.AttrDataFormat.SPECTRUM,
                                  PyTango.AttrWriteType.READ, 
                                  7 ] ],
                  'MocoState' : [ [ PyTango.ArgType.DevString,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ ] ],
                  'Piezo' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ],
                  'ScanSpeed' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ],
                  'OscBeamMainSignal' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ],
                  'OscBeamQuadSignal' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ],
                  'Phase' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ],
                  'Amplitude' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ],
                  'Frequency' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ],
                  'Slope' : [ [ PyTango.ArgType.DevDouble,
                                  PyTango.AttrDataFormat.SCALAR,
                                  PyTango.AttrWriteType.READ_WRITE ] ]


    }
    
    #    Device Properties
    device_property_list = {'serialDevice': [PyTango.DevString,
                                            "name of the system serial device",
                                            [] ],
                            'softwareInBeamAttr': [PyTango.DevString,
                                            "name of the Tango attribute of the in beam",
                                            [] ],
                           }


class Moco(PyTango.Device_4Impl):

    def __init__(self,cl,name):
        PyTango.Device_4Impl.__init__(self, cl, name)
        self.info_stream('In Moco.__init__')
        Moco.init_device(self)

    def init_device(self):
        self.info_stream('In Python init_device method')
        self.get_device_properties(self.get_device_class())
        self.debug_stream("serialDevice: %s; softwareInBeamAttr%s" % (self.serialDevice,self.softwareInBeamAttr))
        self.moco = serial.Serial(self.serialDevice)
        self.moco.timeout = 1.5
        self.moco.open()
        if self.moco.isOpen():
            self.set_state(PyTango.DevState.ON)
        else:
            self.set_state(PyTango.DevState.ALARM)
            self.set_status("Unbable to open serial connection.")
        self.inBeamAttr = PyTango.AttributeProxy(self.softwareInBeamAttr)

    #------------------------------------------------------------------

    def delete_device(self):
        self.info_stream('Moco.delete_device')
        if self.moco.isOpen():
            self.moco.close()

    #------------------------------------------------------------------
    # COMMANDS
    #------------------------------------------------------------------

    def is_RestoreSoftInBeam_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def RestoreSoftInBeam(self):
        inBeam = self.inBeamAttr.read().value
        self.debug_stream("Setting softbeam to %f" % float(inBeam))
        self.setToMoco("SOFTBEAM %f" % float(inBeam))
           
    def is_Tune_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def Tune(self):
        self.setToMoco("TUNE")

    def is_TunePeak_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def TunePeak(self):
        self.setToMoco("TUNE PEAK")

    def is_Go_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def Go(self):
        self.setToMoco("GO")

    def is_Stop_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def Stop(self):
        self.setToMoco("STOP")

    def is_Pause_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def Pause(self, arg):
        self.setToMoco("PAUSE %s" % arg)
      
    def is_SetOperationFlags_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def SetOperationFlags(self, args):
        flags = " ".join(args)
        self.setToMoco("SET %s" % flags)
    
    def is_ClearOperationFlags_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def ClearOperationFlags(self, args):
        self.debug_stream("arg: %s" % repr(args))
        flags = " ".join(args)
        self.debug_stream("flags: %s" % repr(flags))
        self.setToMoco("CLEAR %s" % flags)

    def is_GetInfo_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def GetInfo(self):
        info = self.getFromMoco("?INFO")
        info = [line[:-2] for line in info] #getting rid of last ascii characters "\r\n"
        self.debug_stream("Info: %s" % repr(info))
        return info

    def is_Reset_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def Reset(self):
        self.setToMoco("RESET")
    
    def is_OnlineCmd_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def OnlineCmd(self, arg):
        self.debug_stream("OnlineCmd %s" % arg)
        if arg.startswith('?'):
            ans = self.getFromMoco(arg)
            self.debug_stream("ans = %s" % repr(ans))
            if isinstance(ans, str):
                ans = [ans]
            ans = [line[:-2] for line in ans] #getting rid of last ascii characters "\r\n"
        else:
            self.setToMoco(arg)
            ans = []
        return ans
        
    def is_OscilOn_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def OscilOn(self):
        self.setToMoco("OSCIL ON")
        
    def is_OscilOff_allowed(self):
        return self.get_state() == PyTango.DevState.ON

    def OscilOff(self):
        self.setToMoco("OSCIL OFF")

    #------------------------------------------------------------------
    # ATTRIBUTES
    #------------------------------------------------------------------

    def read_attr_hardware(self, data):
        self.info_stream('In read_attr_hardware')

    def read_InBeamConf(self, the_att):
        self.info_stream("read_InBeamConf")
        ans = self.getFromMoco("?INBEAM")
        inBeamConf = ans[:-2]
        the_att.set_value(inBeamConf)

    def write_InBeamConf(self, the_att):
        self.info_stream("write_InBeamConf")
        conf = the_att.get_write_value()
        self.setToMoco("INBEAM %s" % conf)

    def is_InBeamConf_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_OutBeamConf(self, the_att):
        self.info_stream("read_OutBeamConf")
        ans = self.getFromMoco("?OUTBEAM")
        inBeamConf = ans[:-2]
        the_att.set_value(inBeamConf)

    def write_OutBeamConf(self, the_att):
        self.info_stream("write_OutBeamConf")
        conf = the_att.get_write_value()
        self.setToMoco("OUTBEAM %s" % conf)

    def is_OutBeamConf_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_SetPoint(self, the_att):
        self.info_stream("read_SetPoint")
        ans = self.getFromMoco('?SETPOINT')
        setPoint = float(ans[:-2])
        self.debug_stream("SetPoint = %f" % setPoint)
        the_att.set_value(setPoint)

    def write_SetPoint(self, the_att):
        self.info_stream("write_SetPoint")
        setPoint = the_att.get_write_value()
        self.setToMoco("SETPOINT %f" % setPoint)

    def is_SetPoint_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_Mode(self, the_att):
        self.info_stream("read_Mode")
        ans = self.getFromMoco("?MODE")
        mode = ans[:-2]
        the_att.set_value(mode)

    def write_Mode(self, the_att):
        self.info_stream("write_Mode")
        conf = the_att.get_write_value()
        self.setToMoco("MODE %s" % conf)

    def is_OutBeamConf_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_Tau(self, the_att):
        self.info_stream("read_Tau")
        ans = self.getFromMoco('?TAU')
        tau = float(ans[:-2])
        self.debug_stream("Tau = %f" % tau)
        the_att.set_value(tau)

    def write_Tau(self, the_att):
        self.info_stream("write_Tau")
        tau = the_att.get_write_value()
        self.setToMoco("TAU %f" % tau)

    def is_Tau_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_SoftBeam(self, the_att):
        self.info_stream("read_Tau")
        ans = self.getFromMoco('?SOFTBEAM')
        softBeam = float(ans[:-2])
        self.debug_stream("SoftBeam = %f" % softBeam)
        the_att.set_value(softBeam)

    def write_SoftBeam(self, the_att):
        self.info_stream("write_Tau")
        softBeam = the_att.get_write_value()
        self.setToMoco("SOFTBEAM %f" % softBeam)

    def is_SoftBeam_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_OperationFlags(self, the_att):
        self.info_stream("read_Set")
        ans = self.getFromMoco('?SET')
        set_ = ans[:-2]
        sets = set_.split()
        self.debug_stream("Set = %s" % set_)
        self.debug_stream("Sets = %s" % sets)
        the_att.set_value(sets)

    def is_OperationFlags_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_MocoState(self, the_att):
        self.info_stream("read_MocoState")
        ans = self.getFromMoco('?STATE')
        state = ans[:-2]
        self.debug_stream("State = %s" % state)
        the_att.set_value(state)

    def is_MocoState_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_Piezo(self, the_att):
        self.info_stream("read_Piezo")
        ans = self.getFromMoco('?PIEZO')
        piezo = float(ans[:-2])
        self.debug_stream("Piezo = %f" % piezo)
        the_att.set_value(piezo)

    def write_Piezo(self, the_att):
        self.info_stream("write_Piezo")
        piezo = the_att.get_write_value()
        self.setToMoco("PIEZO %f" % piezo)

    def is_Piezo_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_ScanSpeed(self, the_att):
        self.info_stream("read_ScanSpeed")
        ans = self.getFromMoco('?SPEED')
        speed = float(ans[:-2].split()[0])
        self.debug_stream("ScanSpeed = %f" % speed)
        the_att.set_value(speed)

    def write_ScanSpeed(self, the_att):
        self.info_stream("write_ScanSpeed")
        speed = the_att.get_write_value()
        self.setToMoco("SPEED %f" % speed)

    def is_SpeedScan_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_OscBeamMainSignal(self, the_att):
        self.info_stream("read_OscBeamMainSignal")
        ans = self.getFromMoco('?OSCBEAM')
        values = ans[:-2].split()
        mainSignal = float(values[0])
        self.debug_stream("mainSignal: %f" % mainSignal)
        the_att.set_value(mainSignal)

    def is_OscBeamMainSignal_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_OscBeamQuadSignal(self, the_att):
        self.info_stream("read_OscBeamQuadSignal")
        ans = self.getFromMoco('?OSCBEAM')
        values = ans[:-2].split()
        quadSignal = float(values[1])
        self.debug_stream("quadSignal: %f" % quadSignal)
        the_att.set_value(quadSignal)

    def is_OscBeamQuadSignal_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_Phase(self, the_att):
        self.info_stream("read_Phase")
        ans = self.getFromMoco('?PHASE')
        phase = float(ans[:-2])
        self.debug_stream("phase: %f" % phase)
        the_att.set_value(phase)

    def write_Phase(self, the_att):
        self.info_stream("write_Phase")
        phase = the_att.get_write_value()
        self.setToMoco("PHASE %f" % phase)

    def is_Phase_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_Amplitude(self, the_att):
        self.info_stream("read_Amplitude")
        ans = self.getFromMoco('?AMPLITUDE')
        amplitude = float(ans[:-2])
        self.debug_stream("amplitude: %f" % amplitude)
        the_att.set_value(amplitude)

    def write_Amplitude(self, the_att):
        self.info_stream("write_Amplitude")
        amplitude = the_att.get_write_value()
        self.setToMoco("Amplitude %f" % amplitude)

    def is_Amplitude_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_Frequency(self, the_att):
        self.info_stream("read_Frequency")
        ans = self.getFromMoco('?FREQUENCY')
        frequency = float(ans[:-2])
        self.debug_stream("frequency: %f" % frequency)
        the_att.set_value(frequency)

    def write_Frequency(self, the_att):
        self.info_stream("write_Frequency")
        frequency = the_att.get_write_value()
        self.setToMoco("FREQUENCY %f" % frequency)

    def is_Frequency_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)

    def read_Slope(self, the_att):
        self.info_stream("read_Slope")
        ans = self.getFromMoco('?SLOPE')
        slope = float(ans[:-2])
        self.debug_stream("slope: %f" % slope)
        the_att.set_value(slope)

    def write_Slope(self, the_att):
        self.info_stream("write_Slope")
        slope = the_att.get_write_value()
        self.setToMoco("SLOPE %f" % slope)

    def is_Slope_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)
    #-------------------------------------------------------------------
    # ADITIONAL METHODS
    #-------------------------------------------------------------------

    def setToMoco(self, cmd):
        self.info_stream("setToMoco: %s" % cmd)
        self.moco.write(cmd + "\r")
        self.moco.write("?ERR\r")
        ans = self.moco.readline()
        if ans != "OK\r\n":
            raise Exception("Error: %s" % ans)    

    def getFromMoco(self, cmd):
        MULTILINE_CMDS = ["?HELP", "?INFO"]
        self.moco.write(cmd + "\r")
        if cmd in MULTILINE_CMDS:
            ans = self.moco.readlines()
        else:
            ans = self.moco.readline()
        if ans == "ERROR\r\n":
            self.moco.write("?ERR\r")
            ans = self.moco.readline()
            raise Exception("Error: %s" % ans)
        else:
            self.info_stream("getFromMoco: %s" % ans)
            return ans

if __name__ == '__main__':
    util = PyTango.Util(sys.argv)
    util.add_class(MocoClass, Moco)

    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()
