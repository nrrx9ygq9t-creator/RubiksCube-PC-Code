# 解魔方机器人的上位机程序
## 概述
本项目为解魔方机器人的上位机程序，从hkociemba的[RubiksCube-TwophaseSolver](https://github.com/hkociemba/RubiksCube-TwophaseSolver)程序修改而来。

本人的Python水平有限，无法保证修改后代码的完美性、稳定性和高效性。如果你的目标只是简单地解魔方并探索其模式，[Cube Explorer](http://kociemba.org/cube.htm) 可能是更好的选择。如果你希望深入理解两阶段算法的复杂性，或者你正在进行一个构建能够实现近乎完美的魔方机器人项目，那么可以尝试使用并修改本项目或者修改hkociemba的原始项目。
## 使用方法

此软件未上传到PyPI，因此无法通过 pip 直接安装。你需要从 GitHub 上克隆该项目：
```bash
git clone https://github.com/hkociemba/RubiksCube-TwophaseSolver.git
```

建议使用 Python 3.7 或更高版本。你可以从 [Python 官方网站](https://www.python.org/downloads/) 下载并安装 Python。

低于 Python 3.7 的版本未测试过，可能无法正常运行。

此外，由于此程序调用了 OpenCV、NumPy和Pillow，你还需要安装一些依赖包：
```bash
py -m pip install opencv-python
```
```bash
py -m pip install numpy
```
```bash
py -m pip install pillow
```

运行start_sever.py以启动本地服务器。此时有一些表格需要创建，但仅在第一次运行时创建。这些表格大约占用 80 MB 的磁盘空间，并且根据你的硬件，生成可能需要大约半小时或更长时间。然而，“正是通过这些计算量大的表格，算法才能高效运行，通常能够找到接近最优的解。”

运行client_gui2.py以启动客户端GUI程序。你可以在GUI中手动输入魔方的各个面颜色，点击“解决”按钮，程序将返回解法。

在GUI中，你可以选择使用摄像头，程序将尝试通过摄像头识别魔方的颜色。请确保摄像头已连接，并且在GUI中选择了正确的摄像头。但是我并不建议在平时使用中使用摄像头功能，因为图像识别是用固定点RGB识别颜色的，容易受到光线、摄像头位置、摄像头型号等因素的影响，导致识别错误或失败，只有在四个摄像头都固定后，在group_(num).py中设置好摄像头详细参数后，才能保证识别的准确性。

本程序的魔方识别功能是使用openCV库实现的，识别的原理是通过摄像头拍摄魔方的图像，然后裁切出魔方的六个面，并对每个面进行RGB颜色识别存入vision_params.py中。随后自动输入到GUI中，最后调用twophase算法求解。

一个魔方由其魔方定义字符串定义。一个已解决的魔方的字符串为 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'。   
```python
>>> cubestring = 'DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL'
```
Refer to https://github.com/hkociemba/RubiksCube-TwophaseSolver/blob/master/enums.py for the exact  format.
```python
>>> sv.solve(cubestring,19,2)
```
This will solve the cube described by the definition string with a desired maximum length of 19 moves and  a timeout of 2 seconds. If the timeout is reached, the shortest solution computed so far is returned, even if it exceeds the desired maximum length.
```python
'L3 U1 B1 R2 F3 L1 F3 U2 L1 U3 B3 U2 B1 L2 F1 U2 R2 L2 B2 (19f)'
```
Here, U, R, F, D, L and B denote the Up, Right, Front, Down, Left and Back faces of the cube. 1, 2, and 3 denote a 90°, 180° and 270° clockwise rotation of the corresponding face. 

If you prefer to allocate a constant time t for each solution and receive only the shortest maneuver found within that time t, use the following command:
```python
>>> sv.solve(cubestring,0,t)
```
You can test the performance of the algorithm on your machine with something similar to
```python
>>> import twophase.performance as pf
>>> pf.test(100,0.3)
```
This example generates 100 random cubes, solves each one in 0.3 s and displays a statistic about the solution lengths.   

You also have the possibility to solve a cube not to the solved position but to some favorite pattern represented by the goalstring.

```python
>>> sv.solveto(cubestring,goalstring,20,0.1)
```
will grant e.g. 0.1 s to find a solution with <= 20 moves.   

***

Another feature is to start a local server listening on a port of your choice. It accepts the cube definition string and returns the solution.
```python
>>> import twophase.server as srv
>>> srv.start(8080, 20, 2)
```
Alternatively, start the server in the background:
```python
>>> import twophase.start_server as ss
>>> from threading import Thread
>>> bg = Thread(target=ss.start, args=(8080, 20, 2))
>>> bg.start()
```
Upon successful initiation, a message like   

```Server socket created```  
```Server now listening...```   

indicates the proper functioning of the server. In this example, the server is listening on port 8080, with a desired maximum length of 20 moves and a timeout of 2 seconds.

You can access the server, which may also run on a remote machine, using various methods:

```http://localhost:8080/DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL```  
via a web browser and the server on the same machine on port 8080.

```http://myserver.com:8081/DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL```  
via a web browser and the server on the remote machine myserver.com on port 8081.

```echo DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL | nc localhost 8080```  
using netcat (nc) and the server on the same machine on port 8080.

You can also communicate with the server using a small GUI program that allows you to interactively enter the cube definition string:
```python
>>> import twophase.client_gui
```
![](gui_client.png "")
***
