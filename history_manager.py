import os
import json
import datetime
from ursina import *

# 获取当前文件所在目录
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(GAME_DIR, 'game_history.json')

# 全局变量跟踪当前是否显示历史界面
history_ui_active = False
history_container = None

def save_game_history(score, lines_cleared, duration):
    """
    保存游戏历史记录
    
    Args:
        score: 游戏得分
        lines_cleared: 清除的行数
        duration: 游戏持续时间（秒）
    """
    # 如果分数为0并且没有消除行，可能是游戏刚开始就退出，不保存记录
    if score == 0 and lines_cleared == 0 and duration < 5:  # 少于5秒的游戏不记录
        print("游戏时间太短或无得分，不保存记录")
        return
        
    # 获取当前日期和时间
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # 创建游戏记录
    game_record = {
        "date": date_str,
        "score": score,
        "lines_cleared": lines_cleared,
        "duration": duration,
        "duration_format": format_duration(duration)
    }
    
    # 加载现有历史记录
    history = load_game_history()
    
    # 添加新记录
    history.append(game_record)
    
    # 保存回文件
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        print(f"历史记录已保存 - 分数: {score}, 时间: {date_str}")
    except Exception as e:
        print(f"保存历史记录时出错: {e}")

def load_game_history():
    """
    加载游戏历史记录
    
    Returns:
        list: 游戏历史记录列表
    """
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        print(f"加载历史记录时出错: {e}")
        return []

def get_best_games(count=5):
    """
    获取最高分的游戏记录
    
    Args:
        count: 返回的记录数量
        
    Returns:
        list: 按分数排序的游戏记录列表
    """
    history = load_game_history()
    # 按分数降序排序
    sorted_history = sorted(history, key=lambda x: x["score"], reverse=True)
    return sorted_history[:count]

def format_duration(seconds):
    """
    格式化持续时间为可读形式
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的时间字符串 (mm:ss)
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def close_history_ui():
    """安全地关闭历史记录界面"""
    global history_ui_active, history_container
    
    try:
        print("正在关闭历史界面...")
        if history_container:
            # 先禁用容器防止更多错误
            history_container.enabled = False
            
            # 销毁所有子元素
            for child in history_container.children.copy():  # 使用copy避免在迭代中修改
                destroy(child)
                
            # 最后销毁容器自身
            destroy(history_container)
            history_container = None
            
        history_ui_active = False
        print("历史界面已关闭")
    except Exception as e:
        print(f"关闭历史界面时出错: {e}")
        # 确保状态被重置
        history_ui_active = False
        history_container = None

def show_history_ui():
    """显示历史记录界面"""
    global history_ui_active, history_container
    
    # 防止多次打开
    if history_ui_active:
        print("历史记录界面已经打开")
        return
        
    history_ui_active = True
    print("正在打开历史界面...")
    
    try:
        # 获取最高分记录
        best_games = get_best_games(5)
        
        # 创建UI容器 - 使用较高的排序优先级
        history_container = Entity(parent=camera.ui, enabled=True)
        
        # 创建半透明背景面板
        panel = Entity(
            parent=history_container,
            model='quad',
            scale=(0.7, 0.8),
            color=Color(0, 0, 0, 0.9),
            position=(0, 0),
            z=0  # 使用0作为基准
        )
        
        # 添加标题 - 直接在UI中显示，确保可见
        title = Text(
            text='History',
            parent=camera.ui,  # 直接附加到camera.ui
            position=(0, 0.3,-0.1),
            origin=(0, 0),
            scale=3.0,  # 增大字体
            color=color.yellow
        )
        title.parent = history_container  # 重新设置父级
        
        # 表头 - 使用更明显的颜色
        headers = ["date", "score", "times"]
        header_positions = [-0.15, 0.03, 0.2]
        
        for i, header in enumerate(headers):
            header_text = Text(
                text=header,
                parent=camera.ui,  # 先设置为camera.ui确保创建正确
                position=(header_positions[i], 0.2,-0.1),
                origin=(0, 0),
                scale=1.6,  # 增大字体
                color=color.white  # 使用橙色增加可见性
            )
            header_text.parent = history_container  # 重新设置父级
        
        # 显示历史记录
        if not best_games:
            no_record = Text(
                text='None',
                parent=camera.ui,
                position=(0, 0),
                origin=(0, 0),
                scale=2.0,  # 增大空记录提示
                color=color.red  # 使用红色确保可见
            )
            no_record.parent = history_container
        else:
            y_pos = 0.1
            for i, game in enumerate(best_games):
                # 日期
                date_text = Text(
                    text=game['date'],
                    parent=camera.ui,
                    position=(-0.15, y_pos,-0.1),
                    origin=(0, 0),
                    scale=1.0,  # 增大字体
                    color=color.white
                )
                date_text.parent = history_container
                
                # 分数 - 使用亮色
                score_text = Text(
                    text=str(game['score']),
                    parent=camera.ui,
                    position=(0.05, y_pos,-0.1),
                    origin=(-0.0, 0),
                    scale=1.0,
                    color=color.lime  # 使用高亮颜色
                )
                score_text.parent = history_container
                
                
                # 游戏时长
                time_text = Text(
                    text=game['duration_format'],
                    parent=camera.ui,
                    position=(0.2, y_pos,-0.1),
                    origin=(0, 0),
                    scale=1.0,
                    color=color.white
                )
                time_text.parent = history_container
                
                y_pos -= 0.08  # 增大间距
        
        # 添加返回按钮 - 使按钮更加明显
        close_button = Button(
            text='BACK',
            parent=camera.ui,
            position=(0, -0.35),
            scale=(0.3, 0.08),  # 更大的按钮
            color=color.azure,
            highlight_color=color.cyan,
            pressed_color=color.blue
        )
        close_button.parent = history_container
        close_button.text_entity.scale *= 1.2  # 放大按钮文字
        close_button.on_click = close_history_ui  # 直接设置函数引用
        
        # 确保ESC键可以关闭
        def history_input(key):
            if key == 'escape':
                print("检测到ESC键，关闭历史界面")
                close_history_ui()
                return True
        
        # 设置全局输入处理
        history_container.input = history_input
        
        print("历史界面已成功创建")
    except Exception as e:
        print(f"显示历史记录时出错: {e}")
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        close_history_ui()
