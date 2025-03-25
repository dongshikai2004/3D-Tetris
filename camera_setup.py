from ursina import *

editor_cam = None

def setup_cameras():
    """设置更直观的辅助视图面板，确保网格与实际游戏网格一致"""
    global editor_cam
    
    from config import GRID_WIDTH, GRID_DEPTH
    from tetromino import Tetromino
    
    # 主相机调整，使其能同时看到地面和生成点
    camera.position = (0, 22, -105)  # 降低高度，减少距离
    camera.rotation_x = 30
    
    # 创建编辑器相机
    editor_cam = EditorCamera()
    editor_cam.enabled = True
    editor_cam.world_position = Vec3(-1.684801, -14.967558, 1.87233)
    editor_cam.world_rotation = Vec3(-3.7760412, -15.9722394, 0)
    editor_cam.target_z = -47.12350845336914

    
    # 创建俯视图面板 - 调整大小和位置
    top_panel = Entity(
        parent=camera.ui,
        model='quad',
        color=color.black66,
        scale=(0.35, 0.35),
        position=(0.65, 0.3),
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
        position=(0.65, 0.45),
        origin=(0,0),
        color=color.white,
        scale=1.5
    )
    
    # 创建缓存实体池
    active_marker_pool = []
    placed_marker_pool = []
    
    # 预创建一些标记点实体，修改为圆形更容易看清
    for i in range(20):
        marker = Entity(
            parent=camera.ui,
            model='circle',
            color=color.white,
            scale=(cell_width * 0.8, cell_depth * 0.8),  # 标记大小调整为单元格大小
            z=-0.15,
            enabled=False
        )
        active_marker_pool.append(marker)
        
    for i in range(100):
        marker = Entity(
            parent=camera.ui,
            model='circle',  # 改为圆形，便于区分
            color=color.gray,
            scale=(cell_width * 0.7, cell_depth * 0.7),  # 略小于活动方块
            z=-0.12,
            enabled=False
        )
        placed_marker_pool.append(marker)
    
    # 更新函数 - 修正标记点位置计算
    def update_views():
        from settings import game_paused
        from utils import world_to_grid
        from game_grid import grid_positions
        from ui import orientation_indicator
        
        if game_paused:
            return
        
        try:
            # 重置所有标记点的状态 - 添加安全检查    
            for marker in active_marker_pool + placed_marker_pool:
                if marker and hasattr(marker, 'enabled') and marker.enabled is not None:
                    marker.enabled = False
                
            # 已放置方块标记
            placed_count = 0
            
            for (gx, gy, gz), block_color in list(grid_positions.items()):  # 使用list创建副本避免迭代时修改
                if placed_count >= len(placed_marker_pool):
                    break
                    
                # 确保标记存在且有效
                marker = placed_marker_pool[placed_count]
                if not marker or not hasattr(marker, 'position') or not hasattr(marker, 'enabled'):
                    placed_count += 1
                    continue
                    
                # 计算顶视图中的精确位置
                x_pos = 0.65 - 0.175 + (gx + 0.5) * cell_width
                z_pos = 0.3 - 0.175 + (gz + 0.5) * cell_depth
                
                marker.position = Vec3(x_pos, z_pos, -0.12)
                marker.color = block_color
                marker.enabled = True
                placed_count += 1
                
            # 当前活动方块显示
            current_tetromino = None
            for entity in scene.entities:
                if isinstance(entity, Tetromino) and entity.enabled:
                    current_tetromino = entity
                    break
                    
            if current_tetromino:
                active_count = 0
                # 为活动方块的每个组成块添加标记
                for block in current_tetromino.blocks:
                    if active_count >= len(active_marker_pool) or not block:
                        break
                        
                    # 安全检查
                    marker = active_marker_pool[active_count]
                    if not marker or not hasattr(marker, 'position'):
                        active_count += 1
                        continue
                        
                    pos = block.world_position
                    gx, gy, gz = world_to_grid(Vec3(
                        round(pos.x * 2) / 2,
                        round(pos.y * 2) / 2,
                        round(pos.z * 2) / 2
                    ))
                    
                    # 计算顶视图中的精确位置
                    x_pos = 0.65 - 0.175 + (gx + 0.5) * cell_width
                    z_pos = 0.3 - 0.175 + (gz + 0.5) * cell_depth
                    
                    marker.position = Vec3(x_pos, z_pos, -0.15)
                    marker.color = current_tetromino.color
                    marker.enabled = True
                    active_count += 1
            
            current_tetromino = None
            for entity in scene.entities:
                if isinstance(entity, Tetromino) and entity.enabled:
                    current_tetromino = entity
                    break
                
            if current_tetromino and orientation_indicator:
                # 清除旧的指示模型
                for child in orientation_indicator.children:
                    if hasattr(child, 'is_block') and child.is_block:
                        destroy(child)
                    
            # 创建新的指示模型 - 使用更大的方块增强可见性
                block_size = 0.2
                for pos in current_tetromino.shape[0]:
                    block = Entity(
                        parent=orientation_indicator,
                        model='cube',
                        color=current_tetromino.color,
                        position=(pos[0]*block_size, pos[1]*block_size, pos[2]*block_size),
                        scale=(block_size*0.8, block_size*0.8, block_size*0.8),
                        texture='white_cube'
                    )
                    block.is_block = True  # 标记为方块，以便后续删除
                
            # 同步旋转，保持姿态图的基本角度以增强立体感
                base_rotation = Vec3(-5, 10, 0)  # 基础角度
                # 只同步游戏方块的旋转变化
                orientation_indicator.rotation = Vec3(
                    base_rotation.x + current_tetromino.rotation.x,
                    base_rotation.y + current_tetromino.rotation.y,
                    base_rotation.z + current_tetromino.rotation.z
                )
        except Exception as e:
            print(f"视图更新错误: {e}")
    
    return update_views

def reset_camera():
    """重置编辑器相机位置"""
    global editor_cam
    if editor_cam:
        editor_cam.world_position = Vec3(-1.684801, -14.967558, 1.87233)
        editor_cam.rotation = Vec3(-3.7760412, -15.9722394, 0)
        editor_cam.target_z = -47.12350845336914

def print_pos():
    """打印编辑器相机位置"""
    global editor_cam
    if editor_cam:
        print(editor_cam.world_position, '\n',editor_cam.rotation,'\n',editor_cam.target_z)
