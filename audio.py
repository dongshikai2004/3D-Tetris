from ursina import *
import os

# 音效文件路径
SOUND_LANDING = f'resource/pop.ogg'
SOUND_LINE_CLEAR = f'resource/shape_locked.mp3'
SOUND_GAME_OVER = f'resource/game_over.mp3'
SOUND_GAME_START = f'resource/game_start.wav'

# 创建音效对象
sound_landing = None
sound_line_clear = None
sound_game_over = None
sound_game_start = None

def load_sounds():
    """加载所有音效"""
    global sound_landing, sound_line_clear, sound_game_over, sound_game_start
    
    # 使用默认音效（如果找不到指定的音效文件）
    sound_landing = Audio('click', loop=False, autoplay=False, channel=1)
    sound_line_clear = Audio('coin', loop=False, autoplay=False, channel=2)
    sound_game_over = Audio('error', loop=False, autoplay=False, channel=3)
    sound_game_start = Audio('notification', loop=True, autoplay=False, channel=0)
    print('加载默认音效')
    # 尝试加载自定义音效（如果存在）
    try:
        if os.path.exists(SOUND_LANDING):
            sound_landing = Audio(SOUND_LANDING, loop=False, autoplay=False,channel=1)
        if os.path.exists(SOUND_LINE_CLEAR):
            sound_line_clear = Audio(SOUND_LINE_CLEAR, loop=False, autoplay=False,channel=2)
        if os.path.exists(SOUND_GAME_OVER):
            sound_game_over = Audio(SOUND_GAME_OVER, loop=False, autoplay=False,channel=3)
        if os.path.exists(SOUND_GAME_START):
            sound_game_start = Audio(SOUND_GAME_START, loop=True, autoplay=False,channel=4)
    except Exception as e:
        print(f"加载音效文件时出错: {e}")

def play_landing_sound():
    """播放方块落地音效"""
    if sound_landing:
        sound_landing.play()

def play_line_clear_sound():
    """播放消行音效"""
    if sound_line_clear:
        sound_line_clear.play()

def play_game_over_sound():
    """播放游戏结束音效"""
    if sound_game_over:
        sound_game_over.play()

def play_game_start_sound():
    """播放游戏开始音效"""
    if sound_game_start and not sound_game_start.playing:
        sound_game_start.volume=0.1
        sound_game_start.play()
