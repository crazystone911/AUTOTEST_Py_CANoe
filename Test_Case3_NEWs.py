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
            ignition_status = self.get_Ignition_Status()
            if ignition_status == 4:
                time.sleep(20)
                # 先获取ADB权限
                subprocess.run(f'adb devices', shell=True)
                subprocess.run(f'adb root', shell=True)
                # 创建两个线程并行执行 adb shell bugreportz和sync.pcap
                # _thread.start_new_thread(os.system, ('adb shell bugreportz',))
                # _thread.start_new_thread(os.system, (f'adb shell tcpdump -i eth0 -w /data/sync.pcap',))
                # 延时后点击
                self.click1()
                time.sleep(5)
                self.click2()
                time.sleep(5)
                self.click3()
                time.sleep(5)
                self.click_play()
                print("开始执行歌曲播放循环")
                for i in range(30):  # 执行30个循环
                    self.click_nextsong()  # 点击播放下一首歌曲
                    self.preview_timetamp = time.time()
                    screen_checker.judge_screen()
                    time.sleep(20)  # 等待20秒
                self.Stop()

                # self.preview_timetamp = time.time()
                # # 循环去检测屏幕point点是否发生变化
                # screen_checker.judge_screen()
                # print("Ignition Status is run, SYNC initial completely, Waiting for 600 seconds...")
                # time.sleep(600)
                break
        #     DoEvents()
        # self.Stop()

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
        subprocess.run(f"adb shell input tap {1130} {480}", shell=True)

    def click2(self):
        subprocess.run(f"adb shell input tap {81} {397}", shell=True)

    def click3(self):
        subprocess.run(f"adb shell input tap {1535} {124}", shell=True)

    def click_play(self):
        subprocess.run(f"adb shell input tap {484} {640}", shell=True)

    def click_nextsong(self):
        subprocess.run(f"adb shell input tap {660} {640}", shell=True)


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
    # def judge_screen(self):
    #     for i in range(30):
    #         file_name = f"screenshot_{i}.png"
    #         self.take_screenshot(file_name)
    #         self.pull_screenshot(file_name)
    #         self.delete_screenshot(file_name)
    #
    #         if self.previous_image is not None:
    #             if not self.check_region_similarity(f"{self.local_path}/{self.previous_image}", f"{self.local_path}/{file_name}", 247, 466, 100, 100):
    #                 current_timestamp = time.time()
    #                 time_interval = current_timestamp - self.previous_timestamp
    #                 print(f'像素发生变化，歌曲加载完成！时间间隔：{time_interval} 秒,当前时间为{current_timestamp}')
    #                 if time_interval > 10:
    #                     self.bugreport()
    #                     break
    #         self.previous_image = file_name
    def judge_screen(self):
        prev_frame = None
        delta_timestamp = 0

        while True:
            ret, frame = cap.read()  # 读取摄像头图像
            if ret:
                # 提取指定像素区域，使用切片操作从图像帧中提取行索引300到430（垂直方向）和列索引600到760（水平方向）之间的区域
                region1 = frame[300:430, 600:760]  # 提取区域1
                if prev_frame is not None:
                    region2 = prev_frame[300:430, 600:760]  # 提取区域2

                    # 比较两个区域的相似度
                    res = cv2.matchTemplate(region1, region2, cv2.TM_CCOEFF_NORMED)
                    similarity = np.max(res)

                    if similarity > 0.9 and time.time() - app.preview_timetamp  > 10:
                        delta_timestamp = time.time() - app.preview_timetamp
                        print(f'Exiting loop due to similarity > 0.9 and elapsed time > 10 seconds，current time{time.time()}')
                        self.bugreport()
                        break

                    if similarity > 0.9:
                        print("Similarity greater than 0.9")

                prev_frame = frame  # 更新前一帧图像
                time.sleep(0.1)

            if delta_timestamp > 10:  # 如果加载时间大于5秒退出循环
                self.bugreport()
                break
        # 确保在while循环结束后返回一个结果，例如这里可以返回delta_timestamp的值或其他表示屏幕变化的指标
        return delta_timestamp

    def bugreport(self):
        # 将bugreport push到电脑的某个位置
        os.system(f'adb remount')
        os.system(f'adb pull /data/user_de/0/com.android.shell/files/bugreports C:\\Users\\15297\\Desktop\\bugreport')

        # 获取SYNC.pcap的log
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

    def OnStart(self,st):
        self.started = True
        self.stopped = False
        self.Name = st.Name
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
    cap = cv2.VideoCapture(1)
    for _ in range(10):
        app.Run()
        app.Stop()
        time.sleep(60)
        os.system(f'adb shell rm -r /data/user_de/0/com.android.shell/files/bugreports/*')







