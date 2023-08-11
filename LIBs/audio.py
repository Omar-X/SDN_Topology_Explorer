from kivy.core.audio import SoundLoader

platform_name = "linux"

win_music = "Musics/tadaa.mp3"
lose_music = "Musics/negative_beeps.mp3"
step_music = "Musics/snow-step.mp3"


class Audio:
    def __init__(self, file_path):
        self.file_path = file_path
        self.audio = SoundLoader.load(self.file_path)

    def play_audio(self, wait_time=0.5):
        try:
            self.audio = SoundLoader.load(self.file_path)
            self.audio.play()
        except:
            self.audio = SoundLoader.load(self.file_path)

    def _close_audio(self, *args):
        if platform_name == "android":
            try:
                self.audio.stop()
            except:
                pass

