from ursina import *

# 网格尺寸
GRID_WIDTH = 4
GRID_HEIGHT = 25
GRID_DEPTH = 4

# 调试选项
DEBUG_MODE = True  # 设置为True启用更多的调试输出

# 3D方块形状定义
shapes = {
    'T': [
        [[0,0,0], [1,0,0], [-1,0,0], [0,1,0]],  # T形
    ],
    'J': [
        [[0,0,0], [-1,0,0], [1,0,0], [1,1,0]],  # J形
    ],
    'L': [
        [[0,0,0], [-1,0,0], [1,0,0], [-1,1,0]],  # L形
    ],
    'I': [
        [[0,0,0], [0,1,0], [0,2,0], [0,-1,0]],  # I形
    ],
    'O': [
        [[0,0,0], [1,0,0], [0,1,0], [1,1,0]],  # O形
    ],
    'S': [
        [[0,0,0], [-1,0,0], [0,1,0], [1,1,0]],  # S形
    ],
    'Z': [
        [[0,0,0], [1,0,0], [0,1,0], [-1,1,0]],  # Z形
    ]
}

# 颜色定义
shape_colors = {
    'T': color.magenta,
    'J': color.blue,
    'L': color.orange,
    'I': color.cyan,
    'O': color.yellow,
    'S': color.green,
    'Z': color.red
}

# 自定义颜色
color.black66 = Color(0, 0, 0, 0.66)
color.black50 = Color(0, 0, 0, 0.5)
