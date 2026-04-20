import cv2
import numpy as np
import vision_params 

# ==================== 透视变换参数 ====================
width, height = 300, 300 

# 透视变换的四个点
pts1 = np.float32([[288, 51], [479, 225], [107, 247], [305, 421]])  # 第一张图
pts3 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])  # 目标点

# ==================== RGB 颜色阈值 ====================
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

# ==================== 颜色识别 ====================
def analyze_face(img):
    """
    对透视变换后的魔方面图像进行3x3格子颜色识别（RGB空间）
    返回一个3x3列表，每个元素为颜色字符串（'red','green',...）或'unknown'
    """
    # 将 BGR 图像转换为 RGB
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    colors = [['' for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            y_start = i * height // 3
            y_end = (i + 1) * height // 3
            x_start = j * width // 3
            x_end = (j + 1) * width // 3
            pic = rgb_img[y_start:y_end, x_start:x_end]  # 裁剪的 RGB 区域

            # 各颜色掩膜
            mask_red   = cv2.inRange(pic, red_lower,   red_upper)
            mask_yellow= cv2.inRange(pic, yellow_lower,yellow_upper)
            mask_blue  = cv2.inRange(pic, blue_lower,  blue_upper)
            mask_white = cv2.inRange(pic, white_lower, white_upper)
            mask_orange= cv2.inRange(pic, orange_lower,orange_upper)
            mask_green = cv2.inRange(pic, green_lower, green_upper)

            total_pixels = pic.size // 3  

            # 计算各颜色占比
            red_ratio    = cv2.countNonZero(mask_red)    / total_pixels
            yellow_ratio = cv2.countNonZero(mask_yellow) / total_pixels
            blue_ratio   = cv2.countNonZero(mask_blue)   / total_pixels
            white_ratio  = cv2.countNonZero(mask_white)  / total_pixels
            orange_ratio = cv2.countNonZero(mask_orange) / total_pixels
            green_ratio  = cv2.countNonZero(mask_green)  / total_pixels

            # 找出占比最大的颜色
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

            # 阈值判断（橙色阈值0.3，其余0.4）
            threshold = 0.3 if max_color == 'orange' else 0.4
            if max_ratio >= threshold:
                colors[i][j] = max_color
            else:
                colors[i][j] = 'grey'
    return colors

def grb_color_be():
    # 读取图像
    img = cv2.imread('./img/raw/codecam_0.png')
    if img is None:
        print("无法读取图像，请检查路径：./img/raw/codecam_0.png")
        return

    # 透视变换得到两个面
    matrix1 = cv2.getPerspectiveTransform(pts1, pts3)
    imgOutput1 = cv2.warpPerspective(img, matrix1, (width, height))

    # 保存变换结果（可选）
    cv2.imwrite("./img/aft/beOutput1.png", imgOutput1)

    # 识别两个面的颜色
    face3_colors = analyze_face(imgOutput1)

    # 存储到外部模块
    vision_params.face_col3 = face3_colors

    # 打印结果
    print("第四面颜色（存入 vision_params.face_col3）：")
    for row in face3_colors:
        print(row)


    cv2.waitKey(0)
    cv2.destroyAllWindows()