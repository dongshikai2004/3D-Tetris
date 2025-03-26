from ursina import *
from score_manager import update_high_score
# UI相关全局变量
score = 0
score_text = None
help_text = None
orientation_indicator = None
next_preview = None
high_score_text = None
def show_game_over_ui():

    # 半透明背景面板
    panel = Entity(
        model='quad',
        scale=(2, 2),
        color=Color(0, 0, 0, 1),
        position=(0, 0.3, -0.91),
        parent=camera.ui,
        enabled=True
    )
    
    # 大号红色游戏结束文字
    game_over_text = Text(
        'GAME OVER',
        position=(0, 0.15, -0.95),
        origin=(0, 0),
        scale=3,
        color=color.red,
        parent=camera.ui,
        enabled=True

    )
    
    # 显示最终分数
    score_display = Text(
        f'FINAL SCORE: {score}',
        position=(0, -0.05, -0.95),
        origin=(0, 0),
        scale=2,
        color=color.yellow,
        parent=camera.ui,
        enabled=True
    )
    # 退出提示
    exit_hint = Text(
        'Game will exit in 3 seconds...',
        position=(0, -0.15, -0.95),
        origin=(0, 0),
        scale=1,
        color=color.light_gray,
        parent=camera.ui,
        enabled=True

    )
    print('Game Over!')

def create_ui():
    global score_text, help_text, high_score_text
    
    from utils import create_text
    from score_manager import get_high_score
    
    # 创建分数显示
    score_text = create_text(f'score: {score}', position=(-0.75, 0.45),scale=1)
    score_text.name = 'score_text'
    
    # 添加最高分显示
    high_score = get_high_score()
    high_score_text = Text(
        text=f'high score: {high_score}', 
        position=(-0.75, 0.4),
        color=color.gold
    )
    high_score_text.name = 'high_score_text'
    
    # 创建帮助文本
    help_text = create_text(
        'option:\n'
        'W: X-rotation\n'
        'S: Y-rotation\n'
        'D: Z-rotation\n'
        'Space: accelerate\n'
        'Alt: down\n'
        'P: Pause\n'
        'V:reset camera\n'
        'R: replay',
        position=(-0.75, -0.3),
        scale=0.5  # 缩小一点以容纳更多文本
    )

def update_score(points):
    global score, score_text
    
    score += points
    if score_text:
        try:
            score_text.text = f'  {score}  '
            score_text.scale = 1
        except:
            pass  # 忽略可能的文本更新错误
    if update_high_score(score):
        high_score_text.text = f'high score: {score}'
    

def setup_next_preview():
    """创建下一个方块预览面板"""
    global next_preview
    # 创建预览面板
    preview_panel = Entity(
        parent=camera.ui,
        model='quad',
        color=color.black66,
        scale=(0.25, 0.25),
        position=(0.65, -0.3),
        z=-0.1
    )
    
    # 添加标题
    preview_title = Text(
        text='Next',
        parent=camera.ui,
        position=(0.65, -0.15),
        origin=(0, 0),
        color=color.white,
        scale=1.2
    )
    
    # 创建方块容器
    preview_container = Entity(
        parent=preview_panel,
        position=(0, 0, -0.05),
        rotation=(-5, 10, 0)  # 默认视角与姿态图保持一致
    )
    
    # 添加固定光源，增强立体感
    light = PointLight(
        parent=preview_panel,
        position=(0.1, 0.1, -0.2),
        color=color.white,
        intensity=1.5
    )
    
    next_preview = preview_container
    return next_preview

def update_next_preview(next_shape_key, next_preview):
    """更新下一个方块预览"""
    from config import shapes, shape_colors
    
    if not next_shape_key:
        return
        
    # 清除旧的预览方块
    if next_preview:
        for child in next_preview.children:
            destroy(child)
    
    # 获取下一个方块的形状和颜色
    shape_positions = shapes[next_shape_key][0]
    block_color = shape_colors[next_shape_key]
    
    # 创建新的预览方块
    block_size = 0.15  # 适当调整大小以适应预览面板
    
    for pos in shape_positions:
        block = Entity(
            parent=next_preview,
            model='cube',
            texture='white_cube',
            color=block_color,
            position=(pos[0]*block_size, pos[1]*block_size, pos[2]*block_size),
            scale=(block_size*0.9, block_size*0.9, block_size*0.9)
        )

def setup_orientation_view():
    """创建立体姿态图，展示当前方块的空间朝向"""
    global orientation_indicator
    
    # 创建姿态图面板
    orientation_panel = Entity(
        parent=camera.ui,
        model='quad',
        color=color.black66,
        scale=(0.32, 0.32),  # 略微增大面板尺寸
        position=(-0.65, 0.0),
        z=-0.1
    )
    
    # 添加标题
    orientation_title = Text(
        text='View',
        parent=camera.ui,
        position=(-0.75, 0.13),
        origin=(0,0),
        color=color.white,
        scale=1.2
    )
    
    # 创建方块容器，稍微倾斜以增加立体感
    indicator = Entity(
        parent=orientation_panel, 
        position=(0, 0, -0.05),
        rotation=(30, 45, 0)  # 设置默认旋转角度增强立体感
    )
    
    # 添加参考网格
    grid = Entity(
        parent=indicator,
        model='grid',
        scale=(0.15, 0.15, 0.15),
        color=color.gray,
        position=(0, 0, 0),
        alpha=0.2
    )
    
    orientation_indicator = indicator
    return orientation_indicator
