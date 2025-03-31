#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Created by Mario Chen, 04.04.2021, Shenzhen
# My GitHub site: https://github.com/Mario-Hero
import random
import shutil
import sys
import os
import subprocess
import platform

chardetEnable = False
try:
    import chardet

    chardetEnable = True
except ImportError:
    print('Please install chardet')

# you can change it 用户配置 >>>>>
DEFAULT_TARGET = ''  # 默认解压目标 default decompress target
PASSWD = ['123456','hello']  # 可能的密码 possible passwords
DELETEIT = False  # 注意！解压后删除压缩包 DANGER!! If it is True,will delete rar file after extraction
LOC_WINRAR = "C:\\Program Files\\WinRAR\\"  # location of WinRAR
LOC_7Z = "C:\\Program Files\\7-Zip\\"  # location of 7-Zip
SAVE_MODE = True
# SAVE_MODE: 为真时，如果文件后缀看上去不像压缩文件，就不尝试解压。除非用户只拖入了文件而没拖入文件夹
# SAVE_MODE: If it is True, if the extension name of file doesn't look like a compressed file, then do nothing with it,
# unless the user only drag files into this script.
MULTI_UNRAR = DELETEIT and True  # 解压双重压缩文件 unzip double compressed files
COLLECT_FILES = True  # 如果解压出的文件非常多且都在当前文件夹下，就会把它们移动到当前文件夹下的一个新的文件夹里
TRAVERSE_ALL_FOLDERS = False  # 为真时，遍历所有子文件夹并解压缩。但是不在子文件夹里找密码。
# If it is True, it will traverse all folders and decompress. But it will not search passwords in sub folders.
# <<<<< 用户配置 you can change it


PROGRAM_RAR = "UnRAR.exe"  # the program we use on Windows
PROGRAM_7Z = "7z.exe"  # the program we use on Windows
PROGRAM_7Z_LINUX = "7zzs"  # the program we use on Linux
PROGRAM_7Z_MAC = "7zz"  # the program we use on Mac
LOC_S_WINRAR = ["C:\\Program Files\\WinRAR\\", "C:\\Program Files (x86)\\WinRAR\\", "./",
                ""]  # some possible locations of WinRAR
LOC_S_7Z = ["C:\\Program Files\\7-Zip\\", "C:\\Program Files (x86)\\7-Zip\\", "./",
            ""]  # some possible locations of 7-Zip
RAR_FILE = {"rar", "zip", "7z", "tar", "gz", "xz", "bzip2", "gzip", "wim", "arj", "cab", "chm", "cpio", "cramfs", "deb",
            "dmg", "fat", "hfs", "iso", "lzh", "lzma", "mbr", "msi", "nsis", "ntfs", "rpm", "squashfs", "udf", "vhd",
            "xar", "z"}

NOT_RAR_FILE = {"jpg", "exe", "png", "mkv", "mp4", "mp3", "avi", "mov", "jpeg", "wav", "gif", "mpeg", "webp", "txt",
                "doc", "docx", "ppt", "pptx", "xls", "xlsx", "html", "wps", "torrent", "swf", "bmp", "crdownload",
                "xltd", "downloading", "py", "lnk"}

QUIT_KEYWORD = {'CRC Failed', 'Data Error in encrypted file'}

VAR_STR = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
PAUSE_COMMAND_WINDOWS = "pause"
PAUSE_COMMAND_LINUX = "read -n1 -p \"Press any key to continue...\""
ENABLE_RAR = False  # initial state only
ENABLE_7Z = False  # initial state only
RENAME_UNRAR = True  # 防止解压的文件与压缩包重名 In order to prevent that the decompressed file has the same name with current file, we rename the compressed file first

# for guessing >>>
GUESS_FLAG_INIT = ["密码", "码", "password", "Password"]  # state 0
GUESS_FLAG_START_1 = [":", "："]  # state 1
GUESS_FLAG_START_2 = ["是", "为", "is", "are", " "]  # state 1
GUESS_FLAG_END = ["\n", "   "]  # state 2
GUESS_FLAG_DIVIDE = ["或是", "或", " or "]  # state 3
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
ignoreExtOnce = False


class MyPasswordLib:
    """密码库 Password library"""

    def __init__(self):
        self.keyList = []
        self.newList = []
        self.oldList = PASSWD
        self.lastPWD = ''
        self.traverseList = PASSWD.copy()

    def print_wd(self):
        print("Key:")
        print(self.keyList)
        print("New:")
        print(self.newList)
        print("Old:")
        print(self.oldList)

    def add(self, pwd, isKey=True):
        print(pwd)
        if pwd in self.keyList or pwd in self.newList or pwd in self.oldList:
            return False
        else:
            if isKey:
                self.keyList.append(pwd)
            else:
                self.newList.append(pwd)
            return True

    def update_last_pwd(self, pwd=''):
        """用最后一个密码更新密码库 Update the password lib with the last password"""
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


passwdlib = MyPasswordLib()


def log_error(comment):
    global ERROR_LIST
    ERROR_LIST += comment + '\n'


def random_name():
    """生成随机文件名 Generate a random file name"""
    random_file_name = 'RAR'
    for i in range(random.randint(8, 15)):
        random_file_name += random.choice(VAR_STR)
    return random_file_name


def guess_password_from_comment(comment):
    """从注释中猜测密码 Guess password from comment"""
    global passwdlib
    state = 0
    guessWD = []
    guessPS = 0
    cutIn = 0
    cutOut = 0
    isKey = False
    while True:
        if state == 0:
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
                    state = 3
                    isKey = False
                else:
                    break
            else:
                isKey = True
                guessPS = guessNewPS + guessLen
                state = 1
        elif state == 1:
            foundTemp = False
            foundTemp2 = False
            guessNewPS = len(comment)
            for startStr in GUESS_FLAG_START_1:
                PSTemp = comment.find(startStr, guessPS, guessPS + 20)
                if PSTemp == -1:
                    continue
                else:
                    if PSTemp < guessNewPS and comment.find('\n', guessPS, guessPS + PSTemp) == -1:
                        foundTemp = True
                        guessNewPS = PSTemp + len(startStr)
                        state = 2
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
            state = 2
        elif state == 2:
            guessNewPS = len(comment)
            for endStr in GUESS_FLAG_END:
                PSTemp = comment.find(endStr, guessPS)
                if PSTemp == -1:
                    continue
                else:
                    if PSTemp < guessNewPS:
                        guessNewPS = PSTemp
            guessPS = guessNewPS
            state = 3
            cutOut = guessPS
        elif state == 3:
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
            state = 0
        else:
            state = 0
    return guessWD


def guess_password_from_filename(fileName):
    """从文件名中猜测密码 Guess password from file name"""
    global passwdlib
    for wd in GUESS_FLAG_INIT:
        if wd in fileName:
            if guess_password_from_comment(fileName):
                return True
            else:
                return False
    addNewPWD = False
    if ' ' in fileName:
        for fileNamePart in fileName.split(' '):
            addNewPWD = passwdlib.add(fileNamePart, False) | addNewPWD
    addNewPWD = passwdlib.add(fileName, False) | addNewPWD
    return addNewPWD


def get_password_from_folder(folder):
    """从文件夹中获得密码，不读取子文件夹下的文件 Get password from folder without reading files in sub folders"""
    addNewPWD = False
    file_list = os.listdir(folder)
    for file in file_list:
        file_path = os.path.join(folder, file)
        if os.path.isdir(file_path):
            addNewPWD = guess_password_from_filename(file) | addNewPWD
        else:
            addNewPWD = guess_password_from_filename(os.path.splitext(file)[0]) | addNewPWD
            if file.endswith('.txt'):
                read_txt_file(file_path)
    return addNewPWD


def get_password_from(file):
    """从文件或文件夹中获得密码 Get password from folder or file"""
    addNewPWD = False
    if os.path.isdir(file):
        folderName = os.path.split(file)[1]
        parentFolder = os.path.dirname(file)
        parentFolderName = os.path.split(parentFolder)[1]
        addNewPWD = guess_password_from_filename(folderName) | addNewPWD
        addNewPWD = guess_password_from_filename(parentFolderName) | addNewPWD
        addNewPWD = get_password_from_folder(file) | addNewPWD
    else:
        parentFolder, fileName = os.path.split(file)
        if "." in fileName:
            fileNamePart = fileName[:fileName.rindex('.')]
        else:
            fileNamePart = fileName
        folderName = os.path.split(parentFolder)[1]
        addNewPWD = guess_password_from_filename(fileNamePart) | addNewPWD
        addNewPWD = guess_password_from_filename(folderName) | addNewPWD
        addNewPWD = get_password_from_folder(parentFolder) | addNewPWD
    return addNewPWD


def is_compressed_file(file, multiUnrar=False):
    """判断是否是压缩文件 Determine whether it is a compressed file"""
    global ignoreExtOnce
    if ignoreExtOnce:
        ignoreExtOnce = False
        return True
    if "." in file:
        fileExtension = file[file.rindex('.') + 1:].lower()
        if fileExtension in RAR_FILE:
            return True
        if "删" in fileExtension:
            return True
        if fileExtension in NOT_RAR_FILE:
            return False
    return (not SAVE_MODE) or multiUnrar


def file_rename(file, n):
    """重命名文件 Rename file"""
    pathName, fileName = os.path.split(file)
    if '.' in fileName:
        cutPos = fileName.rfind('.')
        return os.path.join(pathName, fileName[:cutPos] + '(' + str(n) + ')' + fileName[cutPos:])
    else:
        return os.path.join(pathName, fileName + '(' + str(n) + ')')


def run_command(command):
    """运行命令 Run command"""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # Read stdout line by line
    while True:
        output = process.stdout.readline().decode('utf-8', errors='ignore')
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            for word in QUIT_KEYWORD:
                if word in output:
                    process.terminate()
                    return 99

    return process.returncode


def winrar_do(folder, file, password):
    """用WinRAR解压缩 Use WinRAR to decompress"""
    extM = run_command(
        [os.path.join(LOC_WINRAR, PROGRAM_RAR), 'x', '-y', '-p' + password, os.path.join(folder, file), folder])
    # print("winrar", extM)
    if extM == 1:  # not rar file
        return 2
    elif extM == 11 or extM == 99:  # wrong password
        return 1
    elif extM == 2:  # broken file
        return 3
    elif extM != 0:  # error
        return 1
    else:
        print("File: " + file + " Password: " + password)
        return 0


def z7_do(folder, file, password):
    """用7-Zip解压缩 Use 7-Zip to decompress"""
    extM = run_command([os.path.join(LOC_7Z, PROGRAM_7Z), 'x', '-y', '-p' + password,
                        os.path.join(folder, file), '-o' + folder])
    # print("7z", extM)
    if extM != 0:  # error
        return 1
    else:
        print("File: " + file + " Password: " + password)
        return 0


def unrar_fun3(folder, file, multiPart=False):
    global passwdlib
    successThisFile = False
    if not folder:
        folder, file = os.path.split(file)
    originalName = file
    shouldUseWinRAR = file.endswith('.rar')
    if RENAME_UNRAR and not multiPart:  # 分卷解压不重命名 Multipart file decompression without renaming
        if '.' in file:
            fileExtension = file[file.rindex('.'):]
        else:
            fileExtension = ''
        dt_ms = random_name() + fileExtension
        # dt_ms = 'RAR' + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        while os.path.exists(os.path.join(folder, dt_ms)):
            dt_ms = random_name() + fileExtension
        os.rename(os.path.join(folder, file), os.path.join(folder, dt_ms))
        file = dt_ms

    if (ENABLE_RAR and shouldUseWinRAR) or not ENABLE_7Z:
        if passwdlib.lastPWD:
            winRarReturn = winrar_do(folder, file, passwdlib.lastPWD)
        else:
            winRarReturn = winrar_do(folder, file, '123')
        if winRarReturn == 0:
            successThisFile = True
        elif winRarReturn == 2:
            shouldUseWinRAR = False
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
                            guess_password_from_comment(comment)
                            passwdlib.update_last_pwd()
                            # print("Possible passwords:", wdArray)
            if not successThisFile:
                for wd in passwdlib.traverseList:
                    winRarReturn = winrar_do(folder, file, wd)
                    if winRarReturn == 1:
                        continue
                    elif winRarReturn == 0:
                        successThisFile = True
                        passwdlib.update_last_pwd(wd)
                        break
                    elif winRarReturn == 2:
                        break
                    else:
                        break
    if ((not ENABLE_RAR) or (not shouldUseWinRAR)) and ENABLE_7Z and not successThisFile:
        for wd in passwdlib.traverseList:
            z7Return = z7_do(folder, file, wd)
            if z7Return == 1:
                continue
            elif z7Return == 3:
                log_error("Broken file: " + file)
                break
            else:
                successThisFile = True
                passwdlib.update_last_pwd(wd)
                break

    if not successThisFile:
        if RENAME_UNRAR and not multiPart:
            os.rename(os.path.join(folder, file),
                      os.path.join(folder, originalName))
        log_error("No passsword for: " + originalName)
    else:
        if DELETEIT:
            if multiPart:
                for multiFile in multiPartList:
                    os.remove(os.path.join(folder, multiFile))
            else:
                os.remove(os.path.join(folder, file))
            multi_level_unrar()
            collect_files()
        elif RENAME_UNRAR and not multiPart:
            moveTemp = os.path.join(folder, originalName)
            originalPath = moveTemp
            i = 0
            while os.path.exists(moveTemp):
                i += 1
                moveTemp = file_rename(originalPath, i)
            os.rename(os.path.join(folder, file), moveTemp)
            collect_files()


def collect_files():
    """收集散落的大量文件 Collect a large number of scattered files"""
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


def read_txt_file(txtFile):
    """读取txt文件 Read txt file"""
    if chardetEnable:
        f = open(txtFile, 'rb')
        data = f.read()
        fileEncoding = chardet.detect(data).get('encoding')
        with open(txtFile, 'r', encoding=fileEncoding) as ff:
            guess_password_from_comment(ff.read())
    else:
        try:
            with open(txtFile, 'r') as f:
                guess_password_from_comment(f.read())
        except:
            try:
                with open(txtFile, 'r', encoding='utf-8') as f:
                    guess_password_from_comment(f.read())
            except:
                pass


def multi_level_unrar():
    """多级解压缩 Multi-level decompression"""
    global workSpace, lastFileName, lastFileSize, lastSpaceFiles, newSpaceFiles
    if MULTI_UNRAR:
        newSpaceFiles = os.listdir(workSpace)
        get_password_from(workSpace)
        for file in newSpaceFiles:
            if os.path.isfile(os.path.join(workSpace, file)):
                if file not in lastSpaceFiles or (file == lastFileName and DELETEIT):
                    newFileSize = os.path.getsize(
                        os.path.join(workSpace, file))
                    if newFileSize * 1.3 > lastFileSize or is_multi_file(file):
                        if unrar_fun2(os.path.join(workSpace, file), True):
                            break
            else:
                if file not in lastSpaceFiles:
                    get_password_from(os.path.join(workSpace, file))
                    newFileList = os.listdir(os.path.join(workSpace, file))
                    if len(newFileList) < 5:
                        for rarFile in newFileList:
                            filePath = os.path.join(workSpace, file, rarFile)
                            if is_compressed_file(filePath):
                                newFileSize = os.path.getsize(filePath)
                                if newFileSize * 1.3 > lastFileSize or is_multi_file(file):
                                    if unrar_fun2(filePath, True):
                                        break


def get_multi_part_in_folder(folder, startName, ext, rarType):
    """在文件夹中找到分卷解压缩文件 Find multipart compressed files in the folder"""
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


def get_multi_part(filePath):
    """根据单个文件找到分卷解压缩文件 Find multipart compressed files according to a single file"""
    # rarType: 0:like abc.7z.001
    #          1:like abc.part1.rar
    #          2:like abc.zip, abc.z01
    global lastFileStartName
    parentFolder, name = os.path.split(filePath)
    if '.' in name:
        nameSplit = name.split('.')
        if len(nameSplit) <= 2:
            if nameSplit[1] == 'zip' or (nameSplit[1].startswith('z') and nameSplit[1][-1].isdigit()):
                return get_multi_part_in_folder(parentFolder, nameSplit[0], 'zip', 2)
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
                return get_multi_part_in_folder(parentFolder, startName, endExt, rarType)
            elif middleExt:
                rarType = 0
                # print(middleExt)
                return get_multi_part_in_folder(parentFolder, startName, middleExt, rarType)
    return []  # doesn't find multipart files


def is_multi_file(multiFile):
    """判断是否是分卷解压缩文件 Determine whether it is a multipart compressed file"""
    return multiFile.endswith('.zip') or multiFile.endswith(
        '.001') or '.part1.' in multiFile or '.part01.' in multiFile or '.part001.' in multiFile


def unrar_fun2(filePath, multiUnrar=False):
    global lastFileName, lastFileSize, multiPartList, lastMultiPart, multiPartExtracted
    multiPartList = get_multi_part(filePath)
    if multiPartList:
        if len(multiPartList) > 1:
            if not multiPartList[0] in multiPartExtracted:
                multiPartExtracted.extend(multiPartList)
                for multiFile in multiPartList:
                    if is_multi_file(multiFile):
                        lastFileName = multiFile
                        lastMultiPart = True
                        lastFileSize = os.path.getsize(os.path.join(
                            workSpace, multiFile)) * len(multiPartList)
                        unrar_fun3(workSpace, multiFile, True)
                        return True
        else:
            return False
    elif is_compressed_file(filePath, multiUnrar):
        lastFileName = os.path.split(filePath)[1]
        lastMultiPart = False
        lastFileSize = os.path.getsize(filePath)
        unrar_fun3('', filePath)
        return True
    return False


def unrar_fun1(folder):
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
                        unrar_fun2(filePath)
                    elif TRAVERSE_ALL_FOLDERS:
                        unrar_fun1(filePath)

        else:
            workSpace = os.path.split(folder)[0]
            lastSpaceFiles = os.listdir(workSpace)
            unrar_fun2(folder)


if __name__ == '__main__':
    if len(sys.argv) <= 1 and not DEFAULT_TARGET:
        sys.exit(1)
    if platform.system() == 'Windows':  # Windows
        pause_command = PAUSE_COMMAND_WINDOWS
        testWinRAR = bool(os.popen(os.path.join(LOC_WINRAR, PROGRAM_RAR)).read())  # whether winrar exists
        ENABLE_RAR = testWinRAR
        if not testWinRAR:
            for loc in LOC_S_WINRAR:
                testWinRAR = os.popen(os.path.join(loc, PROGRAM_RAR)).read()
                if testWinRAR:
                    LOC_WINRAR = loc
                    ENABLE_RAR = True
                    break

        test7z = bool(os.popen(os.path.join(LOC_7Z, PROGRAM_7Z)).read())  # whether 7z exists
        ENABLE_7Z = test7z
        if not test7z:
            for loc in LOC_S_7Z:
                test7z = os.popen(os.path.join(loc, PROGRAM_7Z)).read()
                if test7z:
                    LOC_7Z = loc
                    ENABLE_7Z = True
                    break

        if (not ENABLE_RAR) and (not ENABLE_7Z):
            print("Cannot find winRAR or 7-zip")
            sys.exit(1)
    else:  # Linux or Mac
        pause_command = PAUSE_COMMAND_LINUX
        LOC_7Z = os.getcwd()
        PROGRAM_7Z = PROGRAM_7Z_LINUX if platform.system() == 'Linux' else PROGRAM_7Z_MAC  # 'Darwin' is Mac
        test7z = bool(os.popen(os.path.join(LOC_7Z, PROGRAM_7Z)).read())  # whether 7z exists
        ENABLE_7Z = test7z
        if not test7z:
            print("Cannot find 7-zip")
            sys.exit(1)

    while len(passwdlib.oldList) < 2:
        passwdlib.oldList.append("0")

    checkEveryFilePassWD = True
    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]) and os.path.isfile(sys.argv[1]):
            SAVE_MODE = False
            if len(sys.argv) == 2:
                # 如果只拖入一个文件，则必解压该文件，忽略其后缀
                # If only one file is dragged in, it WILL be decompressed and its extension ignored
                ignoreExtOnce = True
                # print(PASSWD)
        passwdlib.update_last_pwd()
        if not checkEveryFilePassWD:
            if get_password_from(sys.argv[1]):
                passwdlib.update_last_pwd()
        for inputFolder in sys.argv[1:]:
            if not os.path.exists(inputFolder):
                print(inputFolder + " not exists.")
                continue
            if checkEveryFilePassWD and get_password_from(inputFolder):
                passwdlib.update_last_pwd()
                # passwdlib.printWD()
            unrar_fun1(inputFolder)

        print("Finish.")
        if ERROR_LIST:
            print(ERROR_LIST)
            os.system(pause_command)
    elif DEFAULT_TARGET:
        get_password_from(DEFAULT_TARGET)
        if os.path.isfile(DEFAULT_TARGET):
            SAVE_MODE = False
        # print(PASSWD)
        passwdlib.update_last_pwd()
        unrar_fun1(DEFAULT_TARGET)
        print("Finish.")
        if ERROR_LIST:
            print(ERROR_LIST)
            os.system(pause_command)
