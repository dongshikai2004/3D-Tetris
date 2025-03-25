from ursina import *
from utils import grid_to_world
from score_manager import update_high_score, get_high_score
from ui import update_score, high_score_text,score
# 全局字典保存已放置的方块位置和颜色
grid_positions = {}

def create_game_grid():
    from config import GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH
    
    # 添加水平方向网格线
    for x in range(GRID_WIDTH + 1):
        Entity(
            model='wireframe_cube',
            scale=(0.05, GRID_HEIGHT, GRID_DEPTH),
            position=(x - GRID_WIDTH/2-1/2, GRID_HEIGHT/2- 1/2, -1/2),
            color=color.gray,
            alpha=0.3
        )
    
    # 添加垂直方向网格线
    for z in range(GRID_DEPTH + 1):
        Entity(
            model='wireframe_cube',
            scale=(GRID_WIDTH, GRID_HEIGHT, 0.05),
            position=(-1/2, GRID_HEIGHT/2- 1/2, z - GRID_DEPTH/2-1/2),
            color=color.gray,
            alpha=0.3
        )

def check_lines():
    global high_score_text
    from config import GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH
    
    lines_cleared = 0
    
    # 检查每一层
    for y in range(GRID_HEIGHT):
        # 如果一整层都被填满
        if all(grid_positions.get((x, y, z)) for x in range(GRID_WIDTH) for z in range(GRID_DEPTH)):
            lines_cleared += 1
            
            # 移除该层方块
            for x in range(GRID_WIDTH):
                for z in range(GRID_DEPTH):
                    if (x, y, z) in grid_positions:
                        del grid_positions[(x, y, z)]
            
            # 将上面的方块下移
            new_grid = {}
            for (gx, gy, gz), color in grid_positions.items():
                new_y = gy - 1 if gy > y else gy
                new_grid[(gx, new_y, gz)] = color
            
            grid_positions.clear()
            grid_positions.update(new_grid)
            
            # 更新视觉效果 - 找到并移除对应的实体，然后下移上层实体
            # 1. 首先销毁被消除行的实体
            entities_to_destroy = []
            for entity in scene.entities:
                # 仅处理游戏中的固定方块
                if (hasattr(entity, 'position') and 
                    hasattr(entity, 'scale') and 
                    abs(entity.scale.x - 0.95) < 0.1 and
                    abs(entity.scale.y - 0.95) < 0.1 and
                    abs(entity.scale.z - 0.95) < 0.1 and
                    entity != camera and
                    not hasattr(entity, 'ui') and
                    not getattr(entity, 'is_editor_camera', False) and 
                    entity.name!='score_text' and
                    entity.name!='high_score_text' and
                    # 确保不是UI的子实体
                    (not hasattr(entity, 'parent') or 
                     (entity.parent != camera.ui and not hasattr(entity.parent, 'parent') or 
                      entity.parent.parent != camera.ui))):
                    
                    from utils import world_to_grid
                    grid_pos = world_to_grid(entity.position)
                    if grid_pos[1] == y:
                        entities_to_destroy.append(entity)
            
            for entity in entities_to_destroy:
                destroy(entity)
            
            # 2. 将上层实体下移 - 仅移动游戏方块，排除所有其他实体
            for entity in scene.entities:
                # 使用更精确的条件筛选真正的游戏方块
                if (hasattr(entity, 'position') and 
                    # 固定方块的scale检查
                    hasattr(entity, 'scale') and 
                    abs(entity.scale.x - 0.95) < 0.1 and
                    abs(entity.scale.y - 0.95) < 0.1 and
                    abs(entity.scale.z - 0.95) < 0.1 and
                    # 排除特殊实体和UI相关元素
                    entity != camera and
                    not isinstance(entity, EditorCamera) and
                    not hasattr(entity, 'ui') and
                    # 确保不是UI的直接或间接子实体
                    (not hasattr(entity, 'parent') or 
                     (entity.parent != camera.ui and 
                      (not hasattr(entity.parent, 'parent') or 
                       entity.parent.parent != camera.ui)))):
                    
                    # 如果位置在y以上，则下移
                    from utils import world_to_grid
                    grid_pos = world_to_grid(entity.position)
                    if grid_pos[1] > y:
                        entity.y -= 1
            
            # 更新分数
            update_score(100)
            # 检查是否有新高分并更新显示
            if update_high_score(score):
                high_score_text.text = f'high score: {score}'
                print(f"新高分: {high_score_text.text}")

