from ursina import Vec3, Text, color
import sys

# 确保支持中文字符
def setup_encoding():
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    sys.stdin.reconfigure(encoding='utf-8') if hasattr(sys.stdin, 'reconfigure') else None

# 辅助函数：世界坐标和网格坐标转换
def world_to_grid(world_pos):
    from config.config import GRID_WIDTH, GRID_DEPTH
    # 使用floor而不是round，确保负值正确转换
    x = round(world_pos.x + GRID_WIDTH/2)
    y = round(world_pos.y)
    z = round(world_pos.z + GRID_DEPTH/2)
    return (x, y, z)
    
def grid_to_world(grid_pos):
    from config.config import GRID_WIDTH, GRID_DEPTH
    x, y, z = grid_pos
    # 返回网格中心点的世界坐标
    return Vec3(x - GRID_WIDTH/2, y, z - GRID_DEPTH/2)

# 修改字体设置，使用Ursina内置字体
def create_text(text, position, scale=1, color=color.white):
    return Text(
        text=text,
        position=position,
        scale=scale,
        color=color,
        font='VeraMono.ttf',  # 使用Ursina内置字体
        background=True,
        background_color=color  # 使用我们自定义的透明黑色
    )

# 添加调试功能
def debug_grid():
    """在控制台显示当前网格状态"""
    from config.config import GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH
    from core.game_grid import grid_positions
    
    print("\n当前网格状态:")
    for y in range(GRID_HEIGHT-1, -1, -1):
        row = []
        for x in range(GRID_WIDTH):
            has_block = False
            for z in range(GRID_DEPTH):
                if (x, y, z) in grid_positions:
                    has_block = True
                    break
            row.append('■' if has_block else '□')
        print(''.join(row))
    print("\n")
