import time, os, msvcrt, _thread, cv2, subprocess
import numpy as np
from win32com.client import *
from win32com.client.connect import *
from win32com.client import Dispatch

def DoEvents():
    pythoncom.PumpWaitingMessages()
    time.sleep(0.1)

def DoEventsUntil(cond):
    while not cond():
        DoEvents()


# CanoeSync类是CANoe应用程序对象的包装类，包含了与CANoe应用程序的交互方法。初始化CANoe应用程序对象，
# 并提供方法来加载配置、启动/停止测量，运行测试模块和配置等操作。

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
        self.Running = lambda: self.Measurement.Running
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
                time.sleep(20)
                # 先获取ADB权限
                subprocess.run(f'adb devices', shell=True)
                subprocess.run(f'adb root', shell=True)
                # 延时后点击
                self.click1()
                time.sleep(5)
                self.click2()
                time.sleep(5)
                self.click3()
                time.sleep(5)
                # 循环去检测屏幕point点是否发生变化
                for _ in range(50):
                    screen_checker.adb_click()
                    screen_checker.judge_screen()
                # self.click_nextsong()
                print("Ignition Status is run, SYNC initial completely, Waiting for 600 seconds...")
                time.sleep(600)
                break
            DoEvents()
        self.Stop()

    def Stop(self):
        if self.Running():
            self.Measurement.Stop()
            self.WaitForStop()

    # 定义抓取Ignition_Status的报文，在主函数打印出来
    def get_Ignition_Status(self):
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
            signal = bus.GetSignal(channel_num_LocationServices_1, msg_name_LocationServices_1,
                                   sig_name_LocationServices_1)
            value = signal.Value
            print("LocationServices_1:", value)

    # 运行所有的测试模块
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

    def click1(self):
        # 定义要点击的位置坐标
        x_coordinate1 = 1130
        y_coordinate1 = 480
        # 构建adb shell命令来模拟点击
        adb_command1 = f"adb shell input tap {x_coordinate1} {y_coordinate1}"
        subprocess.run(adb_command1, shell=True)

    def click2(self):
        x_coordinate2 = 81
        y_coordinate2 = 397
        adb_command2 = f"adb shell input tap {x_coordinate2} {y_coordinate2}"
        subprocess.run(adb_command2, shell=True)

    def click3(self):
        x_coordinate3 = 1535
        y_coordinate3 = 124
        adb_command3 = f"adb shell input tap {x_coordinate3} {y_coordinate3}"
        subprocess.run(adb_command3, shell=True)

    def click_play(self):
        x_coordinate4 = 484
        y_coordinate4 = 640
        adb_command4 = f"adb shell input tap {x_coordinate4} {y_coordinate4}"
        subprocess.run(adb_command4, shell=True)

    def click_nextsong(self):
        x_coordinate4 = 660
        y_coordinate4 = 640
        adb_command4 = f"adb shell input tap {x_coordinate4} {y_coordinate4}"
        subprocess.run(adb_command4, shell=True)

    # def slide(self):
    #     # 定义起始和结束位置的坐标
    #     start_x = 500
    #     start_y = 1000
    #     end_x = 500
    #     end_y = 500
    #     # 定义滑动持续时间（毫秒）
    #     duration = 500
    #     # 构建adb shell命令来模拟滑动
    #     adb_command = f"adb shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}"
    #     # 执行adb shell命令
    #     subprocess.run(adb_command, shell=True)


# 用于处理CANoe测量事件，在测量开始和停止时更新相关状态。
class CanoeMeasurementEvents(object):
    """Handler for CANoe measurement events"""

    def OnStart(self):
        CanoeSync.Started = True
        CanoeSync.Stopped = False
        print("< measurement started >")

    def OnStop(self):
        CanoeSync.Started = False
        CanoeSync.Stopped = True
        print("< measurement stopped >")


# 用于包装CANoe测试模块和测试配置对象的类，提供方法来启动测试模块和配置。
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

class ScreenChecker:
    def __init__(self):
        self.local_path = "C:/Users/15297/Desktop/AUTOTEST_Py_CANoe/ScreenShot"
        self.previous_image = None
        self.previous_timestamp = time.time()

    def take_screenshot(self, file_name):
        subprocess.run(f'adb shell screencap -p /data/{file_name}', shell=True)

    def pull_screenshot(self, file_name):
        subprocess.run(f'adb pull /data/{file_name} {self.local_path}/{file_name}', shell=True)

    def delete_screenshot(self, file_name):
        subprocess.run(f'adb shell rm /data/{file_name}', shell=True)

    def adb_click(self, x=660, y=650):
        subprocess.run(f'adb shell input tap {x} {y}', shell=True)

    def check_region_similarity(self, img1_path, img2_path, x, y, width, height):
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        region1 = img1[y:y + height, x:x + width]
        region2 = img2[y:y + height, x:x + width]
        difference = cv2.subtract(region1, region2)
        b, g, r = cv2.split(difference)
        return cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0

    def judge_screen(self):
        for i in range(30):
            file_name = f"screenshot_{i}.png"
            self.take_screenshot(file_name)
            self.pull_screenshot(file_name)
            self.delete_screenshot(file_name)

            if self.previous_image is not None:
                if not self.check_region_similarity(f"{self.local_path}/{self.previous_image}", f"{self.local_path}/{file_name}", 247, 466, 100, 100):
                    current_timestamp = time.time()
                    time_interval = current_timestamp - self.previous_timestamp
                    print(f'像素发生变化，歌曲加载完成！时间间隔：{time_interval} 秒,当前时间为{current_timestamp}')
                    if time_interval > 10:
                        self.bugreport()
                        break
            self.previous_image = file_name

    def bugreport(self):
        # 生成SYNC的bugreport，并将bugreport push到电脑的某个位置
        os.system(f'adb root')
        os.system(f'adb remount')
        os.system(f'adb shell bugreportz')
        os.system(f'adb pull /data/user_de/0/com.android.shell/files/bugreports C:\\Users\\15297\\Desktop\\bugreport')
        os.system(f'adb shell rm -r /data/user_de/0/com.android.shell/files/bugreports/*')

        # 获取SYNC.pcap的log
        os.system(f'tcpdump -i eth0 -w /data/sync.pcap')
        os.system(f'adb pull /data/sync.pcap C:\\Users\\15297\\Desktop\\bugreport')
        os.system(f'adb shell rm -r /data/sync.pcap')



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


# main
if __name__ == "__main__":
    app = CanoeSync()
    screen_checker = ScreenChecker()
    app.Load('CANoeConfig\CX483_sendSIG.cfg')
    for _ in range(10):
        app.Run()
        app.Stop()
        time.sleep(60)







