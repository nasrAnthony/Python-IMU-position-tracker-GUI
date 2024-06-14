Basic Kalman Filter implementation in Python. 


The goal is to estimate the position over time using X, Y, Z accelerometer data. 

Run the json_encoder_v2.py to get data via socket/port. This will genereate a csv
before running the IMU_motion_tracker.py. 

IMU_data.csv already contains data, so IMU_motion_tracker.py can be ran right away to test. 

Results of 4 straight up and down movements will be shown. 

Overview of general logic flow:
![image](https://github.com/nasrAnthony/IMU-position-tracker/assets/132410219/a91fec59-d740-4b6c-ac98-997633042d2e)


GUI output after data collection:
![image](https://github.com/nasrAnthony/Python-IMU-position-tracker-GUI/assets/132410219/9cf88981-b067-4979-be2a-3adca5b435a9)

Other Graphs can be seen by clicking on next graph button:
![image](https://github.com/nasrAnthony/Python-IMU-position-tracker-GUI/assets/132410219/50a1feae-342b-4d70-aa2c-ce026b10f208)
![image](https://github.com/nasrAnthony/Python-IMU-position-tracker-GUI/assets/132410219/f5ed3264-3ef1-42aa-ac16-fc0d25a27c60)

