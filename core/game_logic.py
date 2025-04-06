from ursina import *
from random import choice
import sys
import time
import os
from core.tetromino import Tetromino
from util.utils import debug_grid
from ui.ui import update_next_preview, show_game_over_ui
from util.history_manager import history_ui_active  # 导入历史界面状态

# 添加全局变量以存储下一个方块形状
next_shape_key = None

def save_current_game_state():
    """保存当前游戏状态到历史记录"""
    import config.settings as settings  # 导入设置
    from util.score_manager import get_current_score
    from util.history_manager import save_game_history
    
    # 计算游戏持续时间
    game_duration = time.time() - settings.game_start_time if settings.game_start_time else 0
    
    # 获取当前分数
    score = get_current_score()
    
    # 保存游戏历史
    save_game_history(score, settings.lines_cleared, game_duration)
    print(f"已保存游戏记录 - 分数: {score}, 行数: {settings.lines_cleared}, 时长: {game_duration:.2f}秒")

def end_game_and_exit():
    """延迟退出游戏"""
    from audio.audio import play_game_over_sound  # 导入游戏结束音效函数
    
    # 保存游戏历史
    save_current_game_state()
    
    for entity in scene.entities:
        entity.enabled = False
    show_game_over_ui()
    
    # 播放游戏结束音效
    play_game_over_sound()
    
    print("游戏结束，正在退出...")
    sys.exit(0)

def spawn_tetromino():
    """生成新的俄罗斯方块"""
    global next_shape_key
    
    from config.config import shapes, GRID_WIDTH, GRID_DEPTH, GRID_HEIGHT
    from core.game_grid import grid_positions
    
    try:
        # 首先检查生成位置是否已被占用
        if any(grid_positions.get((x, GRID_HEIGHT, z)) for x in range(GRID_WIDTH) for z in range(GRID_DEPTH)):
            print("生成位置已被占用，游戏结束！")
            
            # 游戏结束界面在Tetromino.land()中处理
            
            # 延迟退出，确保玩家能看到分数
            invoke(end_game_and_exit, delay=3)
            return None
        
        # 如果没有预先选择的下一个形状，就随机生成一个
        current_shape_key = next_shape_key if next_shape_key else choice(list(shapes.keys()))
        # 为下一个方块随机选择新形状
        next_shape_key = choice(list(shapes.keys()))
        
        # 更新预览
        from ui.ui import next_preview
        update_next_preview(next_shape_key, next_preview)
        
        # 生成当前方块
        tetromino = Tetromino(shape_key=current_shape_key)
        invoke(tetromino.update_ghost_position, delay=0.1)
        return tetromino
    except Exception as e:
        print(f"生成方块错误: {e}")
        return None

def process_input(key):
    from config.settings import game_paused, toggle_pause
    from ui.camera_setup import reset_camera
    from core.tetromino import Tetromino
    from util.history_manager import history_ui_active, close_history_ui
    
    # 处理历史界面的ESC键
    if key == 'escape' and history_ui_active:
        close_history_ui()
        return
    
    if key == 'v':
        reset_camera()
        
    # 暂停控制
    if key == 'p':
        toggle_pause()
        return
        
    # 如果游戏已暂停，除了暂停键外不处理其他输入
    if game_paused:
        return
    
    # 如果历史记录界面打开，不处理游戏控制输入
    if history_ui_active:
        return
        
    # 获取当前控制的方块
    current = None
    for entity in scene.entities:
        if isinstance(entity, Tetromino):
            current = entity
            break
    
    # 修改R键行为为重启整个程序（R键单独处理，不需要current存在）
    if key == 'r':
        print("重启程序...")
        restart_program()
        return
        
    # 如果没有找到当前方块，跳过需要current的操作
    if current is None:
        print("警告: 没有找到当前控制的方块")
        return
    
    # 移动控制
    if key == 'left arrow' and current.move_cooldown <= 0:
        current.move(dx=-1)
        current.move_cooldown = 0.1
    if key == 'right arrow' and current.move_cooldown <= 0:
        current.move(dx=1)
        current.move_cooldown = 0.1
    if key == 'up arrow' and current.move_cooldown <= 0:
        current.move(dz=1)
        current.move_cooldown = 0.1
    if key == 'down arrow' and current.move_cooldown <= 0:
        current.move(dz=-1)
        current.move_cooldown = 0.1
    
    # 旋转控制 - 三个轴的旋转
    if key == 'w':  # X轴逆时针
        current.rotate(axis='x')
    if key == 's':  # X轴顺时针
        current.rotate(axis='z')
    if key == 'd':  # Z轴顺时针
        current.rotate(axis='y', clockwise=False)
    
    # 加速下落
    if key == 'space':
        current.fall_speed = 20
    elif current.fall_speed == 20:
        current.fall_speed = 2
    # 直接落地
    if key == 'alt':
        current.fall_speed = 100

def restart_program():
    """完全重启整个程序，而不仅仅是重置游戏状态"""
    try:
        # 在重启前保存当前游戏状态
        save_current_game_state()
        
        # 获取当前程序路径
        python = sys.executable
        script = os.path.abspath(sys.argv[0])
        print(f"Python: {python}, Script: {script}")
        
        # 通知用户
        print("正在重启游戏...")
        # 启动新进程
        
        os.execl(python, python, script)
        # 关闭当前程序
        application.quit()
        
    except Exception as e:
        print(f"重启失败: {e}")
        # 如果重启失败，尝试常规退出
        sys.exit(0)
