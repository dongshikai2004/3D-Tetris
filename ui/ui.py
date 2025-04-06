from ursina import *
from util.score_manager import register_score_changed_callback, get_high_score, get_current_score, add_score
from config.config import GRID_WIDTH, GRID_DEPTH

# UI相关全局变量
score_text = None
help_text = None
orientation_indicator = None
next_preview = None
high_score_text = None

def score_changed_callback(current_score, high_score):
    """分数变化时的回调函数"""
    global score_text
    if score_text:
        try:
            score_text.text = f'score: {current_score}\nhigh score: {high_score}'
            score_text.scale = 1
        except Exception as e:
            print(f"更新分数显示时出错: {e}")

def show_game_over_ui():
    from util.score_manager import get_current_score
    from util.history_manager import show_history_ui

    # 半透明背景面板
    panel = Entity(
        model='quad',
        scale=(2, 2),
        color=Color(0, 0, 0, 0.9),  # 改为半透明
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
    final_score = get_current_score()
    score_display = Text(
        f'FINAL SCORE: {final_score}',
        position=(0, -0.05, -0.95),
        origin=(0, 0),
        scale=2,
        color=color.yellow,
        parent=camera.ui,
        enabled=True
    )
    
    # 添加查看历史记录按钮 - 修复颜色问题
    history_button = Button(
        text='查看历史记录',
        position=(0, -0.15, -0.95),
        origin=(0, 0),
        scale=(0.3, 0.06),  # 更大的按钮
        color=color.azure,
        highlight_color=color.cyan,  # 修复：使用存在的颜色
        pressed_color=color.blue,
        parent=camera.ui
    )
    
    # 使用lambda以保证正确调用
    from util.history_manager import show_history_ui
    history_button.on_click = lambda: show_history_ui()
    
    # 退出提示
    exit_hint = Text(
        'Game will exit in 3 seconds...',
        position=(0, -0.25, -0.95),
        origin=(0, 0),
        scale=1,
        color=color.light_gray,
        parent=camera.ui,
        enabled=True
    )
    
    # 添加重新开始提示
    restart_hint = Text(
        'Press R to Restart',
        position=(0, -0.35, -0.95),
        origin=(0, 0),
        scale=1.2,
        color=color.green,
        parent=camera.ui,
        enabled=True
    )
    print('Game Over!')

def create_ui():
    global score_text, help_text, high_score_text
    
    from util.utils import create_text
    from util.score_manager import get_high_score, get_current_score, register_score_changed_callback
    from util.history_manager import show_history_ui
    
    # 创建分数显示
    current_score = get_current_score()
    high_score = get_high_score()
    score_text = create_text(f'score: {current_score}\nhigh score: {high_score}', position=(-0.75, 0.45),scale=1)
    score_text.name = 'score_text'
    
    # 注册分数变化回调
    register_score_changed_callback(score_changed_callback)
    
    # 添加历史记录按钮 - 修复颜色问题
    history_button = Button(
        text='History',
        position=(-0.7, 0.35),
        scale=(0.15, 0.05),  # 稍微加大按钮
        color=color.azure,
        highlight_color=color.cyan,  # 修复：使用存在的颜色
        pressed_color=color.blue
    )
    
    # 直接设置点击处理函数
    def open_history():
        from util.history_manager import show_history_ui
        show_history_ui()
    
    history_button.on_click = open_history
    
    # 创建俯视图面板 - 调整大小和位置
    top_panel = Entity(
        parent=camera.ui,
        model='quad',
        color=color.black66,
        scale=(0.35, 0.35),
        position=(0.62, 0.3),
        z=-0.1
    )
    
    # 重新设计俯视图网格 - 让网格更精确地对应实际游戏网格
    cell_width = 0.35 / GRID_WIDTH
    cell_depth = 0.35 / GRID_DEPTH
    
    # 添加网格线 - 垂直线(X方向)
    for i in range(1,GRID_WIDTH):
        x_pos = -0.175 + (i * cell_width)
        Entity(
            parent=top_panel,
            model='quad',
            color=color.gray,
            scale=(0.003, 1),
            position=(x_pos*2.8, 0, -0.01),
            alpha=1
        )
    
    # 添加网格线 - 水平线(Z方向)
    for i in range(1,GRID_DEPTH):
        z_pos = -0.175 + (i * cell_depth)
        Entity(
            parent=top_panel,
            model='quad',
            color=color.gray,
            scale=(1, 0.003),
            position=(0, z_pos*2.8, -0.01),
            alpha=1
        )
    

    # 添加俯视图标题
    top_title = Text(
        text='Top View',
        parent=camera.ui,
        position=(0.62, 0.45),
        origin=(0,0),
        color=color.white,
        scale=1.5
    )
    
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
        'R: replay\n'
        'Mouse:Perspective',
        position=(-0.75, -0.3),
        scale=0.6  # 缩小一点以容纳更多文本
    )

def update_score(points):
    """更新游戏分数"""
    add_score(points)  # 使用score_manager中的函数来更新分数

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
    from config.config import shapes, shape_colors
    
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
        position=(-0.6, 0.0),
        z=-0.1
    )
    
    # 添加标题
    orientation_title = Text(
        text='View',
        parent=camera.ui,
        position=(-0.7, 0.13),
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
