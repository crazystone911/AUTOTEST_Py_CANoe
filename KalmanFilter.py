# 手搓卡尔曼滤波 from 华侨大学EDR战队
import numpy as np

class EDR_KalmanFilter:
    def __init__(self):
        self.A = np.matrix([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)  # 状态转移矩阵
        self.statePost = np.matrix(np.zeros((4,1),np.float32))  # 状态估计值
        self.statePre = np.matrix(np.zeros((4,1),np.float32))  # 状态预测值
        self.Q = np.matrix(np.eye(4))  # 过程噪声矩阵
        self.errorCovPost = np.matrix(np.zeros((4, 4),np.float32))  # 协方差矩阵的估计值
        self.errorCovPre = np.matrix(np.zeros((4, 4), np.float32))  # 协方差矩阵的预测值
        self.H = np.matrix(np.zeros((4, 2), np.float32))  # 卡尔曼滤波增益矩阵
        self.C = np.matrix([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)  # 状态观测矩阵
        self.R = np.matrix(np.eye(2))  # 观测噪声矩阵

    def predict(self):  # 按照卡尔曼滤波的公式1、2计算
        self.statePre = self.A * self.statePost  # 卡尔曼滤波公式1
        self.errorCovPre = self.A * self.errorCovPost * self.A.T + self.Q  # 卡尔曼滤波公式2
        return self.statePre  # 返回卡尔曼滤波的预测值

    def correct(self,measurement):  # 按照卡尔曼滤波的公式3、4、5计算
        self.H = self.errorCovPre * self.C.T * np.linalg.inv(self.C * self.errorCovPre * self.C.T + self.R)  # 卡尔曼滤波公式3
        self.statePost = self.statePre + self.H*(measurement - self.C * self.statePre)  # 卡尔曼滤波公式4
        self.errorCovPost = self.errorCovPre - self.H * self.C * self.errorCovPre  # 卡尔曼滤波公式5
        return self.statePost  # 返回卡尔曼滤波的估计值

    def getNext(self, x, y):  # 滤波器的输入输出在此
        measured = np.matrix([[np.float32(x)], [np.float32(y)]])
        self.predict()
        corrected = self.correct(measured)
        x, y = int(corrected[0]), int(corrected[1])
        return x, y

# main
if __name__ == "__main__":
    KalmanFilter = self.statePre