void setup() {
  Serial.begin(115200); // Initialize serial communication with baud rate 115200
  pinMode(A1, INPUT); // Set pin A1 as input
}

void loop() {
  const int numReadings = 10; // Number of readings to store for median filter
  int readings[numReadings]; // Array to store readings
  int index = 0; // Index for circular buffer
  int total = 0; // Variable to store sum of readings
  int voltage; // Variable to store raw voltage reading
  float volt; // Variable to store actual voltage

  // Read voltages and apply median filter
  for (int i = 0; i < numReadings; i++) {
    voltage = analogRead(A1); // Read analog value from pin A1
    readings[index] = voltage; // Store reading in array
    index = (index + 1) % numReadings; // Update circular buffer index

    // Calculate median value
    total = 0;
    for (int j = 0; j < numReadings; j++) {
      total += readings[j];
    }
    volt = total / numReadings * (5.0 / 1024.0); // Calculate average voltage

    Serial.println(volt); // Print the filtered voltage
    delay(100); // Delay for 100 milliseconds
  }
}
