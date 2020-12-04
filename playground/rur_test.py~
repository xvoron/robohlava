import os
import re
import random

def book_read(self):
    text_new = re.sub('[^.,:!?\w]', ' ', text)
    if not text_new is None:
        #print("[Text from image]" + text_new)
        pass
    self.book_text = None

    if bool(text_new.strip()) and len(text_new) > 70:
        if platform == "Windows":
            text_rur = open(self.base_dir + r'\txt_file\rur.txt', 'r', encoding="utf8").read()
        else:
            text_rur = open(self.base_dir + r'/txt_file/rur.txt', 'r', encoding="utf8").read()

        text_rur_new = re.sub('[^.,:!?\w]', ' ', text_rur)
        x = 10
        y = 30
        a = None
        delka = len(text_new)
        while True:
            a = text_rur_new.find(text_new[x:y])
            if a != -1 and a != 0:
                print("\n[Find]")
                print(a)
                x = 10
                y = 30
                self.book_text = re.sub('[^,.\w]', ' ', text_rur[a:a + 200])
                print("[Text to voice] " + self.book_text)
                a = None
                break
            x = y
            y = y + 20
            if y > delka:
                break
    return self.book_text


def rur(text):
    text_max = 116774
    text_padding = 1000
    text_length = 500
    index_start = random.randint(text_padding, text_max-text_padding)
    index_start = index_start +  text[index_start:].find('.')
    index_end = index_start + text_length + text[index_start+text_length:].find('.')
    text = text[index_start+1:index_end+2]
    text = re.sub('[\n]', ' ', text)
    return text
    


def open_rur(path):
    with open(path, 'r', encoding="utf8") as f:
        text_rur = f.read()
    #text_rur = open(path, 'r', encoding="utf8").read()
    return text_rur

if __name__ == "__main__":
    path = os.getcwd() + r'.\rur.txt'
    text = open_rur(path)
    print(rur(text))

