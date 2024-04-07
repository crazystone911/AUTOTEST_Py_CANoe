import time, os, msvcrt, _thread, cv2, subprocess
from win32com.client import *
from win32com.client.connect import *
from win32com.client import Dispatch

def DoEvents():
    pythoncom.PumpWaitingMessages()
    time.sleep(0.1)
def DoEventsUntil(cond):
    while not cond():
        DoEvents()


class CanoeSync(object):
    """Wrapper class for CANoe Application object"""
    Started = False
    Stopped = False
    ConfigPath = ""
    def __init__(self):
        app = DispatchEx('CANoe.Application')
        app.Configuration.Modified = False
        ver = app.Version
        print('Loaded CANoe version ', 
            ver.major, '.', 
            ver.minor, '.',
            ver.Build, '...', sep='')
        self.App = app
        self.Measurement = app.Measurement  
        self.Running = lambda : self.Measurement.Running
        self.WaitForStart = lambda: DoEventsUntil(lambda: CanoeSync.Started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: CanoeSync.Stopped)
        WithEvents(self.App.Measurement, CanoeMeasurementEvents)

    def Load(self, cfgPath):
        # current dir must point to the script file
        cfg = os.path.join(os.curdir, cfgPath)
        cfg = os.path.abspath(cfg)
        print('Opening: ', cfg)
        self.ConfigPath = os.path.dirname(cfg)
        self.Configuration = self.App.Configuration
        self.App.Open(cfg)

    def LoadTestSetup(self, testsetup):
        self.TestSetup = self.App.Configuration.TestSetup
        path = os.path.join(self.ConfigPath, testsetup)
        testenv = self.TestSetup.TestEnvironments.Add(path)
        testenv = CastTo(testenv, "ITestEnvironment2")
         # TestModules property to access the test modules
        self.TestModules = []
        self.TraverseTestItem(testenv, lambda tm: self.TestModules.append(CanoeTestModule(tm)))
    
    def LoadTestConfiguration(self, testcfgname, testunits):
        """ Adds a test configuration and initialize it with a list of existing test units """
        tc = self.App.Configuration.TestConfigurations.Add()
        tc.Name = testcfgname
        tus = CastTo(tc.TestUnits, "ITestUnits2")
        for tu in testunits:
            tus.Add(tu)
        # TestConfigs property to access the test configuration
        self.TestConfigs = [CanoeTestConfiguration(tc)]

    def Start(self): 
        if not self.Running():
            self.Measurement.Start()
            self.WaitForStart()

    def Run(self):
        self.Start()
        print("Press 'q' to exit ...")

        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8")
                if key == 'q':
                    break

            ignition_status = self.get_Ignition_Status()

            if ignition_status == 4:
                print("Ignition Status is 4. Waiting for 600 seconds...")
                time.sleep(30)
                break

            DoEvents()

        self.Stop()

    def Stop(self):
        if self.Running():
            self.Measurement.Stop()
            self.WaitForStop()


    def get_Ignition_Status(self):
        global value
        channel_num_Ignition_Status = 2
        msg_name_Ignition_Status = "BodyInfo_3"
        sig_name_Ignition_Status = "Ignition_Status"
        bus_type_Ignition_Status = "CAN"

        if self.App is not None:
            bus = self.App.GetBus(bus_type_Ignition_Status)
            signal = bus.GetSignal(channel_num_Ignition_Status, msg_name_Ignition_Status, sig_name_Ignition_Status)
            value = signal.Value
            print("Ignition Status:", value)
        return value


    def get_LocationServices_1(self):
        channel_num_LocationServices_1 = 3
        msg_name_LocationServices_1 = "LocationServices_Data1"
        sig_name_LocationServices_1 = "LocationServices_1"
        bus_type_LocationServices_1 = "CAN"

        if self.App is not None:
            bus = self.App.GetBus(bus_type_LocationServices_1)
            signal = bus.GetSignal(channel_num_LocationServices_1, msg_name_LocationServices_1, sig_name_LocationServices_1)
            value = signal.Value
            print("LocationServices_1:", value)


    def RunTestModules(self):
        """ starts all test modules and waits for all of them to finish"""
        for tm in self.TestModules:
            tm.Start()
    
        # wait for test modules to stop
        while not all([not tm.Enabled or tm.IsDone() for tm in app.TestModules]):
            DoEvents()

    def RunTestConfigs(self):
        """ starts all test configurations and waits for all of them to finish"""
        # start all test configurations
        for tc in self.TestConfigs:
            tc.Start()
    
        # wait for test modules to stop
        while not all([not tc.Enabled or tc.IsDone() for tc in app.TestConfigs]):
            DoEvents()

    def TraverseTestItem(self, parent, testf):
        for test in parent.TestModules: 
            testf(test)
        for folder in parent.Folders: 
            found = self.TraverseTestItem(folder, testf)


class CanoeMeasurementEvents(object):
    """Handler for CANoe measurement events"""
    def OnStart(self): 
        CanoeSync.Started = True
        CanoeSync.Stopped = False
        print("< measurement started >")
    def OnStop(self) : 
        CanoeSync.Started = False
        CanoeSync.Stopped = True
        print("< measurement stopped >")


class CanoeTestModule:
    """Wrapper class for CANoe TestModule object"""
    def __init__(self, tm):
        self.tm = tm
        self.Events = DispatchWithEvents(tm, CanoeTestEvents)
        self.Name = tm.Name
        self.IsDone = lambda: self.Events.stopped
        self.Enabled = tm.Enabled
    def Start(self):
        if self.tm.Enabled:
            self.tm.Start()
            self.Events.WaitForStart()

class CanoeTestConfiguration:
    """Wrapper class for a CANoe Test Configuration object"""
    def __init__(self, tc):        
        self.tc = tc
        self.Name = tc.Name
        self.Events = DispatchWithEvents(tc, CanoeTestEvents)
        self.IsDone = lambda: self.Events.stopped
        self.Enabled = tc.Enabled
    def Start(self):
        if self.tc.Enabled:
            self.tc.Start()
            self.Events.WaitForStart()

# 用于处理测试事件，包括在测试开始和停止时更新状态
class CanoeTestEvents:
    """Utility class to handle the test events"""
    def __init__(self):
        self.started = False
        self.stopped = False
        self.WaitForStart = lambda: DoEventsUntil(lambda: self.started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: self.stopped)
    def OnStart(self):
        self.started = True
        self.stopped = False        
        print("<", self.Name, " started >")
    def OnStop(self, reason):
        self.started = False
        self.stopped = True 
        print("<", self.Name, " stopped >")


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = CanoeSync()
    app.Load('CANoeConfig\CX483_sendSIG.cfg')
    for _ in range(10):
        app.Run()
        app.Stop()
        time.sleep(30)







