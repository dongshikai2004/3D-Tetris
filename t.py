from ursina import *

app = Ursina()
sound_game_start = Audio(f'./resource/game_start.wav', loop=True, autoplay=True)
sound_game_start.stop()
app.run()