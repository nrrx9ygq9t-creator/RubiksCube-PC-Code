############# 所有的group_<num>.py文件的结构都是一样的，只在此文件中加了英文注释 ##############
# All group_<num>.py files have the same structure, only this file has added English comments #
# I currently don't have enough time to integrate them together, and I'm very sorry about that.

import cv2
import numpy as np
import vision_params 

# ==================== 透视变换参数 ====================
# ======= Perspective transformation parameters ========
width, height = 300, 300  

# 透视变换的四个点（分别对应两个面） \\ 'Four points for perspective transformation (corresponding to two faces)'
pts1 = np.float32([[416, 0], [459, 205], [176, 0], [143, 211]])  # 第一张图 \\ 'First image'
pts2 = np.float32([[460, 207], [413, 393], [143, 213], [180, 390]])  # 第二张图 \\ 'Second image'
pts3 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])  # 输出图像的四个点 \\ 'Four points of the output image'

# ==================== RGB 颜色阈值 ====================
# =============== RGB color thresholds =================

red_lower   = np.array([150, 0,   0  ])
red_upper   = np.array([255, 100, 100])

yellow_lower= np.array([180, 180, 0  ])
yellow_upper= np.array([255, 255, 150])

blue_lower  = np.array([0,   0,   150])
blue_upper  = np.array([100, 100, 255])

white_lower = np.array([200, 200, 200])
white_upper = np.array([255, 255, 255])

orange_lower= np.array([200, 100, 0  ])
orange_upper= np.array([255, 200, 150])

green_lower = np.array([0,   150, 0  ])
green_upper = np.array([150, 255, 150])

# ==================== 颜色识别====================
# ================ Color recognition ==============
def analyze_face(img):
    """
    对透视变换后的魔方面图像进行3x3格子颜色识别（RGB空间）
    返回一个3x3列表，每个元素为颜色字符串（'red','green',...）或'grey'
    """
    """
    Perform 3x3 grid color recognition (RGB space) on the perspective-transformed image of the magic square
    Return a 3x3 list, where each element is a color string ('red', 'green', ...) or 'grey'
    """
    # 将 BGR 图像转换为 RGB \\ 'Convert BGR image to RGB'
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    colors = [['' for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            y_start = i * height // 3
            y_end = (i + 1) * height // 3
            x_start = j * width // 3
            x_end = (j + 1) * width // 3
            pic = rgb_img[y_start:y_end, x_start:x_end] 

            # 各颜色掩膜  \\ 'Color masks'
            mask_red   = cv2.inRange(pic, red_lower,   red_upper)
            mask_yellow= cv2.inRange(pic, yellow_lower,yellow_upper)
            mask_blue  = cv2.inRange(pic, blue_lower,  blue_upper)
            mask_white = cv2.inRange(pic, white_lower, white_upper)
            mask_orange= cv2.inRange(pic, orange_lower,orange_upper)
            mask_green = cv2.inRange(pic, green_lower, green_upper)

            total_pixels = pic.size // 3  

            # 计算各颜色占比  \\ 'Calculate the proportion of each color'
            red_ratio    = cv2.countNonZero(mask_red)    / total_pixels
            yellow_ratio = cv2.countNonZero(mask_yellow) / total_pixels
            blue_ratio   = cv2.countNonZero(mask_blue)   / total_pixels
            white_ratio  = cv2.countNonZero(mask_white)  / total_pixels
            orange_ratio = cv2.countNonZero(mask_orange) / total_pixels
            green_ratio  = cv2.countNonZero(mask_green)  / total_pixels

            # 找出占比最大的颜色  \\ 'Find the color with the largest proportion'
            ratios = {
                'red': red_ratio,
                'yellow': yellow_ratio,
                'blue': blue_ratio,
                'white': white_ratio,
                'orange': orange_ratio,
                'green': green_ratio
            }
            max_color = max(ratios, key=ratios.get)
            max_ratio = ratios[max_color]

            # 阈值判断（橙色阈值0.3，其余0.4） \\ 'Threshold judgment (orange threshold 0.3, others 0.4)'
            threshold = 0.3 if max_color == 'orange' else 0.4
            if max_ratio >= threshold:
                colors[i][j] = max_color
            else:
                colors[i][j] = 'grey'
    return colors


def grb_color_up():
   
    img = cv2.imread('./img/raw/codecam_2.png')
    if img is None:
        print("无法读取图像，请检查路径：./img/raw/codecam_2.png")  # \\ 'Unable to read image, please check the path: ./img/raw/codecam_2.png'
        return

    # 透视变换得到两个面 \\ 'Perspective transformation to get two faces'
    matrix1 = cv2.getPerspectiveTransform(pts1, pts3)
    imgOutput1 = cv2.warpPerspective(img, matrix1, (width, height))
    matrix2 = cv2.getPerspectiveTransform(pts2, pts3)
    imgOutputd2 = cv2.warpPerspective(img, matrix2, (width, height))
    imgOutput2 = cv2.rotate(imgOutputd2, cv2.ROTATE_90_CLOCKWISE)

    # 保存变换结果 \\ 'Save transformation results'
    cv2.imwrite("./img/aft/upOutput1.png", imgOutput1)
    cv2.imwrite("./img/aft/upOutput2.png", imgOutput2)

    # 识别两个面的颜色 \\ 'Recognize the colors of the two faces'
    face4_colors = analyze_face(imgOutput1)
    face5_colors = analyze_face(imgOutput2)

    # 存储到外部模块 vision_params \\ 'Store in external module vision_params'
    vision_params.face_col4 = face4_colors
    vision_params.face_col5 = face5_colors

    # 打印结果 \\ 'Print results'
    print("第五面颜色（存入 vision_params.face_col4）：") # \\ 'Fifth face colors (stored in vision_params.face_col4):'
    for row in face4_colors:
        print(row)

    print("\n第六面颜色（存入 vision_params.face_col5）：") # \\ 'Sixth face colors (stored in vision_params.face_col5):'
    for row in face5_colors:
        print(row)

    cv2.waitKey(0)
    cv2.destroyAllWindows()