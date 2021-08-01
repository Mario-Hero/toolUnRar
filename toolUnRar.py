#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Created by Mario Chen, 04.04.2021, Shenzhen
# My Github site: https://github.com/Mario-Hero

import sys
import os
import subprocess

# you can change it >>>>>

PASSWD     = ["123456","hello"]  # the possible passwords
DELETEIT   = True                                      # DANGER!! If it is True,will delete rar file after extraction
LOC_WINRAR = "C:\\Program Files\\WinRAR\\"              # location of WinRAR
LOC_7Z     = "C:\\Program Files\\7-Zip\\"               # location of 7-Zip
SAVE_MODE  = True                                       # if the suffix of file doesn't look like a compressed file, then do nothing with it.

# <<<<< you can change it


PROGRAM_RAR  = "UnRAR.exe" # the program we use
PROGRAM_7Z   = "7z.exe"    # the program we use
LOC_S_WINRAR = ["C:\\Program Files\\WinRAR\\","C:\\Program Files (x86)\\WinRAR\\","./",""] # some possible locations of WinRAR
LOC_S_7Z     = ["C:\\Program Files\\7-Zip\\","C:\\Program Files (x86)\\7-Zip\\","./",""]   # some possible locations of 7-Zip
RAR_FILE     = ["rar","zip","7z","tar","gz","xz","bzip2","gzip","wim","arj","cab","chm","cpio","cramfs","deb","dmg","fat","hfs","iso","lzh","lzma","mbr","msi","nsis","ntfs","rpm","squashfs","udf","vhd","xar","z"]
NOT_RAR_FILE = ["jpg","exe","png","mkv","mp4","mp3","avi","mov","jpeg","wav","gif","mpeg","webp","txt","doc","docx","ppt","pptx","xls","xlsx","html","wps","torrent","swf","bmp","crdownload","xltd","downloading"]
ENABLE_RAR = False         # initial state only
ENABLE_7Z = False          # initial state only

# for guessing >>>
GUESS_FLAG_INIT     = ["密码", "码", "password", "Password"]    #0
GUESS_FLAG_START_1  = [":", "："]                            #1
GUESS_FLAG_START_2  = ["是", "为", "is", "are"," "]          #1
GUESS_FLAG_END      = ["\n","   "]                           #2
GUESS_FLAG_DIVIDE   = ["或是", "或", " or "]                 #3
# <<< for guessing

ERROR_LIST = ""


def logError(comment):
    global ERROR_LIST
    ERROR_LIST=ERROR_LIST+comment+'\n'


def guessWDComment(comment):
    guess_flag = 0
    guess_wd: list[str] = []
    guess_ps = 0
    cutIn = 0
    cutOut = 0
    while True:
        if guess_flag == 0:
            guess_newPs = len(comment)
            guess_len = 0
            for initStr in GUESS_FLAG_INIT:
                ps_temp = comment.find(initStr, guess_ps)
                if ps_temp == -1:
                    continue
                else:
                    if ps_temp<guess_newPs:
                        guess_newPs = ps_temp
                        guess_len = len(initStr)
            if guess_newPs == len(comment):
                if not guess_wd:
                    cutIn = 0
                    cutOut = len(comment)
                    guess_flag = 3
                else:
                    break
            else:
                guess_ps = guess_newPs + guess_len
                guess_flag = 1
        elif guess_flag == 1:
            found_temp = False
            found_temp_2 = False
            guess_newPs = len(comment)
            for startStr in GUESS_FLAG_START_1:
                ps_temp = comment.find(startStr, guess_ps, guess_ps + 20)
                if ps_temp == -1:
                    continue
                else:
                    if ps_temp < guess_newPs:
                        found_temp = True
                        guess_newPs = ps_temp + len(startStr)
                        guess_flag = 2
            if found_temp:
                guess_ps = guess_newPs
                cutIn = guess_ps
                continue
            else:
                guess_newPs = len(comment)
                for startStr in GUESS_FLAG_START_2:
                    ps_temp = comment.find(startStr, guess_ps, guess_ps + 20)
                    if ps_temp == -1:
                        continue
                    else:
                        if ps_temp < guess_newPs:
                            found_temp_2 = True
                            guess_newPs = ps_temp + len(startStr)
                            guess_flag = 2
            if found_temp_2:
                guess_ps = guess_newPs
            cutIn = guess_ps
            guess_flag = 2
        elif guess_flag == 2:
            guess_newPs = len(comment)
            for endStr in GUESS_FLAG_END:
                ps_temp = comment.find(endStr, guess_ps)
                if ps_temp == -1:
                    continue
                else:
                    if ps_temp < guess_newPs:
                        guess_newPs = ps_temp
            guess_ps = guess_newPs
            guess_flag = 3
            cutOut = guess_ps
        elif guess_flag == 3:
            found_cut_temp = False
            for divideStr in GUESS_FLAG_DIVIDE:
                if comment.find(divideStr, cutIn, cutOut) != -1:
                    found_cut_temp = True
                    for wd in comment[cutIn:cutOut].split(divideStr):
                        guess_wd.append(wd.strip())
                    break
            if not found_cut_temp:
                guess_wd.append(comment[cutIn:cutOut].strip())
            guess_flag = 0
        else:
            guess_flag = 0
    return guess_wd


def fileNameGuess(fileName):
    global PASSWD
    for wd in GUESS_FLAG_INIT:
        if wd in fileName:
            wdArray = guessWDComment(fileName)
            if wdArray != ['']:
                PASSWD = wdArray + PASSWD
                return True
    if ' ' in fileName:
        PASSWD.insert(0, fileName[fileName.rindex(' '):])
    else:
        PASSWD.insert(0, fileName)
    return False


def getPWFromFolder(file):
    if os.path.isdir(file):
        folderName = os.path.split(file)[1]
        fileNameGuess(folderName)
        file_list = os.listdir(file)
        for oneFile in file_list:
            if oneFile.endswith('.txt'):
                oneFileName = oneFile[:-4]
                fileNameGuess(oneFileName)
            elif os.path.isdir(os.path.join(file, oneFile)):
                fileNameGuess(oneFile)
    else:
        folder, fileName = os.path.split(file)
        fileNamePart = fileName[:fileName.rindex('.')]
        folderName = os.path.split(folder)[1]
        fileNameGuess(fileNamePart)
        fileNameGuess(folderName)
        file_list = os.listdir(folder)
        for oneFile in file_list:
            if oneFile.endswith('.txt'):
                oneFileName = oneFile[:-4]
                fileNameGuess(oneFileName)
            elif os.path.isdir(os.path.join(folder, oneFile)):
                fileNameGuess(oneFile)


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


def winRarDo(folder, file, wd):
    extractStr = " x -y -p" + wd + " \"" + folder + "\\" + file + "\" \"" + folder + "\\\""
    extM = subprocess.call("@\""+LOC_WINRAR+PROGRAM_RAR+"\""+extractStr,shell=True)
    # print("winrar", extM)
    if extM == 1:    # not rar file
        return 2
    elif extM == 11:  # wrong password
        return 1
    elif extM == 2:  # broken file
        return 3
    elif extM != 0:  # error
        return 1
    else:
        return 0


def z7Do(folder, file, wd):
    extractStr = " x -y -p" + wd + " \"" + folder + "\\" + file + "\" -o\"" + folder + "\\\"" 
    extM = subprocess.call("@\""+LOC_7Z+PROGRAM_7Z+"\""+extractStr,shell=True)
    # print("7z", extM)
    if extM !=0:  # error
        if extM == 2:  # fatal error
            return 1
        else:
            return 1
    else:
        return 0


def unrarFile(folder, file):
    successThisFile = False
    fileNameEncrypted = True
    if not folder:
        cutPos = file.rindex("\\")
        folder = file[:cutPos]
        file = file[cutPos+1:]
        #print(folder)
        #print(file)
    if ENABLE_RAR and file.endswith(".rar"):
        winRarReturn = winRarDo(folder, file, PASSWD[0])
        #print(winRarReturn)
        if winRarReturn == 0:
            #successThisFile = True
            return True
        elif winRarReturn == 2:
            pass
        else:
            getCommentStr = " l -p0 -z" + " \"" + folder + "\\" + file + "\""
            commentNumber = subprocess.call("@\""+LOC_WINRAR+PROGRAM_RAR+"\""+getCommentStr,shell=True)
            #commentNumber = 1
            if commentNumber == 0:
                commentM = subprocess.getstatusoutput("@\""+LOC_WINRAR+PROGRAM_RAR+"\""+getCommentStr)
                if commentM[0] == 0:
                    fileNameEncrypted = False
                    try:
                        comment = commentM[1][(commentM[1].index("\n\n")+2):commentM[1].index(folder)]
                        comment = comment[0:comment.rindex("\n\n")]
                    except:
                        pass
                    else:
                        #print(comment)
                        if comment:
                            wdArray = guessWDComment(comment)
                            print("Possible passwords:", wdArray)
                            for wd in wdArray:
                                winRarReturn = winRarDo(folder, file, wd)
                                if winRarReturn == 1:
                                    continue
                                elif winRarReturn == 0:
                                    successThisFile = True
                                    PASSWD.insert(0, wd)
                                    break
                                elif winRarReturn == 2:
                                    break
                                else:
                                    break
            if successThisFile:
                return True
            for index in range(1,len(PASSWD)):
                winRarReturn = winRarDo(folder, file, PASSWD[index])
                if winRarReturn == 1:
                    continue
                elif winRarReturn == 0:
                    successThisFile = True
                    PASSWD[0],PASSWD[index]=PASSWD[index],PASSWD[0]
                    break
                elif winRarReturn == 2:
                    break
                else:
                    break
            
    if not successThisFile:
        if ENABLE_7Z:
            for index in range(len(PASSWD)):
                z7Return = z7Do(folder, file, PASSWD[index])
                if z7Return != 1:
                    continue
                elif z7Return == 3:
                    logError("Broken file: "+file)
                    return successThisFile
                else:
                    successThisFile = True
                    PASSWD[0],PASSWD[index]=PASSWD[index],PASSWD[0]
                    break
                     
    if not successThisFile: 
        logError("No passsword for: "+file)
    return successThisFile


def unrar(folder):
    if os.path.isdir(folder):
        print(folder)
        file_list = os.listdir(folder)
        for file in file_list:
            if os.path.isdir(os.path.join(folder, file)):
                #print(folder +"/"+ file)
                #unrar(folder +"/"+file)
                pass
            else:
                if isCompressedFile(file):
                    if unrarFile(folder, file):
                        if DELETEIT:
                            os.remove(os.path.join(folder, file))
    else:
        if isCompressedFile(folder):
            if unrarFile("", folder):
                if DELETEIT:
                    os.remove(folder)
                  

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.exit(1)
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

    if (not ENABLE_RAR) and (not ENABLE_7Z):
        print("Cannot find winRAR and 7-zip")
        sys.exit(1)
    if len(sys.argv) > 1:
        while len(PASSWD) < 2:
            PASSWD.append("0")
        getPWFromFolder(sys.argv[1])
        if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
            SAVE_MODE = False
        # print(PASSWD)
        # subprocess.call("pause", shell=True)
        for folder in sys.argv[1:]:
            #print(folder)
            unrar(folder)
        print("Finish.")
        if ERROR_LIST:
            print(ERROR_LIST)
            subprocess.call("pause", shell=True)
        sys.exit(0)
