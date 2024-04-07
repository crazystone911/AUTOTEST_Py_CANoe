import threading
import time
import serial.tools.list_ports

# 获取当前可用的串口列表
port_list = list(serial.tools.list_ports.comports())

# 打印可用串口列表
for port in port_list:
    print(port)

# 打开串口
ser = serial.Serial('com4', 115200)


# 异步读取数据的线程函数
def read_serial():
    while True:
        # 从串口读取数据
        voltage = float(ser.readline().decode().strip())
        # 打印电压值
        print("Voltage: ", voltage)


# 创建并运行线程
thread = threading.Thread(target=read_serial)

thread.start()

try:
    # 主线程中异步写入数据
    while True:
        ser.write(b'Async Write Operation')
        time.sleep(1)
except KeyboardInterrupt:
    print("Serial Communication Stopped.")

finally:
    # 等待读取线程结束后再关闭串口
    thread.join()
    if ser.is_open:
        ser.close()
