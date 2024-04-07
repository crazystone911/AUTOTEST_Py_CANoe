import os

os.system(f'adb root')
os.system(f'adb remount')
# os.system(f'adb shell bugreportz')
os.system(f'adb pull /data/user_de/0/com.android.shell/files/bugreports C:\\Users\\15297\\Desktop\\bugreport')
os.system(f'adb shell rm -r /data/user_de/0/com.android.shell/files/bugreports/*')

# 获取SYNC.pcap的log
os.system(f'adb shell tcpdump -i eth0 -w /data/sync.pcap')
os.system(f'adb pull /data/sync.pcap C:\\Users\\15297\\Desktop\\bugreport')
os.system(f'adb shell rm -r /data/sync.pcap')