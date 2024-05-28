import socket
import numpy as np

def json_to_file():
    accelerometer_data_x = [] 
    accelerometer_data_y = [] 
    accelerometer_data_z = []

    JSON_file = open('out_JSON.txt', 'r')

    #csv_out_file = open('treated_data.csv', 'w')
    script_data_file = open('./IMU_data.csv', 'w')

    JSON_content = JSON_file.read().split('}') #split all packets. 

    script_data_file.write("Packet,Gyroscope X (deg/s),Gyroscope Y (deg/s),Gyroscope Z (deg/s),Accelerometer X (g),Accelerometer Y (g),Accelerometer Z (g),Magnetometer X (G),Magnetometer Y (G),Magnetometer Z (G)\n")
    #print(JSON_content)

    #print(packet for packet in JSON_content)
    packet_counter = 0
    #need to insert 2000 fake packets to give room for calibration later. 
    #for i in range(2000):
    #    script_data_file.write(str(packet_counter)+","+str(0)+","+str(0)+","+str(0)+","+str(0)+","+str(0)+","+str(0)+","+str(0)+","+str(0)+","+str(0)+"\n")
    #    packet_counter +=1


    for packet in JSON_content:
        #get accelerometer data. 
        #print(packet.split("accelX")[1].split(',')[0].split(':')[1]
        if(packet !=""):
            acc_X = float(packet.split("accelX")[1].split(',')[0].split(':')[1])
            acc_Y = float(packet.split("accelY")[1].split(',')[0].split(':')[1])
            acc_Z = float(packet.split("accelZ")[1].split(',')[0].split(':')[1]) + 0.999 #correct for gravity

            #get gyroscope data. 
            g_X = float(packet.split("gyroX")[1].split(',')[0].split(':')[1])
            g_Y = float(packet.split("gyroY")[1].split(',')[0].split(':')[1])
            g_Z = float(packet.split("gyroZ")[1].split(',')[0].split(':')[1])

            accelerometer_data_x.append(acc_X)
            accelerometer_data_y.append(acc_Y)
            accelerometer_data_z.append(acc_Z)
            #idx = 0
            #while idx < 9:
            #        csv_out_file.write(str(packet_counter)+","+str(g_X)+","+str(g_Y)+","+str(g_Z)+","+str(acc_X)+","+str(acc_Y)+","+str(acc_Z)+","+str(0)+","+str(0)+","+str(0)+"\n")
            #        idx +=1
            #        packet_counter += 1
            #account for stationary noise. 

            noise_margin = 0.5
            if( -noise_margin < acc_X < noise_margin):
                acc_X = float(0)
                #pass
            if( -noise_margin < acc_Y < noise_margin):
                acc_Y = float(0)
                #pass
            if(-0.1 < acc_Z < 0.1): 
                acc_Z = float(0)
            

            script_data_file.write(str(packet_counter)+","+str(g_X)+","+str(g_Y)+","+str(g_Z)+","+str(acc_X)+","+str(acc_Y)+","+str(acc_Z)+","+str(0)+","+str(0)+","+str(0)+"\n")
            packet_counter += 1

    JSON_file.close()

def listen_json(IP, port_number):
    # Set the IP address and port number (use the same port number that you'll configure in your iPhone app)
    UDP_IP = str(IP)
    UDP_PORT = port_number

    #create a file to forward data into:
    out_file = open('out_JSON.txt', 'w')

    # Create a socket for UDP
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP

    # Bind the socket to the IP and port
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(20)

    print(f"Listening on UDP {UDP_IP}:{UDP_PORT}...")

    while True:
        try:
            # Wait for a packet
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            #write data into file. 
            out_file.write(data.decode())

        except socket.timeout as e:
            sock.close()
            out_file.close()
            print("----------20 seconds elapsed, socket closed.----------")
            print("See the following files")
            print("./out_JSON.txt")
            print("./IMU_data.csv")
            json_to_file()
            break
