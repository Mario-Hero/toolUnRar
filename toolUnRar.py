#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Created by Mario Chen, 04.04.2021, Shenzhen
# My Github site: https://github.com/Mario-Hero

import sys
import os
import subprocess

try:
    import datetime
except ImportError:
    os.system('pip install datetime')
    import datetime

# you can change it >>>>>

PASSWD = ['666', '123456']  # 可能的密码 possible passwords
DELETEIT = True  # 注意！解压后删除压缩包 DANGER!! If it is True,will delete rar file after extraction
LOC_WINRAR = "C:\\Program Files\\WinRAR\\"  # location of WinRAR
LOC_7Z = "C:\\Program Files\\7-Zip\\"  # location of 7-Zip
SAVE_MODE = True  # 如果文件后缀看上去不像压缩文件，就不解压，除非用户拖入的是文件 if the extension name of file doesn't look like a compressed file, then do nothing with it, unless the user drag files into this script.
MULTI_UNRAR = DELETEIT and True  # 解压双重压缩文件 unzip double compressed files

# <<<<< you can change it


PROGRAM_RAR = "UnRAR.exe"  # the program we use
PROGRAM_7Z = "7z.exe"  # the program we use
LOC_S_WINRAR = ["C:\\Program Files\\WinRAR\\", "C:\\Program Files (x86)\\WinRAR\\", "./",
                ""]  # some possible locations of WinRAR
LOC_S_7Z = ["C:\\Program Files\\7-Zip\\", "C:\\Program Files (x86)\\7-Zip\\", "./",
            ""]  # some possible locations of 7-Zip
RAR_FILE = ["rar", "zip", "7z", "tar", "gz", "xz", "bzip2", "gzip", "wim", "arj", "cab", "chm", "cpio", "cramfs", "deb",
            "dmg", "fat", "hfs", "iso", "lzh", "lzma", "mbr", "msi", "nsis", "ntfs", "rpm", "squashfs", "udf", "vhd",
            "xar", "z"]
NOT_RAR_FILE = ["jpg", "exe", "png", "mkv", "mp4", "mp3", "avi", "mov", "jpeg", "wav", "gif", "mpeg", "webp", "txt",
                "doc", "docx", "ppt", "pptx", "xls", "xlsx", "html", "wps", "torrent", "swf", "bmp", "crdownload",
                "xltd", "downloading"]
ENABLE_RAR = False  # initial state only
ENABLE_7Z = False  # initial state only

RENAME_UNRAR = True  # 防止解压的文件与压缩包重名 In order to prevent that the decompressed file has the same name with current file, we rename the compressed file first

# for guessing >>>
GUESS_FLAG_INIT = ["密码", "码", "password", "Password"]  # 0
GUESS_FLAG_START_1 = [":", "："]  # 1
GUESS_FLAG_START_2 = ["是", "为", "is", "are", " "]  # 1
GUESS_FLAG_END = ["\n", "   "]  # 2
GUESS_FLAG_DIVIDE = ["或是", "或", " or "]  # 3
# <<< for guessing

ERROR_LIST = ""
workSpace = ""
lastFileName = ""
lastFileSize = 0
lastSpaceFiles = []
newSpaceFiles = []
multiPartList = []
multiPartExtracted = []

def logError(comment):
    global ERROR_LIST
    ERROR_LIST += comment + '\n'


def guessWDComment(comment):
    guessFlag = 0
    guessWD = []
    guessPS = 0
    cutIn = 0
    cutOut = 0
    while True:
        if guessFlag == 0:
            guessNewPS = len(comment)
            guessLen = 0
            for initStr in GUESS_FLAG_INIT:
                PSTemp = comment.find(initStr, guessPS)
                if PSTemp == -1:
                    continue
                else:
                    if PSTemp < guessNewPS:
                        guessNewPS = PSTemp
                        guessLen = len(initStr)
            if guessNewPS == len(comment):
                if not guessWD:
                    cutIn = 0
                    cutOut = len(comment)
                    guessFlag = 3
                else:
                    break
            else:
                guessPS = guessNewPS + guessLen
                guessFlag = 1
        elif guessFlag == 1:
            foundTemp = False
            foundTemp2 = False
            guessNewPS = len(comment)
            for startStr in GUESS_FLAG_START_1:
                PSTemp = comment.find(startStr, guessPS, guessPS + 20)
                if PSTemp == -1:
                    continue
                else:
                    if PSTemp < guessNewPS:
                        foundTemp = True
                        guessNewPS = PSTemp + len(startStr)
                        guessFlag = 2
            if foundTemp:
                guessPS = guessNewPS
                cutIn = guessPS
                continue
            else:
                guessNewPS = len(comment)
                for startStr in GUESS_FLAG_START_2:
                    PSTemp = comment.find(startStr, guessPS, guessPS + 20)
                    if PSTemp == -1:
                        continue
                    else:
                        if PSTemp < guessNewPS:
                            foundTemp2 = True
                            guessNewPS = PSTemp + len(startStr)
                            # guessFlag = 2
            if foundTemp2:
                guessPS = guessNewPS
            cutIn = guessPS
            guessFlag = 2
        elif guessFlag == 2:
            guessNewPS = len(comment)
            for endStr in GUESS_FLAG_END:
                PSTemp = comment.find(endStr, guessPS)
                if PSTemp == -1:
                    continue
                else:
                    if PSTemp < guessNewPS:
                        guessNewPS = PSTemp
            guessPS = guessNewPS
            guessFlag = 3
            cutOut = guessPS
        elif guessFlag == 3:
            foundCutTemp = False
            for divideStr in GUESS_FLAG_DIVIDE:
                if comment.find(divideStr, cutIn, cutOut) != -1:
                    foundCutTemp = True
                    for wd in comment[cutIn:cutOut].split(divideStr):
                        guessWD.append(wd.strip())
                    break
            if not foundCutTemp:
                guessWD.append(comment[cutIn:cutOut].strip())
            guessFlag = 0
        else:
            guessFlag = 0
    return guessWD


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
        parentFolder, fileName = os.path.split(file)
        if "." in fileName:
            fileNamePart = fileName[:fileName.rindex('.')]
        else:
            fileNamePart = fileName
        folderName = os.path.split(parentFolder)[1]
        fileNameGuess(fileNamePart)
        fileNameGuess(folderName)
        file_list = os.listdir(parentFolder)
        for oneFile in file_list:
            if oneFile.endswith('.txt'):
                oneFileName = oneFile[:-4]
                fileNameGuess(oneFileName)
            elif os.path.isdir(os.path.join(parentFolder, oneFile)):
                fileNameGuess(oneFile)


def isCompressedFile(file, multiUnrar=False):
    if "." in file:
        fileExtension = file[file.rindex('.') + 1:].lower()
        for rar in RAR_FILE:
            if fileExtension == rar:
                return True
        if "删" in fileExtension:
            return True
        for media in NOT_RAR_FILE:
            if fileExtension == media:
                return False
    return (not SAVE_MODE) or multiUnrar


def fileRename(file, n):
    pathName, fileName = os.path.split(file)
    if '.' in fileName:
        cutPos = fileName.rfind('.')
        return os.path.join(pathName, fileName[:cutPos] + '(' + str(n) + ')' + fileName[cutPos:])
    else:
        return os.path.join(pathName, fileName + '(' + str(n) + ')')


def winRarDo(folder, file, wd):
    extM = subprocess.call(
        [os.path.join(LOC_WINRAR, PROGRAM_RAR), 'x', '-y', '-p' + wd, os.path.join(folder, file), folder])
    # print("winrar", extM)
    if extM == 1:  # not rar file
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
    extM = subprocess.call(
        [os.path.join(LOC_7Z, PROGRAM_7Z), 'x', '-y', '-p' + wd, os.path.join(folder, file), '-o' + folder],
        shell=False)
    # print("7z", extM)
    if extM != 0:  # error
        if extM == 2:  # fatal error
            return 1
        else:
            return 1
    else:
        return 0


def unrarFun3(folder, file, multiPart=False):
    successThisFile = False
    if not folder:
        folder, file = os.path.split(file)
    originalName = file
    if RENAME_UNRAR and not multiPart:  # 分卷解压不重命名
        if '.' in file:
            fileExtension = file[file.rindex('.'):]
        else:
            fileExtension = ''
        dt_ms = 'RAR' + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        while os.path.exists(os.path.join(folder, dt_ms + fileExtension)):
            dt_ms = dt_ms + '(1)'
        os.rename(os.path.join(folder, file), os.path.join(folder, dt_ms + fileExtension))
        file = dt_ms + fileExtension

    if ENABLE_RAR and (file.endswith(".rar") or file.endswith(".zip")):
        winRarReturn = winRarDo(folder, file, PASSWD[0])
        if winRarReturn == 0:
            successThisFile = True
        elif winRarReturn == 2:
            pass
        else:
            getCommentStr = " l -p0 -z" + " \"" + folder + "\\" + file + "\""
            commentNumber = subprocess.call("@\"" + LOC_WINRAR + PROGRAM_RAR + "\"" + getCommentStr)
            if commentNumber == 0:
                commentM = subprocess.getstatusoutput("@\"" + LOC_WINRAR + PROGRAM_RAR + "\"" + getCommentStr)
                if commentM[0] == 0:
                    try:
                        comment = commentM[1][(commentM[1].index("\n\n") + 2):commentM[1].index(folder)]
                        comment = comment[0:comment.rindex("\n\n")]
                    except:
                        pass
                    else:
                        # print(comment)
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
            if not successThisFile:
                for index in range(1, len(PASSWD)):
                    winRarReturn = winRarDo(folder, file, PASSWD[index])
                    if winRarReturn == 1:
                        continue
                    elif winRarReturn == 0:
                        successThisFile = True
                        PASSWD[0], PASSWD[index] = PASSWD[index], PASSWD[0]
                        break
                    elif winRarReturn == 2:
                        break
                    else:
                        break

    elif not successThisFile:
        if ENABLE_7Z:
            for index in range(len(PASSWD)):
                z7Return = z7Do(folder, file, PASSWD[index])
                if z7Return == 1:
                    continue
                elif z7Return == 3:
                    logError("Broken file: " + file)
                    break
                else:
                    successThisFile = True
                    PASSWD[0], PASSWD[index] = PASSWD[index], PASSWD[0]
                    break

    if not successThisFile:
        if RENAME_UNRAR and not multiPart:
            os.rename(os.path.join(folder, file), os.path.join(folder, originalName))
        logError("No passsword for: " + originalName)
    else:
        if DELETEIT:
            if multiPart:
                for multiFile in multiPartList:
                    os.remove(os.path.join(folder, multiFile))
            else:
                os.remove(os.path.join(folder, file))
            multiLevelUnrar()
        elif RENAME_UNRAR and not multiPart:
            moveTemp = os.path.join(folder, originalName)
            originalPath = moveTemp
            i = 0
            while os.path.exists(moveTemp):
                i += 1
                moveTemp = fileRename(originalPath, i)
            os.rename(os.path.join(folder, file), moveTemp)


def multiLevelUnrar():
    global workSpace, lastFileName, lastFileSize, lastSpaceFiles, newSpaceFiles
    if MULTI_UNRAR:
        newSpaceFiles = os.listdir(workSpace)
        for file in newSpaceFiles:
            if os.path.isfile(os.path.join(workSpace, file)):
                if file not in lastSpaceFiles or (file == lastFileName and DELETEIT):
                    newFileSize = os.path.getsize(os.path.join(workSpace, file))
                    if newFileSize * 1.3 > lastFileSize:
                        if unrarFun2(os.path.join(workSpace, file), True):
                            break
            else:
                if file not in lastSpaceFiles:
                    newFileList = os.listdir(os.path.join(workSpace, file))
                    if len(newFileList) < 5:
                        for rarFile in newFileList:
                            filePath = os.path.join(workSpace, file, rarFile)
                            if isCompressedFile(filePath):
                                newFileSize = os.path.getsize(filePath)
                                if newFileSize * 1.3 > lastFileSize:
                                    if unrarFun2(filePath, True):
                                        break


def getMultiPartInFolder(folder, startName, ext, rarType):
    # rarType: 0:like abc.7z.001
    #          1:like abc.part1.rar
    fileList = []
    if rarType == 1:
        for file in os.listdir(folder):
            if file.startswith(startName + '.'):
                if file[len(startName) + 1:].startswith('part'):
                    if file.endswith(ext):
                        fileList.append(file)
    else:
        for file in os.listdir(folder):
            if file.startswith(startName + '.'):
                if file[len(startName) + 1:].startswith(ext + '.'):
                    fileList.append(file)
    return fileList


def getMultiPart(filePath):
    name = os.path.split(filePath)[1]
    parentFolder = os.path.split(filePath)[0]
    if '.' in name:
        nameSplit = name.split('.')
        if len(nameSplit) <= 2:
            return []
        elif len(nameSplit) == 3:
            startName = nameSplit[0]
            endExt = ''
            middleExt = ''
            for ext in NOT_RAR_FILE:
                if nameSplit[2] == ext:
                    return []
            for rar in RAR_FILE:
                if nameSplit[2] == rar:
                    endExt = rar
                    break
                elif nameSplit[1] == rar:
                    middleExt = rar
                    break
            if endExt:
                rarType = 1
                return getMultiPartInFolder(parentFolder, startName, endExt, rarType)
            elif middleExt:
                rarType = 0
                return getMultiPartInFolder(parentFolder, startName, middleExt, rarType)
    return []


def unrarFun2(filePath, multiUnrar=False):
    global lastFileName, lastFileSize, multiPartList
    multiPartList = getMultiPart(filePath)
    if multiPartList:
        if not multiPartList[0] in multiPartExtracted:
            multiPartExtracted.extend(multiPartList)
            for multiFile in multiPartList:
                if multiFile.endswith('.001') or '.part1.' in multiFile or '.part01.' in multiFile or '.part001.' in multiFile:
                    lastFileName = multiFile
                    lastFileSize = os.path.getsize(os.path.join(workSpace, multiFile)) * len(multiPartList)
                    unrarFun3(workSpace, multiFile, True)
                    return True
    elif isCompressedFile(filePath, multiUnrar):
        lastFileSize = os.path.getsize(filePath)
        unrarFun3('', filePath)
        return True
    return False


def unrarFun1(folder):
    global workSpace, lastSpaceFiles
    if os.path.exists(folder):
        if os.path.isdir(folder):
            print(folder)
            workSpace = folder
            file_list = os.listdir(folder)
            lastSpaceFiles = file_list
            for file in file_list:
                filePath = os.path.join(folder, file)
                if os.path.exists(filePath):
                    if os.path.isfile(filePath):
                        unrarFun2(filePath)
        else:
            workSpace = os.path.split(folder)[0]
            lastSpaceFiles = os.listdir(workSpace)
            unrarFun2(folder)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.exit(1)
    testWinRAR = os.popen("\"" + LOC_WINRAR + PROGRAM_RAR + "\"").read()
    if not testWinRAR:
        for loc in LOC_S_WINRAR:
            testWinRAR = os.popen("\"" + loc + PROGRAM_RAR + "\"").read()
            if testWinRAR:
                LOC_WINRAR = loc
                ENABLE_RAR = True
                break
    else:
        ENABLE_RAR = True

    test7z = os.popen("\"" + LOC_7Z + PROGRAM_7Z + "\"").read()
    if not test7z:
        for loc in LOC_S_7Z:
            test7z = os.popen("\"" + loc + PROGRAM_7Z + "\"").read()
            if test7z:
                LOC_7Z = loc
                ENABLE_7Z = True
                break
    else:
        ENABLE_7Z = True

    if (not ENABLE_RAR) and (not ENABLE_7Z):
        print("Cannot find winRAR or 7-zip")
        sys.exit(1)
    if len(sys.argv) > 1:
        while len(PASSWD) < 2:
            PASSWD.append("0")
        oldPasswordLength = len(PASSWD)
        getPWFromFolder(sys.argv[1])
        newPasswordLength = len(PASSWD)
        addWD = newPasswordLength - oldPasswordLength
        if addWD > 8:
            PASSWD = PASSWD[addWD:] + PASSWD[:addWD]
        if os.path.isfile(sys.argv[1]):
            SAVE_MODE = False
        # print(PASSWD)
        # subprocess.call("pause")
        for inputFolder in sys.argv[1:]:
            # print(inputFolder)
            unrarFun1(inputFolder)
        print("Finish.")
        if ERROR_LIST:
            print(ERROR_LIST)
            subprocess.call("pause")
