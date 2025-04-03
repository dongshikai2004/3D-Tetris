import os
from ursina import *

# 获取当前文件所在目录
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(GAME_DIR, 'high_score.txt')

# 全局变量跟踪最高分
_high_score = 0
_current_score = 0
_on_score_changed_callbacks = []

def initialize():
    """初始化分数管理器"""
    global _high_score
    _high_score = _load_high_score_from_file()
    print(f"初始化分数管理器 - 最高分: {_high_score}")

def _load_high_score_from_file():
    """从文件中读取最高分数"""
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        # 如果文件不存在或格式不正确，返回0
        return 0

def _save_high_score_to_file():
    """将最高分保存到文件"""
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(_high_score))
        print(f"最高分已保存: {_high_score}")
    except Exception as e:
        print(f"保存最高分时出错: {e}")

def get_high_score():
    """获取当前最高分"""
    return _high_score

def get_current_score():
    """获取当前分数"""
    return _current_score

def reset_score():
    """重置当前分数"""
    global _current_score
    _current_score = 0
    _notify_score_changed()

def add_score(points):
    """增加分数
    
    Args:
        points: 要增加的分数
    
    Returns:
        bool: 如果创造了新纪录返回True，否则返回False
    """
    global _current_score, _high_score
    
    _current_score += points
    
    # 检查是否创造了新的最高分
    is_new_high_score = False
    if _current_score > _high_score:
        _high_score = _current_score
        _save_high_score_to_file()
        is_new_high_score = True
        print(f"新的最高分记录: {_high_score}")
    
    # 通知所有回调函数
    _notify_score_changed()
    
    return is_new_high_score

def register_score_changed_callback(callback):
    """注册分数变化的回调函数"""
    if callback not in _on_score_changed_callbacks:
        _on_score_changed_callbacks.append(callback)

def unregister_score_changed_callback(callback):
    """注销分数变化的回调函数"""
    if callback in _on_score_changed_callbacks:
        _on_score_changed_callbacks.remove(callback)

def _notify_score_changed():
    """通知所有监听者分数已经改变"""
    for callback in _on_score_changed_callbacks:
        try:
            callback(_current_score, _high_score)
        except Exception as e:
            print(f"执行分数更新回调时出错: {e}")

# 初始化
initialize()
