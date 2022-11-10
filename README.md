# Memory-Based-Navigation-Research

# GoPro Research
The GoPro and Serial GPS integration algorithm takes in as many GoPros as can be feasibly connected to the computer via USB, and then also connects a GPS that transmits NMEA data via USB and integrates the two so the research team can collect 120 degree panoramic views using openCV2 and tag them with their GPS coordinates as part of data acquisition. 

The HDF5 reader opens the HDF5 dataset created by the data acquisition. 

# MBN Steering Data Analysis
The algorithm takes in a HDF5 dataset which stores images and their associated steering data from a RC car and uses the values of how much a user uses the joystick to turn to understand where user decision points are. This uses elements of machine learning and signal processing to produce accurate landmarks/decision points. 
