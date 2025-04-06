from ursina import *

editor_cam = None

def setup_cameras():
    """设置更直观的辅助视图面板，确保网格与实际游戏网格一致"""
    global editor_cam
    
    from config.config import GRID_WIDTH, GRID_DEPTH
    from core.tetromino import Tetromino
    
    # 主相机调整，使其能同时看到地面和生成点
    camera.position = (0, 22, -105)  # 降低高度，减少距离
    camera.rotation_x = 30
    
    # 创建编辑器相机
    editor_cam = EditorCamera()
    editor_cam.enabled = True
    editor_cam.world_position = Vec3(-1.684801, -14.967558, 1.87233)
    editor_cam.world_rotation = Vec3(-3.7760412, -15.9722394, 0)
    editor_cam.target_z = -47.12350845336914
    
    # 创建缓存实体池
    active_marker_pool = []
    placed_marker_pool = []
    cell_width = 0.35 / GRID_WIDTH
    cell_depth = 0.35 / GRID_DEPTH
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
        from config.settings import game_paused
        from util.utils import world_to_grid
        from core.game_grid import grid_positions
        from ui.ui import orientation_indicator
        
        if game_paused:
            return
        
        try:
            # 重置所有标记点的状态 - 添加安全检查    
            for marker in active_marker_pool + placed_marker_pool:
                if marker and hasattr(marker, 'enabled') and marker.enabled is not None:
                    marker.enabled = False
                
            # 已放置方块标记 - 修改处理逻辑，确保相同(x,z)位置只显示最上层的方块
            # 首先创建一个字典，保存每个(x,z)位置的最高方块信息
            top_blocks = {}
            
            # 遍历所有已放置的方块，只保留每个(x,z)位置最高的那个
            for (gx, gy, gz), block_color in list(grid_positions.items()):
                # 创建坐标键
                xz_key = (gx, gz)
                # 如果这个位置尚未记录或当前方块比已记录方块更高
                if xz_key not in top_blocks or gy > top_blocks[xz_key][0]:
                    top_blocks[xz_key] = (gy, block_color)
            
            # 现在使用top_blocks来显示标记点
            placed_count = 0
            for (gx, gz), (gy, block_color) in top_blocks.items():
                if placed_count >= len(placed_marker_pool):
                    break
                    
                # 确保标记存在且有效
                marker = placed_marker_pool[placed_count]
                if not marker or not hasattr(marker, 'position') or not hasattr(marker, 'enabled'):
                    placed_count += 1
                    continue
                    
                # 计算顶视图中的精确位置
                x_pos = 0.62 - 0.175 + (gx + 0.5) * cell_width
                z_pos = 0.3 - 0.175 + (gz + 0.5) * cell_depth
                
                marker.position = Vec3(x_pos, z_pos, -0.12)
                marker.color = block_color
                marker.enabled = True
                placed_count += 1
                
            # 当前活动方块显示 - 同样需要处理可能的重叠问题
            current_tetromino = None
            for entity in scene.entities:
                if isinstance(entity, Tetromino) and entity.enabled:
                    current_tetromino = entity
                    break
                    
            if current_tetromino:
                # 收集活动方块的位置信息，同样处理重叠
                active_blocks = {}
                for block in current_tetromino.blocks:
                    if not block:
                        continue
                        
                    pos = block.world_position
                    gx, gy, gz = world_to_grid(Vec3(
                        round(pos.x * 2) / 2,
                        round(pos.y * 2) / 2,
                        round(pos.z * 2) / 2
                    ))
                    
                    # 创建坐标键
                    xz_key = (gx, gz)
                    # 如果这个位置尚未记录或当前方块比已记录方块更高
                    if xz_key not in active_blocks or gy > active_blocks[xz_key][0]:
                        active_blocks[xz_key] = (gy, gx, gz)
                
                # 显示活动方块标记
                active_count = 0
                for (gx, gz), (gy, grid_x, grid_z) in active_blocks.items():
                    if active_count >= len(active_marker_pool):
                        break
                        
                    # 安全检查
                    marker = active_marker_pool[active_count]
                    if not marker or not hasattr(marker, 'position'):
                        active_count += 1
                        continue
                    
                    # 计算顶视图中的精确位置
                    x_pos = 0.62 - 0.175 + (grid_x + 0.5) * cell_width
                    z_pos = 0.3 - 0.175 + (grid_z + 0.5) * cell_depth
                    
                    marker.position = Vec3(x_pos, z_pos, -0.15)
                    marker.color = current_tetromino.color
                    marker.enabled = True
                    active_count += 1
            
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
