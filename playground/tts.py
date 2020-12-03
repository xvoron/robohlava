import pyttsx3
engine = pyttsx3.init()
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_csCZ_Jakub')
engine.setProperty('rate', 200)  # setting up new voice rate
engine.say("I will speak this text")
engine.runAndWait()
