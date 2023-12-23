#Model Creator
#Code part of Tobii Eye Tracking Project
#Made by Akash Samanta

import os
import tkinter as tk

def creator(UAOIName,save,overwrite,askexport):
    base='<FM Version="0,0,2,0">\n  <Functions>\n    '
    allfunction='    <Function fnStyle="0" Tp="-1" Pp="-1" x="900" y="100" style="white" color="16777215">\n      <IDNr>0</IDNr>\n      <FunctionType>2</FunctionType>\n      <IDName>Observation Complete</IDName>\n      <Description>Participant is not focused on any object or his eyes are saccading.</Description>\n    </Function>\n'
    x=700
    y=0
    for i in range(len(UAOIName)):
        function=f'    <Function fnStyle="0" Tp="-1" Pp="-1" x="{x}" y="{y}" style="white" color="16777215">\n      <IDNr>{i+1}</IDNr>\n      <FunctionType>2</FunctionType>\n      <IDName>Observation of {UAOIName[i]} starts</IDName>\n      <Description>Participant has started to focus on {UAOIName[i]}.</Description>\n    </Function>\n'
        allfunction=allfunction+function
        y=y+200
    allfunction=allfunction+'  </Functions>\n'
    allinput='  <Inputs>\n'
    for i in range(len(UAOIName)):
        input=f'    <Input>\n      <IDNr>{i+1}</IDNr>\n      <IDName>Observing {UAOIName[i]}</IDName>\n      <FunctionIDNr>0</FunctionIDNr>\n    </Input>\n'
        allinput=allinput+input
    allinput=allinput+"  </Inputs>\n"

    alloutput='  <Outputs>\n'
    for i in range(len(UAOIName)):
        output=f'    <Output>\n      <IDNr>0</IDNr>\n      <IDName>Observing {UAOIName[i]}</IDName>\n      <FunctionIDNr>{i+1}</FunctionIDNr>\n    </Output>\n'
        alloutput=alloutput+output
    alloutput=alloutput+"  </Outputs>\n"

    end='  <Playbacks>\n    <Playback type="2">END</Playback>\n  </Playbacks>\n</FM>'
    text=base+allfunction+allinput+alloutput+end
    c=1
    path=save+"/"+f'EyePort Model {c}.xfmv'
    while os.path.exists(path):
        c=c+1
        path=save+"/"+f'EyePort Model {c}.xfmv'
    if c!=1 and overwrite==1:
        c=c-1

    if askexport==1:
        askpath=tk.filedialog.asksaveasfilename(initialdir=save,initialfile=f'EyePort Model {c}.xfmv',filetypes=[("XFMV Model File","*.xfmv")])
        if askpath!='':
            if askpath[-5:]!='.xfmv':
                askpath=askpath+'.xfmv'
            path=askpath
        else:
            askexport=0
        
    if askexport==0:
        f=open(save+"/"+f'EyePort Model {c}.txt','w')
    else:
        f=open(path[:-5]+'.txt','w')
    f.write(text)
    f.close()

    try:
        if askexport==0:
            os.rename(save+"/"+f'EyePort Model {c}.txt', save+"/"+f'EyePort Model {c}.xfmv')
        else:
            os.rename(path[:-5]+'.txt', path)
    except FileExistsError:
        if askexport==0:
            os.remove(save+"/"+f'EyePort Model {c}.xfmv')
            os.rename(save+"/"+f'EyePort Model {c}.txt', save+"/"+f'EyePort Model {c}.xfmv')
        else:
            print(path)
            os.remove(path)
            os.rename(path[:-5]+'.txt', path)
    except PermissionError:
        tk.messagebox.showerror('Permission Error','EyePort was unable to export the files because there was no permission to create them. Close any applications that may be using existing files or try elevating EyePort as Administrator.')
        return 0

if __name__=='__main__':
    print("Model Creator\nCode part of Tobii Eye Tracking Project\nMade by Akash Samanta\n")
    print("WARNING! You are running this code snippet alone.\nThis may accomplish only a specific task. Please use EyePort GUI.py instead.")


