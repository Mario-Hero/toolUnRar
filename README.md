# toolUnRar

批量解压缩带密码的压缩包的Python脚本

A Python script for batch extraction with passwords

直接拖入文件夹或压缩文件即可

Just drag in the folder or rar files

支持解压几乎所有压缩文件格式。

Support almost all formats of compressed file.

可携带 Portable



## 需要 Needs

**Windows系统**

Python 3

对于解压RAR文件，需要安装WinRAR 

对于解压7z/zip等其他7-Zip支持解压的文件，需要安装7-Zip

<br>

**Windows**

Python 3

If you need to extract RAR files, you need to install WinRAR.

If you need to extract 7z or other files which supported by 7-Zip, you need to install 7-Zip. 



## 用法 Usage

直接拖入文件夹或压缩文件即可批量解压缩包含密码的压缩文件。如果拖入的是文件夹，则会把该文件夹下的压缩文件解压缩，但不进入下一级目录。通过设置PASSWD来设置字典，通过设置DELETEIT来设置解压后是否删除被成功解压的压缩文件。本脚本会通过文件的后缀识别该文件是否为压缩文件。

<br>

你可以把WinRAR目录下的Unrar.exe和7-Zip目录下的7z.exe直接复制到这个toolUnRar.py文件的相同目录下，这样就可以携带使用了。



## 参数 Parameters

PASSWD = ["hello","123456"] ：你的密码本，该脚本会从这个数组中不断试验密码来解压缩，直到成功为止。

PASSWD： your passwords.

<br>

DELETEIT ：一个危险的参数。为真时，该脚本会直接删除成功解压的压缩文件。为假则不会删除。

DELETEIT：DANGER!! If it is True,will delete compressed file after extraction

<br>

LOC_WINRAR = "C:\\Program Files\\WinRAR\\" 你的WinRAR安装位置。就算这个变量的设置的不对，该程序也会在可能的位置来寻找对应的程序。

LOC_WINRAR: location of WinRAR. Even the location doesn't set correctly. This script will try to find it in possible locations.

<br>

LOC_7Z：7-Zip的安装位置。

LOC_7Z: location of 7-Zip

<br>

SAVE_MODE = True：如果该脚本无法通过后缀判断这是不是压缩文件，则不对该文件进行操作。

SAVE_MODE = True：If the script cannot recognize the format of file from it's suffix, then do nothing with the file.



