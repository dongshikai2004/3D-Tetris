from ursina import *
import time
from random import choice
from block import Block, GhostBlock
from utils import world_to_grid
from config import shapes, shape_colors
from game_grid import grid_positions, check_lines
from settings import game_paused

class Tetromino(Entity):
    def __init__(self, shape_key=None):
        super().__init__()
        self.blocks = []
        self.ghost_blocks = []
        self.shape_key = shape_key if shape_key else choice(list(shapes.keys()))
        self.shape = shapes[self.shape_key]
        self.color = shape_colors[self.shape_key]
        
        # 活动方块使用更亮的颜色（亮度1.3）
        for pos in self.shape[0]:
            block = Block(position=pos, block_color=self.color, brightness=1.3)
            self.blocks.append(block)
            block.parent = self
            
            # 创建幽灵方块（预览）
            ghost = GhostBlock(position=pos, block_color=self.color)
            self.ghost_blocks.append(ghost)
            ghost.parent = self
            
        self.position = (0, 15, 0)
        self.fall_speed = 0.5
        self.move_cooldown = 0
        self.last_fall_time = time.time()
        self.ghost_tetromino = Entity(model=None)  # 用于保存幽灵方块的父实体
        
        # 初始化幽灵方块位置
        self.update_ghost_position()
    
    def update(self):
        # 如果游戏已暂停，不进行更新
        if game_paused:
            return
            
        # 控制方块下落
        if time.time() - self.last_fall_time > 1.0 / self.fall_speed:
            self.move(dy=-1)
            self.last_fall_time = time.time()
        
        # 冷却时间，防止按键过快
        if self.move_cooldown > 0:
            self.move_cooldown -= time.dt
        
        # 更新幽灵方块位置 - 添加安全检查
        if hasattr(self, 'enabled') and self.enabled:
            self.update_ghost_position()
            
    def move(self, dx=0, dy=0, dz=0):
        original_pos = self.position
        self.position += Vec3(dx, dy, dz)
        
        if self.check_collision():
            self.position = original_pos
            # 如果是向下移动且碰撞，则落地
            if dy < 0:
                self.land()
            return False
        
        # 更新幽灵方块位置
        self.update_ghost_position()
        return True
        
    def check_collision(self):
        from config import GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH
        
        # 检查与边界and已有方块的碰撞
        for block in self.blocks:
            world_pos = block.world_position
            # 更加精确的位置处理
            x = round(world_pos.x * 2) / 2
            y = round(world_pos.y * 2) / 2
            z = round(world_pos.z * 2) / 2
            
            grid_pos = world_to_grid(Vec3(x, y, z))
            gx, gy, gz = grid_pos
            
            # 检查边界
            if not (0 <= gx < GRID_WIDTH and gy >= 0 and 0 <= gz < GRID_DEPTH):
                return True
            
            # 检查与其他方块碰撞
            if grid_positions.get((gx, gy, gz)):
                return True
                
        return False
        
    def rotate(self, axis='y', clockwise=True):
        """围绕指定轴旋转方块
        
        Args:
            axis: 旋转轴，可选 'x', 'y', or 'z'
            clockwise: 是否顺时针旋转
        """
        # 使用Vec3构造函数创建副本，而不是使用.copy()
        original_rotation = Vec3(self.rotation.x, self.rotation.y, self.rotation.z)
        
        rotation_amount = 90 if clockwise else -90
        
        if axis == 'y':
            self.rotation_y += rotation_amount
        elif axis == 'x':
            self.rotation_x += rotation_amount
        elif axis == 'z':
            self.rotation_z += rotation_amount
            
        # 检查碰撞并尝试调整位置
        if self.check_collision():
            # 尝试偏移位置解决碰撞，对不同的旋转轴使用不同的调整方案
            offsets = []
            if axis == 'y':
                offsets = [(1,0), (-1,0), (0,1), (0,-1)]
            elif axis == 'x':
                offsets = [(0,1), (0,-1), (1,0), (-1,0)]
            elif axis == 'z':
                offsets = [(1,0), (-1,0), (0,1), (0,-1)]
                
            success = False
            for dx, dz in offsets:
                self.x += dx
                self.z += dz
                if not self.check_collision():
                    self.update_ghost_position()  # 更新成功后更新幽灵位置
                    success = True
                    break
                self.x -= dx
                self.z -= dz
            
            # 如果所有偏移都失败，再尝试上下偏移
            if not success:
                for dy in [1, -1]:
                    self.y += dy
                    if not self.check_collision():
                        self.update_ghost_position()
                        success = True
                        break
                    self.y -= dy
            
            # 如果仍然失败，恢复原始旋转
            if not success:
                self.rotation_x = original_rotation.x
                self.rotation_y = original_rotation.y
                self.rotation_z = original_rotation.z
                return False
                
        self.update_ghost_position()  # 旋转成功后更新幽灵位置
        return True
    
    def update_ghost_position(self):
        """更新幽灵方块位置，展示方块最终落地位置"""
        # 添加安全检查，确保实体仍然有效
        if not hasattr(self, 'enabled') or not self.enabled:
            return
            
        # 清除旧的幽灵方块
        if hasattr(self, 'ghost_tetromino') and self.ghost_tetromino:
            try:
                destroy(self.ghost_tetromino)
            except:
                pass  # 忽略可能的错误
            self.ghost_tetromino = None
            
        # 创建新的幽灵方块
        try:
            self.ghost_tetromino = Entity(
                model=None,
                position=Vec3(*self.position),  # 使用Vec3复制位置，而不是直接引用
                rotation=Vec3(*self.rotation)   # 使用Vec3复制旋转，而不是直接引用
            )
            
            # 创建幽灵块
            ghost_blocks = []
            for block in self.blocks:
                if block and hasattr(block, 'position'):
                    rel_pos = Vec3(*block.position)  # 复制位置
                    ghost = GhostBlock(position=rel_pos, block_color=self.color)
                    ghost.parent = self.ghost_tetromino
                    ghost_blocks.append(ghost)
            
            # 不断下移幽灵方块直到碰撞
            drop_distance = 0
            while True and self.ghost_tetromino and self.ghost_tetromino.enabled:
                self.ghost_tetromino.y -= 1
                drop_distance += 1
                
                # 检查幽灵方块是否碰撞
                if self.check_ghost_collision():
                    self.ghost_tetromino.y += 1  # 回退一步
                    break
                    
                # 防止无限循环
                from config import GRID_HEIGHT
                if drop_distance > GRID_HEIGHT * 2:
                    break
        except Exception as e:
            print(f"幽灵方块更新错误: {e}")
            if hasattr(self, 'ghost_tetromino') and self.ghost_tetromino:
                try:
                    destroy(self.ghost_tetromino)
                except:
                    pass
                self.ghost_tetromino = None
    
    def check_ghost_collision(self):
        """检查幽灵方块是否碰撞"""
        from config import GRID_WIDTH, GRID_DEPTH
        
        if not hasattr(self, 'ghost_tetromino') or not self.ghost_tetromino:
            return False
            
        for ghost in self.ghost_tetromino.children:
            if not hasattr(ghost, 'world_position'):
                continue
                
            world_pos = ghost.world_position
            x = round(world_pos.x * 2) / 2
            y = round(world_pos.y * 2) / 2
            z = round(world_pos.z * 2) / 2
            
            grid_pos = world_to_grid(Vec3(x, y, z))
            gx, gy, gz = grid_pos
            
            # 检查边界
            if not (0 <= gx < GRID_WIDTH and gy >= 0 and 0 <= gz < GRID_DEPTH):
                return True
            
            # 检查与其他方块碰撞
            if grid_positions.get((gx, gy, gz)):
                return True
                
        return False
        
    def land(self):
        from config import GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH
        from utils import world_to_grid, grid_to_world, debug_grid
        from game_logic import spawn_tetromino, end_game_and_exit
        from ui import game_over_ui, score
        
        # 首先销毁幽灵方块，防止后续操作引用已销毁对象
        if hasattr(self, 'ghost_tetromino') and self.ghost_tetromino:
            try:
                destroy(self.ghost_tetromino)
            except:
                pass
            self.ghost_tetromino = None
        
        # 将方块固定到网格中，使用暗色且半透明的版本
        for block in self.blocks:
            world_pos = block.world_position
            # 保留小数点后一位，避免舍入误差
            x = round(world_pos.x * 2) / 2
            y = round(world_pos.y * 2) / 2
            z = round(world_pos.z * 2) / 2
            
            # 转换到网格坐标
            grid_pos = world_to_grid(Vec3(x, y, z))
            gx, gy, gz = grid_pos
            
            # 获取原始颜色
            original_color = block.original_color if hasattr(block, 'original_color') else block.color
            
            # 创建暗色且半透明的版本（亮度0.7，透明度0.7）
            darker_color = Color(
                original_color.r * 0.7,
                original_color.g * 0.7,
                original_color.b * 0.7,
                0.95  # 设置透明度为0.7
            )
            
            # 确保在有效范围内
            if 0 <= gx < GRID_WIDTH and gy >= 0 and 0 <= gz < GRID_DEPTH:
                # 保存暗色方块到网格中
                grid_positions[(gx, gy, gz)] = darker_color
                
                # 计算世界坐标位置
                world_pos_fixed = grid_to_world((gx, gy, gz))
                
                # 创建固定方块，使用暗色且半透明的版本
                Entity(
                    model='cube',
                    color=darker_color,
                    position=world_pos_fixed,
                    scale=(0.95, 0.95, 0.95),
                    texture='white_cube'  # 确保使用与活动方块相同的纹理
                )
                print(f"方块固定在: 网格({gx},{gy},{gz}), 世界({world_pos_fixed})")
            else:
                print(f"警告: 方块在界外 网格({gx},{gy},{gz}), 世界({x},{y},{z})")
        
        # 禁用自身更新，防止销毁后仍然尝试更新幽灵方块
        self.enabled = False
        
        # 处理消除行
        check_lines()
        
        # 检查游戏结束条件 - 检查生成位置附近是否有方块
        spawn_y = 15  # 新方块生成的Y坐标
        spawn_check_range = 3  # 检查生成点上下3格范围内
        
        # 如果生成位置附近已经有方块，或者顶部有方块，则游戏结束
        game_over_condition = any(grid_positions.get((x, y, z)) 
                             for y in range(spawn_y - spawn_check_range, spawn_y + spawn_check_range) 
                             for x in range(GRID_WIDTH) 
                             for z in range(GRID_DEPTH))
        
        if game_over_condition or any(grid_positions.get((x, GRID_HEIGHT-1, z)) 
                                   for x in range(GRID_WIDTH) 
                                   for z in range(GRID_DEPTH)):
            print("检测到游戏结束条件！")
            
            # 创建一个更明显的游戏结束界面
            game_over_ui = []
            
            # 半透明背景面板
            panel = Entity(
                model='quad',
                scale=(2, 2),
                color=Color(0, 0, 0, 1),
                position=(0, 0.3, -0.91),
                parent=camera.ui
            )
            game_over_ui.append(panel)
            
            # 大号红色游戏结束文字
            game_over_text = Text(
                'GAME OVER',
                position=(0, 0.15, -0.95),
                origin=(0, 0),
                scale=3,
                color=color.red,
                parent=camera.ui
            )
            game_over_ui.append(game_over_text)
            
            # 显示最终分数
            score_display = Text(
                f'FINAL SCORE: {score}',
                position=(0, -0.05, -0.95),
                origin=(0, 0),
                scale=2,
                color=color.yellow,
                parent=camera.ui
            )
            game_over_ui.append(score_display)
            
            # 退出提示
            exit_hint = Text(
                'Game will exit in 3 seconds...',
                position=(0, -0.15, -0.95),
                origin=(0, 0),
                scale=1,
                color=color.light_gray,
                parent=camera.ui
            )
            game_over_ui.append(exit_hint)
            
            # 禁用所有游戏更新，但保持UI显示
            for entity in scene.entities:
                if hasattr(entity, 'enabled') and entity not in game_over_ui:
                    entity.enabled = False
            
            # 延迟退出，确保玩家能看到分数
            invoke(end_game_and_exit, delay=2)
            destroy(self)
            return
        
        # 如果游戏没有结束，生成新方块
        new_tetromino = spawn_tetromino()
        
        # 最后销毁当前方块
        destroy(self)
        
        # 打印调试信息
        debug_grid()  # 打印当前网格状态
