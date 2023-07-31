# Memory-Based-Navigation-Research

# GoPro Research
The GoPro and Serial GPS integration algorithm takes in as many GoPros as can be feasibly connected to the computer via USB, and then also connects a GPS that transmits NMEA data via USB and integrates the two so the research team can collect 120 degree panoramic views using openCV2 and tag them with their GPS coordinates as part of data acquisition. 

The HDF5 reader opens the HDF5 dataset created by the data acquisition. 

# MBN Steering Data Analysis
The algorithm takes in a HDF5 dataset which stores images and their associated steering data from a RC car and uses the values of how much a user uses the joystick to turn to understand where user decision points are. This uses elements of machine learning and signal processing to produce accurate landmarks/decision points. 

This Python script performs the following:

1. Library Imports:
This code uses several Python libraries, including numpy for numerical operations, math for basic mathematical functions, h5py to read and write HDF5 files (used for storing large datasets), PIL for manipulating images, os and shutil for filesystem operations, glob for pathname pattern expansion, and plotly for data visualization.

2. Defining Auxiliary Functions:
Two helper functions are defined: traverse_datasets, which recursively traverses HDF5 files and yields the path of all datasets inside, and percentage_diff, which calculates the percentage difference between two given numbers.

3. Interactive User Input:
The script enters an interactive mode where it asks the user whether they want to process an individual HDF5 file or an entire folder of them.

4. Data Extraction:
Depending on the user's choice, the script reads the appropriate HDF5 files. For each file, it creates a corresponding directory. Within each file, it identifies and saves image data, and extracts steering data, storing them in appropriate data structures.

5. Landmark Identification:
In this context, landmarks refer to significant or distinctive features in the steering data. The script finds landmarks based on certain conditions related to maximum, minimum, and surrounding values of the steering data.

6. Window Definition and Defaults:
Depending on whether a folder or file is processed, a 'landmark window' size is set. This window is a range of data around each landmark that is to be considered in the analysis. The script also asks the user if they want to use default parameters or customize them. These parameters include the window size, the floor and ceiling of the steering data, the minimum distance between two landmarks, and the number of images to be considered in the 'negative' folders (those that don't contain landmarks).

7. False Positive Handling:
False positives, i.e., points identified as landmarks which are not truly significant, are detected and removed from the analysis. This is done by checking the percentage difference between steering data values at different indices. If the differences meet certain conditions, the point is considered a false positive and removed.

8. Region of Consideration (ROC):
For each landmark identified, a region of consideration (ROC) is defined as a range of data points around the landmark, based on the window size. These ROCs are stored in a list and sorted.

Overall, this script is a comprehensive solution for HDF5 file processing and analysis, with specific emphasis on identifying and analyzing landmarks within the data. It provides interactive user control and parameter customization, along with sophisticated data handling and visualization capabilities.

9. Rate of Change Correction:
The script starts to analyze each Region of Consideration (ROC) around the identified landmarks. It calculates the rate of change of the steering data within each ROC and identifies where this rate of change is at a maximum, indicating a possible landmark. If necessary, it corrects the position of the landmark to ensure it aligns with the maximum rate of change. Warnings are printed when a landmark's accuracy is questionable, suggesting an increase in the window size.

10. Checking Landmark Proximity:
The script checks if any of the identified landmarks are too close together (defined by the tooclose variable). If any two landmarks are found within this specified distance from each other, a warning is printed and both landmarks are removed from the landmark array.

11. Data Visualization:
The script then plots a line graph of the steering data with vertical lines indicating the locations of the landmarks and the boundaries of their ROIs. For file processing, this figure is displayed to the user.

12. User-Led Landmark Modification:
The user is given the option to manually modify the landmarks. They can choose to change or delete existing landmarks or add new ones. To aid in this, a zoomed-in view of each landmark's ROI is displayed, and the user is prompted for their desired action. If landmarks are added, they are immediately incorporated into the landmark array and the data visualization.

13. Final Visualization and Image Compilation:
A final figure with the updated landmarks and their ROIs is generated. The script then compiles a list of images corresponding to each landmark's ROI, adding these images to the landmarkimages list.

In summary, this part of the script focuses on refining the landmark identification process by analyzing the rate of change of the steering data, offering interactive user modification, and visually representing the results for more intuitive understanding. It's a careful and comprehensive approach to ensure the identification of most relevant and accurate landmarks in the steering data.

Following the implementation of the landmark detection strategy, the script then proceeds with image organization and data management. Specifically:

Image Sorting and Organization: The script extracts all the image files from a specified folder path. It then generates an organized structure of subfolders according to a defined naming convention based on the detected landmarks and the directionality information (positive/negative/left/right/straight). This structure helps to categorize the images based on their steering information. The script then moves the corresponding images into their designated folders. In addition, if the number of images in the last directory is odd, all the images in that directory are moved to the "00-negative" directory.

Limiting Negative Image Count: If a specified number of images (numimgs) has been defined, the script checks every 'negative' folder and ensures that the total number of images in each such folder does not exceed this specified limit. If there are too many images in a folder, the excess ones are deleted.

Landmark and Steering Data Storage: For analysis purposes, all landmark and steering data are saved to text files in a newly created or cleared 'Analysis' directory. The landmarks are stored in 'landmarks.txt', and the steering data are stored in 'steeringdata.txt'. This makes it easier to examine the effectiveness of the landmark detection strategy.

Plot Saving: The final plot of the steering data with landmarks is given a title based on the folder name and saved in two formats: HTML and JSON. The plot is saved to 'plot.html' and 'plot.json'.

Loop Control: The script then checks whether there are more datasets to process. If processing a series of datasets (i.e., folderorfile == "folder"), the script automatically starts processing the next dataset if the current dataset is not the last one. If processing a single file, the script prompts the user whether they want to run another dataset.

By the end of this script, the user is left with a well-organized folder of images sorted according to their steering information, landmark and steering data for further analysis, and a visual representation of the detected landmarks on the steering data.
