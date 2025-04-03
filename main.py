# -*- coding: utf-8 -*-
from ursina import *
import sys
import time

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
import settings  # 导入settings模块以直接访问变量
from history_manager import close_history_ui, history_ui_active  # 导入历史记录管理函数

# 确保支持中文字符
setup_encoding()

# 初始化Ursina应用
app = Ursina(title="Tetris")
window.title='Tetris'
window.cog_menu.visible=False
window.exit_button.enabled=True

# 添加窗口关闭事件处理
def on_window_close():
    from game_logic import save_current_game_state
    print("检测到窗口关闭事件，保存游戏记录...")
    save_current_game_state()
    application.quit()
    
# 注册窗口关闭事件
window.exit_button.on_click = on_window_close

# 加载音效
load_sounds()

# 初始化游戏统计信息
settings.game_start_time = time.time()
settings.lines_cleared = 0

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

# 处理输入 - 增强输入处理，确保ESC键能关闭历史界面
def input(key):
    from history_manager import history_ui_active, close_history_ui
    
    print(f"键盘输入: {key}")
    
    # 如果是ESC键并且历史界面打开，优先处理
    if key == 'escape' and history_ui_active:
        print("检测到ESC键，正在关闭历史界面")
        close_history_ui()
        return  # 不继续处理其他输入
    
    # 正常处理游戏输入
    process_input(key)

# 生成第一个方块
spawn_tetromino()

# 运行游戏
app.run()
