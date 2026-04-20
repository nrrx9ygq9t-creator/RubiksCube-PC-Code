################## A simple graphical interface which communicates with the server #####################################

############ Client_gui2 reads from the webcam and performs automatic input. With just one button press, ###############
######### it can complete all operations including taking photos, parsing, inputting, sending to the server, ###########
######################### receiving operation codes, and sending to the serial port. ###################################

############################### Client_gui2从网络摄像头进行读取并自动输入，#############################################
##########可以只按一个按钮就完成拍照、解析、输入、发送到服务器，接收操作码并发送到串口的所有操作。 #####################

from tkinter import *
import socket
import cubie
import time
import vision_params
import sys
import serial
import contextlib
from PIL import Image, ImageTk
import cv2
import tkinter.filedialog as filedialog
import os

########################################################################################################################

############################################## Real-time Image #########################################################
################################################## 实时图像 ############################################################
class CameraTkinter:
    def __init__(self, parent, camera_index=0, w=320, h=240):
        """parent: a Tkinter container (Frame) where the preview label will be placed."""
        self.parent = parent
        self.camera_index = camera_index
        self.w = w
        self.h = h
        self.cap = None
        self.available = False
        # preview label placed in the parent frame
        self.camera_label = Label(self.parent, text='')
        # pack label at top and do not expand so controls remain visible
        self.camera_label.pack(side=TOP, fill=X)
        self.current_frame = None
        # try to open camera
        self._open_camera(self.camera_index)
        self.update_frame()

    def _open_camera(self, index):
        try:
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
            cap = cv2.VideoCapture(index)
            # small test if opened
            if cap is not None and cap.isOpened():
                self.cap = cap
                self.available = True
                self.camera_index = index
                self.camera_label.config(text='')
            else:
                self.cap = None
                self.available = False
                # 在摄像头不可用时显示指定的图像或文本   
                # Display a specified image or text when the camera is unavailable    
                self.camera_label.config(image='', text='')
        except Exception:
            self.cap = None
            self.available = False
            self.camera_label.config(image='', text='')

    def switch_camera(self, index):
        """Switch to another camera index."""
        self._open_camera(index)

    def get_frame(self):
        return self.current_frame

    def update_frame(self):
        if not self.available or self.cap is None:
            # show blank / placeholder
            try:
                self.camera_label.config(image='', text='')
            except Exception:
                pass
            self.parent.after(200, self.update_frame)
            return
        try:
            ret, frame = self.cap.read()
        except Exception:
            ret = False
            frame = None
        if ret and frame is not None:
            try:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # store latest frame (RGB numpy array)
                self.current_frame = frame
                img = Image.fromarray(frame)
                img = img.resize((self.w, self.h), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(img)
                self.camera_label.imgtk = imgtk
                self.camera_label.config(image=imgtk, text='')
            except Exception:
                pass
        self.parent.after(30, self.update_frame)


########################################################################################################################

############################################ Serial Port Settings ######################################################
################################################## 串口设置 ############################################################
class SerialOutputStream:
    def __init__(self, port, baudrate=115200):     # 波特率默认115200  \\ The default baud rate is 115200
        self.ser = serial.Serial(port, baudrate)
        
    def write(self, message):
        self.ser.write(message.encode())
        
    def flush(self):
        self.ser.flush()

@contextlib.contextmanager
def redirect_stdout_to_serial(port, baudrate=115200):    # 波特率默认115200  \\ The default baud rate is 115200
    original_stdout = sys.stdout
    sys.stdout = SerialOutputStream(port, baudrate)
    try:
        yield
    finally:
        sys.stdout = original_stdout


########################################################################################################################

#################################### some global variables and constants ###############################################
############################################ 全局变量和默认信息 ########################################################
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '8080'
width = 60  # width of a facelet in pixels
facelet_id = [[[0 for col in range(3)] for row in range(3)] for fc in range(6)]
colorpick_id = [0 for i in range(6)]
curcol = None
t = ("U", "R", "F", "D", "L", "B")
cols = ("yellow", "green", "red", "white", "blue", "orange")
# 图像默认保存设置
SAVE_DIR = "./img/raw"
SAVE_BASENAME = "capture"
SAVE_EXT = "png"  # 'jpg' or 'png'
########################################################################################################################

# ################################################ Diverse functions ###################################################


def show_text(txt):
    """展示信息"""
    # print(txt)
    display.insert(INSERT, txt)
    root.update_idletasks()


def create_facelet_rects(a):
    """Initialize the facelet grid on the canvas."""
    offset = ((1, 0), (2, 1), (1, 1), (1, 2), (0, 1), (3, 1))
    for f in range(6):
        for row in range(3):
            y = 10 + offset[f][1] * 3 * a + row * a
            for col in range(3):
                x = 10 + offset[f][0] * 3 * a + col * a
                facelet_id[f][row][col] = canvas.create_rectangle(x, y, x + a, y + a, fill="grey")
                if row == 1 and col == 1:
                    canvas.create_text(x + width // 2, y + width // 2, font=("", 14), text=t[f], state=DISABLED)
    for f in range(6):
        canvas.itemconfig(facelet_id[f][1][1], fill=cols[f])


def create_colorpick_rects(a):
    """Initialize the "paintbox" on the canvas."""
    global curcol
    global cols
    for i in range(6):
        x = (i % 3) * (a + 5) + 7 * a
        y = (i // 3) * (a + 5) + 7 * a
        colorpick_id[i] = canvas.create_rectangle(x, y, x + a, y + a, fill=cols[i])
        canvas.itemconfig(colorpick_id[0], width=4)
        curcol = cols[0]


def get_definition_string():
    """根据色块颜色生成立方体定义字符串。"""
    """Generate the cube definition string from the facelet colors. """
    color_to_facelet = {}
    for i in range(6):
        color_to_facelet.update({canvas.itemcget(facelet_id[i][1][1], "fill"): t[i]})
    s = ''
    for f in range(6):
        for row in range(3):
            for col in range(3):
                s += color_to_facelet[canvas.itemcget(facelet_id[f][row][col], "fill")]
    return s
########################################################################################################################

############################# Solve the displayed cube with a local or remote server ###################################
########################################### 用本地或远程服务器解决打乱的魔方 ###########################################


def solve():
    """连接服务器并返回操作码。"""
    """Connect to the server and return the solving maneuver."""
    display.delete(1.0, END)  # 清空输出窗口    \\    clear output window
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        show_text('创建套接字失败！')  # \\  'Failed to create socket'
        return
    # host = 'f9f0b2jt6zmzyo6b.myfritz.net'  # my RaspberryPi, if online
    host = txt_host.get(1.0, END).rstrip()  # 默认 localhost    | defalt
    port = int(txt_port.get(1.0, END))  # 端口默认 8080         | defalt port

    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        show_text('无法解析主机名！')  # \\  'Hostname could not be resolved.'
        return
    try:
        s.connect((remote_ip, port))
    except BaseException as e:
        show_text('无法连接至服务器！ ' + e.__doc__)  # \\  'Cannot connect to server.'
        return
    show_text('已连接到 ' + remote_ip + '\n')  # \\  'Connected with '
    try:
        defstr = get_definition_string() + '\n'
    except BaseException as e:
        show_text('无效的色块配置！\n颜色错误或缺失。 ' + e.__doc__)  # \\  'Invalid facelet configuration.\nWrong or missing colors. '
        return
    show_text(defstr)
    try:
        s.sendall((defstr + '\n').encode())
    except BaseException as e:
        show_text('无法向服务器发送魔方配置信息。 ' + e.__doc__)
        return
    do_code=s.recv(2048).decode()
    show_text(do_code)
    send=do_code
    cleaned = send.split('(')[0].strip()
    print(cleaned)
########################################################################################################################

################################# Functions to change the facelet colors ###############################################
############################################## 自动改色 ################################################################


def clean():
    """用中心块的颜色填充其所在面。"""
    """Restore the cube to a clean cube."""
    for f in range(6):
        for row in range(3):
            for col in range(3):
                canvas.itemconfig(facelet_id[f][row][col], fill=canvas.itemcget(facelet_id[f][1][1], "fill"))


def empty():
    """清空除中心块外的所有色块。"""
    """Remove the facelet colors except the center facelets colors."""
    for f in range(6):
        for row in range(3):
            for col in range(3):
                if row != 1 or col != 1:
                    canvas.itemconfig(facelet_id[f][row][col], fill="grey")


def random():
    """使用可以被还原的色块组合填充。"""
    """Generate a random cube and sets the corresponding facelet colors."""
    cc = cubie.CubieCube()
    cc.randomize()
    fc = cc.to_facelet_cube()
    idx = 0
    for f in range(6):
        for row in range(3):
            for col in range(3):
                canvas.itemconfig(facelet_id[f][row][col], fill=cols[fc.f[idx]])
                idx += 1
########################################################################################################################

############################################# Edit the facelet colors ##################################################
#################################################### 手动填色 ##########################################################


def click(_event):
    """用鼠标左键选色并输入。"""
    """Define how to react on left mouse clicks"""
    global curcol
    idlist = canvas.find_withtag("current")
    if len(idlist) > 0:
        if idlist[0] in colorpick_id:
            curcol = canvas.itemcget("current", "fill")
            for i in range(6):
                canvas.itemconfig(colorpick_id[i], width=1)
            canvas.itemconfig("current", width=5)
        else:
            canvas.itemconfig("current", fill=curcol)

########################################################################################################################

################################################## Capture image #######################################################
###################################################### 拍照片 ##########################################################



def capture_image():
    """Save the latest frame from the CameraTkinter preview to a user-chosen file."""
    # Save frames from all camera preview instances
    any_saved = False
    ext = SAVE_EXT.lstrip('.')
    for cam in cameras:
        try:
            if not getattr(cam, 'available', False) or cam.get_frame() is None:
                show_text(f'摄像头 {getattr(cam, "camera_index", "?")} 无可用帧，跳过\n')  # \\  'Camera {index} has no available frame, skipping'
                continue
            fname = os.path.join(SAVE_DIR, f"codecam_{getattr(cam, 'camera_index', 0)}.{ext}")
            os.makedirs(os.path.dirname(fname), exist_ok=True)
            bgr = cv2.cvtColor(cam.get_frame(), cv2.COLOR_RGB2BGR)
            cv2.imwrite(fname, bgr)
            show_text('已保存图片: ' + fname + '\n')  # \\  'Saved image: '
            any_saved = True
        except Exception as e:
            show_text('保存图片失败: ' + str(e) + '\n')  # \\  'Failed to save image: '
    if not any_saved:
        show_text('未保存任何图片。\n')  # \\  'No images were saved.'


########################################################################################################################

############################################# Auto input and solve it ##################################################
###################################################### 操作 ############################################################


# Most of this part is similar to the solve() function, for repeated Chinese annotations, please refer to the previous text.
def doall():
    capture_image()
    transfer()
    display.delete(1.0, END)  # 清空输出窗口
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        show_text('创建套接字失败！')
        return
    # host = 'f9f0b2jt6zmzyo6b.myfritz.net'  # my RaspberryPi, if online
    host = txt_host.get(1.0, END).rstrip()  # 默认 localhost
    port = int(txt_port.get(1.0, END))  # 端口默认 8080

    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        show_text('无法解析主机名！')
        return
    try:
        s.connect((remote_ip, port))
    except BaseException as e:
        show_text('无法连接至服务器！ ' + e.__doc__)
        return
    show_text('已连接到 ' + remote_ip + '\n')
    try:
        defstr = get_definition_string() + '\n'
    except BaseException as e:
        show_text('无效的色块配置！\n颜色错误或缺失。 ' + e.__doc__)
        return
    show_text(defstr)
    try:
        s.sendall((defstr + '\n').encode())
    except BaseException as e:
        show_text('无法向服务器发送魔方配置信息。 ' + e.__doc__)
        return
    do_code=s.recv(2048).decode()
    show_text(do_code)
    send=do_code
    cleaned = send.split('(')[0].strip()
    print(cleaned)
    with redirect_stdout_to_serial('COM5'):     #### 这里的 COM5 是串口号，请根据实际情况修改
        print(cleaned)                          #### \\ The COM5 here is the serial port number, 
                                                ####    please modify it according to your actual situation.

########################################################################################################################


########################################### functions to set the slider values #########################################
###################################################### 解析并输入 ######################################################


def transfer():
    """从外部解析颜色信息并自动输入GUI中。"""
    """Parse color information from external source and automatically input it into the GUI."""
    ##--------------##
    ##      0=U     ##
    ##      1=R     ##
    ##      2=F     ##
    ##      3=D     ##
    ##      4=L     ##
    ##      5=B     ##
    ##--------------##

    from threading import Thread
    from group_1 import grb_color_up
    from group_2 import grb_color_do
    from group_3 import grb_color_fo
    from group_4 import grb_color_be

    thr = Thread(target=grb_color_up, args=())
    thr.start()
    thr = Thread(target=grb_color_do, args=())
    thr.start()
    thr = Thread(target=grb_color_fo, args=())
    thr.start()
    thr = Thread(target=grb_color_be, args=())
    thr.start()
    time.sleep(0.1)

    ###########face 0##############
    if len(vision_params.face_col0) == 0:
        return


    # 固定面索引  \\ Fixed face index
    fixed_face_index = 2

    for i in range(3):
        for j in range(3):
            canvas.itemconfig(facelet_id[fixed_face_index][i][j], fill=vision_params.face_col0[i][j])




    ###########face 1##############
    if len(vision_params.face_col1) == 0:
        return


    # 固定面索引
    fixed_face_index = 1   

    for i in range(3):
        for j in range(3):
            canvas.itemconfig(facelet_id[fixed_face_index][i][j], fill=vision_params.face_col1[i][j])
            


    ###########face 2##############
    if len(vision_params.face_col2) == 0:
        return


    # 固定面索引
    fixed_face_index = 0

    for i in range(3):
        for j in range(3):
            canvas.itemconfig(facelet_id[fixed_face_index][i][j], fill=vision_params.face_col2[i][j])

    


    ###########face 3##############
    if len(vision_params.face_col3) == 0:
        return


    # 固定面索引
    fixed_face_index = 3

    for i in range(3):
        for j in range(3):
            canvas.itemconfig(facelet_id[fixed_face_index][i][j], fill=vision_params.face_col3[i][j])

            


    ###########face 4##############
    if len(vision_params.face_col4) == 0:
        return


    # 固定面索引
    fixed_face_index = 4

    for i in range(3):
        for j in range(3):
            canvas.itemconfig(facelet_id[fixed_face_index][i][j], fill=vision_params.face_col4[i][j])
            


    ###########face 5##############
    if len(vision_params.face_col5) == 0:
        return


    # 固定面索引
    fixed_face_index = 5

    for i in range(3):
        for j in range(3):
            canvas.itemconfig(facelet_id[fixed_face_index][i][j], fill=vision_params.face_col5[i][j])
########################################################################################################################

########################################## Generate and display the TK_widgets #########################################
###################################################### 界面配置 ########################################################


root = Tk()
root.wm_title("解魔方")  # \\  "Solve the Rubik's Cube"
# container for 4 camera previews (2x2 grid)
container = Frame(root)
container.pack(padx=5, pady=5)

# create camera cells
cameras = []
index_entries = []

def set_camera_index(app_obj, entry_widget):
    try:
        idx = int(entry_widget.get())
    except Exception:
        show_text('请输入有效的摄像头编号\n')  # \\  'Please enter a valid camera index'
        return
    app_obj.switch_camera(idx)
    show_text('摄像头切换到: %s\n' % idx)  # \\  'Switched camera to: %s\n'

cell_w = 180
cell_h = 140
for i in range(4):
    row = i // 2
    col = i % 2
    cell = Frame(container, width=cell_w, height=cell_h)
    cell.grid(row=row, column=col, padx=8, pady=8)
    # make sure the cell keeps its size
    cell.grid_propagate(False)
    # camera preview in this cell
    cam = CameraTkinter(cell, camera_index=i, w=cell_w, h=cell_h-40)
    cameras.append(cam)
    # controls under the preview
    ctrl = Frame(cell)
    ctrl.pack(side=BOTTOM, fill=X, pady=2)
    entry = Entry(ctrl, width=6, font=("Arial", 11))
    entry.insert(0, str(i))
    entry.pack(side=LEFT, padx=(8,4))
    index_entries.append(entry)
    btn = Button(ctrl, text='设定', command=lambda a=cam, e=entry: set_camera_index(a, e), width=6, height=1, font=("Arial", 10))
    btn.pack(side=LEFT)    # 'Set' #

# main control canvas
canvas = Canvas(root, width=12 * width + 20, height=9 * width + 20)
canvas.pack()      # 'solve' #
bsolve = Button(text="解决", height=2, width=10, relief=RAISED, command=solve, bg="pink", fg="black")
bsolve_window = canvas.create_window(10 + 10.5 * width, 10 + 6.5 * width, anchor=NW, window=bsolve)
bclean = Button(text="复位", height=1, width=10, relief=RAISED, command=clean)    # \\ 'Reset'
bclean_window = canvas.create_window(10 + 10.5 * width, 10 + 7.5 * width, anchor=NW, window=bclean)
bempty = Button(text="清空", height=1, width=10, relief=RAISED, command=empty)    # \\ 'Clear'
bempty_window = canvas.create_window(10 + 10.5 * width, 10 + 8 * width, anchor=NW, window=bempty)
brandom = Button(text="随机", height=1, width=10, relief=RAISED, command=random)  # \\ 'Random'
brandom_window = canvas.create_window(10 + 10.5 * width, 10 + 8.5 * width, anchor=NW, window=brandom)
display = Text(height=7, width=39)
text_window = canvas.create_window(10 + 6.5 * width, 10 + .5 * width, anchor=NW, window=display)
hp = Label(text='    服务器和端口')                                               # \\  'Server and Port'
hp_window = canvas.create_window(10 + 0 * width, 10 + 0.6 * width, anchor=NW, window=hp)
txt_host = Text(height=1, width=20)
txt_host_window = canvas.create_window(10 + 0 * width, 10 + 1 * width, anchor=NW, window=txt_host)
txt_host.insert(INSERT, DEFAULT_HOST)
txt_port = Text(height=1, width=20)
txt_port_window = canvas.create_window(10 + 0 * width, 10 + 1.5 * width, anchor=NW, window=txt_port)
txt_port.insert(INSERT, DEFAULT_PORT)
canvas.bind("<Button-1>", click)
create_facelet_rects(width)
create_colorpick_rects(width)

                     # 'Do All' #
btransfer = Button(text="操作", height=2, width=13, relief=RAISED, command=doall, bg="lightblue", fg="black")
canvas.create_window(10 + 0.5 * width, 10 + 6.2 * width, anchor=NW, window=btransfer)
btransfer = Button(text="解析并输入", height=1, width=13, relief=RAISED, command=transfer)  # \\ 'Parse and Input'
canvas.create_window(10 + 0.5 * width, 10 + 7.9 * width, anchor=NW, window=btransfer)

# Capture button to save current preview frame
bcapture = Button(text="保存拍照", height=1, width=13, relief=RAISED, command=capture_image)  # \\ 'Save Capture'
canvas.create_window(10 + 0.5 * width, 10 + 8.4 * width, anchor=NW, window=bcapture)


def on_closing():
    # release camera resources
    for cam in cameras:
        try:
            if getattr(cam, 'cap', None) is not None:
                try:
                    cam.cap.release()
                except Exception:
                    pass
        except Exception:
            pass
    try:
        root.destroy()
    except Exception:
        pass

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
#______________________________________________________________________________________________________________________#
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
#                                                                                                                      #
#                                               Acknowledgments                                                        #
#   Python:                  Yu Yingnan                 Dr.Li Jianhua            Hu Yangyu                             #
#   C programming language:  Yang Jintao                Dr.Li Jianhua            Hu Yangyu                             #
#   Modelling:               Huang Chenzhan                                                                            #
#   Structural design:       Dr.Feng Guizhen            Huang Chenzhan           Hu Yangyu                             #
#   Embedded:                Yang Jintao                Hu Yangyu                                                      #
#   Test:                    Yang Jintao                Huang Chenzhan           Hu Yangyu                             #
#   Funds and equipments:    Hu Yangyu                  Huang Chenzhan           Yang Jintao                           #
#                            Yu Yingnan                 Deng Jinchuan            Zhang Nan                             #
#   Assembly:                Huang Chenzhan             Yan Bo                   Hu Yangyu                             #
#   3D printing:             Cang Hai Qing Mo                                                                          #
#                                                                                                                      #
#   Yang Jintao said that our Chinese teacher Wang Yingxiao is also very important,so I had to add her name. :D        #
#   Special thankness:           Wang Yingxiao                                                                         #
#                                                                                                                      #
#----------------------------------------------------------------------------------------------------------------------#
#                                                                                                                      #
#       This Python program was downloaded from GitHub.It is a wonderful work made by hkociemba.This program is        #
#   open-source,so that we can make some modifications on this basis to make it suitable for our new machine.          #
#       At first,I tried to use PyAutoGUI to input the colour,but that is very inconvenient.I started to see how       #
#   hkociemba did in this program.Finally I found that OpenCV is a good choice,but it can't work very well.On          #
#   Bilibili,I found a PNG-based algorithm and began to use RGB to get every square's color.Finally, I integrated      #
#   these functions, resulting in this program.                                                                        #
#       Thanks also to DeepSeek and Dou Bao.They play a very important role in embedded development.                   #
#                                                                                                                      #
#----------------------------------------------------------------------------------------------------------------------#
#                                                                                                                      #
#                  We are from the School of Mechanical Engineering at Shijiazhuang Tiedao University                  #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                     -----------------         --------                                               #
#                                    /               /         /         \                                             #
#                                   ------     ------         /   /--     \                                            #
#                                        /    /              /   /   \    /                                            #
#                                       /    /              /   /    /   /                                             #
#                                      /    /              /   /    /   /                                              #
#                                     /    /              /   /    /   /                                               #
#                                    /    /              /   /----/   /                                                #
#                                   /    /              /            /                                                 #
#                                  ------              -------------                                                   #
#                                                                                                                      #
#                                                                                                                      #
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
#______________________________________________________________________________________________________________________# 