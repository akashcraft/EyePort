#Data Analysis Rotating Head
#Stable - Can also receive Data from Unrestrained Cases but may not give desired results
#Code part of Tobii Eye Tracking Project
#Made by Akash Samanta

import openpyxl as xls
import pandas as pd
import tabulate
import math,cv2
import matplotlib.pyplot as plt
from CustomObjectDetector import CustomObjectDetect
from ObjectDetector import ObjectDetect

#Functions

def transform(X,Y,Z,Xdeg,Ydeg,Zdeg): #Function to produce your expected vector in given orientation
    X1=X
    Y1=(Y*math.cos(Xdeg*(math.pi/180)))-(Z*math.sin(Xdeg*(math.pi/180)))
    Z1=(Y*math.sin(Xdeg*(math.pi/180)))+(Z*math.cos(Xdeg*(math.pi/180)))
    X2=(X1*math.cos(Ydeg*(math.pi/180)))+(Z1*math.sin(Ydeg*(math.pi/180)))
    Y2=Y1
    Z2=(Z1*math.cos(Ydeg*(math.pi/180)))-(X1*math.sin(Ydeg*(math.pi/180)))
    X3=(X2*math.cos(Zdeg*(math.pi/180)))-(Y2*math.sin(Zdeg*(math.pi/180)))
    Y3=(Y2*math.cos(Zdeg*(math.pi/180)))+(X2*math.sin(Zdeg*(math.pi/180)))
    Z3=Z2
    return (X3,Y3,Z3)

def normalizev1(L,sen=270): #Backup Algorithm #Sensitivity
    if len(L)==0:
        return 0,[0,],[],[]
    elif len(L)==1:
        return 1,[1,],['Object 1'],['Object 2']
    else:
        Check,Result=[],[]
        pos=[0,] #Main index to use when showing unique areas of interest
        AOIName=['Object 1',]
        UAOIName=['Object 1',]
        ucount=2
        for i in range(len(L)):
            Check.append(transform(L[i][0],L[i][1],L[i][2],-L[i][3],-L[i][4],-L[i][5]))
        flag=0
        Result.append(Check[0])
        for i in range(1,len(Check)):
            for j in range(len(Result)):
                if abs(Check[i][0]-Result[j][0])<sen and abs(Check[i][1]-Result[j][1])<sen and abs(Check[i][2]-Result[j][2])<sen:
                    flag=0
                    AOIName.append('Object '+str(j+1))
                    break
                else:
                    flag=1
            if flag==1:
                Result.append(Check[i])
                AOIName.append(f'Object {ucount}')
                UAOIName.append(f'Object {ucount}')
                ucount=ucount+1
                pos.append(i)
                flag=0
        #print(Check,Result)
        return(len(Result)),pos,AOIName,UAOIName

def normalize(L,sen): #Uses unit vectors #Sensitivity (Sweet Spot is 0.2)
    if len(L)==0:
        return 0,[0,],[],[]
    elif len(L)==1:
        return 1,[0,],['Object 1'],['Object 1']
    else:
        Result=[]
        pos=[0,] #Main index to use when showing unique areas of interest
        AOIName=['Object 1',]
        UAOIName=['Object 1',]
        ucount=2
        Result.append(L[0])
        for i in range(1,len(L)):
            for j in range(len(Result)):
                Target = transform(L[i][0],L[i][1],L[i][2],Result[j][3]-L[i][3],Result[j][4]-L[i][4],Result[j][5]-L[i][5])
                unit1=((Target[0]**2)+(Target[1]**2)+(Target[2]**2))**(0.5)
                unit2=((Result[j][0]**2)+(Result[j][1]**2)+(Result[j][2]**2))**(0.5)
                if abs(Result[j][0]/unit2-Target[0]/unit1)<sen and abs(Result[j][1]/unit2-Target[1]/unit1)<sen and abs(Result[j][2]/unit2-Target[2]/unit1)<sen:
                    flag=0
                    AOIName.append('Object '+str(j+1))
                    break
                else:
                    flag=1 #Only when it is significantly different
            if flag==1:
                Result.append(L[i])
                AOIName.append(f'Object {ucount}')
                UAOIName.append(f'Object {ucount}')
                ucount=ucount+1
                pos.append(i)
                flag=0
        #print(len(L),len(Result))
        return (len(Result)),pos,AOIName,UAOIName

def analyzer(sdir,vdir,sen=0.20,thit=200,useai=0,manual=0,type=1): #Data Directory, Video Directory, Sensitivity for UAOI, Fixation Time, Use AI?, Type of Recording
    if type==0:
        thit=int(thit/4)
    #Counters and AOIs
    GX=[] #All Gyro_X D/s
    GY=[] #All Gyro_Y D/s
    GZ=[] #All Gyro_Z D/s
    X,Y,Z=[],[],[] #All 3D Gaze
    X2,Y2=[],[] #All 2D Gaze
    Timestamps=[] #All Timestamps
                
    #Column Settings
    columnselect=[1,2,3,4,5,6,7,8,9]

    #Loading Excel File
    book = xls.load_workbook(sdir)
    #Getting Sheet
    #or use book.active
    sheet = book['Data']
    col = sheet.iter_cols

    #Data Collection begins
    #sheet.max_row:
    for j in columnselect:
        for col in sheet.iter_cols(j,j):
            for i in range(1, sheet.max_row):
                if j==2:
                    X.append(col[i].value)
                elif j==3:
                    Y.append(col[i].value)
                elif j==4:
                    Z.append(col[i].value)
                elif j==5:
                    GX.append(col[i].value)
                elif j==6:
                    GY.append(col[i].value)
                elif j==7:
                    GZ.append(col[i].value)
                elif j==8:
                    X2.append(col[i].value)
                elif j==9:
                    Y2.append(col[i].value)
                else:
                    Timestamps.append(col[i].value)
        
    #Analysis Begins
    #Calculating Actual Gyro Degrees from start of recording
    #From Degrees/Second to Degrees
    AGyro_X=[0,]
    AGyro_Y=[0,]
    AGyro_Z=[0,]

    #Deletes all rows where there is no gaze data
    j=0
    while True:
        try:
            if X[j]==0 and Y[j]==0 and Z[j]==0 and GX[j]==0 and GY[j]==0 and GZ[j]==0:
                del X[j]
                del Y[j]
                del Z[j]
                del GX[j]
                del GY[j]
                del GZ[j]
                del Timestamps[j]
            j=j+1
        except:
            break
    
    #TY=GY
    #ti=Timestamps
    #j=0
    #while True:
    #    try:
    #        if TY[j]==0:
    #            del TY[j]
    #            del ti[j]
    #        j=j+1
    #    except:
    #        break
    #plt.plot(ti,TY)
    #plt.xlabel('Timestamps [ms]')
    #plt.ylabel('Degrees/Second [deg/s]')
    #plt.show()

    #This loop calculates all degrees values from degrees/second. Only one integration is required.
    for i in range(1,len(Timestamps)):
        if (Timestamps[i]-Timestamps[i-1])==0:
            AGyro_X.append(AGyro_X[-1])
            AGyro_Y.append(AGyro_Y[-1])
            AGyro_Z.append(AGyro_Z[-1])
        else:
            time_diff=(Timestamps[i]-Timestamps[i-1])/1000
            acc_X=(GX[i]-GX[i-1])/time_diff
            acc_Y=(GY[i]-GY[i-1])/time_diff
            acc_Z=(GZ[i]-GZ[i-1])/time_diff
            xval=AGyro_X[i-1]+(GX[i-1]*time_diff)+(0.5*acc_X*(time_diff**2))
            AGyro_X.append(xval)
            yval=AGyro_Y[i-1]+(GY[i-1]*time_diff)+(0.5*acc_Y*(time_diff**2))
            AGyro_Y.append(yval)
            zval=AGyro_Z[i-1]+(GZ[i-1]*time_diff)+(0.5*acc_Z*(time_diff**2))
            AGyro_Z.append(zval)
        
    #Main Algorithm - Here the different gaze points are identified
    ignore=0 #Used to identify patterns in the excel file and help the loop below. Not returned.
    tripper=0 #Trips functions to capture AOI. This value should match with thit - the fixation duration. Not returned.
    count=0 #Counts total number of trips. This is returned.
    s=500 #Sensitivity in mm (Worked many times) User cannot change this setting. But you as a developer can!

    AllAOI=[]
    Seconds,End=[],[]
    GazeX,GazeY=[],[]
    for i in range(len(Timestamps)-2):
        if tripper==thit and ignore!=1: #Around 2 seconds. Users can change this setting if they wish
            AllAOI.append((X[i-1],Y[i-1],Z[i-1],AGyro_X[i-1],AGyro_Y[i-1],AGyro_Z[i-1]))
            Seconds.append(Timestamps[int(i-thit)]) #Get the Timestamp from when the AOI was looked at
            if X2[int(i-thit)]!=0: #Also store the Gaze 2D coordinates
                GazeX.append(X2[int(i-thit)])
                GazeY.append(Y2[int(i-thit)])
            else:
                y=int(i-thit)
                while True: #Essentially this loop finds a valid Gaze Point which is NOT 0,0
                    if X2[y]==0:
                        y=y+1
                    else:
                        break
                GazeX.append(X2[y])
                GazeY.append(Y2[y])
            count=count+1
        if X[i]!=0 and Y[i]!=0 and Z[i]!=0:
                if X[i+1]!=0 and Y[i+1]!=0 and Z[i+1]!=0:
                    ignore=0
                else:
                    if X[i+2]!=0 and Y[i+2]!=0 and Z[i+2]!=0:
                        ignore=2
                    else:
                        ignore=1
        else:
            ignore=1
        if ignore==0:
            Xdeg=AGyro_X[i+1]-AGyro_X[i]
            Ydeg=AGyro_Y[i+1]-AGyro_Y[i]
            Zdeg=AGyro_Z[i+1]-AGyro_Z[i]
            EX,EY,EZ=transform(X[i],Y[i],Z[i],Xdeg,Ydeg,Zdeg)
            if abs(EX-X[i+1])<s and abs(EY-Y[i+1])<s and abs(EZ-Z[i+1])<s:
                tripper=tripper+1
            else:
                if tripper>thit:
                    End.append(Timestamps[i])
                tripper=0
        elif ignore==2:
            Xdeg=AGyro_X[i+2]-AGyro_X[i]
            Ydeg=AGyro_Y[i+2]-AGyro_Y[i]
            Zdeg=AGyro_Z[i+2]-AGyro_Z[i]
            EX,EY,EZ=transform(X[i],Y[i],Z[i],Xdeg,Ydeg,Zdeg)
            if abs(EX-X[i+2])<s and abs(EY-Y[i+2])<s and abs(EZ-Z[i+2])<s:
                tripper=tripper+1
            else:
                if tripper>thit:
                    End.append(Timestamps[i]) #Good Time to add End Time when AOI goes out of interest
                tripper=0
        else:
            #print(tripper) #For DEBUG ONLY Good way to see when the AOI is registered or the tripper value
            pass
    
    if len(Seconds)-len(End)==1:
        End.append(Timestamps[-1])
    
    #Getting Frames and Using Object Detection
    if manual==0:
        unique_count,pos,AOIName,UAOIName=normalize(AllAOI,sen)
    else:
        unique_count,pos,AOIName,UAOIName=len(AllAOI),[i for i in range(len(AllAOI))],[f'Object {i+1}' for i in range(len(AllAOI))],[f'Object {i+1}' for i in range(len(AllAOI))]
    startsec=Timestamps[0] #Starting Timestamp
    picarray=[] #For Frames with Gaze
    nopicarray=[] #For Frames without Gaze NOT RETURNED but needed for ObjectDetector.py
    answer=[] #To store all object detection text answers
    answerarray=[] #To store object detection frames

    video = cv2.VideoCapture(vdir)
    fps = video.get(cv2.CAP_PROP_FPS)
    videoduration = video.get(cv2.CAP_PROP_FRAME_COUNT)
    videoduration = videoduration/fps

    #Syncronization Step - To align video seconds and timestamps
    ratio=videoduration/((Timestamps[-1]-startsec)/1000)
    for i in range(len(Seconds)):
        Seconds[i]=((Seconds[i]-startsec)/1000)*ratio
    for i in range(len(End)):
        End[i]=((End[i]-startsec)/1000)*ratio

    for i in range(len(Seconds)): #Get all frames
        video.set(cv2.CAP_PROP_POS_FRAMES,int(fps*Seconds[i]))
        ret,frame=video.read()
        if type==1: #If recorded in TOBII Proprietary Mode, then add the gaze circles
            x=GazeX[i]
            y=GazeY[i]
            if x>1:
                x=1
            if y>1:
                y=1
            frame=cv2.circle(frame,(int(x*1920),int(y*1080)), 40, (0, 0, 255), 4)
        frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        picarray.append(frame)
    
    if useai==1: #If AI needed, then call ObjectDetector.py
        for i in range(len(Seconds)):
            video.set(cv2.CAP_PROP_POS_FRAMES,int(fps*Seconds[i]))
            ret,frame=video.read()
            print("Normal Object Detection")
            frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            nopicarray.append(frame)
            text,returned_image = ObjectDetect(frame, GazeX[i], GazeY[i])
            answer.append(text.capitalize())
            if type==1: #If recorded in TOBII Proprietary Mode, then add the gaze circles
                x=GazeX[i]
                y=GazeY[i]
                if x>1:
                    x=1
                if y>1:
                    y=1
                returned_image=cv2.circle(returned_image,(int(x*1920),int(y*1080)), 40, (255, 0, 0), 4)
            answerarray.append(returned_image)
    elif useai==2: #If AI needed, then call CustomObjectDetector.py
        for i in range(len(Seconds)):
            video.set(cv2.CAP_PROP_POS_FRAMES,int(fps*Seconds[i]))
            ret,frame=video.read()
            print("Custom Object Detection")
            frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            nopicarray.append(frame)
            text,returned_image = CustomObjectDetect(frame, GazeX[i], GazeY[i])
            answer.append(text.capitalize())
            if type==1: #If recorded in TOBII Proprietary Mode, then add the gaze circles
                x=GazeX[i]
                y=GazeY[i]
                if x>1:
                    x=1
                if y>1:
                    y=1
                returned_image=cv2.circle(returned_image,(int(x*1920),int(y*1080)), 40, (255, 0, 0), 4)
            answerarray.append(returned_image)
    else:
        print("No Object Detection")
    #Information for Gaze 2D Graph Color and Size
    tX,tY,color,size=[],[],[],[]
    for i in range(len(X2)):
        if X2[i]!=0:
            if X2[i] in GazeX and Y2[i] in GazeY:
                color.append(2)
                size.append(1000)
            else:
                color.append(1)
                size.append(100)
            tX.append(X2[i]*1920)
            tY.append(Y2[i]*(-1080))
            
    X2,Y2=tX,tY
    #print(count,unique_count,pos)
    return count,unique_count,picarray,answerarray,answer,pos,AOIName,UAOIName,Seconds,End,X2,Y2,color,size

if __name__=='__main__':
    print("Data Analyzer Rotating Head\nCode part of Tobii Eye Tracking Project\nMade by Akash Samanta\n")
    print("WARNING! You are running this code snippet alone.\nThis may accomplish only a specific task. Please use EyeFRAM GUI.py instead.\n")
    c=21
    #C:\Users\AkashCraft\Documents\Tobii Pro Glasses Project\Project{c} Data Export.xlsx
    count,unique_count,picarray,answerarray,answer,pos,AOIName,UAOIName,Seconds,End,X,Y,color,size=analyzer(
        sdir=rf'C:\Users\AkashCraft\Documents\Tobii Pro Glasses Project\Project{c} Data Export.xlsx',
        vdir=rf'C:\Users\AkashCraft\Documents\Tobii Pro Glasses Project\Project{c}.mp4',
        sen=0.1,
        thit=200,
        useai=0,
        manual=0,
        type=1)
    print("The System has detected",count,"area of interests in the given session\nWith",unique_count,"of them being unique.\n")
