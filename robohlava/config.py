# -*- coding:utf-8 -*-

"""
  ____ ___  _   _ _____ ___ ____   _____ ___ _     _____
 / ___/ _ \| \ | |  ___|_ _/ ___| |  ___|_ _| |   | ____|
| |  | | | |  \| | |_   | | |  _  | |_   | || |   |  _|
| |__| |_| | |\  |  _|  | | |_| | |  _|  | || |___| |___
 \____\___/|_| \_|_|   |___\____| |_|   |___|_____|_____|

"""

#--------------------------------------------------------------
# FLAGS
#--------------------------------------------------------------
flag_arduino = True
flag_voice = True
flag_realsense = True

#--------------------------------------------------------------
# CONSTANTS
#--------------------------------------------------------------

# Video
WIDTH = 640
HEIGHT = 480
#WIDTH = 1280
#HEIGHT = 720

# Arduino
arduino_base = [105, 50]    # [horizontal, vertical]
arduino_right = [70, 50]
arduino_left = [150, 50]
arduino_padding = 20
arduino_x_constant = 2
arduino_y_constant = 5
arduino_x_multiplicator = 0.03
arduino_y_multiplicator = 0.1
arduino_com_port = 'COM3'

# Voice
voice_padding_constant = 2.5
voice_padding_init = 60

# OS
os = "Windows"

# Number of frames to start tracking/untracking person after appear/disappear
num_person2track = 20
num_person2untrack = 20

# Every N frames net-yolo will process
yolo_ratio = 1
greeting_yolo_ratio = 1


# Games
games_maximum_stage_choice_btn = 5
games_change_person_text = ['Proč jseš tak pomaly, tak zkusím nekoho \
        jíneho ... ale nevylučuju, že to znovu nebudeš ty ...']

# Person class properties
person_memory_length = 20

#--------------------------------------------------------------
# TEXTS
#--------------------------------------------------------------

# RUR
text_rur_max = 116774
text_rur_padding = 1000
text_rur_length = 500

# Init
init_phrase = "Jsem hotov k praci"

# Yolo
yolo_end_text = "Vidím před sebou ... "


# Buttons
info_label_default_text = "Vydržte než to dokončím!"
info_label_game_text = "Vyber si na obrazovce!"
btn1_text = "Čtení textu!"
btn2_text = "Not implemented yet"
btn3_text = "Poznám co ukážeš!"
btn4_text = "Not implemented yet"

button_cancel_text = ["Už tě to nebaví? Vyber si neco jineho..."]

#--------------------------------------------------------------
# TIMERS
#--------------------------------------------------------------
timer_init2wait = 400
timer_wait2search = 200
timer_search2sleep = 200
timer_greeting2games = 200
timer_sleep2wait = 400
timer_book2game = 200

# Games
game_start_delay = 10

# Book
timer_book_start = 100
timer_book2games = 150

# Yolo
timer_yolo_start = 100
timer_yolo2games = 150

#--------------------------------------------------------------
# STAGES
#--------------------------------------------------------------
stage_greeting2games = 4

#--------------------------------------------------------------
# COLORS BGR format for openCV
#--------------------------------------------------------------
color_yolo = (18, 78, 35)               ##234e12 
color_mini = (18, 78, 35)               ##234e12 
color_center_circle = (36, 155, 69)     ##459b24
color_tracking_person = (0, 0, 224)     ##E00000
color_person = (255, 0, 0)             ##234e12

# Colors lib:
# (12, 20, 146)              ##92140C
