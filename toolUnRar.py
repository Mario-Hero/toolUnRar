#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Created by Mario Chen, 04.04.2021, Shenzhen
# My Github site: https://github.com/Mario-Hero

import sys
import os
import subprocess

# you can change it >>>>>

PASSWD = ["hello","123456"] # the passwords
DELETEIT = True # DANGER!! If it is True,will delete rar file after extraction
LOC_WINRAR = "C:\\Program Files\\WinRAR\\" # location of WinRAR
LOC_7Z = "C:\\Program Files\\7-Zip\\" # location of 7-Zip
SAVE_MODE = True # if the suffix of file is not like a compressed file, then do nothing with it.

# <<<<< you can change it


PROGRAM_RAR  = "UnRAR.exe" # the program we use
PROGRAM_7Z   = "7z.exe"    # the program we use
LOC_S_WINRAR = ["C:\\Program Files\\WinRAR\\","C:\\Program Files (x86)\\WinRAR\\","./",""] # some possible locations of WinRAR
LOC_S_7Z     = ["C:\\Program Files\\7-Zip\\","C:\\Program Files (x86)\\7-Zip\\","./",""]   # some possible locations of 7-Zip
RAR_FILE = ["rar","zip","7z","tar","gz","XZ","BZIP2","GZIP","WIM","ARJ","CAB","CHM","CPIO","CramFS","DEB","DMG","FAT","HFS","ISO","LZH","LZMA","MBR","MSI","NSIS","NTFS","RAR","RPM","SquashFS","UDF","VHD","XAR","Z"]
NOT_RAR_FILE = ["jpg","exe","png","mkv","mp4","mp3","avi","jpeg","wav","gif","mpeg","webp","txt","doc","docx","ppt","pptx","xls","xlsx","html","wps","torrent","swf","bmp"]

ENABLE_RAR = False # initial state only
ENABLE_7Z = False  # initial state only


def isCompressedFile(file):
    file = file.lower()
    for rar in RAR_FILE:
        if file.endswith("." + rar):
            return True
    for media in NOT_RAR_FILE:
        if file.endswith("." + media):
            return False
    return not SAVE_MODE


def utfIsNumber(uchar):
    return uchar >= u'\u0030' and uchar<=u'\u0039'


def unrarFile(folder, file):
    successThisFile = False
    if not folder:
        cutPos = file.rindex("\\")
        folder = file[:cutPos]
        file = file[cutPos+1:]
        #print(folder)
        #print(file)
    if ENABLE_RAR and file.endswith(".rar"):
        for wd in PASSWD:
            extractStr = " x -y -p" + wd + " " + folder + "\\" + file + " " + folder + "/"         
            extM = subprocess.call("@\""+LOC_WINRAR+PROGRAM_RAR+"\""+extractStr,shell=True)
            if extM == 1:
                break
            elif extM == 11:
                continue
            elif extM != 0:
                continue
            else:
                successThisFile = True
                break
    if not successThisFile:
        if ENABLE_7Z:
            for wd in PASSWD:
                extractStr = " x -y -p" + wd + " " + folder + "\\" + file + " -o" + folder + "/" 
                extM = subprocess.call("@\""+LOC_7Z+PROGRAM_7Z+"\""+extractStr,shell=True)
                if extM !=0:
                    continue
                else:
                    successThisFile = True
                    break      
    if not successThisFile: 
        print("Failed："+file)
    return successThisFile


def unrar(folder):
    if os.path.isdir(folder):
        print(folder)
        file_list = os.listdir(folder)
        for file in file_list:
            if os.path.isdir(folder + "/" + file):
                #print(folder +"/"+ file)
                #unrar(folder +"/"+file)
                pass
            else:
                if isCompressedFile(file):
                    if unrarFile(folder, file):
                        if DELETEIT:
                            os.remove(folder + "/" + file)
    else:
        if isCompressedFile(folder):
            if unrarFile("", folder):
                if DELETEIT:
                    os.remove(folder)
            
        

if __name__ == '__main__':
    testRar = os.popen("\""+LOC_WINRAR+PROGRAM_RAR+"\"").read()    
    if not testRar:
       for loc in LOC_S_WINRAR:
           testRar = os.popen("\""+loc+PROGRAM_RAR+"\"").read()
           if testRar:
               LOC_WINRAR = loc
               ENABLE_RAR = True
               break
    else:
        ENABLE_RAR = True

    test7z = os.popen("\""+LOC_7Z+PROGRAM_7Z+"\"").read()    
    if not test7z:
       for loc in LOC_S_7Z:
           test7z = os.popen("\""+loc+PROGRAM_7Z+"\"").read()
           if test7z:
               LOC_7Z = loc
               ENABLE_7Z = True
               break
    else:
        ENABLE_7Z = True

    for folder in sys.argv[1:]:
        #print(folder)
        unrar(folder)
    print("Finish.")
    #os.system("pause")
