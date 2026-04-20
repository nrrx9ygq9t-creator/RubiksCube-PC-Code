# #################################### Computer vision parameters ######################################################

######################## 这个程序本来存贮了许多计算机视觉参数，但现在只有少数几个参数被使用了。 ######################## 
############ 'This program originally stored many computer vision parameters, but now only a few are used.' ############

############################ 由于完成此项目的时间有限，许多参数没有来的及被删除。 ###############################
############ 'Due to limited time to complete this project, many parameters have not been deleted.' #############


# default values for the parameters

# black-filter
# rgb_L = 50  # threshold for r, g and b values. rgb-pixels with r,g,b< rgb_L are consider to be no facelet-pixel

# white-filter
# sat_W = 60  # hsv-pixels with a saturation s > sat_W are considered not to be a white facelet-pixel
# val_W = 150  # hsv-pixels with a value v < sat_W are considered not to be a white facelet-pixel

# this parameter cannot be changed by the GUI
# sigma_W = 300  # a grid square is considered part of a white facelet if the standard deviation of the hue is <= sigma_W

# color-filter
# sigma_C = 5  # a grid square is considered part of a facelet if the standard deviation of the hue is <= sigma_C
# delta_C = 5  # pixels within the interval [hue-delta,hue+delta] are considered to belong to the same facelet

# These parameters depend on the actually used cube colors and the lightning conditions
# orange_L = 6  # lowest allowed hue for color orange
# orange_H = 23  # highest allowed hue for color orange
# yellow_H = 50  # highest allowed hue for color yellow
# green_H = 100  # highest allowed hue for color green
# blue_H = 160  # highest allowed hue for color blue
# hue values > blue_H and < orange_L describe the color red

# The colors of a cube face are stored here by the function group_<num>.analyze_face
face_col0 = []   # 面色
face_col1 = []  
face_col2 = []
face_col3 = []
face_col4 = []
face_col5 = []

face_hsv = []  # the colors (as hsv-values) of a cube face

# These dictionaries define the colors of all 6 faces and are filled by the client_gui2.transfer routine
cube_col1 = {}  # 中心块色，可能失去作用？  \\ 'Center block color, may be obsolete?'
code_col2 = {}
cube_hsv = {}  # the colors (as hsv-values) of the 6 faces
