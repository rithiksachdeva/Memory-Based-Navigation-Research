import cv2
import time
import socket
from goprocam import GoProCamera, constants
import sys
import serial
import pynmea2
from serial.tools import list_ports
import threading
import h5py
import numpy as np

portname = ""
MAX_IMAGE = 10
SHOW = False
Latitude = 0.0
Longitude = 0.0
Date = time.time()
Timestamp = time.time()

def webcam(portname):
        global Latitude
        global Longitude
        global portname
        global MAX_IMAGE
        FPS = 12
        RES = '1080p'
        WRITE = True

        f = h5py.File(str(time.time())+".hdf5", 'w')

        picTime = time.time()
        t=time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_addr=GoProCamera.GoPro.getWebcamIP(portname)
        gpCam = GoProCamera.GoPro(ip_address=ip_addr, camera=constants.gpcontrol, webcam_device=sys.argv[1])
        gpCam.webcamFOV(constants.Webcam.FOV.Linear)
        gpCam.video_settings(res=RES, fps=str(FPS))
        gpCam.gpControlSet(constants.Stream.WINDOW_SIZE, constants.Stream.WindowSize.R720)
        gpCam.livestream("start")
        cap = cv2.VideoCapture("udp://"+ip_addr+":8554", cv2.CAP_FFMPEG)
        counter = 0
        while True:
            nmat, frame = cap.read()
            if SHOW == True:
                cv2.imshow("GoPro OpenCV", frame)
            if WRITE == True and time.time() - picTime >= 1:
                #cv2.imwrite(str(time.time())+"-"+str(counter)+".jpg", frame)
                picTime = time.time()
                #print("https://www.google.com/maps/@?api=1&map_action=pano&viewpoint="+str(Latitude)+"%2C"+str(Longitude))
                grp = f.create_group(str(time.time()));
                dset = grp.create_dataset('Camera', data=frame)
                dset.attrs["Latitude"] = Latitude
                dset.attrs["Longitude"] = Longitude

                if counter > int(MAX_IMAGE):
                    break
                counter += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if time.time() - t >= 2.5:
                sock.sendto("_GPHD_:0:0:2:0.000000\n".encode(), (ip_addr, 8554))
                t=time.time()
        f.close()
        # When everything is done, release the capture
        cap.release()
        cv2.destroyAllWindows()
        print("webcam done")

def readGPS():
        global Latitude
        global Longitude
        global Heading
        global Date
        global Timestamp
        BAUDRATE=115200
        port = list(list_ports.comports())
        for p in port:
            print(p.device)
        text = input("Serial Port: ")

        # configure the serial connections (the parameters differs on the device you are connecting to)
        ser = serial.Serial(
            port=text,
            baudrate=BAUDRATE,
            timeout=5,
        )

        ser.isOpen()
        # Reading the data from the serial port. This will be running in an infinite loop.

        while 1:
            try:
                data = ser.readline()
                if data[0] == 36:
                    str_data = data.decode()
                    nmea_data = pynmea2.parse(str_data)
                    if isinstance(nmea_data, pynmea2.types.talker.RMC):
                        #print(nmea_data)
                        Latitude = pynmea2.dm_to_sd(nmea_data.lat)
                        Longitude = -(pynmea2.dm_to_sd(nmea_data.lon))
                        Date = nmea_data.datestamp
                        #print("https://www.google.com/maps/@?api=1&map_action=pano&viewpoint="+str(Latitude)+"%2C"+str(Longitude))
                    elif isinstance(nmea_data, pynmea2.types.talker.GGA):
                        #print(nmea_data)
                        Latitude = pynmea2.dm_to_sd(nmea_data.lat)
                        Longitude = -(pynmea2.dm_to_sd(nmea_data.lon))
                        Timestamp = nmea_data.timestamp
                        #print("https://www.google.com/maps/@?api=1&map_action=pano&viewpoint="+str(Latitude)+"%2C"+str(Longitude))
                    elif isinstance(nmea_data, pynmea2.types.talker.HDT):
                        #print(nmea_data)
                        Heading = (nmea_data.split(','))[2]
                    else:
                        splitline = str_data.split(',')
                        #print(splitline[0])
                #time.sleep(1)
            except serial.SerialException as e:
                print('Device error: {}'.format(e))
                break
            except pynmea2.ParseError as e:
                print('Parse error: {}'.format(e))
                continue
        ser.close()

if __name__ == "__main__":
        if len(sys.argv) > 2:
                MAX_IMAGE = sys.argv[2]
        portname = sys.argv[1]
        threadGPS = threading.Thread(target = readGPS, args = ())
        threadGPS.start()
        threadWebcam = threading.Thread(target = webcam, args = ())
        threadWebcam.start()
        threadGPS.join()
        threadWebcam.join()
        print("thread finished...exiting")
