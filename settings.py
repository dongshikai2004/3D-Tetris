from ursina import *
from game_grid import grid_positions
import tetromino
from block import Block  # Assuming Block class is in a module named block

# 游戏状态
game_paused = False
pause_ui = []
invoke_sequence_pairs = []  # 存储延迟执行的函数序列
score = 0  # 游戏分数

def update_score(points):
    """更新游戏分数"""
    global score, score_text
    score += points
    if 'score_text' in globals() and score_text:
        try:
            score_text.text = f'分数: {score}'
        except:
            pass

def toggle_pause():
    """切换游戏暂停状态"""
    global game_paused, pause_ui
    from tetromino import Tetromino
    
    game_paused = not game_paused
    
    if game_paused:
        # 创建暂停界面
        pause_panel = Entity(model='quad', scale=(0.4, 0.15), color=color.black66, position=(0, 0, -0.1), parent=camera.ui)
        pause_text = Text(text='PAUSED', origin=(0, 0), scale=3, color=color.orange, position=(0, 0), parent=camera.ui)
        pause_hint = Text(text='Press P to resume', origin=(0, 0), scale=1.5, color=color.white, position=(0, -0.05), parent=camera.ui)
        
        pause_ui = [pause_panel, pause_text, pause_hint]
        
        # 暂停游戏实体
        for entity in scene.entities:
            if isinstance(entity, Tetromino):
                entity.enabled = False
    else:
        # 清除暂停界面
        for ui in pause_ui:
            destroy(ui)
        pause_ui = []
        
        # 恢复游戏实体
        for entity in scene.entities:
            if isinstance(entity, Tetromino):
                entity.enabled = True

def setup_lighting():
    # 调整主光源
    main_light = DirectionalLight(y=2, z=3, rotation=(45, -45, 45))
    
    # 增加环境光
    AmbientLight(color=color.rgba(0.7, 0.7, 0.8, 0.5))
    
    return main_light

def reset_game():
    global grid_positions, score, score_text, help_text, invoke_sequence_pairs
    from audio import play_game_start_sound  # 导入游戏启动音效函数
    
    # 清理现有的invoke调用
    try:
        for seq in invoke_sequence_pairs:
            if hasattr(seq, 'kill'):
                seq.kill()  # 停止现有序列
    except:
        pass
    
    # 重置序列列表
    invoke_sequence_pairs = []
    
    # 清除网格上的所有方块
    grid_positions.clear()
    
    # 清除场景中的所有方块
    for entity in scene.entities.copy():
        if isinstance(entity, Block) or isinstance(entity, tetromino.Tetromino):
            if entity != camera and entity != camera.ui:
                destroy(entity)
    
    # 重置分数
    score = 0
    if 'score_text' in globals() and score_text:
        try:
            score_text.text = f'分数: {score}'
        except:
            pass
    
    # 清除所有实体，包括幽灵方块
    for entity in scene.entities:
        if (not isinstance(entity, Sky) and 
            entity != camera and 
            not isinstance(entity, DirectionalLight)):
            destroy(entity)
    
    # 重置游戏状态
    grid_positions.clear()
    update_score(-score)  # 重置分数为0
    game_paused = False
    pause_ui = []
    
    # 更新UI
    from ui import create_ui
    create_ui()
    from game_logic import spawn_tetromino
    # 生成新方块
    spawn_tetromino()
    
    # 播放游戏启动音效
    play_game_start_sound()
    
    print("游戏已重置")
