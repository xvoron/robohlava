import io
import pygame
from gtts import gTTS


def speak(text):
    with io.BytesIO() as file:
        gTTS(text=text, lang="cs").write_to_fp(file)
        file.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue


def speak2(text):
    tts = gTTS(text=text, lang='cs')
    tts.save('file.mp3')
    pygame.mixer.init()
    pygame.mixer.music.load('file.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

if __name__ == "__main__":
    test_text = "Ahoj jak se maš?"
    speak2(test_text)

