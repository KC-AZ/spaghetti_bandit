class AudioManager:
    """
    Drop files into assets/audio/ and uncomment the relevant TODO lines.
    Supported sfx keys: 'jump', 'coin', 'death', 'grapple'
    """
    def __init__(self):
        self.music_vol = 0.7
        self.sfx_vol   = 1.0
        # TODO: self.music   = Audio('assets/audio/theme.mp3',   loop=True, autoplay=False)
        # TODO: self.jump    = Audio('assets/audio/jump.mp3',    autoplay=False)
        # TODO: self.coin    = Audio('assets/audio/coin.mp3',    autoplay=False)
        # TODO: self.death   = Audio('assets/audio/death.mp3',   autoplay=False)
        # TODO: self.grapple = Audio('assets/audio/grapple.mp3', autoplay=False)

    def play_music(self): pass  # TODO: self.music.volume = self.music_vol; self.music.play()
    def stop_music(self): pass  # TODO: self.music.stop()
    def play(self, name): pass  # TODO: sfx = getattr(self, name, None); sfx and sfx.play()
