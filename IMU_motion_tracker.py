#Anthony Nasr
#2024-04-06
#v1

#imports
import os 
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from scipy.signal import savgol_filter
import copy
#not needed...
from scipy.signal import filtfilt, butter


file_out = open('./position_log.txt', 'w')

class data_container():
    '''
    This section of the code deals with parsing the data generated by ./json_decoder.py
    raw JSON -> [./json_decoder.py] -> csv
    '''
    def __init__(self):
        self.file_name = './IMU_data.csv' #Change this to target file name. 
        self.list_acc_data = []
        self.list_g_data = []
        self.list_m_data = []
        self.acc_x = [] #acc data just in x
        self.acc_y = [] #acc data just in y
        self.acc_z = [] #acc data just in z
        self.acc_post_fitler_x = [] #acc data just in x
        self.acc_post_fitler_y = [] #acc data just in y
        self.acc_post_fitler_z = [] #acc data just in z
        self.IMU = None #initialy None
        self.read_content()

    #getters:
    def get_acc_data(self) -> list[float]:
        return self.list_acc_data
    
    def get_g_data(self) -> list[float]:
        return self.list_g_data

    def get_m_data(self) -> list[float]:
        return self.list_m_data  
    
    def get_IMU(self): 
        #returns a copy of IMU object. 
        return self.IMU
    
    def get_acc_x_pre_fitler(self):
        return self.acc_x
    def get_acc_y_pre_fitler(self):
        return self.acc_y
    def get_acc_z_pre_fitler(self):
        return self.acc_z
    
    def get_acc_x_post_fitler(self):
        return self.acc_post_fitler_x
    def get_acc_y_post_fitler(self):
        return self.acc_post_fitler_y
    def get_acc_z_post_fitler(self):
        return self.acc_post_fitler_z

    def fitler_jerk(self, data):
        tolerance = 0 #counts number of 0's between sign changes. 
        potential_jerk_flag = False
        temp_data = copy.deepcopy(data)
        for i in range(len(data)):
            #print(data[i], "tolerance: "+str(tolerance))
            if( 10 >= tolerance >= 5):
                if(i+1 <len(data)-1 and data[i+1]!=float(0)):
                    #jerk is detected. 
                    for j in range(i,i+25):
                        temp_data[j] = float(0) #flatten the jerk window (approx 30 packets ahead of the )
                        potential_jerk_flag = False #reset
                    tolerance = 0 #reset
                    #print("HERE", str(tolerance))
            if(tolerance > 11):
                potential_jerk_flag = False
                tolerance = 0
            if potential_jerk_flag and data[i] == float(0):
                tolerance +=1
            if(i+1 < len(data) and data[i]!=float(0) and data[i+1]==float(0)): #encountered a crossing from + -> - or - -> +
                potential_jerk_flag = True #set warning for probable jerk and begin to count 0. 
        return temp_data
    
    def read_content(self):
        with open(self.file_name, 'r') as target_file: #read perms
            content = target_file.readlines()
        for i in range(1, len(content)): #iterate over all data lines. 
            '''
            title structure:
            #Packet number,Gyroscope X (deg/s),Gyroscope Y (deg/s),Gyroscope Z (deg/s),
            #Accelerometer X (g),Accelerometer Y (g),Accelerometer Z (g),Magnetometer X (G),Magnetometer Y (G),Magnetometer Z (G)
            ''' 
            data_line = content[i]
            split_data = data_line.strip().split(',')
            
            #X Y Z gyroscope data
            temp_g_x = float(split_data[1]) #index 1 holds gyro x data. 
            temp_g_y = float(split_data[2]) #index 2 holds gyro y data. 
            temp_g_z = float(split_data[3]) #index 3 holds gyro z data. 
            
            #append to gyroscope data list.
            self.list_g_data.append((temp_g_x, temp_g_y, temp_g_z)) #one tuple of all three instances. 1 tuple = 1 packet. 

            #X Y Z accelerometer data
            temp_acc_x = float(split_data[4]) #index 4 holds acc x data. 
            temp_acc_y = float(split_data[5]) #index 5 holds acc y data. 
            temp_acc_z = float(split_data[6]) #index 6 holds acc z data. 

            #append to accelerometer data list.
            self.acc_x.append(temp_acc_x)
            self.acc_y.append(temp_acc_y)
            self.acc_z.append(temp_acc_z)

            #X Y Z magnometer data
            temp_m_x = float(split_data[7]) #index 4 holds mag x data. 
            temp_m_y = float(split_data[8]) #index 5 holds mag y data. 
            temp_m_z = float(split_data[9]) #index 6 holds mag z data. 

            #append to magnometer data list.
            self.list_m_data.append((temp_m_x, temp_m_y, temp_m_z))

        #print confirmation of completion. 
        print(f"Filtering jerk data from {self.file_name}.")
        self.acc_post_fitler_z = self.fitler_jerk(self.acc_z)
        self.acc_post_fitler_x = self.fitler_jerk(self.acc_x)
        self.acc_post_fitler_y = self.fitler_jerk(self.acc_y)
        for i in range(len(self.acc_post_fitler_z)):
            self.list_acc_data.append((self.acc_post_fitler_x[i], self.acc_post_fitler_y[i], self.acc_post_fitler_z[i]))
        print(f"Data successfully extracted and filtered from {self.file_name}.") 


'''
Rough implementation of 1D kalman filter [X Y Z Acceleration ->(KF)-> X Y Z Displacement]
'''
class kalman_filter():

    def __init__(self, accelerometer_data):
        self.acc_data = accelerometer_data
        self.dt = 0.1  #Assuming a 0.01 second time step, adjust as needed
        #Initial state vector
        self.x = np.array([[0],  #Position along x
                      [0],  #Velocity along x
                      [0],  #Position along y
                      [0],  #Velocity along y
                      [0],  #Position along z
                      [0]]) #Velocity along z
        
        self.P = np.eye(6) #Initial covariance matrix
        #State transition matrix
        self.F = np.array([[1, self.dt, 0,  0,  0,  0],
                      [0,  1, 0,  0,  0,  0],
                      [0,  0, 1, self.dt,  0,  0],
                      [0,  0, 0,  1,  0,  0],
                      [0,  0, 0,  0,  1, self.dt],
                      [0,  0, 0,  0,  0,  1]])
        #Control input matrix
        self.B = np.array([[(self.dt**2)/2, 0,         0],
                      [self.dt,        0,         0],
                      [0,         (self.dt**2)/2, 0],
                      [0,         self.dt,        0],
                      [0,         0,         (self.dt**2)/2],
                      [0,         0,         self.dt]])
    
        #Process noise covariance matrix
        self.q = 0.1  #Adjust based on empirical tuning
        self.Q = self.q * np.array([[self.dt**4/4, self.dt**3/2, 0,       0,       0,       0],
                          [self.dt**3/2, self.dt**2,   0,       0,       0,       0],
                          [0,       0,       self.dt**4/4, self.dt**3/2, 0,       0],
                          [0,       0,       self.dt**3/2, self.dt**2,   0,       0],
                          [0,       0,       0,       0,       self.dt**4/4, self.dt**3/2],
                          [0,       0,       0,       0,       self.dt**3/2, self.dt**2]])

        #Corrected measurement matrix for acceleration measurements
        self.H = np.array([[0, 1, 0, 0, 0, 0],  #Measurement mapping for acceleration in X
                      [0, 0, 0, 1, 0, 0],  #Measurement mapping for acceleration in Y
                      [0, 0, 0, 0, 0, 1]]) #Measurement mapping for acceleration in Z

        #Measurement noise covariance matrix
        self.r = 0.1 #Adjust based on the known sensor noise
        self.R = self.r * np.eye(3)

        #Identity matrix
        self.I = np.eye(6)
    
    #Getters
    def get_data(self):
        return self.acc_data
    
    def get_dt(self):
        return self.dt
    
    def run_filter(self):
        positions = [] 
        for measurement in self.get_data():
            # Predict
            self.x = self.F @ self.x  # State prediction
            self.P = self.F @ self.P @ self.F.T + self.Q  # Covariance prediction
            # Update
            Z = np.array(measurement).reshape(3, 1)
            y = Z - (self.H @ self.x)  # Measurement residual
            S = self.H @ self.P @ self.H.T + self.R  # Residual covariance
            K = self.P @ self.H.T @ np.linalg.inv(S)  # Kalman gain
            self.x = self.x + (K @ y)  # State update
            self.P = (self.I - (K @ self.H)) @ self.P  # Covariance update

            # Store the position
            positions.append((self.x[0, 0], self.x[2, 0], self.x[4, 0]))
    
        return positions


'''
end of main content
'''

#--------------------------------------- Form correction algorithm -------------------------------------------------------
'''
This section of the code will take in the estimated positions from the kalman filter and attempt to recognize the number of reps. 
Furthermore, it will attempt to spot "bad" reps and determine the reason. 
'''
class arbitter():
    def __init__(self):
        self.rep_list = [] #will hold all rep objects. 
    
    def get_rep_list(self) -> None:
        return self.rep_list
    
    def clear_repList (self) -> None:
        self.rep_list = [] #empty list...
    
    def add_rep(self, rep) -> None: #add rep to rep list. 
        self.rep_list.append(rep)
    

class rep(): 
    def __init__(self, rep_ID):
        self.start_pos = (None, None, None)
        self.good_form = True #assumed to be true, unless other wise proven false. 
        self.rep_num = rep_ID #each rep is given an ID for graphing purposes later on in the application. (i.e rep 1 , rep 2, rep 3  , rep 4 etc...)
        #self.expected_max_height = self.update_max_height(data) #this needs to be compared to z coordinate everytime. If reached (within a margin), means that rep can be counted once original position is reached again.
        self.summited  = False #default is false, until proven true. y coordinate  = max height. 
        self.reason_for_failure = None #will be set as a string explanation of why it it labeled as "bad". 
        self.rep_position_data = [] 

    def get_expected_max_height(self) -> int:
        return self.expected_max_height

    def get_summited(self) -> bool:
        return self.summited

    def get_rep_num(self) -> int:
        return self.rep_num

    def get_form_flag(self) -> str:
        if(self.good_form):
            return ("good")
        else:
             return ("bad")
        
    def get_travel_data(self) -> list:
        return self.rep_position_data
    
    def set_start_pos(self, start_position) -> None:
        self.start_pos = start_position
    
    def set_rep_num(self, rep_ID) -> None:
        self.rep_num = rep_ID
    
    def set_summited(self) -> None:
        self.summited = True

    def set_reason(self, reason) -> None:
        self.reason_for_failure = reason

    def reset_good_form(self) -> None:
        self.good_form = False

    def update_position_list(self, tuple) -> None:
        self.rep_position_data.append(tuple)

    #def update_max_height(self, data) -> None:
    #    max_height = 0.0 #start at 0. Update as we iterate. 
    #    for i in range(len(data)): #go through given position data. 
    #        if(data[i] > max_height): #compare heights. 
    #            max_height = data[i] #replace temp_max_height with new highest. 
#
    #    self.expected_max_height = max_height #update max height variable. 




#defining classes:
class user(): #mock user to hold rep count and current exerice being 
    def __init__(self, data):
        self.reps = None #reps are None to begin with
        self.current_exerice = 'Shoulder press' #this algorithm will also be 
        self.speed = 2 #default speed is 2... user may change this in app. 
        self.start_pos = (0.0, 0.0, 0.0) #starting curl position is assumed to always be (0,0,0)
        self.latest_pos = (None, None, None) #compare the current position with the previous one
        self.original_y = self.start_pos[1] #starting y position should be maintained within certain margins. 
        self.original_x = self.start_pos[0] #starting x position should be maintained within certain margins.
        self.leeway_z = 0.30 #arbitrary. Can be edited based on person's dimensions. PERCENTAGE BASED NOW. START HIGH AND TUNE!
        self.leeway_x = 0.05 #lee way allowed in x axis.
        self.leeway_y = 0.05 #lee way allowed in y axis.
        self.current_rep = None #place holder for the current rep. 
        self.arbitter = arbitter() #creating the arbitter class within the 
        self.rep_counter =  0
        self.expected_max_height = self.update_max_height(data) #this needs to be compared to z coordinate everytime. If reached (within a margin), means that rep can be counted once original position is reached again.

        
    #getters    
    def get_arbitter(self) -> arbitter:
        return self.arbitter
    
    def get_reps(self) -> int:
        return self.reps
    
    def get_current_exerice(self) -> str:
        return self.current_exerice
    
    def get_speed(self) -> float:
        return self.speed

    def get_max_height(self) -> float:
        return self.expected_max_height
    
    #setters:
    def set_reps(self, new_reps) -> None:
        #set new reps
        self.reps = new_reps

    def set_current_exerice(self, new_exerice) -> None:
        #set new exercise
        self.current_exerice = new_exerice

    def set_speed(self, new_speed) -> None:
        #set speed
        self.speed = new_speed

    #misc:
    def inc_reps(self) -> None:
        #inc reps
        self.reps += 1

    def compare_speed(self, current_rep_speed) -> bool:
        #check if rep speed is greater than preset target speed. 
        #if returns True -> rep speed violation. 
        return self.speed < current_rep_speed

    #def rep_ceck(self, new_position_tuple) -> bool:
    
    def update_max_height(self, data) -> None:
        max_height = float(0) #start at 0. Update as we iterate. 
        for i in range(len(data)): #go through given position data. 
            current_z = float(data[i][2])
            if(current_z > max_height): #compare heights. 
                max_height = data[i][2] #replace temp_max_height with new highest. 

        return max_height #update max height variable
    
    #method will check for displacements in x, y, and z. It will then update the newest position to the latest position. 
    def update_current_position(self, new_position_tuple) -> None:
        #(x, y, z)...
        if(self.current_rep != None):
            self.current_rep.update_position_list(new_position_tuple)
        #each rep may have a slightly different starting point, account for that in lee way. Once coordinates are back within a certain margin of the 
        #starting position, the rep is complete and we can register the next position as the starting position of the next rep.
        #the first position sent after being still or more than X seconds, (chose an x) will be considered the starting position of the 1st rep. 
        #if(new_position_tuple == self.start_pos): #check if we are at the bottom of rep. NEED to add adequate leeway.
        if(self.start_pos[2] - 0.10 <= new_position_tuple[2] <= self.start_pos[2] + 0.10): #allow 5% height above original position, but 25% down under, allows for shoulder dip and fatigue in posture. 
            if(self.current_rep == None):
                #create a new rep object.
                self.rep_counter += 1
                temp_rep = rep(self.rep_counter)
                temp_rep.update_position_list(new_position_tuple) #position is added to the rep travel path. 
                #update the place holder.  
                self.current_rep = temp_rep

            elif(self.current_rep.get_summited()):
                #rep is complete. Summit acheived and return to Original position is acheived. 
                self.arbitter.add_rep(self.current_rep) #add rep to arbitter. 
                self.current_rep = None #reset... 

        if(not(-0.05 < new_position_tuple[0] < 0.05)): #checking if x position is wihtin tolerated bounds. 
            if(self.current_rep != None):
                reason = "Error in form detected : x out_of_bounds" + " original x "+str(self.original_x) + " new x "+str(new_position_tuple[0])
                print(reason)
                #set bad form flag in rep object. 
                self.current_rep.reset_good_form()

        if(not(-0.05 < new_position_tuple[1] < 0.05)): #checking if x position is wihtin tolerated bounds. 
            if(self.current_rep != None):
                reason = "Error in form detected : y out_of_bounds" + " original y "+str(self.original_y) + " new x "+str(new_position_tuple[1])
                print(reason)
                #set bad form flag in rep object. 
                self.current_rep.reset_good_form()

        #if(self.current_rep != None and new_position_tuple[3] == self.current_rep.get_expected_max_height()):
        if(self.current_rep != None and (self.get_max_height()*(1-self.leeway_z) <= new_position_tuple[2] <= self.get_max_height())):
            #print("hi", self.get_max_height())
            self.current_rep.set_summited() #highest point is achieved. 

#----------------------------------------End of form correction section---------------------------------------------------





#--------------------------------------------------------Graphing-------------------------------------------------
'''
This section of the code purely deals with the graphing of the probabilistic data generated by the KF entity.
'''
def graph_data():
    out = []
    #create data_container instance
    data_arbiter = data_container()
    #create kalman filter instance:
    KF = kalman_filter(data_arbiter.get_acc_data())
    #run the Kalman filter. 
    estimated_positions = KF.run_filter()

    test_user = user(estimated_positions)
    print("Max height detected: "+ str(test_user.get_max_height()))
    #dump data into log
    file_out.write("--------Full position data log-----------\n")
    for tuple in estimated_positions:
        #print(tuple)
        file_out.write(str(tuple)+'\n')
        #flip z in correct orientation. 

        test_user.update_current_position((tuple[0], tuple[1], -1*tuple[2]))

    #dump each rep travel path into log
    file_out.write("--------Specific Rep travel data-----------\n")
    for rep in test_user.get_arbitter().get_rep_list():
        for data in rep.get_travel_data():
            file_out.write(f"Rep #{rep.get_rep_num()}: {str(data)}\n")
        print(f"Rep #: {str(rep.get_rep_num())} was completed with {rep.get_form_flag()} form." )    

    # Unpack the positions into separate lists
    #x_coords, y_coords, z_coords = zip(*estimated_positions)
    x_coords, y_coords, z_coords = zip(*[(x, y, -z) for x, y, z in estimated_positions]) # z is multplied by -1 because directions are inverted. 
    
    # Unpack the accelerometer data into separate lists for x, y, and z
    x_acc, y_acc, z_acc = zip(*data_arbiter.get_acc_data())
    
    t = np.arange(len(x_acc)) * KF.get_dt()  #time axis for acceleration plots. 
    # Create a new figure for 3D plotting
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    #Plot the points
    ax.scatter(x_coords, y_coords, z_coords, c='r', marker='o')
    
    #Plot the lines connecting points
    ax.plot(x_coords, y_coords, z_coords, label='Estimated travel path')
    
    #Labels and title
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_zlabel('Z Position')
    ax.set_title('Estimated Position Over Time')
    
    #Show the first point in orange
    ax.scatter(x_coords[0], y_coords[0], z_coords[0], c='orange', marker='o', s=100, label='Start')
    
    #Show the last point in green
    ax.scatter(x_coords[-1], y_coords[-1], z_coords[-1], c='green', marker='o', s=100, label='End')
    
    #Showcase legend
    ax.legend()
    out.append(ax)
    plt.show()
    
    #Plot Z position over time. 
    plt.figure(figsize=(10, 3))
    plt.plot(t, z_coords, label='Z position over time', color='purple')
    # Scatter plot to show each point
    plt.scatter(t, z_coords, color='orange')  # Choose a color that stands out
    plt.title('Z position over time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('m')
    plt.legend()
    plt.grid(True)
    plt.show()
    out.append(plt)
    #Acceleration in X
    plt.figure(figsize=(10, 3))
    plt.plot(t, x_acc, label='X-Axis Acceleration', color='red')
    plt.title('Acceleration in X')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Acceleration (m/s^2)')
    plt.legend()
    plt.grid(True)
    plt.show()
    out.append(plt)
    #Acceleration in Y
    plt.figure(figsize=(10, 3))
    plt.plot(t, y_acc, label='Y-Axis Acceleration', color='green')
    plt.title('Acceleration in Y')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Acceleration (m/s^2)')
    plt.legend()
    plt.grid(True)
    plt.show()
    out.append(plt)
    
    #Acceleration in Z
    plt.figure(figsize=(10, 3))
    plt.plot(t, data_arbiter.get_acc_z_pre_fitler(), label='Z-Axis Acceleration', color='blue')
    plt.title('Acceleration in Z pre-jerk removal')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Acceleration (m/s^2)')
    plt.legend()
    plt.grid(True)
    plt.show()
    out.append(plt)
    #acceleration in Z post fitler
    plt.figure(figsize=(10, 3))
    plt.plot(t, data_arbiter.get_acc_z_post_fitler(), label='Z-Axis Acceleration', color='green')
    plt.title('Z-Axis Acceleration after removing Jerk')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Acceleration (m/s^2)')
    plt.legend()
    plt.grid(True)
    plt.show()
    out.append(plt)
    return out
    #--------------------------------------------------End of Graphing-------------------------------------------------


