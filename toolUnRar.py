#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Created by Mario Chen, 04.04.2021, Shenzhen
# My Github site: https://github.com/Mario-Hero

import sys
import os

# you can change it >>>>>

PASSWD = ["hello","123456","laksdjflkdf"] # the passwords
DELETEIT = False # DANGER!! If it is True,will delete rar file after extraction
LOC_WINRAR = "C:\\Program Files\\WinRAR\\" # location of WinRAR
LOC_7Z = "C:\\Program Files\\7-Zip\\"

# <<<<< you can change it


PROGRAM_RAR  = "UnRAR.exe" # the program we use
PROGRAM_7Z   = "7z.exe"    # the program we use
LOC_S_WINRAR = ["C:\\Program Files\\WinRAR\\","C:\\Program Files (x86)\\WinRAR\\","./",""] # some possible locations of WinRAR
LOC_S_7Z     = ["C:\\Program Files\\7-Zip\\","C:\\Program Files (x86)\\7-Zip\\","./",""]   # some possible locations of 7-Zip

ENABLE_RAR = False # initial state only
ENABLE_7Z = False  # initial state only

def utfIsNumber(uchar):
    return uchar >= u'\u0030' and uchar<=u'\u0039'


def unrarFile(folder, file):
    successThisFile = False
    testTime = 0
    if not folder:
        cutPos = file.rindex("\\")
        folder = file[:cutPos]
        file = file[cutPos+1:]
        #print(folder)
        #print(file)
    while testTime <=1 and not successThisFile:
        if ENABLE_RAR:
            if (testTime == 0 and file.endswith(".rar")) or testTime == 1:
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
        if successThisFile:
            break
        if ENABLE_7Z:
            if (testTime == 0 and file.endswith(".7z")) or testTime == 1:
                for wd in PASSWD:
                    extractStr = " x -y -p" + wd + " " + folder + "/" + file + " -o " + folder + "/"         
                    extM = os.popen("@\""+LOC_WINRAR+PROGRAM_RAR+"\""+extractStr).read().strip()
                    #print(extM)
                    #print(extM[-1])
                    if utfIsNumber(extM[-1]) or "错误" in extM or "无法" in extM or "errors" in extM or "Incorrect" in extM:
                        pass
                    else:
                        if "正常" in extM or "OK" in extM :
                            #print("Success: "+file)
                            successThisFile = True
                            break
        if successThisFile:
            break
        testTime = testTime + 1
        
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
