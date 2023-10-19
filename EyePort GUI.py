from tkinter import *
from tkinter import ttk
import tkinter as tk
from customtkinter import *
from PIL import ImageTk, Image
from tobiiglassesctrl import TobiiGlassesController
import os,subprocess,cv2,time
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import openpyxl as xls
import csv
import AppOpener,webbrowser

from Data_Extraction_Rotating_Head import extract
from Data_Collection_Rotating_Head import collect
from Data_Analysis_Rotating_Head import analyzer
from ModelCreator import creator
import logging

logging.getLogger('matplotlib.font_manager').disabled = True
welcome = True
fullscreenmode = 0
root = CTk()
connection_type=""
settings = []
recordactive = False
connected = False
disconnect = 0
gp = []
sync = 10
thit = 200
asense = 0.2
recordmode = 0
wipaddress = ''
eipadress = ''
default_wip = "192.168.71.50"
default_eip = "fe80::76fe:48ff:fe22:4109"
previewenabled = True
recsavefolder = ""
exportsavefolder = ""
loaddata = ""
loadvideo = ""
loadeddata = False
loadedvideo = False
rememberloadbool = True
useai = 0
exportstatus = 3


#Settings Creator and Default Settings
def createsettings():
    firstsettings = "EyePort Settings File - Any corruption may lead to configuration loss\nMade by Akash Samanta\nLight\n100\nWi-Fi\n192.168.71.50\nfe80::76fe:48ff:fe22:4109\n1\nEyePort Custom\n100\n0\nRecsave\nNormal\n1\n1\nLoad1\nLoad2\n200\n0\nExpsave\n0\n0\n0\n0\n"
    try:
        f=open("Settings.txt","w")
    except PermissionError:
        tk.messagebox.showerror("EyePort Administrator Privileges Needed","Because of the nature of this EyePort install, you will need to launch EyePort as administrator. To prevent this behaviour, please install EyePort again on a user directory.")
        quit()
    f.write(firstsettings)
    f.close()

#Record Page Functions
#Battery Indicator
def batteryrefresh():
    Battery = tobiiglasses.get_battery_status()
    #Storage = tobiiglasses.get_storage_info()
    l=Battery['level']
    text21.configure(text=f"{l}%")
    if l>95:
        batteryicon.configure(image=imgtk9)
    elif l>55:
        batteryicon.configure(image=imgtk10)
    elif l>35:
        batteryicon.configure(image=imgtk11)
    elif l>10:
        batteryicon.configure(image=imgtk12)
    else:
        batteryicon.configure(image=imgtk13)
    timelefticon.configure(image=imgtk14)
    h=Battery['remaining_time']//3600
    m=int((Battery['remaining_time']/60)%60)
    text22.configure(text=f"{h}h {m}m")
    text21.grid(row=0,column=2,pady=(10,0),padx=10,sticky='w')
    text22.grid(row=0,column=4,pady=(10,0),padx=10,sticky='w')
    batteryicon.grid(row=0,column=1,pady=(10,0),sticky='e')
    timelefticon.grid(row=0,column=3,pady=(10,0),sticky='e')

#Connection to Glasses
def connectsuccess(number):
    global cap,connected,gp
    if number==0:
        connected=False
        tk.messagebox.showerror("Connection Failed","EyePort is unable to connect with the TOBII Glasses.\nPlease check the connection and try again.")
    else:
        connectedsettings()
        connected=True
        batteryrefresh()
        connectbutton.configure(text="Connection Success",fg_color="green",state="disabled")
        calibratebutton.configure(state="normal")
        recordbutton.configure(state="normal")
        disconnectbutton.configure(state="normal")      
        if previewenabled and connection_type=='Wi-Fi':
            previewnotavail.grid_forget()
            connectpreview.grid_forget()
            ethernetpreview.grid_forget()
            videolabel.grid(row=1,column=0,rowspan=4,padx=20,pady=(10,20),sticky='nw')
            #cap = cv2.VideoCapture(0) #Use this instead to try with Local Camera Feed
            cap = cv2.VideoCapture("rtsp://%s:8554/live/scene" % wipaddress)
            tobiiglasses.start_streaming()
            gp.clear()
            video_stream()
        else:
            if connection_type=="Ethernet":
                ethernetpreviewfun()
            else:
                previewnotavailfun()
            tobiiglasses.start_streaming()

def connect():
    #print(connection_type) #For Debug Only
    global tobiiglasses,wipaddress,eipadress
    if connection_type=="Wi-Fi":
        try:
            wipaddress = wipentry.get()
            #print(wipaddress) #For Debug Only
            tobiiglasses=TobiiGlassesController(wipaddress, video_scene=True, timeout=2)
            connectsuccess(1)
            value[5]=wipaddress+"\n"
            writesettings()
        except ConnectionError:
            connectsuccess(0)
        except:
            tk.messagebox.showerror("IP Address Invalid","Looks like the Wi-Fi IP Address you entered in settings is invalid. Please check the address and try again.")
    else:
        try:
            eipaddress = eipentry.get()
            #tk.messagebox.showinfo("Ethernet Connection","The code for ethernet connection is not written yet. Please change the connection mode to Wi-Fi in Settings.")
            tobiiglasses=TobiiGlassesController(eipaddress, video_scene=False, timeout=2)
            connectsuccess(1)
            value[6]=eipaddress+"\n"
            writesettings()
        except ConnectionError:
            connectsuccess(0)
        except:
            tk.messagebox.showerror("IP Address Invalid","Looks like the Ethernet IP Address you entered in settings is invalid. Please check the address and try again.")

#Save Folder
def savelocation():
    global recsavefolder
    ask=tk.filedialog.askdirectory()
    if ask=="" and recsavefolder=="Recsave":
        recsavefolder=os.getcwd()
    elif ask=="" and recsavefolder!="Recsave":
        pass
    else:
        recsavefolder=ask
    value[11]=recsavefolder+'\n'
    writesettings()

#Record
def recorddatacollect():
    if stopper:
        data=tobiiglasses.get_data()
        if data['mems']['gy']['ts']>0:
            datacollect.append(data['mems']['gy'])
        if data['mems']['ac']['ts']>0:
            datacollect.append(data['mems']['ac'])
        if data['gp']['ts']>0:
            datacollect.append(data['gp'])
        if data['gp3']['ts']>0:
            datacollect.append(data['gp3'])
        root.after(10,recorddatacollect)

def record():
    global video,recordactive,recording_id,recsavefolder,recordactive,stopper,datacollect
    calibsuccess.grid_forget()
    calibfail.grid_forget()
    recordsettings()
    recordbutton.configure(text='Stop',command=stoprecord)
    if recsavefolder=="Recsave":
        recsavefolder=os.getcwd()
        value[11]=recsavefolder+'\n'
        writesettings()
    try:
        if recordmode==0 and previewenabled:
            c=1
            pcheck=os.path.join(recsavefolder,f'Project{c}.avi')
            while os.path.exists(pcheck):
                c=c+1
                pcheck=os.path.join(recsavefolder,f'Project{c}.avi')
            if c==1:
                path=os.path.join(recsavefolder,'Project1.avi')
            else:
                if overwritexl==0:
                    path=pcheck
                else:
                    path=os.path.join(recsavefolder,f'Project{c-1}.avi')
            video = cv2.VideoWriter(path,cv2.VideoWriter_fourcc(*'XVID'),30,(1920,1080))
            datacollect=[]
        elif recordmode==0 and previewenabled==False:
            stopper=True
            datacollect=[]
            recorddatacollect()
        else:
            project_id = tobiiglasses.create_project("Study001")
            participant_id = tobiiglasses.create_participant(project_id, "Test")
            recording_id = tobiiglasses.create_recording(participant_id)
            tobiiglasses.send_custom_event("start_recording", "Start of the recording ")
            tobiiglasses.start_recording(recording_id)
        recordactive=True
        recordstatus.configure(image=imgtk26)
        recordstatus.grid(row=2,column=1,columnspan=4,pady=10,sticky='s')
    except:
        tk.messagebox.showerror("Error Starting Recording","EyePort is unable to communicate with the TOBII Glasses. Perhaps check the connection again?")
        recordactive=False
        stream_reset()
        recordstopsettings()

def stoprecord():
    global recordactive,recording_id
    recordactive=False
    recordstopsettings()
    recordbutton.configure(text='Record Now',command=record)
    try:
        if recordmode==0 and previewenabled:
            video.release()
            collect(recsavefolder,datacollect,overwritexl)
        elif recordmode==0 and previewenabled==False:
            stopper=False
            collect(recsavefolder,datacollect,overwritexl)
        else:
            tobiiglasses.stop_recording(recording_id)
        batteryrefresh()
        recordstatus.grid_forget()
        recordstatus.configure(image=imgtk27)
        recordstatus.grid(row=2,column=1,columnspan=4,pady=10,sticky='s')
        recordstatus.after(3000,recordstatus.grid_forget)
    except PermissionError:
        tk.messagebox.showerror('Permission Error',"EyePort was unable to unable to save the recording because there was no permission to access them. Close any applications that may using the files or try elevating EyePort as Administrator.")
        recordstatus.grid_forget()
    except:
        tk.messagebox.showerror("Error Stopping Recording","EyePort is unable to stop the recording. This could be a problem with the code or due to poor/no connection with the TOBII Glasses.")
        recordstatus.grid_forget()

#Calibrate
def calibforget():
    calibsuccess.grid_forget()
    calibfail.grid_forget()
    connectmode.grid(row=1,column=1,columnspan=4,pady=(20,0),sticky='n')

def calibrate():
    project_id = tobiiglasses.create_project("Study001")
    participant_id = tobiiglasses.create_participant(project_id, "Test")
    calibration_id = tobiiglasses.create_calibration(project_id, participant_id)
    tk.messagebox.showinfo("Start Calibration","Please ask the user to look at the calibration card and then dismiss this prompt to start calibration.")
    tobiiglasses.start_calibration(calibration_id)
    res = tobiiglasses.wait_until_calibration_is_done(calibration_id)
    if sf>0.33:
        row=2
    else:
        connectmode.grid_forget()
        row=1
    if res is False:
        calibratebutton.configure(text="Calibration Failed",fg_color="dark red",state="disabled")
        calibfail.grid(row=row,column=1,columnspan=4)
        tk.messagebox.showwarning("Calibration Failure","Please ask the user to keep looking at the card during the calibration process. There weren't enough valid samples to complete the calibration. Please try again.")
        calibfail.after(3000,calibforget)
        calibratebutton.configure(text="Calibrate Glasses",fg_color="#3b8ed0",state="normal",hover_color="#36719f")
    else:
        calibratebutton.configure(text="Calibrate Again",fg_color="green",state="normal",hover_color="#006400")
        calibsuccess.grid(row=row,column=1,columnspan=4)
        calibsuccess.after(3000,calibforget)
        
#Streaming Output
def video_stream():
    global sf,disconnect,recordactive,recordmode,sync,gp #Scale Factor, Disconnect Flag, Record Flags
    try:
        ret , frame = cap.read()
        dim = (int(1920*sf),int(1080*sf))
        data  = tobiiglasses.get_data()
        if data['gp']['ts']>0:
            while len(gp)!=sync:
                gp.append([data['gp']['gp'][0],data['gp']['gp'][1]])
                data  = tobiiglasses.get_data()
            cv2.circle(frame,(int(gp[0][0]*1920),int(gp[0][1]*1080)), 40, (0, 0, 255), 4)
            del gp[0]
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(cv2image, dim, interpolation = cv2.INTER_CUBIC)
        img = Image.fromarray(resized)
        imgtk = ImageTk.PhotoImage(image=img)
        videolabel.imgtk = imgtk
        videolabel.configure(image=imgtk)
        if recordactive and recordmode==0:
            if data['mems']['gy']['ts']>0:
                datacollect.append(data['mems']['gy'])
            if data['mems']['ac']['ts']>0:
                datacollect.append(data['mems']['ac'])
            if data['gp']['ts']>0:
                datacollect.append(data['gp'])
            if data['gp3']['ts']>0:
                datacollect.append(data['gp3'])
            #cv2image2 = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)
            video.write(frame)
        videolabel.after(10, video_stream)
    except:
        if disconnect==0:
            tk.messagebox.showerror("Error Streaming","The video signal from the glasses was unexpectedly interrupted. Perhaps check the connection again?")
            recordactive=False
            stream_reset()
    finally:
        disconnect=0

def stream_reset():
    global recordactive,disconnect,tobiiglasses,connected
    disconnect=1
    if recordactive==False:
        connected=False
        recordstatus.grid_forget()
        disconnectedsettings()
        connectbutton.configure(text="Connect Glasses",fg_color="#3b8ed0",state="normal")
        calibratebutton.configure(state="disabled",text='Calibrate Glasses',fg_color="#3b8ed0")
        recordbutton.configure(state="disabled",text='Record Now',command=record)
        disconnectbutton.configure(state="disabled")
        calibsuccess.grid_forget()
        text21.grid_forget()
        text22.grid_forget()
        batteryicon.grid_forget()
        timelefticon.grid_forget()
        videolabel.grid_forget()
        connectpreviewfun()      
        if previewenabled:
            cap.release()
        tobiiglasses.stop_streaming()
        tobiiglasses.close()
    else:
        ans = tk.messagebox.askyesno("Disconnect Confirmation","You have a recording in progress. Data collected so far will be lost. Are you sure you want to disconnect the glasses?")
        if ans:
            recordactive=False
            recordstopsettings()
            stoprecord()
            stream_reset()

def resizerecord(e):
    global sf,imgtk21,imgtk22,imgtk23
    w=0.819*e.width-149.201
    h=e.height-68
    w1=(h/1080)*1920
    h1=(w/1920)*1080
    if h+w1<=w+h1:
        sf=h/1080
    else:
        sf=w/1920
    imgtk21 = CTkImage(light_image=image27,size=(int(1920*sf),int(1080*sf))) #Connect
    imgtk22 = CTkImage(light_image=image28,size=(int(1920*sf),int(1080*sf))) #Disabled
    imgtk23 = CTkImage(light_image=image29,size=(int(1920*sf),int(1080*sf))) #Ethernet
    connectpreview.configure(image=imgtk21)
    previewnotavail.configure(image=imgtk22)
    ethernetpreview.configure(image=imgtk23)

def previewnotavailfun():
    ethernetpreview.grid_forget()
    connectpreview.grid_forget()
    previewnotavail.grid(row=1,column=0,rowspan=4,padx=20,pady=(10,20),sticky='nw')

def connectpreviewfun():
    ethernetpreview.grid_forget()
    connectpreview.grid(row=1,column=0,rowspan=4,padx=20,pady=(10,20),sticky='nw')
    previewnotavail.grid_forget()

def ethernetpreviewfun():
    ethernetpreview.grid(row=1,column=0,rowspan=4,padx=20,pady=(10,20),sticky='nw')
    connectpreview.grid_forget()
    previewnotavail.grid_forget()

#Analyze Page Functions
def analyze_reset():
    global exportstatus
    exportstatus = 3
    export_reset()
    text56.configure(text="You will need to analyze data first before you can export.",text_color=("red","yellow"))
    text58.configure(text="You will need to analyze data first before you can export.",text_color=("red","yellow"))
    text62.configure(text="You will need to analyze data first before you can export.",text_color=("red","yellow"))
    text64.configure(text="You will need to analyze data first before you can export.",text_color=("red","yellow"))
    export1.configure(state='disabled')
    export2.configure(state='disabled')
    export5.configure(state='disabled')
    export6.configure(state='disabled')
    imgframe2.grid_forget()
    editnames.grid_forget()
    showgraph.grid_forget()
    analyzeframe.rowconfigure(8,weight=0)
    for i in imgframe.grid_slaves(row=None,column=None):
        i.grid_remove()
    try:
        for i in imgframe2.grid_slaves(row=None,column=None):
            i.grid_remove()
    except:
        pass
    try:
        table1.grid_remove()
        table2.grid_remove()
        sct.grid_remove()
    except:
        pass
    try:
        text59.grid_remove()
    except:
        pass
    
    text44.configure(text="\n"*46)
    text44.grid(row=0,column=0,columnspan=3,padx=(10,0),pady=(10,0),sticky='w')

def loadjson():
    global loaddata,loadeddata
    analyze_reset()
    #Main code disable only for faster access
    loadfile.configure(fg_color='#3b8ed0',text='Load File',hover_color="#36719f")
    text13.configure(text="Select the excel file which EyePort creates or use the livedata.json.gz file from the SD Card.")
    loaddata = tk.filedialog.askopenfilename(title='Load Glass Data',initialdir='/',filetypes=[("Acceptable Files","*.xlsx *.json.gz")])
    if loaddata!='':
        if loaddata[-4:]=='xlsx':
            print("Excel File")
        elif loaddata[-2:]=='gz':
            print("JSON File")
            loaddata = extract(loaddata,overwritexl)
        loadeddata = True
        loadfile.configure(fg_color='green',text='Loaded',hover_color="#006400")
        if loadedvideo:
            analyze.configure(state="normal")
            text43.configure(text='Click \"Analyze Now\" to start analyzing. Analysis may take longer if Object Detection is used.',text_color=("black","white"))
        t="Using "+loaddata
        if len(t)>90:
            t=t.split('/')[-1]
            t="Using "+t
        text13.configure(text=t)
        value[15]=loaddata+"\n"
        writesettings()
    else:
        loadeddata = False
        analyze.configure(state="disabled")
        text43.configure(text="Please load both the Glass data and Video files to start analysis.",text_color=("red","yellow"))

def autoloadfiles():
    global loaddata,loadeddata,loadedvideo,loadvideo,value
    temp1=value[15][:-1]
    temp2=value[16][:-1]
    if rememberloadbool==False:
        text43.configure(text="Please load both the Glass data and Video files to start analysis.",text_color=("red","yellow"))
    if os.path.exists(temp1) and os.path.exists(temp2):
        pass
    else:
        temp1='Load1'
        temp2='Load2'
        text43.configure(text="Please load both the Glass data and Video files to start analysis.",text_color=("red","yellow"))
    if rememberloadbool==True and temp1!='Load1' and temp2!='Load2':
        loaddata = temp1
        loadvideo = temp2
        loadeddata = True
        loadedvideo = True
        analyze.configure(state="normal")
        loadfile.configure(fg_color='green',text='Auto Loaded',hover_color="#006400")
        loadfile1.configure(fg_color='green',text='Auto Loaded',hover_color="#006400")
        t1="Using "+loaddata
        if len(t1)>90:
            t1=t1.split('/')[-1]
            t1="Using "+t1
        t2="Using "+loadvideo
        if len(t2)>90:
            t2=t2.split('/')[-1]
            t2="Using "+t2
        text13.configure(text=t1)
        text41.configure(text=t2)
        text43.configure(text='Click \"Analyze Now\" to start analyzing. Analysis may take longer if Object Detection is used.',text_color=("black","white"))

def loadvid():
    global loadvideo,loadedvideo
    analyze_reset()
    #Main code disable only for faster access
    loadfile1.configure(fg_color='#3b8ed0',text='Load File',hover_color="#36719f")
    text41.configure(text="Select the video file which EyePort creates or use the fullstream.mp4 file from the SD Card.")
    loadvideo = tk.filedialog.askopenfilename(title='Load Video',initialdir='/',filetypes=[("Video Files","*.mp4 *.avi")])
    if loadvideo!='':
        if loadvideo[-3:]=='avi':
            print("AVI File")
        elif loadvideo[-3:]=='mp4':
            print("MP4 File")
        loadedvideo = True
        loadfile1.configure(fg_color='green',text='Loaded',hover_color="#006400")
        if loadeddata:
            analyze.configure(state="normal")
            text43.configure(text='Click \"Analyze Now\" to start analyzing. Analysis may take longer if Object Detection is used.',text_color=("black","white"))
        t="Using "+loadvideo
        if len(t)>90:
            t=t.split('/')[-1]
            t="Using "+t
        text41.configure(text=t)
        value[16]=loadvideo+"\n"
        writesettings()
    else:
        loadedvideo = False
        analyze.configure(state="disabled")
        text43.configure(text="Please load both the Glass data and Video files to start analysis.",text_color=("red","yellow"))

def uniqueduration():
    global notimeslooked,totduration
    notimeslooked=[0 for i in range(len(UAOIName))]
    totduration=[0 for i in range(len(UAOIName))]
    for i in range(len(UAOIName)):
        for j in range(len(AOIName)):
            if UAOIName[i]==AOIName[j]:
                notimeslooked[i]=notimeslooked[i]+1
                totduration[i]=totduration[i]+(EndSec[j]-StartSec[j])

def editAOI():
    root.bind("<Return>",saveAOI)
    editnames.configure(text="Save Changes",command=saveAOI)
    col=0
    row=2
    for i in range(len(UAOIName)):
        globals()['t%s' % i].grid_forget()
        globals()['t%s' % i] = CTkEntry(imgframe2,placeholder_text=UAOIName[i],
                               width=100,
                               height=30,
                               border_width=2,
                               corner_radius=5,
                               font=CTkFont(size=15),
                               justify=CENTER)
        if col==4:
            col=0
            row=row+2
        globals()['t%s' % i].grid(row=row,column=col,sticky='n',pady=(0,10)) 
        col=col+1

def saveAOI(a=''):
    global UAOIName,AOIName,pos,picarray
    root.unbind("<Return>")
    store=[]
    check=[]
    for i in range(len(UAOIName)):
        a=(globals()['t%s' % i].get())
        if a=='':
            store.append(UAOIName[i])
        else:
            store.append(a)
    if use_manual==0:
        flag=0
        for i in store:
            if i in check:
                tk.messagebox.showwarning("Failed to assign Unique Names","You cannot assign identical names to Unique Areas of Interest. Use Manual Mode to override this behaviour.")
                flag=1
                break
            else:
                check.append(i)
        if flag==1:
            editAOI()
            return 0
        for i in range(len(AOIName)):
            for j in range(len(UAOIName)):
                if AOIName[i]==UAOIName[j]:
                    AOIName[i]=store[j]
        UAOIName=store
    else:
        AOIName=store
        pos.clear()
        for i in range(len(store)):
            if store[i] not in check:
                check.append(store[i])
                pos.append(i)
        UAOIName=check
        editnames.configure(state='disabled')
        

    if use_manual==0:
        col=0
        row=2
        for i in range(len(UAOIName)):
            if col==4:
                col=0
                row=row+2
            globals()['t%s' % i].grid_forget()
            globals()['t%s' % i] = CTkLabel(imgframe2,text=UAOIName[i],font=CTkFont(size=15))
            globals()['t%s' % i].grid(row=row,column=col,sticky='n',pady=(0,10)) 
            col=col+1
    else:
        for i in imgframe2.grid_slaves(row=None,column=None):
            i.grid_remove()
        text45.grid(row=0,column=0,padx=(10,0),pady=10,sticky='w')
        ucounttext="Unique Area of Interests: "+str(len(UAOIName))
        text45.configure(text=ucounttext)

        col=0
        row=1
        for i in range(len(picarray)):
            if i in pos:
                img = Image.fromarray(picarray[i])
                imgsave.append(img)
                aimgtk = CTkImage(light_image=img,size=(int(1920*0.17),int(1080*0.17)))
                if col==4:
                    col=0
                    row=row+2
                e1 = CTkLabel(imgframe2,text='',image=aimgtk)
                e1.grid(row=row,column=col,sticky='nsew',padx=(10,0),pady=(0,5))
                col=col+1
        
        col=0
        row=1
        for i in range(len(UAOIName)):
            if col==4:
                col=0
                row=row+2
            globals()['t%s' % i] = CTkLabel(imgframe2,text=UAOIName[i],font=CTkFont(size=15))
            globals()['t%s' % i].grid(row=row+1,column=col,sticky='nsew',pady=(0,10))
            col=col+1

        uniqueduration()

    col=0
    row=2
    for i in range(len(AOIName)):
        if col==4:
            col=0
            row=row+2
        e2 = CTkLabel(imgframe,text=AOIName[i],font=CTkFont(size=15))
        e2.grid(row=row,column=col,sticky='nsew',pady=(0,10))    
        col=col+1
    editnames.configure(text="Edit Names",command=editAOI)
    showtables()

def analyze():
    global AOIName,UAOIName,StartSec,EndSec,GazeX,GazeY,color,size,unique_count,imgsave,pos,picarray,exportstatus
    imgsave=[]
    analyze_reset()
    if os.path.exists(loaddata)==False or os.path.exists(loadvideo)==False:
        tk.messagebox.showerror('Problem Loading Files','EyePort was unable to open the files. The files may have been moved or deleted. Please check the loaded files in file explorer.')
        return 0
    try:
        if loadvideo[-3:].lower()=='avi': #EyePort Custom Mode
            count,unique_count,picarray,answerarray,answer,pos,AOIName,UAOIName,StartSec,EndSec,GazeX,GazeY,color,size=analyzer(loaddata,loadvideo,asense,thit,useai,use_manual,0)
            print("Analyzing Eye FRAM Custom Files")
        else: #TOBII Proprietary
            count,unique_count,picarray,answerarray,answer,pos,AOIName,UAOIName,StartSec,EndSec,GazeX,GazeY,color,size=analyzer(loaddata,loadvideo,asense,thit,useai,use_manual,1)
            print("Analyzing TOBII Proprietary Files")
    except PermissionError:
        tk.messagebox.showerror('Permission Error','EyePort was unable to analyze the files because there was no permission to access them. Close any applications that may be using the files or try elevating EyePort as Administrator.')
        return 0
    except:
        tk.messagebox.showerror('Failed to Analyze','EyePort was unable to analyze the files. The files may be corrupted containing data in an incorrect format. There could also be a problem with the algorithm. Please try again with different files and if the issue persists, contact the developer.')
        return 0
    counttext="Area of Interests: "+str(count)
    ucounttext="Unique Area of Interests: "+str(unique_count)
    analyzeframe.rowconfigure(8,weight=1)
    text44.grid(row=0,column=0,padx=(10,0),pady=10,sticky='w')
    text44.configure(text=counttext)
    if useai in [1,2]:
        UAOIName.clear()
        store=[]
        for i in range(len(answer)):
            if i in pos:
                if answer[i] not in store:
                    store.append(answer[i])
                    UAOIName.append(answer[i]+' 1')
                else:
                    l=store.count(answer[i])
                    UAOIName.append(answer[i]+f' {l+1}')
        store.clear()
        for i in range(len(AOIName)):
            word = AOIName[i].split()
            store.append(UAOIName[int(word[1])-1])
        AOIName=store

    col=0
    row=1
    for i in range(len(picarray)):
        if useai in [1,2]:
            img = Image.fromarray(answerarray[i])
        else:
            img = Image.fromarray(picarray[i])
        aimgtk = CTkImage(light_image=img,size=(int(1920*0.17),int(1080*0.17)))
        if col==4:
            col=0
            row=row+2
        e1 = CTkLabel(imgframe,text='',image=aimgtk)
        e1.grid(row=row,column=col,sticky='nsew',padx=(10,0),pady=(0,5))
        e2 = CTkLabel(imgframe,text=AOIName[i],font=CTkFont(size=15))
        e2.grid(row=row+1,column=col,sticky='nsew',pady=(0,10))      
        col=col+1
    
    imgframe2.grid(row=8,column=0,columnspan=5,sticky='nsew',padx=20)
    text45.grid(row=0,column=0,padx=(10,0),pady=10,sticky='w')
    text45.configure(text=ucounttext)

    col=0
    row=1
    for i in range(len(picarray)):
        if i in pos:
            img = Image.fromarray(picarray[i])
            imgsave.append(img)
            aimgtk = CTkImage(light_image=img,size=(int(1920*0.17),int(1080*0.17)))
            if col==4:
                col=0
                row=row+2
            e1 = CTkLabel(imgframe2,text='',image=aimgtk)
            e1.grid(row=row,column=col,sticky='nsew',padx=(10,0),pady=(0,5))
            col=col+1
    
    col=0
    row=1
    for i in range(unique_count):
        if col==4:
            col=0
            row=row+2
        globals()['t%s' % i] = CTkLabel(imgframe2,text=UAOIName[i],font=CTkFont(size=15))
        globals()['t%s' % i].grid(row=row+1,column=col,sticky='nsew',pady=(0,10))
        col=col+1
            

    editnames.grid(row=10,column=0,columnspan=2,padx=20,pady=20,sticky='w')
    showgraph.grid(row=10,column=2,pady=20,sticky='w')
    if unique_count==0:
        editnames.configure(state='disabled')
        showgraph.configure(state='disabled')
    else:
        editnames.configure(state='normal')
        showgraph.configure(state='normal')
    uniqueduration()
    showtables()
    text56.configure(text="Click the \"Export CSV\" button to export a csv file from the analyzed glass data.",text_color=("black","white"))
    text58.configure(text="Click the \"Export XMFV\" button to also export a partial model of the scenario.",text_color=("black","white"))
    text62.configure(text="Click the \"Export XLSX\" button to export a xlsx file from the analyzed glass data.",text_color=("black","white"))
    text64.configure(text="Click the \"Export Images\" button to export images of the Areas of Interest.",text_color=("black","white"))
    export1.configure(state='normal')
    export2.configure(state='normal')
    export5.configure(state='normal')
    export6.configure(state='normal')
    exportstatus = 0
    root.state('zoomed')

def showtables():
    global table1,table2,sct
    table1 = ttk.Treeview(analyzeframe)
    table1.grid_forget()
    table1['columns'] = ("AOI","No","Duration")
    table1.column("#0",minwidth=50,width=50)
    table1.column("AOI",anchor=W,width=140,minwidth=140)
    table1.column("No",anchor=CENTER,width=120,minwidth=120)
    table1.column("Duration",anchor=CENTER,width=90,minwidth=90)
    table1.heading("#0",text="No",anchor=CENTER)
    table1.heading("AOI",text="Unique Area of Interest",anchor=W)
    table1.heading("No",text="No of times looked",anchor=CENTER)
    table1.heading("Duration",text="Total Duration",anchor=CENTER)

    id=1
    for i in range(len(UAOIName)):
        table1.insert(parent='',index='end',iid=id,text=id,values=(UAOIName[i],notimeslooked[i],f"{round(totduration[i],2)} s"))
        id=id+1
    table1.grid(row=11,column=1,padx=10,pady=(0,20),sticky='w')

    table2 = ttk.Treeview(analyzeframe)
    table2.grid_forget()
    table2['columns'] = ("AOI","Start","End","Duration","Type")
    table2.column("#0",minwidth=50,width=50)
    table2.column("AOI",anchor=W,width=140,minwidth=140)
    table2.column("Start",anchor=CENTER,width=90,minwidth=90)
    table2.column("End",anchor=CENTER,width=90,minwidth=90)
    table2.column("Duration",anchor=CENTER,width=90,minwidth=90)
    table2.column("Type",anchor=W,width=135,minwidth=135)
    table2.heading("#0",text="No",anchor=CENTER)
    table2.heading("AOI",text="Area of Interest",anchor=W)
    table2.heading("Start",text="Start Time",anchor=CENTER)
    table2.heading("End",text="End Time",anchor=CENTER)
    table2.heading("Duration",text="Duration",anchor=CENTER)
    table2.heading("Type",text="Description",anchor=W)

    id=1
    for i in range(len(AOIName)):
        if round(EndSec[i]-StartSec[i],2)<(thit/100)+1:
            desc='Short'
        elif round(EndSec[i]-StartSec[i],2)<(thit/100)+2:
            desc='Medium'
        elif round(EndSec[i]-StartSec[i],2)<(thit/100)+5:
            desc='Long'
        else:
            desc='Prolonged'
        table2.insert(parent='',index='end',iid=id,text=id,values=(AOIName[i],f"{round(StartSec[i],2)} s",f"{round(EndSec[i],2)} s",f"{round(EndSec[i]-StartSec[i],2)} s",desc))
        id=id+1
    table2.grid(row=11,column=0,padx=(20,0),pady=(0,20),sticky='w')

    figure = plt.Figure(figsize=(8,3.5), dpi=65)
    ax = figure.add_subplot(111)
    ax.scatter(GazeX,GazeY,s=size,c=color,alpha=0.5,cmap='Blues')
    scatter = FigureCanvasTkAgg(figure, analyzeframe)
    sct = scatter.get_tk_widget()
    sct.grid(row=11,column=2,sticky='nw')
    ax.set_xlabel('Gaze X 2D Coordinates')
    ax.set_ylabel('Gaze Y 2D Coordinates')

    if unique_count==0:
        text59.grid(row=12,column=0,sticky='nw')

def showgraphs():
    plt.ioff
    f = plt.figure()
    f.set_figwidth(15)
    f.set_figheight(8)
    plt.subplot(2,2,1)
    plt.scatter(GazeX,GazeY,s=size,c=color,alpha=0.5,cmap='Blues')
    plt.xlabel('Gaze X 2D Coordinates')
    plt.ylabel('Gaze Y 2D Coordinates')
    cbar = plt.colorbar()
    cbar.set_label('Fixation')

    plt.subplot(2,2,2)
    plt.bar(UAOIName,notimeslooked,width=0.3)
    plt.xlabel('Areas of Interest')
    plt.ylabel('No of times looked')

    plt.subplot(2,2,3)
    plt.plot(StartSec,AOIName,'o',color='Red')
    plt.ylabel('Areas of Interest')
    plt.xlabel('Time(s)')

    plt.subplot(2,2,4)
    plt.bar(UAOIName,totduration,width=0.3,color='Orange')
    plt.xlabel('Areas of Interest')
    plt.ylabel('Total Duration(s)')
    plt.show()

#Export Page Functions
def resizeexport(e):
    global exportresizebool
    if e.height>=310:
        exportresizebool = True
        imgtk18 = CTkImage(light_image=image21,dark_image=image22,size=(270,200))
        imgtk19 = CTkImage(light_image=image23,dark_image=image24,size=(228,200))
        imgtk20 = CTkImage(light_image=image25,dark_image=image26,size=(209,200))
    else:
        exportresizebool = False
        imgtk18 = CTkImage(light_image=image21,dark_image=image22,size=(202,150))
        imgtk19 = CTkImage(light_image=image23,dark_image=image24,size=(171,150))
        imgtk20 = CTkImage(light_image=image25,dark_image=image26,size=(125,120))
    exportclick.configure(image=imgtk20)
    exportsuccess.configure(image=imgtk18)
    exportfail.configure(image=imgtk19)
    exportsuccess.grid_forget()
    exportfail.grid_forget()
    export3.grid_forget()
    export4.grid_forget()
    if exportstatus==2:
        if exportresizebool:
            exportfail.grid(row=1,column=1,columnspan=2,sticky='nsew')
            export3.grid(row=2,column=1,sticky='se',pady=(25,0),padx=(0,10))
            export4.grid(row=2,column=2,sticky='sw',pady=(25,0),padx=(10,0))
            export3.configure(state='disabled')
            export4.configure(state='disabled')
        else:
            exportfail.grid(row=1,column=1,rowspan=2,sticky='nsew')
            export3.grid(row=1,column=2,sticky='s',pady=7,padx=(10,0))
            export4.grid(row=2,column=2,sticky='n',pady=7,padx=(10,0))
            export3.configure(state='disabled')
            export4.configure(state='disabled')
    elif exportstatus==1:
        if exportresizebool:
            exportsuccess.grid(row=1,column=1,columnspan=2,sticky='nsew')
            export3.grid(row=2,column=1,sticky='se',pady=(25,0),padx=(0,10))
            export4.grid(row=2,column=2,sticky='sw',pady=(25,0),padx=(10,0))
            export3.configure(state='normal')
            export4.configure(state='normal')
        else:
            exportsuccess.grid(row=1,column=1,rowspan=2,sticky='nsew')
            export3.grid(row=1,column=2,sticky='s',pady=7,padx=(10,0))
            export4.grid(row=2,column=2,sticky='n',pady=7,padx=(10,0))
            export3.configure(state='normal')
            export4.configure(state='normal')
    elif exportstatus==0:
        exportclick.grid(row=1,column=1,columnspan=2,sticky='nsew')

def exportsaver():
    global exportsavefolder
    export_reset()
    ask=tk.filedialog.askdirectory()
    if ask=="" and exportsavefolder=='Expsave':
        exportsavefolder=os.getcwd()
    elif ask=="" and exportsavefolder!="Expsave":
        pass
    else:
        exportsavefolder=ask
    text54.configure(text=f"Using {exportsavefolder}")
    exportsave.configure(text='Selected',fg_color='green',hover_color="#006400")
    value[19]=exportsavefolder+'\n'
    writesettings()

def exportcsv():
    global exportsavefolder,exportstatus
    export_reset()
    if exportsavefolder=='Expsave':
        exportsavefolder=os.getcwd()
        text54.configure(text=f"Using {exportsavefolder}")
        value[19]=exportsavefolder+'\n'
        writesettings()
        if askexport==0:
            tk.messagebox.showinfo("No Export Folder",f"You have not provided an export folder to export to.\nEyePort will save the files in\n{exportsavefolder}")
    
    c=1
    path=exportsavefolder+"/"+f'EyePort Scenario {c}.csv'
    while os.path.exists(path):
        c=c+1
        path=exportsavefolder+"/"+f'EyePort Scenario {c}.csv'
    if c!=1 and overexport==1:
        path=exportsavefolder+"/"+f'EyePort Scenario {c-1}.csv'
        d=c-1
    else:
        d=c

    if askexport==1:
        askpath=tk.filedialog.asksaveasfilename(initialdir=exportsavefolder,initialfile=f'EyePort Scenario {d}.csv',filetypes=[("CSV File","*.csv")])
        if askpath!='':
            if askpath[-4:]!='.csv':
                askpath=askpath+'.csv'
            path=askpath
    
    try:
        fcsv=open(path,'w',newline='')
        writer = csv.writer(fcsv)
        writer.writerow(['Time','ActiveFunction','ActiveFunctionOutput','DownstreamCoupledFunction','CoupledFunctionAspect','TimeTolerance'])
        
        for i in range(len(AOIName)):
            if i==len(AOIName)-1:
                writer.writerow([int(StartSec[i]),UAOIName.index(AOIName[i])+1,'Observing '+AOIName[i],0,'I'])
                writer.writerow([int(EndSec[i]),0,'Changing Focus or Saccading',0,'I'])
                break
            else:
                writer.writerow([int(StartSec[i]),UAOIName.index(AOIName[i])+1,'Observing '+AOIName[i],0,'I'])
                writer.writerow([int(EndSec[i]),0,'Changing Focus or Saccading',UAOIName.index(AOIName[i+1])+1,'I'])
        fcsv.close()
        exportstatus = 1
        exportsuccessful()
        print("Exported CSV File")
    except PermissionError:
        exportstatus = 2
        exportfailed()
        tk.messagebox.showerror('Permission Error','EyePort was unable to export the files because there was no permission to write them. Close any applications that may be using the files or try elevating EyePort as Administrator.')
        return 0
    except:
        exportstatus = 2
        exportfailed()
        tk.messagebox.showerror('Unknown Error','EyePort was unable to export the files. This may be due to a problem with the code. Please try again with different files and if the issue persists, contact the developer.')
        return 0

def exportxmfv():
    global exportsavefolder,exportstatus
    export_reset()
    if exportsavefolder=='Expsave':
        exportsavefolder=os.getcwd()
        text54.configure(text=f"Using {exportsavefolder}")
        value[19]=exportsavefolder+'\n'
        writesettings()
        if askexport==0:
            tk.messagebox.showinfo("No Export Folder",f"You have not provided an export folder to export to.\nEyePort will save the files in\n{exportsavefolder}")
    
    try:
        creator(UAOIName, exportsavefolder, overexport, askexport)
        exportstatus = 1
        exportsuccessful()
        print("Exported XMFV File")
    except PermissionError:
        exportstatus = 2
        exportfailed()
        tk.messagebox.showerror('Permission Error','EyePort was unable to export the files because there was no permission to write them. Close any applications that may be using the files or try elevating EyePort as Administrator.')
        return 0
    except:
        exportstatus = 2
        exportfailed()
        tk.messagebox.showerror('Unknown Error','EyePort was unable to export the files. This may be due to a problem with the code. Please try again with different files and if the issue persists, contact the developer.')
        return 0

def exportxlsx():
    global exportsavefolder,exportstatus
    export_reset()
    if exportsavefolder=='Expsave':
        exportsavefolder=os.getcwd()
        text54.configure(text=f"Using {exportsavefolder}")
        value[19]=exportsavefolder+'\n'
        writesettings()
        if askexport==0:
            tk.messagebox.showinfo("No Export Folder",f"You have not provided an export folder to export to.\nEyePort will save the files in\n{exportsavefolder}")
    
    c=1
    path=exportsavefolder+"/"+f'EyePort Data Export {c}.xlsx'
    while os.path.exists(path):
        c=c+1
        path=exportsavefolder+"/"+f'EyePort Data Export {c}.xlsx'
    if c!=1 and overexport==1:
        path=exportsavefolder+"/"+f'EyePort Data Export {c-1}.xlsx'
        d=c-1
    else:
        d=c

    if askexport==1:
        askpath=tk.filedialog.asksaveasfilename(initialdir=exportsavefolder,initialfile=f'EyePort Data Export {d}.xlsx',filetypes=[("Excel File","*.xlsx")])
        if askpath!='':
            if askpath[-5:]!='.xlsx':
                askpath=askpath+'.xlsx'
            path=askpath
    
    try:
        wb = xls.Workbook()
        ws = wb.active
        ws.title = "Data"
        c1 = ws.cell(row=1, column=1)
        c1.value = "No"
        c2 = ws.cell(row=1, column=2)
        c2.value = "Area of Interest"
        c3 = ws.cell(row=1, column=3)
        c3.value = "Start Time"
        c4 = ws.cell(row=1, column=4)
        c4.value = "End Time"
        c5 = ws.cell(row=1, column=5)
        c5.value = "Duration"
        c6 = ws.cell(row=1, column=6)
        c6.value = "Description"
        c7 = ws.cell(row=1, column=7)
        c7.value = "Gaze Point 2D X"
        c8 = ws.cell(row=1, column=8)
        c8.value = "Gaze Point 2D Y"

        for i in range(len(AOIName)):
            if round(EndSec[i]-StartSec[i],2)<(thit/100)+1:
                desc='Short'
            elif round(EndSec[i]-StartSec[i],2)<(thit/100)+2:
                desc='Medium'
            elif round(EndSec[i]-StartSec[i],2)<(thit/100)+5:
                desc='Long'
            else:
                desc='Prolonged'
            cell = ws.cell(row=i+2,column=1)
            cell.value = i+1
            cell = ws.cell(row=i+2,column=2)
            cell.value = AOIName[i]
            cell = ws.cell(row=i+2,column=3)
            cell.value = round(StartSec[i],2)
            cell = ws.cell(row=i+2,column=4)
            cell.value = round(EndSec[i],2)
            cell = ws.cell(row=i+2,column=5)
            cell.value = round(EndSec[i]-StartSec[i],2)
            cell = ws.cell(row=i+2,column=6)
            cell.value = desc
            cell = ws.cell(row=i+2,column=7)
            cell.value = GazeX[i]
            cell = ws.cell(row=i+2,column=8)
            cell.value = GazeY[i]

        wb.save(path)
        exportstatus = 1
        exportsuccessful()
        print("Exported XLSX File")
    except PermissionError:
        exportstatus = 2
        exportfailed()
        tk.messagebox.showerror('Permission Error','EyePort was unable to export the files because there was no permission to write them. Close any applications that may be using the files or try elevating EyePort as Administrator.')
        return 0
    except:
        exportstatus = 2
        exportfailed()
        tk.messagebox.showerror('Unknown Error','EyePort was unable to export the files. This may be due to a problem with the code. Please try again with different files and if the issue persists, contact the developer.')
        return 0

def exportimg():
    global exportsavefolder,exportstatus
    export_reset()
    if exportsavefolder=='Expsave':
        exportsavefolder=os.getcwd()
        text54.configure(text=f"Using {exportsavefolder}")
        value[19]=exportsavefolder+'\n'
        writesettings()
        if askexport==0:
            tk.messagebox.showinfo("No Export Folder",f"You have not provided an export folder to export to.\nEyePort will save the files in\n{exportsavefolder}")
    
    try:
        for i in range(len(UAOIName)):
            imgsave[i].save(exportsavefolder+"/"+f"{UAOIName[i]}"+".png")
        exportstatus = 1
        exportsuccessful()
        print("Exported Images")
    except PermissionError:
        exportstatus = 2
        exportfailed()
        tk.messagebox.showerror('Permission Error','EyePort was unable to export the files because there was no permission to write them. Close any applications that may be using the files or try elevating EyePort as Administrator.')
        return 0
    except:
        exportstatus = 2
        exportfailed()
        tk.messagebox.showerror('Unknown Error','EyePort was unable to export the files. This may be due to a problem with the code. Please try again with different files and if the issue persists, contact the developer.')
        return 0

def exportsuccessful():
    exportsuccess.grid_forget()
    exportfail.grid_forget()
    export3.grid_forget()
    export4.grid_forget()
    if exportresizebool:
        exportsuccess.grid(row=1,column=1,columnspan=2,sticky='nsew')
        export3.grid(row=2,column=1,sticky='se',pady=(25,0),padx=(0,10))
        export4.grid(row=2,column=2,sticky='sw',pady=(25,0),padx=(10,0))
        export3.configure(state='normal')
        export4.configure(state='normal')
    else:
        exportsuccess.grid(row=1,column=1,rowspan=2,sticky='nsew')
        export3.grid(row=1,column=2,sticky='s',pady=7,padx=(10,0))
        export4.grid(row=2,column=2,sticky='n',pady=7,padx=(10,0))
        export3.configure(state='normal')
        export4.configure(state='normal')

def exportfailed():
    exportsuccess.grid_forget()
    exportfail.grid_forget()
    export3.grid_forget()
    export4.grid_forget()
    if exportresizebool:
        exportfail.grid(row=1,column=1,columnspan=2,sticky='nsew')
        export3.grid(row=2,column=1,sticky='se',pady=(25,0),padx=(0,10))
        export4.grid(row=2,column=2,sticky='sw',pady=(25,0),padx=(10,0))
        export3.configure(state='disabled')
        export4.configure(state='disabled')
    else:
        exportfail.grid(row=1,column=1,rowspan=2,sticky='nsew')
        export3.grid(row=1,column=2,sticky='s',pady=7,padx=(10,0))
        export4.grid(row=2,column=2,sticky='n',pady=7,padx=(10,0))
        export3.configure(state='disabled')
        export4.configure(state='disabled')

def export_reset():
    global exportstatus
    exportstatus = 0
    exportclick.grid_forget()
    exportsuccess.grid_forget()
    exportfail.grid_forget()
    export3.grid_forget()
    export4.grid_forget()

def openexplorer():
    os.system(f'start "" "{exportsavefolder}"')

def dynafram():
    appnames = AppOpener.give_appnames()
    if 'dynafram' in appnames:
        AppOpener.open('dynaFRAM')
    else:
        ans=tk.messagebox.askyesno("DynaFRAM not installed","EyePort has detected that DynaFRAM is not installed on your computer. Would you like EyePort to open the website for you to install it?")
        if ans:
            webbrowser.open("https://www.engr.mun.ca/~d.smith/dynafram.html")

#Scroll MouseWheel
def scroll(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def scroll2(event):
    canvas2.yview_scroll(int(-1*(event.delta/120)), "units")

#Navigation and Settings Functions
def fullscreen():
    if fullscreenmode==1:
        root.state('zoomed')
    else:
        root.state('normal')

def resize(event):
    if event.width>1180:
        text46.grid(row=1,column=2,columnspan=2,sticky='nw',padx=(60,0),pady=(5,0))
        text47.grid(row=2,column=2,columnspan=2,sticky='nw',padx=(70,0),pady=(10,0))
        text48.grid(row=3,column=2,columnspan=2,sticky='nw',padx=(70,0),pady=(2,0))
        scaling_optionmenu2.grid(row=4,column=2,columnspan=2,sticky='nw',padx=(70,0),pady=5)
        text50.grid(row=5,column=2,columnspan=2,sticky='nw',padx=(70,0),pady=(10,0)) #Fixation
        text51.grid(row=6,column=2,columnspan=2,sticky='nw',padx=(70,0),pady=(2,0)) #Description
        text52.grid(row=7,column=3,sticky='nw',padx=(15,0)) #ms Text
        slider_2.grid(row=7,column=2,columnspan=2,sticky='nw',padx=(70,0),pady=(5,10)) #Slider
        text65.grid(row=8,column=2,columnspan=2,sticky='nw',padx=(70,0),pady=(2,0)) #Choose
        text66.grid(row=9,column=2,columnspan=2,sticky='nw',padx=(70,0))#Theme
        frame6.grid(row=10,column=2,rowspan=2,columnspan=2,sticky='nw',padx=(70,0)) #Object Detection
        radio_button_8.grid(row=0,column=0,sticky='w',padx=3,pady=5)
        radio_button_9.grid(row=1,column=0,sticky='w',padx=3,pady=5)
        radio_button_10.grid(row=2,column=0,sticky='w',padx=(3,20),pady=5)
        check_7.grid(row=12,column=2,columnspan=2,sticky='nw',padx=(70,0)) #Use Manual
        #check_1.grid(row=9,column=2,sticky='nw',padx=(70,0))
        check_2.grid(row=13,column=2,columnspan=2,sticky='nw',padx=(70,0))
        check_4.grid(row=14,column=2,columnspan=2,sticky='nw',padx=(70,0))
        text60.grid(row=15,column=2,columnspan=2,rowspan=2,sticky='nw',padx=(60,0)) #Export Settings
        check_5.grid(row=17,column=2,columnspan=2,sticky='nw',padx=(70,0)) #Overwrite Old Exports
        check_6.grid(row=18,column=2,columnspan=2,sticky='nw',padx=(70,0)) #Ask Export
        reset.grid(row=19,column=2,columnspan=2,rowspan=2,sticky='nw',padx=(70,0)) #Reset Button
        text34.grid(row=29,column=0,sticky='nw',padx=(30,0),pady=(5,0)) #Spacer
    else:
        check_5.grid_forget()
        check_6.grid_forget()
        check_7.grid_forget()
        reset.grid_forget()
        text34.grid_forget()
        text60.grid_forget()
        text46.grid(row=29,column=0,columnspan=2,sticky='nw',padx=(20,0),pady=(25,0)) #Analyze Settings
        text47.grid(row=30,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(10,0)) #Detection
        text48.grid(row=31,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,0)) #Description
        scaling_optionmenu2.grid(row=32,column=0,columnspan=2,sticky='w',padx=(30,0),pady=5) #Sensitivity ComboBox
        text50.grid(row=33,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(10,0)) #Fixation
        text51.grid(row=34,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,0)) #Description
        text52.grid(row=35,column=0,columnspan=2,sticky='nw',padx=(35,0)) #ms Text
        slider_2.grid(row=36,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,10)) #Slider
        text65.grid(row=37,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,0)) #Choose
        text66.grid(row=38,column=0,columnspan=2,sticky='nw',padx=(30,0))#Theme
        frame6.grid(row=39,column=0,rowspan=3,columnspan=2,sticky='w',padx=(30,0),pady=2) #Object Detection
        radio_button_8.grid(row=0,column=0,sticky='w',padx=3,pady=5)
        radio_button_9.grid(row=1,column=0,sticky='w',padx=3,pady=5)
        radio_button_10.grid(row=2,column=0,sticky='w',padx=(3,20),pady=5)
        check_7.grid(row=42,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(20,0)) #Use Manual
        #check_1.grid(row=37,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(10,0)) #Check Object Detection
        check_2.grid(row=43,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(10,0)) #Check Remember Load
        check_4.grid(row=44,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(10,0)) #Overwrite Old Excel Files
        text60.grid(row=45,column=0,columnspan=2,sticky='nw',padx=(20,0),pady=(25,0)) #Export Settings
        check_5.grid(row=46,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(10,0)) #Overwrite Old Exports
        check_6.grid(row=47,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(10,0)) #Ask Export
        reset.grid(row=48,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(20)) #Reset Button

def recordsettings():
    text26.configure(text="You cannot change this settings while a recording is ongoing.",text_color=("red","yellow"))
    radio_button_4.configure(state='disabled')
    locationsave.configure(state="disabled")
    radio_button_5.configure(state='disabled')

def recordstopsettings():
    locationsave.configure(state="normal")
    text26.configure(text="Choose how you would like the recordings to be saved.",text_color=("black","white"))
    radio_button_4.configure(state='normal')
    radio_button_5.configure(state='normal')

def connectedsettings():
    switch_1.configure(state='disabled')
    radio_button_6.configure(state='disabled')
    radio_button_7.configure(state='disabled')
    wipentry.configure(state='disabled')
    eipentry.configure(state='disabled')
    resip.configure(state='disabled')
    text27.configure(text="You cannot change this setting while the glasses are connected.",text_color=("red","yellow"))
    text29.configure(text="You cannot change this setting while the glasses are connected.",text_color=("red","yellow"))

def disconnectedsettings():
    switch_1.configure(state='normal')
    radio_button_6.configure(state='normal')
    radio_button_7.configure(state='normal')
    wipentry.configure(state='normal')
    eipentry.configure(state='normal')
    resip.configure(state='normal')
    text27.configure(text="Choose how you would be connecting the glasses to EyePort.",text_color=("black","white"))
    text29.configure(text="It is recommended that you leave these settings alone unless you are absolutely sure about the changes.",text_color=("black","white"))

def destroyer():
    if connected:
        ans = tk.messagebox.askyesno("Glasses still connected","The TOBII Glasses are still connected to EyePort. It is recommended that you disconnect them before closing the program. Are you sure you still want to quit EyePort?")
    else:
        ans = tk.messagebox.askyesno("Quit Program Confirmation","Are you sure you want to quit EyePort?")
    if ans:
        try:
            plt.close("all")
        except:
            pass
        image1.close()
        image2.close()
        image3.close()
        image4.close()
        image5.close()
        image6.close()
        image7.close()
        image8.close()
        image9.close()
        image10.close()
        image11.close()
        image12.close()
        image13.close()
        image14.close()
        image15.close()
        image16.close()
        image17.close()
        image18.close()
        image19.close()
        image20.close()
        image21.close()
        image22.close()
        image23.close()
        image24.close()
        image25.close()
        image26.close()
        image27.close()
        image28.close()
        image29.close()
        image30.close()
        image31.close()
        image32.close()
        image33.close()
        image34.close()
        image35.close()
        image36.close()
        image37.close()
        image38.close()
        image39.close()
        image40.close()
        image41.close()
        root.destroy()

def checklasttoggle():
    global previewenabled
    switch_1.configure(state='normal')
    if int(value[7][:-1])==1:
        switch_1.select()
        previewenabled = True
    else:
        switch_1.deselect()
        previewenabled = False

def previewtoggle():
    global previewenabled
    status = switch_1.get()
    if status == 1:
        previewenabled = True
    else:
        previewenabled = False
    value[7]=str(status)+"\n"
    writesettings()

def updatetheme():
    global settingsframe
    chk=theme_var.get()
    if chk==0:
        set_appearance_mode("Light")
        value[2]="Light\n"
    elif chk==1:
        set_appearance_mode("Dark")
        value[2]="Dark\n"
    else:
        set_appearance_mode("System")
        value[2]="System\n"
    writesettings()

def updaterecmode():
    global recordmode
    status = recmode_var.get()
    if status==1:
        recordmode = 1
        value[8] = "Tobii Proprietary\n"
    else:
        recordmode = 0
        value[8] = "EyePort Custom\n"
    writesettings()

def updateconmode():
    global connection_type,previewenabled
    conmode = conmode_var.get()
    if conmode==0:
        value[4]="Wi-Fi\n"
        connection_type="Wi-Fi"
        contip.configure(image=imgtk25)
        checklasttoggle()
    else:
        previewenabled = False
        switch_1.deselect()
        switch_1.configure(state='disabled')
        value[4]="Ethernet\n"
        contip.configure(image=imgtk24)
        connection_type="Ethernet"
    writesettings()

def updatescale(new_scaling: str):
    value[3]=new_scaling.replace("%","")+"\n"
    if int(value[3])<101:
        root.minsize(1058,620)
        root.geometry("1058x620+450+200")
    elif int(value[3])==110:
        root.minsize(1230,720)
        root.geometry("1230x720+350+150")
    elif int(value[3])==120:
        root.minsize(1315,770)
        root.geometry("1315x770+250+100")
        
    new_scaling_float = int(new_scaling.replace("%","")) / 100
    set_widget_scaling(new_scaling_float)
    writesettings()

def updatesync(a):
    global sync,gp
    gp.clear()
    text36.configure(text=str(int(a))+" ms")
    sync = int(a/10)
    value[9] = str(int(a))+"\n"
    writesettings()

def updateasense(a: str):
    global asense
    if a=='Extremely Low':
        asense=0.5
    elif a=='Very Low':
        asense=0.35
    elif a=='Low':
        asense=0.2
    elif a=='Normal':
        asense=0.1
    elif a=='High':
        asense=0.05
    else:
        asense=0.01
    value[12]=a+"\n"
    writesettings()

def updateuseai():
    global useai
    useai = useai_var.get()
    value[13]=str(useai)+"\n"
    writesettings()

def updatetimehit(a):
    global thit
    thit = a
    if thit%50==0:
        text52.configure(text=str(thit/100)+'0 s')
    else:
        text52.configure(text=str(thit/100)+' s')
    value[17] = str(int(a))+"\n"
    writesettings()

def rememberload():
    global rememberloadbool
    status = check_2.get()
    if status==1:
        rememberloadbool=True
    else:
        rememberloadbool=False
    value[14]=str(status)+"\n"
    writesettings()

def overwritexlsx():
    global overwritexl
    overwritexl=check_4.get()
    value[20]=str(overwritexl)+"\n"
    writesettings()

def overexporter():
    global overexport
    overexport=check_5.get()
    value[21]=str(overexport)+"\n"
    writesettings()

def askexporter():
    global askexport
    askexport=check_6.get()
    value[22]=str(askexport)+"\n"
    writesettings()

def usemanual():
    global use_manual
    use_manual=check_7.get()
    value[23]=str(use_manual)+"\n"
    writesettings()

def usefullscreen():
    global fullscreenmode
    fullscreenmode = check_3.get()
    value[18]=str(fullscreenmode)+"\n"
    writesettings()

def restoreip():
    w=tk.StringVar(value=default_wip)
    e=tk.StringVar(value=default_eip)
    wipentry.configure(textvariable=w)
    eipentry.configure(textvariable=e)
    value[5]=default_wip+"\n"
    value[6]=default_eip+"\n"
    writesettings()

#Welcome Page
def showagain():
    val = showagain.get()
    value[10]=str(val)+'\n'
    writesettings()

#User Manual
def showusermanual():
    path = ".\EyePort User Manual.pdf"
    if os.path.exists(path):
        subprocess.Popen([path], shell=True)
    else:
        tk.messagebox.showerror("Problem Opening User Manual","EyePort was not able to find the User Manual. The file may have been moved or deleted.")        

#Page Loading
def analyzepage():
    usermanual2.pack_forget()
    usermanual2.pack(side=tk.BOTTOM,pady=10,padx=20)
    videoframe.unbind('<Configure>')
    expframe.unbind('<Configure>')
    canvas2.bind_all("<MouseWheel>", scroll2)
    recordframe.pack_forget()
    exportframe.pack_forget()
    container.pack_forget()
    welcomeframe.destroy()
    container2.pack(fill=tk.BOTH,side=tk.LEFT,expand=True)
    canvas2.pack(side="left", fill="both", expand=True)
    scrollbar2.pack(side="right", fill="y")
    analyzeframe.columnconfigure(2,weight=1)
    analyzeframe.rowconfigure(7,weight=1)
    text2.grid(row=0,column=0,sticky='nw',padx=(20,0),pady=12)
    
    text12.grid(row=1,column=0,columnspan=2,sticky='w',padx=(20,0),pady=(5,0))
    text13.grid(row=2,column=0,columnspan=2,sticky='w',padx=(30,0))
    loadfile.grid(row=1,column=2,columnspan=3,rowspan=2,padx=(0,20),pady=(5,0),sticky='e')
    
    text40.grid(row=3,column=0,columnspan=2,sticky='w',padx=(20,0),pady=(5,0))
    text41.grid(row=4,column=0,columnspan=2,sticky='w',padx=(30,0))
    loadfile1.grid(row=3,column=2,columnspan=3,rowspan=2,padx=(0,20),pady=(5,0),sticky='e')

    text42.grid(row=5,column=0,columnspan=2,sticky='w',padx=(20,0),pady=(5,0))
    text43.grid(row=6,column=0,columnspan=2,sticky='w',padx=(30,0))
    analyze.grid(row=5,column=2,columnspan=3,rowspan=2,padx=(0,20),pady=(5,0),sticky='e')

    imgframe.grid(row=7,column=0,columnspan=5,sticky='nsew',padx=20,pady=20)
    text44.grid(row=0,column=0,columnspan=3,padx=(10,0),pady=10,sticky='w')

def exportpage():
    usermanual2.pack_forget()
    usermanual2.pack(side=tk.BOTTOM,pady=10,padx=20)
    videoframe.unbind('<Configure>')
    expframe.bind('<Configure>',resizeexport)
    expframe.rowconfigure((0,3),weight=1)
    expframe.columnconfigure((0,3),weight=1)
    if exportsavefolder!='Expsave':
        text54.configure(text=f"Using {exportsavefolder}")
        exportsave.configure(text='Auto Selected',fg_color='Green',hover_color="#006400")
    recordframe.pack_forget()
    container2.pack_forget()
    container.pack_forget()
    welcomeframe.destroy()
    exportframe.pack(fill=tk.BOTH,side=tk.LEFT,expand=True)
    exportframe.columnconfigure(0,weight=3)
    exportframe.columnconfigure(1,weight=1)
    exportframe.rowconfigure(11,weight=1)
    text4.grid(row=0,column=0,sticky='nw',padx=(20,0),pady=12)

    text53.grid(row=1,column=0,sticky='w',padx=(20,0),pady=(5,0))
    text54.grid(row=2,column=0,sticky='w',padx=(30,0))
    exportsave.grid(row=1,column=1,rowspan=2,padx=(0,20),pady=(5,0),sticky='e')
    
    text55.grid(row=3,column=0,sticky='w',padx=(20,0),pady=(5,0))
    text56.grid(row=4,column=0,sticky='w',padx=(30,0))
    export1.grid(row=3,column=1,rowspan=2,padx=(0,20),pady=(5,0),sticky='e')

    text57.grid(row=5,column=0,sticky='w',padx=(20,0),pady=(5,0))
    text58.grid(row=6,column=0,sticky='w',padx=(30,0))
    export2.grid(row=5,column=1,rowspan=2,padx=(0,20),pady=(5,0),sticky='e')

    text61.grid(row=7,column=0,sticky='w',padx=(20,0),pady=(5,0))
    text62.grid(row=8,column=0,sticky='w',padx=(30,0))
    export5.grid(row=7,column=1,rowspan=2,padx=(0,20),pady=(5,0),sticky='e')

    text63.grid(row=9,column=0,sticky='w',padx=(20,0),pady=(5,0))
    text64.grid(row=10,column=0,sticky='w',padx=(30,0))
    export6.grid(row=9,column=1,rowspan=2,padx=(0,20),pady=(5,0),sticky='e')

    expframe.grid(row=11,column=0,columnspan=2,sticky='nsew',padx=20,pady=20)

def recordpage():
    usermanual2.pack_forget()
    usermanual2.pack(side=tk.BOTTOM,pady=10,padx=20)
    videoframe.bind('<Configure>',resizerecord)
    expframe.unbind('<Configure>')
    container2.pack_forget()
    exportframe.pack_forget()
    container.pack_forget()
    welcomeframe.destroy()
    recordframe.pack(fill=tk.BOTH,side=tk.LEFT,expand=True)
    recordframe.columnconfigure(0,weight=3)
    recordframe.columnconfigure(1,weight=1)
    recordframe.rowconfigure(7,weight=4)
    text3.grid(row=0,column=0,sticky='nw',padx=(20,0),pady=12)
    
    text14.grid(row=1,column=0,sticky='w',padx=(20,0),pady=(5,0))
    text15.grid(row=2,column=0,sticky='w',padx=(30,0))
    connectbutton.grid(row=1,column=1,rowspan=2,padx=(0,40),pady=(5,0),sticky='e')
    
    text16.grid(row=3,column=0,sticky='w',padx=(20,0),pady=(5,0))
    text17.grid(row=4,column=0,sticky='w',padx=(30,0))
    calibratebutton.grid(row=3,column=1,rowspan=2,padx=(0,40),pady=(5,0),sticky='e')
    
    text18.grid(row=5,column=0,sticky='w',padx=(20,0),pady=(5,0))
    text19.grid(row=6,column=0,sticky='w',padx=(30,0))
    recordbutton.grid(row=5,column=1,rowspan=2,padx=(0,40),pady=(5,0),sticky='e')
    videoframe.columnconfigure(0,weight=1)
    videoframe.rowconfigure(2,weight=1)
    videoframe.grid(row=7,column=0,columnspan=2,sticky='nsew',padx=20,pady=20)
    text20.grid(row=0,column=0,padx=(20,0),pady=(10,0),sticky='w')
    if connected:
        if previewenabled:
            videolabel.grid(row=1,column=0,rowspan=4,padx=20,pady=(10,20),sticky='nw')
        else:
            if connection_type=='Wi-Fi':
                previewnotavailfun()
            else:
                ethernetpreviewfun()
    else:
        connectpreviewfun()
    locationsave.grid(row=3,column=1,columnspan=4,padx=20,sticky='e')
    disconnectbutton.grid(row=4,column=1,columnspan=4,padx=20,pady=(10,20),sticky='e')

    if connection_type=='Wi-Fi':
        connectmode.configure(image=imgtk29)
    else:
        connectmode.configure(image=imgtk28)
    calibforget()

    #calibfail.grid(row=1,column=1,padx=(0,45),sticky='ne') #For Testing only
    #calibsuccess.grid(row=1,column=1,padx=(0,50),sticky='ne')
    #calibsuccess.after(3000,calibsuccess.grid_forget)

def settingspage():
    usermanual2.pack_forget()
    usermanual2.pack(side=tk.BOTTOM,pady=10,padx=20)
    videoframe.unbind('<Configure>')
    expframe.unbind('<Configure>')
    canvas.bind_all("<MouseWheel>", scroll)
    container2.pack_forget()
    exportframe.pack_forget()
    recordframe.pack_forget()
    welcomeframe.destroy()
    container.pack(fill=tk.BOTH,side=tk.LEFT,expand=True)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    text5.grid(row=0,column=0,columnspan=2,sticky='nw',padx=(20,0),pady=12) #Settings
    text6.grid(row=1,column=0,columnspan=2,sticky='nw',padx=(20,0),pady=(5,0)) #General Appearance
    text11.grid(row=2,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,0)) #Choose
    text7.grid(row=3,column=0,columnspan=2,sticky='nw',padx=(30,0))#Theme
    frame2.grid(row=4,column=0,rowspan=3,columnspan=2,sticky='w',padx=(30,0),pady=2) #Frame
    radio_button_1.pack(side=tk.TOP,ipadx=3,ipady=3,padx=3,pady=3)
    radio_button_2.pack(side=tk.TOP,ipadx=3,ipady=3,padx=3,pady=3)
    radio_button_3.pack(side=tk.TOP,ipadx=3,ipady=3,padx=3,pady=3)
    text8.grid(row=7,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(5,0)) #UI
    scaling_optionmenu.grid(row=8,column=0,columnspan=2,sticky='w',padx=(30,0),pady=5) #ComboBox
    check_3.grid(row=9,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(15,0))
    text24.grid(row=10,column=0,columnspan=2,sticky='nw',padx=(20,0),pady=(25,0)) #Connection
    text25.grid(row=11,column=0,columnspan=2,sticky='sw',padx=(30,0),pady=(2,0)) #Type
    text27.grid(row=12,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,0)) #Choose
    frame4.grid(row=13,column=0,rowspan=2,columnspan=2,sticky='w',padx=(30,0),pady=2) #Frame
    radio_button_6.pack(side=tk.TOP,ipadx=3,ipady=3,padx=3,pady=3)
    radio_button_7.pack(side=tk.TOP,ipadx=3,ipady=3,padx=3,pady=3)
    if connection_type=='Wi-Fi':
        contip.configure(image=imgtk25)
    else:
        contip.configure(image=imgtk24)
    contip.grid(row=13,column=1,rowspan=2,sticky='w') #Picture
    #text33.grid(row=14,column=0,sticky='w',padx=(30,0),pady=(2,0)) #Note
    text28.grid(row=15,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(5,0)) #IP Settings
    text29.grid(row=16,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,0)) #Recommend
    frame5.grid(row=17,column=0,columnspan=2,rowspan=2,sticky='nw',padx=(30,0),pady=2) #Frame
    text31.grid(row=0,column=0,sticky='w',padx=(30,0),pady=(2,0)) #Wifi
    text32.grid(row=1,column=0,sticky='w',padx=(30,0),pady=(2,0)) #Ethernet
    wipentry.grid(row=0,column=1,sticky='w',padx=(10,0),pady=5) #Entry1
    eipentry.grid(row=1,column=1,sticky='w',padx=(10,0),pady=5) #Entry2
    resip.grid(row=0,column=2,rowspan=2,sticky='nsew',padx=20,pady=20) #Restore
    text35.grid(row=19,column=0,columnspan=2,sticky='w',padx=(30,0),pady=(2,20))
    text9.grid(row=20,column=0,columnspan=2,sticky='nw',padx=(20,0)) #Recording
    switch_1.grid(row=21,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=5) #Switch
    text10.grid(row=22,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(5,0)) #Mode
    text26.grid(row=23,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,0)) #Choose
    frame3.grid(row=24,column=0,columnspan=2,sticky='w',padx=(30,0),pady=2) #Frame
    radio_button_4.pack(side=tk.TOP,padx=3,pady=3,ipadx=10,ipady=3,anchor='w')
    radio_button_5.pack(side=tk.TOP,padx=3,pady=3,ipadx=10,ipady=3,anchor='w')
    text23.grid(row=25,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(10,0)) #Gaze
    text30.grid(row=26,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,0)) #Description
    text36.grid(row=27,column=0,columnspan=2,sticky='nw',padx=(35,0)) #ms Text
    slider_1.grid(row=28,column=0,columnspan=2,sticky='nw',padx=(30,0),pady=(2,0)) #Slider
    
def welcomepage():
    welcomeframe.pack(fill=tk.BOTH,side=tk.LEFT,expand=True)
    welcomeframe.columnconfigure((0,1),weight=1)
    welcomeframe.rowconfigure((0,6),weight=1)
    text37.grid(row=1,column=0,columnspan=2,sticky='nsew')
    text38.grid(row=2,column=0,columnspan=2,sticky='n')
    text39.grid(row=3,column=0,columnspan=2,sticky='n')
    gorecbutton.grid(row=4,column=0,pady=(20,0),padx=5,sticky='e')
    usermanual.grid(row=4,column=1,pady=(20,0),padx=5,sticky='w')
    showagain.grid(row=5,column=0,columnspan=2,pady=(20,50),sticky='n')

#Getting settings
if not os.path.exists("Settings.txt"):
    createsettings()

#For other functions to write to the settings file
def writesettings():
    f=open("Settings.txt","w")
    f.writelines(value)
    f.close()

#Normal Reset from app
def resetsettings2():
    global previewenabled,settings,recordmode,sync,fullscreenmode
    settings=[]
    ans=tk.messagebox.askyesno("Settings Reset","Are you sure you want to reset all settings?\nEyePort will apply the Default Settings.")
    if ans:
        settings=[]
        #set_appearance_mode("Light")
        #set_widget_scaling(1.0)
        radio_button_1.select()
        radio_button_6.select()
        radio_button_4.select()
        scaling_optionmenu.set("100%")
        text36.configure(text='100ms')
        slider_1.set(100)
        slider_2.set(200)
        text52.configure(text='2.00 s')
        switch_1.configure(state='normal')
        switch_1.select()
        radio_button_9.select()
        check_2.select()
        check_3.deselect()
        check_4.deselect()
        check_5.deselect()
        check_6.deselect()
        check_7.deselect()
        fullscreenmode = False
        scaling_optionmenu2.set("Normal")
        previewenabled = True
        recordmode = 0
        sync=20
        restoreip()
        text54.configure(text="Choose where you would like to export your analyzed files.")
        exportsave.configure(text='Export Folder',fg_color="#3b8ed0",hover_color="#36719f")
        value=[]
        createsettings()
        applysettings()

#In case settings files was corrupted
def resetsettings():
    global settings
    settings=[]
    tk.messagebox.showerror("Settings File Corruption","The Settings File looks corrupted, which may have occurred due to tampering with the software files. Unable to apply your settings. EyePort will start in Default Settings.")
    createsettings()
    applysettings()

#Boot and apply settings
def applysettings():
    global value,themeframe,connection_type,recordmode,sync,welcome,recsavefolder,rememberloadbool,thit,useai,fullscreenmode,exportsavefolder,overwritexl,overexport,askexport,use_manual
    f=open("Settings.txt","a+")
    f.seek(0)
    value=f.readlines()
    check=[['EyePort Settings File - Any corruption may lead to configuration loss'],['Made by Akash Samanta'],['Light','Dark','System'],['80','90','100','110','120'],['Wi-Fi','Ethernet'],[],[],['0','1'],['EyePort Custom','Tobii Proprietary'],[str(j) for j in range(50,501,50)],['0','1'],[],["Extremely Low","Very Low", "Low", "Normal", "High","Very High"],['0','1','2'],['0','1'],[],[],[str(j) for j in range(25,501,25)],['0','1'],[],['0','1'],['0','1'],['0','1'],['0','1']]
    #print(len(value),len(check)) #For Debug Only
    for i in range(len(check)):
        try:
            if check[i]!=[]:
                if value[i][:-1] not in check[i]:
                    #print(value[i][:-1],check[i]) #For Debug Only
                    resetsettings()
        except:
            #print("FAIL") #For Debug Only
            resetsettings()
    if value[2][:-1]=="Light":
        set_appearance_mode("Light")
        settings.append(0)
    elif value[2][:-1]=="Dark":
        set_appearance_mode("Dark")
        settings.append(1)
    else:
        set_appearance_mode("System")
        settings.append(2)
    settings.append(int(value[3][:-1])/100)
    set_widget_scaling(settings[1])
    if value[4][:-1]=="Wi-Fi":
        connection_type="Wi-Fi"
        settings.append(0)
    else:
        connection_type="Ethernet"
        settings.append(1)
    settings.append(value[5][:-1])
    settings.append(value[6][:-1])
    settings.append(int(value[7][:-1]))
    if value[8][:-1]=="EyePort Custom":
        recordmode = 0
        settings.append(0)
    else:
        recordmode = 1
        settings.append(1)
    sync = int(int(value[9][:-1])/10)
    settings.append(int(value[9][:-1])) #Gaze Sync
    recsavefolder=value[11][:-1] #Record Save Folder Address
    if value[10][:-1]=="1": #Welcome Screen
        welcome=False
    else:
        welcome=True
    settings.append(value[12][:-1]) #Detection Sensitivity
    updateasense(value[12][:-1])
    useai=int(value[13][:-1])
    settings.append(useai) #Use AI Object Detection
    settings.append(int(value[14][:-1])) #Remember Last Loaded Files
    if int(value[14][:-1])==1:
        rememberloadbool=True
    else:
        rememberloadbool=False
    settings.append(int(value[17][:-1])) #Fixation Time
    thit = int(value[17][:-1])
    fullscreenmode = int(value[18][:-1])
    exportsavefolder=value[19][:-1]
    if os.path.exists(exportsavefolder)==False:
        exportsavefolder='Expsave'
    overwritexl = int(value[20][:-1])
    overexport = int(value[21][:-1])
    askexport = int(value[22][:-1])
    use_manual = int(value[23][:-1])
    #print(settings) #For Debug Only
    #print(recordmode)
    f.close()

#Making the Application
root.title("EyePort Software")
root.protocol("WM_DELETE_WINDOW", destroyer)
root.iconbitmap(r".\Resources\EyePort.ico")
applysettings()
if int(value[3])<101:
    root.minsize(1058,620)
    root.geometry("1058x620+450+200")
elif int(value[3])==110:
    root.minsize(1230,720)
    root.geometry("1230x720+350+150")
elif int(value[3])==120:
    root.minsize(1315,770)
    root.geometry("1315x770+250+100")
    
#Frames
frame1=CTkFrame(root,fg_color="Grey") #Left Bar
container2=CTkFrame(root)
canvas2=CTkCanvas(container2)
analyzeframe=CTkFrame(canvas2)
exportframe=CTkFrame(root)
recordframe=CTkFrame(root)
welcomeframe=CTkFrame(root)
container=CTkFrame(root)
canvas=CTkCanvas(container)
settingsframe=CTkFrame(canvas) 
videoframe = CTkFrame(recordframe)
imgframe = CTkFrame(analyzeframe)
imgframe2 = CTkFrame(analyzeframe)
imgframe3 = CTkFrame(analyzeframe)
expframe = CTkFrame(exportframe)
frame2 = CTkFrame(settingsframe) #Theme
frame3 = CTkFrame(settingsframe) #Recording Mode
frame4 = CTkFrame(settingsframe) #Connection Mode
frame5 = CTkFrame(settingsframe) #IP Entry
frame6 = CTkFrame(settingsframe) #Object Detection

#Button Scaling
bsize=16
bheight=35
bwidth=200

#Images
try:
    image1 = Image.open(r".\Resources\UserManual.png")
    image2 = Image.open(".\Resources\Record.png")
    image3 = Image.open(".\Resources\Analyze.png")
    image4 = Image.open(".\Resources\Export.png")
    image5 = Image.open(".\Resources\Settings.png")
    image6 = Image.open(".\Resources\Save.png")
    image7 = Image.open(".\Resources\CalibSuccess.png")
    image8 = Image.open(".\Resources\DCalibSuccess.png")
    image9 = Image.open(".\Resources\CalibFail.png")
    image10 = Image.open(".\Resources\DCalibFail.png")
    image11 = Image.open(".\Resources\FullBat.png")
    image12 = Image.open(".\Resources\QFBat.png")
    image13 = Image.open(".\Resources\HalfBat.png")
    image14 = Image.open(".\Resources\LowBat.png")
    image15 = Image.open(".\Resources\ZeroBat.png")
    image16 = Image.open(".\Resources\Timeleft.png")
    image17 = Image.open(".\Resources\EyeLight.png")
    image18 = Image.open(".\Resources\EyeDark.png")
    image19 = Image.open(".\Resources\Exit.png")
    image20 = Image.open(".\Resources\Edit.png")
    image21 = Image.open(".\Resources\ExportSuccess.png")
    image22 = Image.open(".\Resources\DExportSuccess.png")
    image23 = Image.open(".\Resources\ExportFailed.png")
    image24 = Image.open(".\Resources\DExportFailed.png")
    image25 = Image.open(".\Resources\ExportClick.png")
    image26 = Image.open(".\Resources\DExportClick.png")
    image27 = Image.open(".\Resources\ConnectGlasses.png")
    image28 = Image.open(".\Resources\PreviewDisabled.png")
    image29 = Image.open(".\Resources\PreviewEthernet.png")
    image30 = Image.open(".\Resources\EthernetTip.png")
    image31 = Image.open(".\Resources\DEthernetTip.png")
    image32 = Image.open(".\Resources\EthernetMode.png")
    image33 = Image.open(".\Resources\DEthernetMode.png")
    image34 = Image.open(".\Resources\WifiTip.png")
    image35 = Image.open(".\Resources\DWifiTip.png")
    image36 = Image.open(".\Resources\WifiMode.png")
    image37 = Image.open(".\Resources\DWifiMode.png")
    image38 = Image.open(".\Resources\RecordProgress.png")
    image39 = Image.open(".\Resources\DRecordProgress.png")
    image40 = Image.open(".\Resources\RecordSaved.png")
    image41 = Image.open(".\Resources\DRecordSaved.png")
except:
    tk.messagebox.showerror("Missing Resources","EyePort cannot find some critical resource files in the install location. This may be due to a corruption or illegal download. Please re-install the EyePort software again.")
    quit()
imgtk1 = CTkImage(light_image=image1)
imgtk2 = CTkImage(light_image=image2)
imgtk3 = CTkImage(light_image=image3)
imgtk4 = CTkImage(light_image=image4)
imgtk5 = CTkImage(light_image=image5)
imgtk6 = CTkImage(light_image=image6)
imgtk7 = CTkImage(light_image=image7,dark_image=image8,size=(135,190))
imgtk8 = CTkImage(light_image=image9,dark_image=image10,size=(148,200))
imgtk9 = CTkImage(light_image=image11)
imgtk10 = CTkImage(light_image=image12)
imgtk11 = CTkImage(light_image=image13)
imgtk12 = CTkImage(light_image=image14)
imgtk13 = CTkImage(light_image=image15)
imgtk14 = CTkImage(light_image=image16)
imgtk15 = CTkImage(light_image=image17,dark_image=image18,size=(400,400))
imgtk16 = CTkImage(light_image=image19)
imgtk17 = CTkImage(light_image=image20,size=(290,165))
imgtk18 = CTkImage(light_image=image21,dark_image=image22,size=(270,200))
imgtk19 = CTkImage(light_image=image23,dark_image=image24,size=(228,200))
imgtk20 = CTkImage(light_image=image25,dark_image=image26,size=(209,200))
imgtk21 = CTkImage(light_image=image27)
imgtk22 = CTkImage(light_image=image28)
imgtk23 = CTkImage(light_image=image29)
imgtk24 = CTkImage(light_image=image30,dark_image=image31,size=(200,50))
imgtk25 = CTkImage(light_image=image34,dark_image=image35,size=(210,50))
imgtk26 = CTkImage(light_image=image38,dark_image=image39,size=(170,30))
imgtk27 = CTkImage(light_image=image40,dark_image=image41,size=(150,30))
imgtk28 = CTkImage(light_image=image32,dark_image=image33,size=(180,53))
imgtk29 = CTkImage(light_image=image36,dark_image=image37,size=(184,53))

#Left Bar Elements
heading1 = CTkLabel(frame1, text="EyePort", font=CTkFont(size=30))
heading2 = CTkLabel(frame1, text="Software", font=CTkFont(size=15))
text1 = CTkLabel(frame1, text="Made by Akash Samanta")
quitbutton = CTkButton(frame1,text="Quit",command=destroyer, font=CTkFont(size=bsize),width=bwidth,height=bheight,fg_color="dark red", image=imgtk16,hover_color='#530000')
exportdata = CTkButton(frame1,text="Export Data",command=exportpage, font=CTkFont(size=bsize),width=bwidth,height=bheight, image=imgtk4)
analyzedata = CTkButton(frame1,text="Analyze Data",command=analyzepage, font=CTkFont(size=bsize),width=bwidth,height=bheight, image=imgtk3)
recorddata = CTkButton(frame1,text="Record Data",command=recordpage, font=CTkFont(size=bsize),width=bwidth,height=bheight, image=imgtk2)
settingsbutton = CTkButton(frame1,text="Settings",command=settingspage, font=CTkFont(size=bsize),width=bwidth,height=bheight, image=imgtk5)

text2 = CTkLabel(analyzeframe, text="Analyze Data", font=CTkFont(size=25))
text3 = CTkLabel(recordframe, text="Record Data", font=CTkFont(size=25))
text4 = CTkLabel(exportframe, text="Export Data", font=CTkFont(size=25))

#Welcome Elements
text37 = CTkLabel(welcomeframe, text="", image = imgtk15)
text38 = CTkLabel(welcomeframe, text="Welcome to EyePort", font=CTkFont(size=45))
text39 = CTkLabel(welcomeframe, text="To get started, go to the \"Record Data\" page, or if you are new, try reading the User Manual.", font=CTkFont(size=15))
gorecbutton = CTkButton(welcomeframe,text="Record Data",command=recordpage, font=CTkFont(size=bsize),width=bwidth,height=bheight,image=imgtk2)
usermanual = CTkButton(welcomeframe,text="User Manual",command=showusermanual, font=CTkFont(size=bsize),width=bwidth,height=bheight, image=imgtk1)
showagain_var = tk.IntVar(value=0)
showagain = CTkCheckBox(welcomeframe, text="Do not show this page again on startup", command=showagain,variable=showagain_var, onvalue=1, offvalue=0)

#Settings Elements
usermanual2 = CTkButton(frame1,text="User Manual",command=showusermanual, font=CTkFont(size=bsize),width=bwidth,height=bheight, image=imgtk1)
text5 = CTkLabel(settingsframe, text="Settings", font=CTkFont(size=25))
text6 = CTkLabel(settingsframe, text="General Appearance", font=CTkFont(size=17))
text7 = CTkLabel(settingsframe, text="Theme", font=CTkFont(size=15))
theme_var = tk.IntVar(value=settings[0])
radio_button_1 = CTkRadioButton(frame2, text="Light", variable=theme_var, value=0, command=updatetheme)
radio_button_2 = CTkRadioButton(frame2, text="Dark", variable=theme_var, value=1, command=updatetheme)
radio_button_3 = CTkRadioButton(frame2, text="System", variable=theme_var, value=2, command=updatetheme)
text8 = CTkLabel(settingsframe, text="UI Scaling", font=CTkFont(size=15))
scaling_optionmenu = CTkOptionMenu(settingsframe, values=["80%", "90%", "100%", "110%", "120%"],command=updatescale)
scaling_optionmenu.set(value[3][:-1]+"%")
fullscr_var = tk.IntVar(value=fullscreenmode)
check_3 = CTkCheckBox(settingsframe, text="Start in Fullscreen Mode", variable=fullscr_var, onvalue=1, offvalue=0, font=CTkFont(size=15),command=usefullscreen)
text9 = CTkLabel(settingsframe, text="Recording Preferences", font=CTkFont(size=17))
text23 = CTkLabel(settingsframe, text="Gaze Point and Video Sync", font=CTkFont(size=15))
text30 = CTkLabel(settingsframe, text="Every video stream has a lag. Increase this slider if the gaze point is updating sooner than the video stream.", font=CTkFont(size=12))
text11 = CTkLabel(settingsframe, text="Choose how you would like the app to look.", font=CTkFont(size=12))
text10 = CTkLabel(settingsframe, text="Recording Mode", font=CTkFont(size=15))
text24 = CTkLabel(settingsframe, text="Connection Settings", font=CTkFont(size=17))
text25 = CTkLabel(settingsframe, text="Connection Type", font=CTkFont(size=15))
text26 = CTkLabel(settingsframe, text="Choose how you would like the recordings to be saved.", font=CTkFont(size=12))
recmode_var = tk.IntVar(value=settings[6])
radio_button_4 = CTkRadioButton(frame3, text="EyePort Custom", variable=recmode_var, value=0, command=updaterecmode)
radio_button_5 = CTkRadioButton(frame3, text="Tobii Proprietary", variable=recmode_var, value=1, command=updaterecmode)
text27 = CTkLabel(settingsframe, text="Choose how you would be connecting the TOBII Glasses to EyePort.", font=CTkFont(size=12))
conmode_var = tk.IntVar(value=settings[2])
radio_button_6 = CTkRadioButton(frame4, text="Wi-Fi", variable=conmode_var, value=0, command=updateconmode)
radio_button_7 = CTkRadioButton(frame4, text="Ethernet", variable=conmode_var, value=1, command=updateconmode)
text28 = CTkLabel(settingsframe, text="IP Settings", font=CTkFont(size=15))
text29 = CTkLabel(settingsframe, text="It is recommended that you leave these settings alone unless you are absolutely sure about the changes.", font=CTkFont(size=12))
text35 = CTkLabel(settingsframe, text="Only last working addresses will be saved.", font=CTkFont(size=12))
preview_var = tk.IntVar(value=settings[5])
switch_1 = CTkCheckBox(settingsframe, text="Enable Live Preview", variable=preview_var, onvalue=1, offvalue=0, font=CTkFont(size=15),command=previewtoggle)
if settings[2]==1:
    switch_1.deselect()
    switch_1.configure(state='disabled')
    previewenabled = False
else:
    checklasttoggle()
slider_1 = CTkSlider(settingsframe, from_=50, to=500, number_of_steps=9, command=updatesync)
slider_1.set(settings[7])
text31 = CTkLabel(frame5, text="Wi-Fi:", font=CTkFont(size=15))
text32 = CTkLabel(frame5, text="Ethernet:", font=CTkFont(size=15))
wip_var = tk.StringVar(value=settings[3])
eip_var = tk.StringVar(value=settings[4])
wipentry = CTkEntry(frame5,placeholder_text="192.168.71.50",textvariable=wip_var,width=180,height=25,border_width=2,corner_radius=5)
eipentry = CTkEntry(frame5,placeholder_text="fe80::76fe:48ff:fe22:4109",textvariable=eip_var,width=180,height=25,border_width=2,corner_radius=5)
#text33 = CTkLabel(settingsframe, text="Please note that an ethernet connection does not support live preview.", font=CTkFont(size=12))
contip = CTkLabel(settingsframe,text='',compound='left',justify='left')
text34 = CTkLabel(settingsframe, text="\n\n\n\n", font=CTkFont(size=12))
resip = CTkButton(frame5,text="Restore Defaults",font=CTkFont(size=15),width=120,height=30,command=restoreip)
reset = CTkButton(settingsframe,text="Reset All Settings",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=resetsettings2)
text36 = CTkLabel(settingsframe, text=str(sync*10)+' ms', font=CTkFont(size=12))
text46 = CTkLabel(settingsframe, text="Analysis Preferences", font=CTkFont(size=17))
text47 = CTkLabel(settingsframe, text="Detection Sensitivity", font=CTkFont(size=15))
text48 = CTkLabel(settingsframe, text="Choose how sensitive the analyzing algorithm should be to detect Unique Areas of Interest.", font=CTkFont(size=12))
scaling_optionmenu2 = CTkOptionMenu(settingsframe, values=["Extremely Low","Very Low", "Low", "Normal", "High","Very High"], command=updateasense)
scaling_optionmenu2.set(settings[8])
useai_var = tk.IntVar(value=settings[9])
text65 = CTkLabel(settingsframe, text="Automatic Object Detection", font=CTkFont(size=15))
text66 = CTkLabel(settingsframe, text="Choose if you would like to use object detection along with the type of objects to be detected.", font=CTkFont(size=12))
radio_button_8 = CTkRadioButton(frame6, text="Disabled", variable=useai_var, value=0, command=updateuseai)
radio_button_9 = CTkRadioButton(frame6, text="General", variable=useai_var, value=1, command=updateuseai)
radio_button_10 = CTkRadioButton(frame6, text="Ships and Icebergs", variable=useai_var, value=2, command=updateuseai)
#check_1 = CTkCheckBox(settingsframe, text="Use Object Detection", variable=useai_var, onvalue=1, offvalue=0, font=CTkFont(size=15),command=updateuseai)
rememberload_var = tk.IntVar(value=settings[10])
check_2 = CTkCheckBox(settingsframe, text="Remember last Loaded Files", variable=rememberload_var, onvalue=1, offvalue=0, font=CTkFont(size=15),command=rememberload)
text50 = CTkLabel(settingsframe, text="Fixation Time", font=CTkFont(size=15))
text51 = CTkLabel(settingsframe, text="Choose how long a user should focus on an object to register it as an Area of Interest.", font=CTkFont(size=12))
slider_2 = CTkSlider(settingsframe, from_=25, to=500, number_of_steps=19, command=updatetimehit) 
slider_2.set(settings[11])
if thit%50==0:
    text52 = CTkLabel(settingsframe, text=str(thit/100)+'0 s', font=CTkFont(size=12))
else:
    text52 = CTkLabel(settingsframe, text=str(thit/100)+' s', font=CTkFont(size=12))
overwritexl_var = tk.IntVar(value=overwritexl)
check_4 = CTkCheckBox(settingsframe, text="Overwrite Old Excel Files", variable=overwritexl_var, onvalue=1, offvalue=0, font=CTkFont(size=15),command=overwritexlsx)
text60 = CTkLabel(settingsframe, text="Export Settings", font=CTkFont(size=17))
overexport_var = tk.IntVar(value=overexport)
check_5 = CTkCheckBox(settingsframe, text="Overwrite Old Exports", variable=overexport_var, onvalue=1, offvalue=0, font=CTkFont(size=15),command=overexporter)
askexport_var = tk.IntVar(value=askexport)
check_6 = CTkCheckBox(settingsframe, text="Ask for File Names before Exporting", variable=askexport_var, onvalue=1, offvalue=0, font=CTkFont(size=15),command=askexporter)
unrestrained_var = tk.IntVar(value=use_manual)
check_7 = CTkCheckBox(settingsframe, text="Manual Mode", variable=unrestrained_var, onvalue=1, offvalue=0, font=CTkFont(size=15),command=usemanual)
scrollbar=CTkScrollbar(container,command=canvas.yview)
settingsframe.bind("<Configure>",resize)
settingsframe.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas_frame = canvas.create_window((0, 0), window=settingsframe, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>",lambda e: canvas.itemconfig(canvas_frame, width=e.width))

#Export Elements
text53 = CTkLabel(exportframe, text="Step 1: Select Output Folder", font=CTkFont(size=15))
text54 = CTkLabel(exportframe, text="Choose where you would like to export your analyzed files.", font=CTkFont(size=12))
text55 = CTkLabel(exportframe, text="Step 2: Export Scenario File", font=CTkFont(size=15))
text56 = CTkLabel(exportframe, text="Click the \"Export CSV\" button to export a csv file from the analyzed glass data.", font=CTkFont(size=12))
text56.configure(text="You will need to analyze data first before you can export.",text_color=("red","yellow"))
text57 = CTkLabel(exportframe, text="Step 3: Export Model File (Optional)", font=CTkFont(size=15))
text58 = CTkLabel(exportframe, text="Click the \"Export XFMV\" button to also export a partial model of the scenario.", font=CTkFont(size=12))
text58.configure(text="You will need to analyze data first before you can export.",text_color=("red","yellow"))
text61 = CTkLabel(exportframe, text="Step 4: Export Excel File (Optional)", font=CTkFont(size=15))
text62 = CTkLabel(exportframe, text="Click the \"Export XLSX\" button to export a xlsx file from the analyzed data.", font=CTkFont(size=12))
text62.configure(text="You will need to analyze data first before you can export.",text_color=("red","yellow"))
text63 = CTkLabel(exportframe, text="Step 5: Export Images (Optional)", font=CTkFont(size=15))
text64 = CTkLabel(exportframe, text="Click the \"Export Image\" button to export images of the Areas of Interest.", font=CTkFont(size=12))
text64.configure(text="You will need to analyze data first before you can export.",text_color=("red","yellow"))

exportsave = CTkButton(exportframe,text="Export Folder",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=exportsaver)
export1 = CTkButton(exportframe,text="Export CSV",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=exportcsv,state='disabled')
export2 = CTkButton(exportframe,text="Export XMFV",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=exportxmfv,state='disabled')
export5 = CTkButton(exportframe,text="Export XLSX",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=exportxlsx,state='disabled')
export6 = CTkButton(exportframe,text="Export Images",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=exportimg,state='disabled')
exportsuccess = CTkLabel(expframe,text='',image=imgtk18)
exportfail = CTkLabel(expframe,text='',image=imgtk19)
exportclick = CTkLabel(expframe,text='',image=imgtk20)
export3 = CTkButton(expframe,text="Show in Explorer",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=openexplorer,state='normal')
export4 = CTkButton(expframe,text="Open DynaFRAM",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=dynafram,state='normal')

#Analyze Elements
text12 = CTkLabel(analyzeframe, text="Step 1: Load Glass Data", font=CTkFont(size=15))
text13 = CTkLabel(analyzeframe, text="Select the excel file which EyePort creates or use the livedata.json.gz file from the SD Card.", font=CTkFont(size=12))
text40 = CTkLabel(analyzeframe, text="Step 2: Load Video File", font=CTkFont(size=15))
text41 = CTkLabel(analyzeframe, text="Select the video file which EyePort creates or use the fullstream.mp4 file from the SD Card.", font=CTkFont(size=12))
text42 = CTkLabel(analyzeframe, text="Step 3: Start Analysis", font=CTkFont(size=15))
text43 = CTkLabel(analyzeframe, text="Click \"Analyze Now\" to start analyzing. Analysis may take longer if Object Detection is used.", font=CTkFont(size=12))
text44 = CTkLabel(imgframe, text="\n"*46, font=CTkFont(size=15))
loadfile = CTkButton(analyzeframe,text="Load File",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=loadjson)
loadfile1 = CTkButton(analyzeframe,text="Load File",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=loadvid)
analyze = CTkButton(analyzeframe,text="Analyze Now",font=CTkFont(size=bsize),width=bwidth,height=bheight,state="disabled",command=analyze)
text45 = CTkLabel(imgframe2, text="", font=CTkFont(size=15))
text49 = CTkLabel(imgframe3, text="Object Detections:", font=CTkFont(size=15))
editnames = CTkButton(analyzeframe,text="Edit Names",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=editAOI)
showgraph = CTkButton(analyzeframe,text="Show More Graphs",font=CTkFont(size=bsize),width=bwidth,height=bheight,command=showgraphs)
scrollbar2=CTkScrollbar(container2,command=canvas2.yview)
analyzeframe.bind("<Configure>",lambda e: canvas2.configure(scrollregion=canvas2.bbox("all")))
canvas_frame2 = canvas2.create_window((0, 0), window=analyzeframe, anchor="nw")
canvas2.configure(yscrollcommand=scrollbar2.set)
canvas2.bind("<Configure>",lambda e: canvas2.itemconfig(canvas_frame2, width=e.width))
text59 = CTkLabel(analyzeframe, text="\n"*30, font=CTkFont(size=15))

#Record Elements
text14 = CTkLabel(recordframe, text="Step 1: Connect Glasses", font=CTkFont(size=15))
text15 = CTkLabel(recordframe, text="Once the glasses are connected using Wi-Fi or Ethernet, click \"Connect Glasses\".", font=CTkFont(size=12))
connectbutton = CTkButton(recordframe,text="Connect Glasses",command=connect,font=CTkFont(size=bsize),width=bwidth,height=bheight)
text16 = CTkLabel(recordframe, text="Step 2: Calibrate Glasses (Optional)", font=CTkFont(size=15))
text17 = CTkLabel(recordframe, text="It is highly recommended that you calibrate your glasses. You can calibrate more than once.", font=CTkFont(size=12))
calibratebutton = CTkButton(recordframe,text="Calibrate Glasses",command=calibrate,state="disabled",font=CTkFont(size=bsize),width=bwidth,height=bheight)
text18 = CTkLabel(recordframe, text="Step 3: Start Recording", font=CTkFont(size=15))
text19 = CTkLabel(recordframe, text="Click the \"Record Now\" button to start recording.", font=CTkFont(size=12))
recordbutton = CTkButton(recordframe,text="Record Now",state="disabled",font=CTkFont(size=bsize),command=record,width=bwidth,height=bheight,fg_color='dark red',hover_color='#530000')
text20 = CTkLabel(videoframe, text="TOBII Glasses Live View", font=CTkFont(size=15))
videolabel = Label(videoframe)
previewnotavail = CTkLabel(videoframe,text='')
connectpreview = CTkLabel(videoframe,text='')
ethernetpreview = CTkLabel(videoframe,text='')
recordstatus = CTkLabel(videoframe,text='')
connectmode = CTkLabel(videoframe,text='')
text21 = CTkLabel(videoframe, text="Not Available", font=CTkFont(size=12))
text22 = CTkLabel(videoframe, text="Not Available", font=CTkFont(size=12))
disconnectbutton = CTkButton(videoframe,text="Disconnect Glasses",command=stream_reset,font=CTkFont(size=bsize),width=bwidth,height=bheight,state='disabled',fg_color='dark red',hover_color='#530000')
refreshbattery = CTkButton(videoframe,command=batteryrefresh,font=CTkFont(size=bsize),width=150,height=bheight)
batteryicon = CTkLabel(videoframe,text='')
timelefticon = CTkLabel(videoframe,text='')
locationsave = CTkButton(videoframe,text="Save Location",command=savelocation,font=CTkFont(size=bsize),width=bwidth,height=bheight, image=imgtk6)
calibsuccess = CTkLabel(videoframe,text='',image=imgtk7)
calibfail = CTkLabel(videoframe,text='',image=imgtk8)

frame1.pack(fill=tk.Y,side=tk.LEFT)
heading1.pack(side=tk.TOP,pady=(10,0))
heading2.pack(side=tk.TOP,pady=(0,10))
recorddata.pack(side=tk.TOP,pady=10,padx=20)
analyzedata.pack(side=tk.TOP,pady=10,padx=20)
exportdata.pack(side=tk.TOP,pady=10,padx=20)
quitbutton.pack(side=tk.TOP,pady=10,padx=20)
text1.pack(side=tk.BOTTOM,pady=10,padx=20)
settingsbutton.pack(side=tk.BOTTOM,padx=20,pady=(10,0))

autoloadfiles()
if welcome:
    welcomepage()
else:
    recordpage()
root.after(800,fullscreen)

root.mainloop()


