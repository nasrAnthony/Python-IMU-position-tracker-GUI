Basic Kalman Filter implementation in Python. 


The goal is to estimate the position over time using X, Y, Z accelerometer data. 

Run the json_encoder_v2.py to get data via socket/port. This will genereate a csv
before running the IMU_motion_tracker.py. 

IMU_data.csv already contains data, so IMU_motion_tracker.py can be ran right away to test. 

Results of 4 straight up and down movements will be shown. 

Overview of general logic flow:
![image](https://github.com/nasrAnthony/IMU-position-tracker/assets/132410219/a91fec59-d740-4b6c-ac98-997633042d2e)
