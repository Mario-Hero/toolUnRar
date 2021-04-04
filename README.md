# toolUnRar

批量解压缩带密码的压缩包的Python脚本

A Python script for batch extraction with passwords

直接拖入文件夹或rar文件即可

Just drag in the folder or rar files



## 需要 Needs

**Windows系统**

Python 3

**已安装WinRAR (WinRAR installed)**  (only support language of 中文 or English )



## 用法 Usage

直接拖入文件夹或rar文件即可批量解压缩包含密码的rar文件。如果拖入的是文件夹，则会把该文件夹下的rar解压缩，但不进入下一级目录。通过设置PASSWD来设置字典，通过设置DELETEIT来设置解压后是否删除被成功解压的rar文件。



**目前仅能解压rar文件。**

**Currently, only rar files can be extracted.**



**目前仅支持中文版和英文版的WinRAR**



## 参数 parameters

PASSWD = ["hello","123456"] ：你的密码本，该脚本会从这个数组中不断试验密码来解压缩，直到成功为止。

PASSWD： your passwords.



DELETEIT ：一个危险的参数。为真时，该脚本会直接删除成功解压的rar文件。为假则不会删除。

DELETEIT：DANGER!! If it is True,will delete rar file after extraction



LOC_WINRAR = "C:\\Program Files\\WinRAR\\" 你的WinRAR安装位置。就算这个变量的位置不对，该程序也能找到它。

LOC_WINRAR: location of WinRAR



