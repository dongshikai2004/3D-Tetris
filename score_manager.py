import os

# 获取当前文件所在目录
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(GAME_DIR, 'high_score.txt')
def get_high_score():
    """从文件中读取最高分数"""
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        # 如果文件不存在或格式不正确，返回0
        return 0

def update_high_score(new_score):
    """更新最高分数
    
    Args:
        new_score: 新的分数
        
    Returns:
        bool: 如果创造了新纪录返回True，否则返回False
    """
    current_high = get_high_score()
    print('current_high:', current_high)
    print('new_score:', new_score)
    if new_score > current_high:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(new_score))
        return True  # 表示有新的最高分
    return False  # 表示没有超过最高分
