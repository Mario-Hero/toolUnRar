#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Created by Mario Chen, 04.04.2021, Shenzhen
# My Github site: https://github.com/Mario-Hero
import random
import shutil
import sys
import os
import subprocess
import platform

try:
    import chardet
    chardetEnable = True
except ImportError:
    print('Please install chardet')
    chardetEnable = False

# you can change it >>>>>
DEFAULT_TARGET = ''
PASSWD = ['123456', 'hello']  # 可能的密码 possible passwords
DELETEIT = False  # 注意！解压后删除压缩包 DANGER!! If it is True,will delete rar file after extraction
LOC_WINRAR = "C:\\Program Files\\WinRAR\\"  # location of WinRAR
LOC_7Z = "C:\\Program Files\\7-Zip\\"  # location of 7-Zip
# 如果文件后缀看上去不像压缩文件，就不解压，除非用户拖入的是文件 if the extension name of file doesn't look like a compressed file, then do nothing
# with it, unless the user drag files into this script.

SAVE_MODE = True
MULTI_UNRAR = DELETEIT and True  # 解压双重压缩文件 unzip double compressed files
COLLECT_FILES = True  # 如果解压出的文件非常多且都在当前文件夹下，就会把它们移动到当前文件夹下的一个新的文件夹里
# <<<<< you can change it


PROGRAM_RAR = "UnRAR.exe"  # the program we use
PROGRAM_7Z = "7z.exe"  # the program we use
PROGRAM_7Z_LINUX = "7zzs"  # the program we use on Linux
LOC_S_WINRAR = ["C:\\Program Files\\WinRAR\\", "C:\\Program Files (x86)\\WinRAR\\", "./",
                ""]  # some possible locations of WinRAR
LOC_S_7Z = ["C:\\Program Files\\7-Zip\\", "C:\\Program Files (x86)\\7-Zip\\", "./",
            ""]  # some possible locations of 7-Zip
RAR_FILE = {"rar", "zip", "7z", "tar", "gz", "xz", "bzip2", "gzip", "wim", "arj", "cab", "chm", "cpio", "cramfs", "deb",
            "dmg", "fat", "hfs", "iso", "lzh", "lzma", "mbr", "msi", "nsis", "ntfs", "rpm", "squashfs", "udf", "vhd",
            "xar", "z"}
NOT_RAR_FILE = {"jpg", "exe", "png", "mkv", "mp4", "mp3", "avi", "mov", "jpeg", "wav", "gif", "mpeg", "webp", "txt",
                "doc", "docx", "ppt", "pptx", "xls", "xlsx", "html", "wps", "torrent", "swf", "bmp", "crdownload",
                "xltd", "downloading", "py"}
VAR_STR = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
PAUSE_COMMAND = "pause"
PAUSE_COMMAND_LINUX = "read -n1 -p \"Press any key to continue...\""
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
lastFileStartName = ''
lastMultiPart = False


class myPasswordLib:
    def __init__(self):
        self.keyList = []
        self.newList = []
        self.oldList = PASSWD
        self.lastPWD = ''
        self.traverseList = PASSWD.copy()

    def printWD(self):
        print("Key:")
        print(self.keyList)
        print("New:")
        print(self.newList)
        print("Old:")
        print(self.oldList)

    def add(self, pwd, isKey=True):
        if pwd in self.keyList or pwd in self.newList or pwd in self.oldList:
            return False
        else:
            if isKey:
                self.keyList.append(pwd)
            else:
                self.newList.append(pwd)
            return True

    def updateLastPWD(self, pwd=''):
        if pwd:
            if self.lastPWD != pwd:
                self.lastPWD = pwd
                if len(self.newList) < 8:
                    returnList = [self.lastPWD] + \
                                 self.keyList + self.newList + self.oldList
                else:
                    returnList = [self.lastPWD] + \
                                 self.keyList + self.oldList + self.newList
                for i in range(len(returnList) - 1):
                    if returnList[i + 1] == self.lastPWD:
                        returnList.pop(i + 1)
                        break
                self.traverseList = returnList
        else:
            if self.lastPWD:
                if len(self.newList) < 8:
                    returnList = [self.lastPWD] + \
                                 self.keyList + self.newList + self.oldList
                else:
                    returnList = [self.lastPWD] + \
                                 self.keyList + self.oldList + self.newList
                for i in range(len(returnList) - 1):
                    if returnList[i + 1] == self.lastPWD:
                        returnList.pop(i + 1)
                        break
                self.traverseList = returnList
            else:
                if len(self.newList) < 8:
                    self.traverseList = self.keyList + self.newList + self.oldList
                else:
                    self.traverseList = self.keyList + self.oldList + self.newList


passwdlib = myPasswordLib()


def logError(comment):
    global ERROR_LIST
    ERROR_LIST += comment + '\n'


def randomName():
    randomFileName = 'RAR'
    for i in range(random.randint(8, 15)):
        randomFileName += random.choice(VAR_STR)
    return randomFileName


def guessWDComment(comment):
    global passwdlib
    guessFlag = 0
    guessWD = []
    guessPS = 0
    cutIn = 0
    cutOut = 0
    isKey = False
    while True:
        if guessFlag == 0:
            isKey = False
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
                    isKey = False
                else:
                    break
            else:
                isKey = True
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
                        passwdlib.add(wd.strip(), isKey)
                        guessWD.append(wd.strip())
                    break
            if not foundCutTemp:
                passwdlib.add(comment[cutIn:cutOut].strip(), isKey)
                guessWD.append(comment[cutIn:cutOut].strip())
            guessFlag = 0
        else:
            guessFlag = 0
    return guessWD


def fileNameGuess(fileName):
    global passwdlib
    for wd in GUESS_FLAG_INIT:
        if wd in fileName:
            if guessWDComment(fileName):
                return True
            else:
                return False
    addNewPWD = False
    if ' ' in fileName:
        for fileNamePart in fileName.split(' '):
            addNewPWD = passwdlib.add(fileNamePart, False) | addNewPWD
    addNewPWD = passwdlib.add(fileName, False) | addNewPWD
    return addNewPWD


def getPWFromFolder(file):
    addNewPWD = False
    if os.path.isdir(file):
        folderName = os.path.split(file)[1]
        addNewPWD = fileNameGuess(folderName) | addNewPWD
        file_list = os.listdir(file)
        for oneFile in file_list:
            if oneFile.endswith('.txt'):
                oneFileName = oneFile[:-4]
                addNewPWD = fileNameGuess(oneFileName) | addNewPWD
                readTxtFile(os.path.join(file, oneFile))
            else:
                addNewPWD = fileNameGuess(os.path.splitext(oneFile)[0]) | addNewPWD
    else:
        parentFolder, fileName = os.path.split(file)
        if "." in fileName:
            fileNamePart = fileName[:fileName.rindex('.')]
        else:
            fileNamePart = fileName
        folderName = os.path.split(parentFolder)[1]
        addNewPWD = fileNameGuess(fileNamePart) | addNewPWD
        addNewPWD = fileNameGuess(folderName) | addNewPWD
        file_list = os.listdir(parentFolder)
        for oneFile in file_list:
            if oneFile.endswith('.txt'):
                oneFileName = oneFile[:-4]
                addNewPWD = fileNameGuess(oneFileName) | addNewPWD
                readTxtFile(os.path.join(parentFolder, oneFile))
            else:
                addNewPWD = fileNameGuess(os.path.splitext(oneFile)[0]) | addNewPWD
    return addNewPWD


def isCompressedFile(file, multiUnrar=False):
    if "." in file:
        fileExtension = file[file.rindex('.') + 1:].lower()
        if fileExtension in RAR_FILE:
            return True
        if "删" in fileExtension:
            return True
        if fileExtension in NOT_RAR_FILE:
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
        [os.path.join(LOC_7Z, PROGRAM_7Z), 'x', '-y', '-p' + wd,
         os.path.join(folder, file), '-o' + folder],
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
    global passwdlib
    successThisFile = False
    if not folder:
        folder, file = os.path.split(file)
    originalName = file
    if RENAME_UNRAR and not multiPart:  # 分卷解压不重命名
        if '.' in file:
            fileExtension = file[file.rindex('.'):]
        else:
            fileExtension = ''
        dt_ms = randomName() + fileExtension
        # dt_ms = 'RAR' + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        while os.path.exists(os.path.join(folder, dt_ms)):
            dt_ms = randomName() + fileExtension
        os.rename(os.path.join(folder, file), os.path.join(folder, dt_ms))
        file = dt_ms

    if ENABLE_RAR and file.endswith('.rar'):
        if passwdlib.lastPWD:
            winRarReturn = winRarDo(folder, file, passwdlib.lastPWD)
        else:
            winRarReturn = winRarDo(folder, file, '666')
        if winRarReturn == 0:
            successThisFile = True
        elif winRarReturn == 2:
            pass
        else:
            getCommentStr = " l -p0 -z" + " \"" + folder + "\\" + file + "\""
            print("\"" + LOC_WINRAR + PROGRAM_RAR + "\"" + getCommentStr)
            commentNumber = subprocess.call(
                "\"" + LOC_WINRAR + PROGRAM_RAR + "\"" + getCommentStr)

            if commentNumber == 0:
                commentM = subprocess.getstatusoutput(
                    "\"" + LOC_WINRAR + PROGRAM_RAR + "\"" + getCommentStr)
                if commentM[0] == 0:
                    try:
                        comment = commentM[1][(commentM[1].index(
                            "\n\n") + 2):commentM[1].index(folder)]
                        comment = comment[0:comment.rindex("\n\n")]
                    except:
                        pass
                    else:
                        # print(comment)
                        if comment:
                            # wdArray = guessWDComment(comment)
                            guessWDComment(comment)
                            passwdlib.updateLastPWD()
                            # print("Possible passwords:", wdArray)
            if not successThisFile:
                for wd in passwdlib.traverseList:
                    winRarReturn = winRarDo(folder, file, wd)
                    if winRarReturn == 1:
                        continue
                    elif winRarReturn == 0:
                        successThisFile = True
                        passwdlib.updateLastPWD(wd)
                        break
                    elif winRarReturn == 2:
                        break
                    else:
                        break
    elif ENABLE_7Z:
        if not successThisFile:
            for wd in passwdlib.traverseList:
                z7Return = z7Do(folder, file, wd)
                if z7Return == 1:
                    continue
                elif z7Return == 3:
                    logError("Broken file: " + file)
                    break
                else:
                    successThisFile = True
                    passwdlib.updateLastPWD(wd)
                    break

    if not successThisFile:
        if RENAME_UNRAR and not multiPart:
            os.rename(os.path.join(folder, file),
                      os.path.join(folder, originalName))
        logError("No passsword for: " + originalName)
    else:
        if DELETEIT:
            if multiPart:
                for multiFile in multiPartList:
                    os.remove(os.path.join(folder, multiFile))
            else:
                os.remove(os.path.join(folder, file))
            multiLevelUnrar()
            collectFiles()
        elif RENAME_UNRAR and not multiPart:
            moveTemp = os.path.join(folder, originalName)
            originalPath = moveTemp
            i = 0
            while os.path.exists(moveTemp):
                i += 1
                moveTemp = fileRename(originalPath, i)
            os.rename(os.path.join(folder, file), moveTemp)
            collectFiles()


def collectFiles():
    global workSpace, lastFileName, lastFileSize, lastSpaceFiles, newSpaceFiles, lastFileStartName, lastMultiPart
    if COLLECT_FILES:
        newFileList = []
        for file in os.listdir(workSpace):
            if os.path.isfile(os.path.join(workSpace, file)):
                if not (file in lastSpaceFiles):
                    newFileList.append(file)
            else:
                if not (file in lastSpaceFiles):
                    return
        # print(newFileList)
        if len(newFileList) > 7:
            if not lastMultiPart:
                if '.' in lastFileName:
                    newFolderName = lastFileName[:lastFileName.rfind('.')]
                else:
                    newFolderName = lastFileName
            else:
                newFolderName = lastFileStartName
            newFolderPath = os.path.join(workSpace, newFolderName)
            if not os.path.exists(newFolderPath):
                os.mkdir(newFolderPath)
            for file in newFileList:
                shutil.move(os.path.join(workSpace, file), newFolderPath)


def readTxtFile(txtFile):
    if chardetEnable:
        f = open(txtFile, 'rb')
        data = f.read()
        fileEncoding = chardet.detect(data).get('encoding')
        with open(txtFile, 'r', encoding=fileEncoding) as ff:
            guessWDComment(ff.read())
    else:
        try:
            with open(txtFile, 'r') as f:
                guessWDComment(f.read())
        except:
            try:
                with open(txtFile, 'r', encoding='utf-8') as f:
                    guessWDComment(f.read())
            except:
                pass


def multiLevelUnrar():
    global workSpace, lastFileName, lastFileSize, lastSpaceFiles, newSpaceFiles
    if MULTI_UNRAR:
        newSpaceFiles = os.listdir(workSpace)
        getPWFromFolder(workSpace)
        for file in newSpaceFiles:
            if os.path.isfile(os.path.join(workSpace, file)):
                if file not in lastSpaceFiles or (file == lastFileName and DELETEIT):
                    newFileSize = os.path.getsize(
                        os.path.join(workSpace, file))
                    if newFileSize * 1.3 > lastFileSize or isMultiFile(file):
                        if unrarFun2(os.path.join(workSpace, file), True):
                            break
            else:
                if file not in lastSpaceFiles:
                    getPWFromFolder(os.path.join(workSpace, file))
                    newFileList = os.listdir(os.path.join(workSpace, file))
                    if len(newFileList) < 5:
                        for rarFile in newFileList:
                            filePath = os.path.join(workSpace, file, rarFile)
                            if isCompressedFile(filePath):
                                newFileSize = os.path.getsize(filePath)
                                if newFileSize * 1.3 > lastFileSize or isMultiFile(file):
                                    if unrarFun2(filePath, True):
                                        break


def getMultiPartInFolder(folder, startName, ext, rarType):
    # rarType: 0:like abc.7z.001
    #          1:like abc.part1.rar
    #          2:like abc.zip, abc.z01
    fileList = []
    if rarType == 1:
        for file in os.listdir(folder):
            if file.startswith(startName + '.'):
                if file[len(startName) + 1:].startswith('part'):
                    if file.endswith(ext):
                        fileList.append(file)
    elif rarType == 0:
        for file in os.listdir(folder):
            if file.startswith(startName + '.'):
                if file[len(startName) + 1:].startswith(ext + '.'):
                    fileList.append(file)
    else:
        foundZip = False
        foundZipPart = False
        for file in os.listdir(folder):
            if file.startswith(startName + '.z') and file[-1].isdigit():
                foundZipPart = True
                fileList.append(file)
            elif file == startName + '.zip':
                foundZip = True
                fileList.append(file)
        if foundZip and foundZipPart:
            return fileList
        else:
            return []
    return fileList


def getMultiPart(filePath):
    # rarType: 0:like abc.7z.001
    #          1:like abc.part1.rar
    #          2:like abc.zip, abc.z01
    global lastFileStartName
    parentFolder, name = os.path.split(filePath)
    if '.' in name:
        nameSplit = name.split('.')
        if len(nameSplit) <= 2:
            if nameSplit[1] == 'zip' or (nameSplit[1].startswith('z') and nameSplit[1][-1].isdigit()):
                return getMultiPartInFolder(parentFolder, nameSplit[0], 'zip', 2)
            else:
                return []
        elif len(nameSplit) > 3:
            newSplit = []
            for i in range(len(nameSplit)):
                if i == 0:
                    newSplit.append(nameSplit[0])
                elif i <= len(nameSplit) - 3:
                    newSplit[0] += '.' + nameSplit[i]
                else:
                    newSplit.append(nameSplit[i])
            nameSplit = newSplit
            print(nameSplit)
        if len(nameSplit) == 3:
            startName = nameSplit[0]
            endExt = ''
            middleExt = ''
            if nameSplit[2] in NOT_RAR_FILE:
                return []

            if nameSplit[2] in RAR_FILE:
                endExt = nameSplit[2]
            elif nameSplit[1] in RAR_FILE:
                middleExt = nameSplit[1]

            lastFileStartName = startName
            if endExt:
                rarType = 1
                # print(endExt)
                return getMultiPartInFolder(parentFolder, startName, endExt, rarType)
            elif middleExt:
                rarType = 0
                # print(middleExt)
                return getMultiPartInFolder(parentFolder, startName, middleExt, rarType)
    return []


def isMultiFile(multiFile):
    return multiFile.endswith('.zip') or multiFile.endswith(
        '.001') or '.part1.' in multiFile or '.part01.' in multiFile or '.part001.' in multiFile


def unrarFun2(filePath, multiUnrar=False):
    global lastFileName, lastFileSize, multiPartList, lastMultiPart, multiPartExtracted
    multiPartList = getMultiPart(filePath)
    if multiPartList:
        if len(multiPartList) > 1:
            if not multiPartList[0] in multiPartExtracted:
                multiPartExtracted.extend(multiPartList)
                for multiFile in multiPartList:
                    if isMultiFile(multiFile):
                        lastFileName = multiFile
                        lastMultiPart = True
                        lastFileSize = os.path.getsize(os.path.join(
                            workSpace, multiFile)) * len(multiPartList)
                        unrarFun3(workSpace, multiFile, True)
                        return True
        else:
            return False
    elif isCompressedFile(filePath, multiUnrar):
        lastFileName = os.path.split(filePath)[1]
        lastMultiPart = False
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
    if len(sys.argv) <= 1 and not DEFAULT_TARGET:
        sys.exit(1)
    if platform.system() == 'Windows':
        testWinRAR = os.popen(os.path.join(LOC_WINRAR, PROGRAM_RAR)).read()
        if not testWinRAR:
            for loc in LOC_S_WINRAR:
                testWinRAR = os.popen(os.path.join(loc, PROGRAM_RAR)).read()
                if testWinRAR:
                    LOC_WINRAR = loc
                    ENABLE_RAR = True
                    break
        else:
            ENABLE_RAR = True
        test7z = os.popen(os.path.join(LOC_7Z, PROGRAM_7Z)).read()
        if not test7z:
            for loc in LOC_S_7Z:
                test7z = os.popen(os.path.join(loc, PROGRAM_7Z)).read()
                if test7z:
                    LOC_7Z = loc
                    ENABLE_7Z = True
                    break
        else:
            ENABLE_7Z = True

        if (not ENABLE_RAR) and (not ENABLE_7Z):
            print("Cannot find winRAR or 7-zip")
            sys.exit(1)
    elif platform.system() == 'Linux':
        PAUSE_COMMAND = PAUSE_COMMAND_LINUX
        LOC_7Z = os.path.join(
            os.path.split(sys.argv[0])[0])
        PROGRAM_7Z = PROGRAM_7Z_LINUX
        test7z = os.popen(os.path.join(LOC_7Z, PROGRAM_7Z)).read()
        if not test7z:
            print("Cannot find 7-zip")
            sys.exit(1)
        else:
            ENABLE_7Z = True

    while len(passwdlib.oldList) < 2:
        passwdlib.oldList.append("0")

    checkEveryFilePassWD = True
    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]) and os.path.isfile(sys.argv[1]):
            SAVE_MODE = False
        # print(PASSWD)
        passwdlib.updateLastPWD()
        if not checkEveryFilePassWD:
            if getPWFromFolder(sys.argv[1]):
                passwdlib.updateLastPWD()
        for inputFolder in sys.argv[1:]:
            if os.path.exists(sys.argv[1]):
                if checkEveryFilePassWD:
                    if getPWFromFolder(inputFolder):
                        passwdlib.updateLastPWD()
                unrarFun1(inputFolder)
            else:
                print(inputFolder + " not exists.")
        print("Finish.")
        if ERROR_LIST:
            print(ERROR_LIST)
            os.system(PAUSE_COMMAND)
    elif DEFAULT_TARGET:
        getPWFromFolder(DEFAULT_TARGET)
        if os.path.isfile(DEFAULT_TARGET):
            SAVE_MODE = False
        # print(PASSWD)
        passwdlib.updateLastPWD()
        unrarFun1(DEFAULT_TARGET)
        print("Finish.")
        if ERROR_LIST:
            print(ERROR_LIST)
            os.system(PAUSE_COMMAND)
