from ursina import *

class Block(Entity):
    def __init__(self, position=(0,0,0), block_color=color.white, brightness=1.0):
        # 保存原始颜色
        self.original_color = block_color
        
        # 调整亮度和不透明度
        adjusted_color = Color(
            min(block_color.r * brightness, 1.0),
            min(block_color.g * brightness, 1.0),
            min(block_color.b * brightness, 1.0),
            1.0  # 确保活动方块完全不透明
        )
        
        super().__init__(
            position=position,
            model='cube',
            texture='white_cube',
            color=adjusted_color,
            scale=(0.95, 0.95, 0.95),  # 稍微缩小以便看到边界
            collider='box'  # 添加碰撞体，帮助调试
        )

class GhostBlock(Entity):
    """预览块，显示方块的最终下落位置"""
    def __init__(self, position=(0,0,0), block_color=color.white):
        # 更半透明的幽灵方块
        super().__init__(
            position=position,
            model='cube',
            texture='white_cube',
            color=Color(block_color.r, block_color.g, block_color.b, 0.2),  # 更透明
            scale=(0.95, 0.95, 0.95)
        )
