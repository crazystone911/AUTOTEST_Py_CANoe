import serial.tools.list_ports
import serial

# 获取当前可用的串口列表
port_list = list(serial.tools.list_ports.comports())

# 打印可用串口列表
for port in port_list:
    print(port)

# 打开串口
ser = serial.Serial('com4', 115200)

while True:
    # 从串口读取数据
    voltage = float(ser.readline().decode().strip())

    # 打印电压值
    print("Voltage: ", voltage)

# 关闭串口
# ser.close()

