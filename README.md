# EyePort
Software to collect, analyze, and export Eye-Tracking Data. Made for TOBII Pro Glasses 2.

<img width="795" alt="EyePort" src="https://github.com/akashcraft/EyePort/assets/113077967/4dc4d6e3-5482-46a0-8f7b-78667bd4d46d">

## Installation
Download the latest version from [akashcraft.ca](https://akashcraft.ca/eyeport.html) or from the releases section. The User Manual is included with the software.

## Collecting Data
EyePort is designed for the TOBII Pro Glasses 2. The unofficial API for connecting the glasses can be found [here](https://github.com/ddetommaso/TobiiGlassesPyController) (@detommaso). The data collected are in the form of Gaze 2D Coordinates, Gaze 3D Vectors and IMU measurements. They are either streamed or accessed locally from the glass SD Card.

![image](https://github.com/akashcraft/EyePort/assets/113077967/73a34fd2-1718-49dc-a6a5-4273f656c2e6)

EyePort then creates a Excel file to hold these data. Some cases, this extraction is all you need. But EyePort can do a lot more; these are discussed in the next section.

## Analyzing Data
Using a simple timing algorithm on Gaze 2D Coordinates, EyePort can quickly determine Areas of Interest (AOIs) and Unique Areas of Interest (UAOIs). This is perfect for cases where the user does not move their head as illustrated below.

https://github.com/akashcraft/EyePort/assets/113077967/d9307e84-4651-437d-87f2-a8a86601c599

As soon as head orientations change, the previous technique will not work. To overcome this, gyroscope values are used to normalize the AOI detections. Using matrix calculation and single integration, the detections are reverted back to a global coordinate system. This way the UAOIs can be determined with good accuracy.

https://github.com/akashcraft/EyePort/assets/113077967/40066f1c-8903-489a-8453-8c85a6ff5040

The detections can be identified using an pre-trained ImageAI model. For this identification, the YOLO (You look only once) algorithm was used. Details about this algorithm can be found here. EyePort can detect everyday objects or Ships and Icebergs (Custom model) for the maritime industry.

![Analysis](https://github.com/akashcraft/EyePort/assets/113077967/ae227c9e-9927-4794-a0e2-b9929fdaeea8)

## Exporting Data
This version of EyePort was mainly catered to serving DynaFRAM which is a FRAM Model Visualizer. To learn more about FRAM and FRAM Modelling, click [here](https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html). EyePort creates partial input files containing eye-tracking data for DynaFRAM. You can download DynaFRAM from [here](https://www.engr.mun.ca/~d.smith/dynafram.html).

https://github.com/akashcraft/EyePort/assets/113077967/d466440f-bf52-4a4c-bcc7-7f9d9b390677

EyePort Version 3.0 will focus on expanding the applications of eye-tracking. It will be used as a safety assessment tool and an instructor aid for the maritime industry.

## Limitations
Some limitations include:
- No Unrestrained Motion
- Needs Good Lighting for Image Detection
- Only works with TOBII Pro Glasses 2

The unrestrained motion (where user can freely move around along with rotating head) was difficult to achieve with just the glasses alone. The IMU does contain an accelerometer. But double integrating the acceleration to position caused a huge exponential shift to infinity with lots of error being introduced with each integration. There needs to be external lasers or cameras to overcome this.

![image](https://github.com/akashcraft/EyePort/assets/113077967/044d6650-bc5a-4cfd-a3f9-192879a09c2a)


## Who can use this?
You can download and edit the source code files. EyePort is not to be resold for any commercial purposes.
Should you wish to publish this in your socials, please provide appropriate credits.  

You can add this as your description if you like:
Source Code: https://github.com/akashcraft/EyePort 
AkashCraft: [akashcraft.ca](https://akashcraft.ca)  

Thanks!
