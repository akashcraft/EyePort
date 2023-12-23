# EyePort
Software to collect, analyze, and export Eye-Tracking Data from TOBII Pro Glasses 3.

<img width="600" alt="EyePort" src="https://github.com/akashcraft/EyePort/assets/113077967/8affdd2f-cd01-48b8-8563-96bb8061ab81">

## User Manual
Please read the User Manual which is embedded in the application or alternatively download from [here](https://github.com/akashcraft/EyePort/files/13757497/EyePort.User.Manual.pdf).<br>
To learn how EyePort works in detail, read the detailed explanation from [here](https://github.com/akashcraft/EyePort/files/13757398/EyePort.Algorithm.Explanation.pdf).

## Features
- Areas of Interest Detection
- Unique Areas of Interest Detection
- Head Orientation Times
- Radar Violations
- No-Go Zones
- Dead Man Switch
- Multi-Language Support (English, French, Dutch)
- Dark Mode
- Compact and Fullscreen Modes
- Better Visuals and Progress Bars

## Installation
Download the latest version from [akashcraft.ca](https://akashcraft.ca/eyeport.html) or from the releases section. Should you wish to run the source code yourself, Run the **EyePort GUI.py** file. Here are the requirements:

- Python 3.10 (Very Important due to compatibility with some packages) [Get it here](https://www.python.org/downloads/release/python-3100/)
- customtkinter [Get it here](https://github.com/TomSchimansky/CustomTkinter)
- ImageAI (For Object Detection to work) [Get it here](https://github.com/OlafenwaMoses/ImageAI/)
- g3pylib (Glasses API) [Get it here](https://github.com/tobiipro/g3pylib)
- matplotlib 
- AppOpener
- Pillow
- openpyxl
- opencv-python
- image_similarity_measures
- pyfftw
- tkVideoPlayer

Install via the [requirements.txt](https://github.com/akashcraft/EyePort/files/13757333/requirements.txt)
```
pip install -r requirements.txt
```
or simply paste the following in terminal
```
pip install customtkinter, g3pylib, matplotlib, AppOpener, Pillow, opencv-python, openpyxl, image_similarity_measures, pyfftw, tkVideoPlayer
```

## Important Notes
EyePort comes in two versions. Lite Version does not contain Image Detection while Full Version does. EyePort makes a distinction between the two versions on the interface. You will need to manually install the Object Detection Module (regular local install) or [ImageAI package](https://github.com/OlafenwaMoses/ImageAI/) (systemwide development environment) if you want Image Detection to work. It has a lot of dependencies based on CPU/CUDA processing.

EyePort stores its configuration data in the Settings.txt which must be located in the same project folder. If this is not possible, EyePort will attempt to re-create the files during the pre-GUI checks. Resources folder contains all the GUI elements and this folder **must not** be deleted. EyePort will not load the GUI in that case.

## Collecting Data
EyePort is designed for the TOBII Pro Glasses 3. You can connect and record from the glasses from EyePort directly. Should you wish to stream and download the recording folder from the glasses, use TOBII Glasses Controller from [here](https://connect.tobii.com/s/g3-downloads?language=en_US). It essentially does the same thing but with the added convenience of not removing the SD Card from the glasses everytime.

The official API for connecting the glasses can be found [here](https://github.com/tobiipro/g3pylib). The data collected are in the form of Gaze 2D Coordinates, Gaze 3D Vectors, and IMU measurements which are accessed locally from the glass SD Card. EyePort then creates a Excel file to hold these data. Some cases, this extraction is all you need. But EyePort can do a lot more; these are discussed in the next section.

<img width="600" src="https://github.com/akashcraft/EyePort/assets/113077967/2489f63a-ee72-4dd1-a351-f843d6b640fa">


## Analyzing Data
Using a simple timing and tolerance algorithm based on Gaze 2D Coordinates, EyePort can quickly determine Areas of Interest (AOIs). The detections are then cropped into smaller squares of images (size can be adjusted by user) and then matched against each other to uniquely identify common or similar looking objects (done using image_similarity_measures). Matrix calculation and Single integration calculations were dropped since EyePort V3.0.0.

The detections can be identified using an pre-trained ImageAI model. For this identification, the YOLO (You look only once) algorithm was used. Details about this algorithm can be found [here](https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html). EyePort can detect General Objects, Ships and Icebergs, or VISTA Diesel Engine.

<img width="600" src="https://github.com/akashcraft/EyePort/assets/113077967/ec17f438-9819-41d5-9717-bc8a77d6816e">

## Exporting Data
EyePort V2.0.0 was mainly catered to serving DynaFRAM which is a FRAM Model Visualizer. To learn more about FRAM and FRAM Modelling, click [here](https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html). EyePort creates partial input files containing eye-tracking data for DynaFRAM. You can download DynaFRAM from [here](https://www.engr.mun.ca/~d.smith/dynafram.html).

EyePort V3.0.0 focuses on expanding the applications of eye-tracking. It can be used as an safety assessment tool and an instructor aid for the maritime industry.

<img width="600" src="https://github.com/akashcraft/EyePort/assets/113077967/7de91922-1e9b-4e6c-9ca6-fdeba323b48a">

## Limitations
Some limitations include:
- Needs Lighting and 500+ samples for Good Image Detection
- Only works with TOBII Pro Glasses 3

The unrestrained motion (where user can freely move around along with rotating head) limitation was overcome in later builds of EyePort. This was possible because IMU sensor data was no longer the primary source of tracking.

## Who can use this?
You are free to download and edit the source code files however you like. But, EyePort is not to be resold for any commercial purpose(s).
Should you wish to publish this in your project or socials, please provide appropriate credits.

You can add this as your references (or description) if you like:

Source Code: https://github.com/akashcraft/EyePort<br>
Website: [akashcraft.ca](https://akashcraft.ca)

Thanks!

## References
livedata.json Structure Help<br>
https://www.researchgate.net/publication/318207515_Data_Conversion_Tool_For_Tobii_Pro_Glasses_2_Live_Data_Files_From_json_to_txt

TOBII g3pylib Documentation<br>
https://tobiipro.github.io/g3pylib/g3pylib.html
