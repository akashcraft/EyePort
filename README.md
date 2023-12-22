Software to collect, analyze, and export Eye-Tracking Data from TOBII Pro Glasses 3.

<img width="795" alt="EyePort" src="https://github.com/akashcraft/EyePort/assets/113077967/8affdd2f-cd01-48b8-8563-96bb8061ab81">

## Installation
Download the latest version from [akashcraft.ca](https://akashcraft.ca/eyeport.html) or from the releases section. Should you wish to run the source code yourself, Run the **EyePort GUI.py** file. Here are the requirements:

- Python 3.10 (Very Important due to compatibility with some packages) [Get it here](https://www.python.org/downloads/release/python-3100/)
- customtkinter [Get it here](https://github.com/TomSchimansky/CustomTkinter)
- ImageAI [Get it here](https://github.com/OlafenwaMoses/ImageAI/)
- matplotlib 
- AppOpener
- Pillow
- openpyxl
- opencv-python
- image_similarity_measures
- pyfftw
- tkVideoPlayer

Install via the [requirements.txt](https://github.com/akashcraft/EyePort/files/13757320/requirements.txt)
```
pip install -r requirements.txt
```
or simply paste the following in terminal
```
pip install customtkinter, matplotlib, AppOpener, Pillow, opencv-python, openpyxl, image_similarity_measures, pyfftw, tkVideoPlayer
```

## Important Notes
You will need to manually install the ImageAI package if you want Image Detection to work. It has a lot of dependencies depending on if you want CPU/CUDA GPU to do the work and the site gets updates regularly. Hence, I did not include it here. There are two pre-trained models for you to work with in the releases section. Use the link above to get the ImageAI package or simply do not choose it in EyePort Settings.

EyePort comes in two versions. Lite Version does not contain Image Detection while Full Version does. EyePort makes a distinguishes this on the interface depending on which mode is being used.

EyePort stores its configuration data in the Settings.txt which must be located in the same project folder. If this is not possible, EyePort will attempt to re-create the files during the pre-GUI checks. Resources folder contains all the GUI elements and this folder **must not** be deleted. EyePort will not load the GUI in that case.

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
Should you wish to publish this in your project or socials, please provide appropriate credits.  

You can add this as your references (or description) if you like:

Source Code: https://github.com/akashcraft/EyePort 
AkashCraft: [akashcraft.ca](https://akashcraft.ca)  

Thanks!

## References
livedata.json Structure Help
https://www.researchgate.net/publication/318207515_Data_Conversion_Tool_For_Tobii_Pro_Glasses_2_Live_Data_Files_From_json_to_txt

Converting 2D gaze data into 3D scene
https://academic.oup.com/jcde/article/7/2/228/5813739#202866113

Davide De Tommaso and Agnieszka Wykowska. 2019. TobiiGlassesPySuite: An open-source suite for using the Tobii Pro Glasses 2 in eye-tracking studies. In 2019 Symposium on Eye Tracking Research and Applications (ETRA ’19), June 25–28, 2019, Denver , CO, USA. ACM, New York, NY, USA, 5 pages.
https://doi.org/10.1145/3314111.3319828
