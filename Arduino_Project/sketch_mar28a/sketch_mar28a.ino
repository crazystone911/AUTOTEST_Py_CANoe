void setup() {
  Serial.begin(115200); // 初始化串口通信
}

void loop() {
  int sensorValue = analogRead(A1); // 读取 A1 脚的电压值
  float voltage = sensorValue * (5.0 / 1023.0); // 将电压值转换为实际电压
  
  Serial.print("Voltage on A1: ");
  Serial.print(voltage, 2); // 保留两位小数
  Serial.println(" V");
  
  delay(100); // 延迟一秒钟
}
