#Custom Object Detector
#Code part of Tobii Eye Tracking Project
#Made by Akash Samanta

from imageai.Detection.Custom import CustomObjectDetection
from PIL import Image
import cv2

def CustomObjectDetect(picarray,GazeX,GazeY,type):
    detector = CustomObjectDetection()
    detector.setModelTypeAsYOLOv3()
    if type==2:
        detector.setModelPath("CustomOcean2.pt")
        detector.setJsonPath("CustomOceanConfig2.json")
    else:
        detector.setModelPath("CustomDiesel.pt")
        detector.setJsonPath("CustomDiesel.json")
    detector.loadModel()
    returned_image, detections = detector.detectObjectsFromImage(
        input_image=picarray,
        output_type="array",
        minimum_percentage_probability=20
    )
    #im = Image.fromarray(returned_image)
    #im.show()

    Gaze=[GazeX,GazeY]
    Names=[]
    Probability=[]
    BoxPoints=[]
    for i in detections:
        Names.append(i["name"])
        Probability.append(i["percentage_probability"])
        BoxPoints.append(i["box_points"])
    #print(Names,Probability)

    if (type==2):
        hit=[]
        hitbox=[]
        for j in range(len(BoxPoints)):
            if BoxPoints[j][2]>Gaze[0]*1920 and BoxPoints[j][0]<Gaze[0]*1920 and BoxPoints[j][3]>Gaze[1]*1080 and BoxPoints[j][1]<Gaze[1]*1080:
                hit.append(Names[j])
                hitbox.append(BoxPoints[j])
        #print(hit,hitbox)

        if len(hit)==0:
            returned_image=cv2.cvtColor(returned_image, cv2.COLOR_BGR2RGB)
            return "Failed to Identify",returned_image
        elif len(hit)==1:
            return(hit[0]),returned_image
        else:
            smallarea=0
            for i in range(len(hitbox)):
                w=hitbox[i][2]-hitbox[i][0]
                l=hitbox[i][3]-hitbox[i][1]
                a=l*w
                if i==0:
                    smallarea=a
                    small=0
                else:
                    if a<smallarea:
                        smallarea=a
                        small=i
            return(hit[small]),returned_image
    else:
        if Names==[]:
            return "Detection Failure",returned_image
        else:
            return Names[0],returned_image


if __name__=='__main__':
    print("Object Detection\nCode part of Tobii Eye Tracking Project\nMade by Akash Samanta\n")
    print("WARNING! You are running this code snippet alone.\nThis may accomplish only a specific task. Please use EyeFRAM GUI.py instead.\n")
    
