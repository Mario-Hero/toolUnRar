#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Created by Mario Chen, 04.04.2021, Shenzhen
# My Github site: https://github.com/Mario-Hero

import sys
import os


PASSWD = ["hello","123456","laksdjflkdf"] # the passwords
DELETEIT = False # DANGER!! If it is True,will delete rar file after extraction
LOC_WINRAR = "C:\\Program Files\\WinRAR\\" # location of WinRAR



PROGRAM_RAR = "UnRAR.exe" # the program we use
LOC_S_WINRAR = ["C:\\Program Files\\WinRAR\\","C:\\Program Files (x86)\\WinRAR\\","./",""] # some possible locations of WinRAR


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
    for wd in PASSWD:
        extractStr = " x -y -p" + wd + " " + folder + "/" + file + " " + folder + "/"         
        extM = os.popen("@\""+LOC_WINRAR+PROGRAM_RAR+"\""+extractStr).read().strip()
        #print(extM)
        #print(extM[-1])
        if "is not RAR" in extM or "不是 RAR" in extM:
            break
        elif utfIsNumber(extM[-1]) or "错误" in extM or "无法" in extM or "errors" in extM or "Incorrect" in extM:
            pass
        else:
            if "正常" in extM or "OK" in extM :
                #print("Success: "+file)
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
                if unrarFile(folder, file):
                    if DELETEIT:
                        os.remove(folder + "/" + file)
    else:
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
               break
    for folder in sys.argv[1:]:
        #print(folder)
        unrar(folder)
    print("Finish.")
    #os.system("pause")
