# -*- coding: utf-8 -*-
from ursina import *
import sys

# 导入所有模块
from utils import setup_encoding
from config import *
from block import Block, GhostBlock
from tetromino import Tetromino
from ui import create_ui, setup_next_preview, setup_orientation_view
from game_grid import create_game_grid, check_lines, grid_positions
from camera_setup import setup_cameras, reset_camera, editor_cam
from game_logic import spawn_tetromino, process_input
from settings import setup_lighting, toggle_pause, reset_game, game_paused
from audio import load_sounds, play_game_start_sound  # 导入音效相关函数

# 确保支持中文字符
setup_encoding()

# 初始化Ursina应用
app = Ursina(title="Tetris")
window.title='Tetris'
window.cog_menu.visible=False
window.exit_button.enabled=True

# 加载音效
load_sounds()

# 播放游戏启动音效
play_game_start_sound()

# 增强的光照设置
main_light = setup_lighting()

# 初始化游戏
create_game_grid()
create_ui()

# 设置相机并获取更新函数
update_views = setup_cameras()

# 设置方向指示器
orientation_indicator = setup_orientation_view()

# 设置下一个方块预览
next_preview = setup_next_preview()

# 定义应用更新函数
def update():
    update_views()

# 处理输入
def input(key):
    print(key)
    process_input(key)

# 生成第一个方块
spawn_tetromino()
# 运行游戏
app.run()
