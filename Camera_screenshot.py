import cv2
import time
import numpy as np

# 初始化摄像头
cap = cv2.VideoCapture(1)  # 0 表示第一个摄像头，如果有多个摄像头可以尝试不同的编号
print('初始化摄像头成功')

# 初始化前一帧图像
prev_frame = None
print('初始化前一帧图像成功')

while True:
    ret, frame = cap.read()  # 读取摄像头图像
    print('读取摄像头图像成功')

    if ret:
        # 提取指定像素区域
        region1 = frame[155:245, 345:445]  # 提取区域1
        if prev_frame is not None:
            region2 = prev_frame[155:245, 345:445]  # 提取区域2

            # 比较两个区域的相似度
            res = cv2.matchTemplate(region1, region2, cv2.TM_CCOEFF_NORMED)
            similarity = np.max(res)
            if similarity > 0.9:
                print('指定像素区域相似度大于90%')
            else:
                print('指定像素区域相似度小于90%')

        prev_frame = frame  # 更新前一帧图像
        time.sleep(0.5)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # 按下 'q' 键退出循环
        break

# 释放摄像头并关闭窗口
cap.release()
cv2.destroyAllWindows()
