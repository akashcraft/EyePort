Software to collect, analyze, and export Eye-Tracking Data from TOBII Pro Glasses 3.

<img width="795" alt="EyePort" src="https://github.com/akashcraft/EyePort/assets/113077967/8affdd2f-cd01-48b8-8563-96bb8061ab81">

## Installation
Download the latest version from [akashcraft.ca](https://akashcraft.ca/eyeport.html) or from the releases section. Should you wish to run the source code yourself, Run the **EyePort GUI.py** file. Here are the requirements:

- Python 3.10 (Very Important due to compatibility with some packages) [Get it here](https://www.python.org/downloads/release/python-3100/)
- customtkinter [Get it here](https://github.com/TomSchimansky/CustomTkinter)
- ImageAI [Get it here](https://github.com/OlafenwaMoses/ImageAI/)
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
You will need to manually install the ImageAI package if you want Image Detection to work. It has a lot of dependencies depending on if you want CPU/CUDA GPU to do the work and the site gets updates regularly. Hence, I did not include it here. There are two pre-trained models for you to work with in the releases section. Use the link above to get the ImageAI package or simply do not choose it in EyePort Settings.

EyePort comes in two versions. Lite Version does not contain Image Detection while Full Version does. EyePort makes a distinction between the two versions on the interface.

EyePort stores its configuration data in the Settings.txt which must be located in the same project folder. If this is not possible, EyePort will attempt to re-create the files during the pre-GUI checks. Resources folder contains all the GUI elements and this folder **must not** be deleted. EyePort will not load the GUI in that case.

## Collecting Data
EyePort is designed for the TOBII Pro Glasses 3. The official API for connecting the glasses can be found [here](https://github.com/tobiipro/g3pylib). The data collected are in the form of Gaze 2D Coordinates, Gaze 3D Vectors, and IMU measurements. They are accessed locally from the glass SD Card.

![image](https://github.com/akashcraft/EyePort/assets/113077967/73a34fd2-1718-49dc-a6a5-4273f656c2e6)

EyePort then creates a Excel file to hold these data. Some cases, this extraction is all you need. But EyePort can do a lot more; these are discussed in the next section.

## Analyzing Data
Using a simple timing and tolerance algorithm based on Gaze 2D Coordinates, EyePort can quickly determine Areas of Interest (AOIs). The detections are then cropped into smaller squares of images (size can be adjusted by user) and then matched against each other to uniquely identify common or similar looking objects.

<img width="700" alt="EyePort" src="https://github.com/akashcraft/EyePort/assets/113077967/c44d3ee5-0f48-4346-80a0-4ff3f275f6c8">

Matrix calculation and Single integration calculations were dropped since EyePort V3.0.0 due to the following reasons.
-	More Calculations (Potentially slowing down user systems)
-	Higher Chances of Error (If gyroscope calibration was not done correctly)
-	New Glasses had a worse Gyroscope (values starting in the 7-10 degrees/second range even if the glasses are stationary)
-	Difficulty Filtering Errors and Calibrating the Gyroscope

The detections can be identified using an pre-trained ImageAI model. For this identification, the YOLO (You look only once) algorithm was used. Details about this algorithm can be found [here](https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html). EyePort can detect General Objects, Ships and Icebergs, or VISTA Diesel Engine.

To learn how EyePort works in detail (including Head Orientation calculations and other features). Please read the detailed [explanation document](https://github.com/akashcraft/EyePort/files/13757398/EyePort.Algorithm.Explanation.pdf).

## Exporting Data
EyePort V2.0.0 was mainly catered to serving DynaFRAM which is a FRAM Model Visualizer. To learn more about FRAM and FRAM Modelling, click [here](https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html). EyePort creates partial input files containing eye-tracking data for DynaFRAM. You can download DynaFRAM from [here](https://www.engr.mun.ca/~d.smith/dynafram.html).

EyePort V3.0.0 focuses on expanding the applications of eye-tracking. It will be used as a safety assessment tool and an instructor aid for the maritime industry.

## Limitations
Some limitations include:
- Needs Lighting and 500+ samples for Good Image Detection
- Only works with TOBII Pro Glasses 3

The unrestrained motion (where user can freely move around along with rotating head) limitation was overcome in later builds of EyePort. This was possible because IMU sensor were no longer the primary source of tracking.

## Who can use this?
You can download and edit the source code files however you like. However, EyePort is not to be resold for any commercial purpose(s).
Should you wish to publish this in your project or socials, please provide appropriate credits.  

You can add this as your references (or description) if you like:

Source Code: https://github.com/akashcraft/EyePort 
Website: [akashcraft.ca](https://akashcraft.ca)

Thanks!

## References
livedata.json Structure Help
https://www.researchgate.net/publication/318207515_Data_Conversion_Tool_For_Tobii_Pro_Glasses_2_Live_Data_Files_From_json_to_txt

TOBII g3pylib Documentation
https://tobiipro.github.io/g3pylib/g3pylib.html

https://academic.oup.com/jcde/article/7/2/228/5813739#202866113

Davide De Tommaso and Agnieszka Wykowska. 2019. TobiiGlassesPySuite: An open-source suite for using the Tobii Pro Glasses 2 in eye-tracking studies. In 2019 Symposium on Eye Tracking Research and Applications (ETRA ’19), June 25–28, 2019, Denver , CO, USA. ACM, New York, NY, USA, 5 pages.
https://doi.org/10.1145/3314111.3319828
