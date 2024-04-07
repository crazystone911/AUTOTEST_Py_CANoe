float processNoise = 0.01; // Process noise covariance
float measurementNoise = 1.0; // Measurement noise covariance
float kalmanGain = 0.0; // Kalman gain
float estimate = 0.0; // Initial estimate
float errorCovariance = 1.0; // Initial error covariance

void setup() {
  Serial.begin(115200); // Initialize serial communication with baud rate 115200
  pinMode(A1, INPUT); // Set pin A1 as input
}

void loop() {
  int voltage = analogRead(A1); // Read analog value from pin A1
  float volt = voltage * (5.0 / 1024.0); // Convert analog reading to voltage

  // Prediction phase
  float predictedEstimate = estimate;
  float predictedErrorCovariance = errorCovariance + processNoise;

  // Update phase
  kalmanGain = predictedErrorCovariance / (predictedErrorCovariance + measurementNoise);
  estimate = predictedEstimate + kalmanGain * (volt - predictedEstimate);
  errorCovariance = (1 - kalmanGain) * predictedErrorCovariance;

  Serial.println(estimate); // Print the filtered voltage estimate
  delay(100); // Delay for 100 milliseconds
}
