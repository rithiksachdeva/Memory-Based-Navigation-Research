# Memory-Based-Navigation-Research

## GoPro Stereoscopic Imaging
The GoPro and Serial GPS integration algorithm takes in as many GoPros as can be feasibly connected to the computer via USB, and then also connects a GPS that transmits NMEA data via USB and integrates the two so the research team can collect 120 degree panoramic views using openCV2 and tag them with their GPS coordinates as part of data acquisition. It's implemented using modules like `cv2`, `time`, `socket`, `sys`, `serial`, `pynmea2`, `threading`, `h5py`, and `numpy`. 

Here's a high-level summary of the script:

1. **GPS Data Reading:** The script can connect to a GPS device via a specified serial port and read GPS data from it, specifically, the latitude and longitude coordinates. The reading process is implemented in the function `readGPS()`. Any encountered errors during the data reading or parsing process will be handled and printed out.

2. **Video Capture:** The script is capable of setting up a GoPro camera for video capturing in the function `webcam()`. The GoPro camera is set to stream the video over UDP to the script. During the video capturing, every frame captured from the camera is checked, and if the condition meets (when `WRITE` is `True` and the time gap from the last capture is larger than or equal to 1 second), the frame is stored into an HDF5 file. The storing process also includes recording the current latitude and longitude into the attributes of the frame's dataset in the HDF5 file.

3. **Multithreading:** The script utilizes Python's threading module to simultaneously perform GPS data reading and video capturing. The main function runs two threads, one for each of the aforementioned operations. After both threads finish their tasks, the program prints a message indicating their completion and then exits.

4. **Customizable Parameters:** The number of frames to be captured from the video (`MAX_IMAGE`) and the port name for the GoPro camera (`portname`) can be passed as command-line arguments when running the script.

In essence, this script is an application for synchronously capturing video from a GoPro camera and reading GPS data from a GPS device, saving each video frame along with the corresponding geographic coordinates in an HDF5 file.

## GoPro Research

This script is intended to read an HDF5 (Hierarchical Data Format version 5) file, which is commonly used for storing large amounts of data, and extract specific information from it, specifically, image data. This script uses modules such as `cv2`, `numpy`, `h5py`, and `time`.

Here's a high-level summary of the script:

1. **HDF5 File Reading:** The script opens an HDF5 file with a specified filename in read mode using the `h5py.File` function. In this case, the filename is '1658622612.6630862.hdf5'. 

2. **Data Extraction:** Once the file is opened, the script prints all root-level object names (keys), which can either be group names or dataset names. For each group key in the file, the script retrieves the group object and prints its type to verify it.

3. **Attribute Reading and Image Data Retrieval:** The script then accesses a dataset named 'Camera' within each group and prints all of its attributes. These attributes often carry metadata related to the dataset. The script reads the entire dataset into a NumPy array using the `[:]` operator.

4. **Image Writing:** After the image data is loaded into a NumPy array, the script writes the image data into a JPEG file with a filename derived from the current timestamp. This is achieved by using the `cv2.imwrite` function.

In essence, this script is a tool for extracting image data and corresponding metadata from an HDF5 file and saving the image data as JPEG files. The script is particularly useful for dealing with large datasets of images stored in HDF5 format.

## MBN Steering Data Analysis
The algorithm takes in a HDF5 dataset which stores images and their associated steering data from a RC car and uses the values of how much a user uses the joystick to turn to understand where user decision points are. This uses elements of machine learning and signal processing to produce accurate landmarks/decision points. 

### Library Imports
This code uses several Python libraries, including numpy for numerical operations, math for basic mathematical functions, h5py to read and write HDF5 files (used for storing large datasets), PIL for manipulating images, os and shutil for filesystem operations, glob for pathname pattern expansion, and plotly for data visualization.

### Defining Auxiliary Functions
Two helper functions are defined: traverse_datasets, which recursively traverses HDF5 files and yields the path of all datasets inside, and percentage_diff, which calculates the percentage difference between two given numbers.

### Summarized Workflow
The script enters an interactive mode where it asks the user whether they want to process an individual HDF5 file or an entire folder of them. Depending on the user's choice, the script reads the appropriate HDF5 files. For each file, it creates a corresponding directory. Within each file, it identifies and saves image data, and extracts steering data, storing them in appropriate data structures.

### Landmark Identification
In this context, landmarks refer to significant or distinctive features in the steering data. The script finds landmarks based on certain conditions related to maximum, minimum, and surrounding values of the steering data. Depending on whether a folder or file is processed, a 'landmark window' size is set. This window is a range of data around each landmark that is to be considered in the analysis. The script also asks the user if they want to use default parameters or customize them. These parameters include the window size, the floor and ceiling of the steering data, the minimum distance between two landmarks, and the number of images to be considered in the 'negative' folders (those that don't contain landmarks). 

For each landmark identified, a region of consideration (ROC) is defined as a range of data points around the landmark, based on the window size. These ROCs are stored in a list and sorted. The script starts to analyze each Region of Consideration (ROC) around the identified landmarks. It calculates the rate of change of the steering data within each ROC and identifies where this rate of change is at a maximum, indicating a possible landmark. If necessary, it corrects the position of the landmark to ensure it aligns with the maximum rate of change. Warnings are printed when a landmark's accuracy is questionable, suggesting an increase in the window size.

The script checks if any of the identified landmarks are too close together (defined by the tooclose variable). If any two landmarks are found within this specified distance from each other, a warning is printed and both landmarks are removed from the landmark array. The script then plots a line graph of the steering data with vertical lines indicating the locations of the landmarks and the boundaries of their ROIs. For file processing, this figure is displayed to the user.

False positives, i.e., points identified as landmarks which are not truly significant, are detected and removed from the analysis. This is done by checking the percentage difference between steering data values at different indices. If the differences meet certain conditions, the point is considered a false positive and removed.

The user is given the option to manually modify the landmarks. They can choose to change or delete existing landmarks or add new ones. To aid in this, a zoomed-in view of each landmark's ROI is displayed, and the user is prompted for their desired action. If landmarks are added, they are immediately incorporated into the landmark array and the data visualization.

A final figure with the updated landmarks and their ROIs is generated. The script then compiles a list of images corresponding to each landmark's ROI, adding these images to the landmarkimages list.
