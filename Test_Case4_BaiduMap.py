import random

# 随机生成江苏省境内的一个地址（示例数据，实际应用中需替换为真实数据）
jiangsu_addresses = [
    "南京市中山东路1号",
    "苏州市观前街100号",
    "南通市人民中路200号",
    "无锡市人民西路50号",
    "常州市广场北路88号",
    "南京市红十字医院",
    "南湖公园",
    "新疆学员餐厅",
    "南京市江宁地方税务局",
    "雨花台区铁心桥老年公寓",
    "南京海事局梅山海事处",
    "宝钢梅山化工",
    "银杏湖国际高尔夫俱乐部",
    "长荡湖国家湿地公园",
    "连山茶场",
    "金沙湾乡村俱乐部",
    "乾元观",
    "句容市行政服务中心食堂",

]

random_address = random.choice(jiangsu_addresses)

# 构建 ADB 命令发送地址给导航应用
adb_command = f'adb shell input text "{random_address}"'
adb_command_trigger_search = 'adb shell input keyevent KEYCODE_ENTER'

# 执行 ADB 命令
import subprocess
subprocess.run(adb_command, shell=True)
subprocess.run(adb_command_trigger_search, shell=True)

print(f"随机地址 '{random_address}' 已发送至 SYNC 导航应用作为目的地。")
