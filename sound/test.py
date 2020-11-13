import winsound
import time

winsound.PlaySound("snoring1", winsound.SND_ASYNC | winsound.SND_ALIAS)
time.sleep(20)
print("working")
time.sleep(5)
print("working")
winsound.PlaySound(None, winsound.SND_ASYNC)

