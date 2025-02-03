# toolUnRar

**Last Update: 2025.02.03**



批量解压缩带密码的压缩包的Python脚本

A Python script for batch rar extraction with passwords

直接拖入文件夹或压缩文件到脚本（的快捷方式上）上即可

Just drag the folder or rar files onto the script(or its shortcut).

能分析压缩包注释、附近文件的文件名、文本文档的内容来获取密码

Able to analyze the comments of the compressed package, file names of nearby files and content of text files to obtain the password.

支持解压几乎所有压缩文件格式。

Support almost all formats of compressed file.

支持分卷解压缩。

Support decompressing multi-part compressed files.

可携带 Portable.

支持Windows和Linux操作系统。 Support Windows and Linux.

在Mac上没有测试过，理论上可以。 Support Mac theoretically?

<br>

## 用途 Where to use it

从论坛下载的压缩包，其密码往往是约定好的那几个密码，所以可以把常用的密码输入这个Python脚本，就可以解压这些文件了。这些压缩包有时是双重压缩，该脚本也支持解压这种文件。假如密码不是约定的密码，你可以把密码作为文件夹的名称，把压缩包保存在该文件夹下，该Python脚本也能识别这种存储密码的形式。

The passwords of compressed packages downloaded from the forum are usually the same, so you can input the commonly used passwords into the Python script to extract those files. These files are sometimes multi-compressed, the script also supports decompressing them. If the passwords are not the common passwords, you can rename the folder to the password and save the compressed package under the folder. The Python script can also recognize this form of storing the password.

<br>

## 更新 Update Log

**2025.02.03:**  新增参数 TRAVERSE_ALL_FOLDERS，为真时，遍历所有文件夹并解压缩。Add new parameter TRAVERSE_ALL_FOLDERS. If it is True, it will traverse all folders and decompress.

**2022.11.04:**  支持Linux系统。Support Linux.

**2022.03.12:**  新增参数DEFAULT_TARGET，直接双击打开脚本时将会对DEFAULT_TARGET进行解压。Add new parameter DEFAULT_TARGET. Double click the script, the DEFAULT_TARGET will be decompressed.

**2022.02.27:** 有这么一种情况，压缩包里没有文件夹，全是图片，解压出来图片会全部散在当前文件夹，非常尴尬。所以针对这种情况设计了算法：如果解压出来的文件过多且不包含任何文件夹，则把这些文件剪切到当前文件夹的以压缩包文件名命名的文件夹中。通过参数COLLECT_FILES设置，默认开启。In such a case, there is no folder in the compressed package, but all pictures. The extracted pictures will be scattered in the current folder, which is very embarrassing... Therefore, an algorithm is designed for this situation: if the extracted files are too many and do not contain any folders, cut these files into the folder named as same as the compressed package file name in the current folder. This function can be set through the parameter COLLECT_FILES, which is enabled by default.

**2022.02.14:** 支持解压形如abc.7z.001，abc.part1.rar，abc.z01的分卷压缩文件（但是不会对分卷进行批量重命名避免解压时文件名重复的问题，我真不信有人分卷解压出来还是一样文件名的分卷的）。Support decompressing multi-part compressed files, such as abc.7z.001, abc.part1.rar and abc.z01.

**2021.11.05:** 支持直接解压双重压缩文件（假如压缩包里又套一个压缩包，就可以继续解压），使用参数 **MULTI_UNRAR** 进行设置。支持解压与压缩包同名的文件。Support direct extraction of double compressed files (if there is another compressed package in this package, the program can continue to extract files), use the parameter **MULTI_UNRAR** to set. Support extracting files with the same name as the compressed package.

**2021.08.01:** 新增在压缩包所在的文件夹里找密码的功能。该程序会遍历分析该文件夹下的所有文件夹的名称和所有txt文件的文件名，并暂时添加到密码库中。Add the ability to find the password in the folder where the archive is located. The program will traverse the names of all folders and txt files under the parent folder , and temporarily add them to the password library.

如下图，在解压该文件夹下的某个压缩文件时，0001~0007均会添加到密码本的开头。

As shown in the picture below, 0001 ~ 0007 will be added to the beginning of password library when extracting a compressed file under this folder.

<img src="https://raw.githubusercontent.com/Mario-Hero/toolUnRar/main/pic/1.jpg" style="zoom:67%;" />

**2021.05.02:** 新增在压缩包的注释里找密码的功能。Added the ability to find the password in the comments of the archive.

<br>

## 依赖 Dependency

**Windows x64:**

Python 3

对于解压RAR文件，需要安装WinRAR，或者直接打包下载本项目即可。

对于解压7z/zip等其他7-Zip支持解压的文件，需要安装7-Zip，或者直接打包下载本项目即可。

If you need to extract RAR files, you need to install WinRAR or download all the files of this project.

If you need to extract 7z or other files which supported by 7-Zip, you need to install 7-Zip or download all the files of this project.

<br>

**Linux x64:**

Python 3

直接打包下载本项目即可。7zzs为Linux下的7z解压程序。如果你的系统是32位或Arm的，可以从[官网](https://sparanoid.com/lab/7z/download.html)下载对应版本替换之。

Download all the files of this project. The 7zzs inside is a 7z decompressor under Linux. If your system is 32-bit or Arm, you can download the corresponding version from [the official site](https://7-zip.org/download.html) to replace it.

<br>

## 用法 Usage

Windows系统下，直接拖入文件夹或压缩文件到Python脚本toolUnRar.py上（或者脚本的快捷方式上）即可批量解压缩包含密码的压缩文件。如果拖入的是文件夹，则会把该文件夹下的压缩文件解压缩，但不进入下一级目录。通过设置PASSWD来设置字典，通过设置DELETEIT来设置解压后是否删除被成功解压的压缩文件。本脚本会通过文件的后缀识别该文件是否为压缩文件。

If you are using Windows, just drag folders or compressed files into the toolUnRar.py python script (or its shortcut) to decompress the compressed file. If a folder is dragged in, the compressed files under the folder will be decompressed, but will not enter the child folders. Set the dictionary by setting parameter PASSWD and whether to delete the successfully decompressed compressed file after decompression by setting parameter  DELETEIT. This script will identify whether the file is a compressed file through the extention of the file.

<br>

Linux系统下, 先给文件添加执行权限。In Linux system, add execution permission to the file first.

```bash
chmod +x ./toolUnRar.py
chmod +x ./7zzs
```

Linux下无法拖入文件到脚本上执行，需要把文件路径作为参数在命令行下运行。例如: `./toolUnRar.py ~/myfile.rar`

The file cannot be dragged in. You need to copy the file path as a parameter to the command line and run it. For example: `./toolUnRar.py ~/myfile.rar`

<br>

## 支持的密码表示形式 Supported password formats

该脚本能够从父级文件夹的名称、父级文件夹下的所有文件夹的名称和所有txt文件的文件名中获取密码，可以识别：password: xxx, password xxx, 密码：xxx，密码:xxx, 密码 xxx. 如果不包含密码和password这两个关键字，该脚本会按空格分隔文本，并把它们都暂时加入密码本。

The script can obtain the password from the name of the parent folder, the names of all folders and txt files under the parent folder. It can identify format like these: password: xxx, password xxx, 密码：xxx，密码:xxx, 密码 xxx.  If the two keywords password and 密码 are not included, the script will separate the text by spaces and temporarily add them to the password list.

<br>

## 参数 Parameters

TRAVERSE_ALL_FOLDERS = False: 为真时，遍历所有文件夹并解压缩。
TRAVERSE_ALL_FOLDERS = False: If it is True, it will traverse all folders and decompress.

<br>

DEFAULT_TARGET = '路径：直接双击打开脚本时将会对DEFAULT_TARGET路径进行解压。

DEFAULT_TARGET = 'Path'：If you just double click the script, the DEFAULT_TARGET will be decompressed.

<br>

PASSWD = ["hello","123456"] ：你的密码本，该脚本会从这个数组中不断试验密码来解压缩，直到成功为止。

PASSWD = ["hello","123456"] ： your passwords.

<br>

DELETEIT = False：一个危险的参数。为真时，该脚本会直接删除成功解压的压缩文件。为假则不会删除。

DELETEIT = False：DANGER!! If it is True,will delete compressed file after extraction

<br>

SAVE_MODE = True：如果该脚本无法通过后缀判断这是不是压缩文件，则不对该文件进行操作。

SAVE_MODE = True：If the script cannot recognize the format of file from it's extention, then do nothing with this file.

<br>

MULTI_UNRAR = DELETEIT and True：为真时支持双重解压，要求DELETEIT也为真。

MULTI_UNRAR = DELETEIT and True：Unzip double compressed files if MULTI_UNRAR and DELETEIT is True

## License

The project is released under GNU General Public License v3.0.
