# -*- coding: utf-8 -*-
# Game Initialization
import pygame
import os
import sqlite3
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import re
from urllib.parse import quote
import random


pygame.init()

os.environ['SDL_VIDEO_CENTERED'] = '1'

# Game Resolution
screen_width=800
screen_height=600
screen=pygame.display.set_mode((screen_width, screen_height))
background = pygame.image.load('build.png')

pygame.mixer.music.load('CokeTown.mp3')
pygame.mixer.music.play(-1)

icon = pygame.image.load('books.png')
pygame.display.set_icon(icon)

# download kani_data_input
kanzi_data = []
 
# Text Renderer
def text_format(message, textFont, textSize, textColor):
    newFont=pygame.font.Font(textFont, textSize)
    newText=newFont.render(message, 0, textColor)
 
    return newText

def remove_tag(content):
   cleanr =re.compile('<.*?>')
   cleantext = re.sub(cleanr, '', content)
   return cleantext

def replaceAll(in_str, arr):
    out_str = in_str
    for st in arr:
        out_str = out_str.replace(st, ' ')
    return out_str
    
 
# Colors
white=(255, 255, 255)
black=(0,0,0)
gray=(50, 50, 50)
red=(255, 0, 0)
green=(0, 255, 0)
blue=(15, 78, 119)
yellow=(255, 255, 0)
brown=(243, 156, 18)
 
# Game Fonts
# font = "Bubblegum.ttf"
font = 'Bubblegum.ttf'

 
 
# Game Framerate
clock = pygame.time.Clock()
FPS=30

conn = sqlite3.connect('words.db')
cur = conn.cursor()

# Main Menu
def main_menu():
 
    menu=True
    selected="start"
    table_name = ""
    start_menu = ["start","quit","word create"]
    
    table_menu = []
    level_menu = ['10', '20', '30', 'back']

    def load_table():
        if table_menu:
            table_menu.remove('back')
        for table in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
            if not str(table)[2:-3] in table_menu:  
                table_menu.append(str(table)[2:-3]) 
        if 'recent_game' in table_menu:
            table_menu.remove('recent_game')    
        if 'downloaded_word' in table_menu:
            table_menu.remove('downloaded_word')
        if not 'download_persent' in table_menu:
            cur.execute("CREATE TABLE IF NOT EXISTS download_persent (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, persent INTEGER)")
            conn.commit()
            if not "word Download" in start_menu:
                start_menu.append("word Download")   
        else:
            table_menu.remove('download_persent')
            if [i for i in cur.execute("SELECT persent FROM download_persent WHERE id=1;")] :
                if 119 != [i for i in cur.execute("SELECT persent FROM download_persent WHERE id=1;")][0][0]:
                    if not "word Download" in start_menu:
                        start_menu.append("word Download")  
            else:
                if not "word Download" in start_menu:
                    start_menu.append("word Download")   
        if 'sqlite_sequence' in table_menu:
            table_menu.remove('sqlite_sequence')
        table_menu.append('back')   
    
    load_table()
    menus = [start_menu, table_menu, level_menu]
    menus_index = 0
    menu_index = 0
    page_index = 0
    

    while menu:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            if event.type==pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if menu_index + 3 > len(menus[menus_index]) - 1:
                        menu_index = len(menus[menus_index]) - 1
                        page_index = len(menus[menus_index]) // 3
                    else:
                        menu_index += 3
                        page_index += 1
                elif event.key==pygame.K_LEFT:
                    if menu_index - 3 < 0:
                        menu_index = 0
                        page_index = 0
                    else:
                        menu_index -= 3
                        page_index -= 1
                elif event.key==pygame.K_DOWN:
                    if menu_index + 1 > len(menus[menus_index]) - 1:
                        menu_index = len(menus[menus_index]) - 1
                        page_index = len(menus[menus_index]) // 3
                    else:
                        menu_index += 1
                elif event.key==pygame.K_UP:
                    if menu_index - 1 < 0:
                        menu_index = 0
                        page_index = 0
                    else:
                        menu_index -= 1
                page_index = menu_index // 3
                selected=menus[menus_index][menu_index]
                if event.key==pygame.K_RETURN:
                    if menus_index == 0:
                        if selected==menus[menus_index][0]:
                            menus_index = 1
                        elif selected==menus[menus_index][1]:
                            pygame.quit()
                            quit()
                        elif selected==menus[menus_index][2]:
                            menu_index = 0
                            exec(open(('input_db.py'), encoding='UTF8').read())
                            load_table()       
                        elif len(start_menu) == 4:
                            if selected == menus[menus_index][3]:
                                cur.execute("CREATE TABLE IF NOT EXISTS recent_game (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, word text, read_word text)")
                                download_persent = 0
                                persent = [i for i in cur.execute("SELECT persent FROM download_persent WHERE id=1;")]
                                if len(persent) == 0:
                                    cur.execute("INSERT into download_persent(persent) values (1);")
                                    conn.commit()
                                    persent.append(0)
                                else:
                                    persent[0] = persent[0][0] + 1
                                    # print(persent[0])
                                    download_persent = persent[0] * (100 / 120)
                                escape = False
                                for level in range(persent[0] // 20 + 1, 7):
                                    cur.execute("CREATE TABLE IF NOT EXISTS grade" + str(level) +"(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, word text, read_word text)")
                                    cur.execute("CREATE TABLE IF NOT EXISTS downloaded_word (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, word text)")
                                    kanzi_datas = []
                                    arr = []
                                    kanzi_read_kanzi = dict()
                                    
                                    if not 'downloaded_word' in table_menu:
                                        kanzi_url = "https://joyokanji.info/year.html"+"?js="+str(level)
                                        with urllib.request.urlopen(kanzi_url) as response:
                                            html = response.read()
                                            soup = BeautifulSoup(html, 'html.parser')
                                            kanzi_data = str(soup.find_all('td','rei underline'))

                                        kanzi_data = remove_tag(kanzi_data)


                                        remove_strs = ['，', ',','⇔', '」','「','（','）','｜', '※','[',']']
                                        kanzi_data = replaceAll(kanzi_data, remove_strs)

                                        for kanzi in kanzi_data.split(' '):
                                            kanzi = kanzi.strip()
                                            if kanzi:
                                                arr.append(kanzi)

                                        arr = list(set(arr))
                                        for i in arr:
                                            cur.execute("INSERT into downloaded_word(word) values (\""+i+"\");")
                                    else:
                                        arr = [i for i in cur.execute("SELECT word from downloaded_word")]
                                        cur.execute("delete from downloaded_word")
                                        table_menu.append('downloaded_word')


                                    for indx in range(persent[0] % 20 , 20):
                                        read_word_url1 = "https://www.sanseido.biz/User/Dic/Index.aspx?TWords="
                                        read_word_url2 = "&st=1&DORDER=151617&DailyJJ=checkbox&DailyEJ=checkbox&DailyJE=checkbox"
                                        read_kanzi_data= ""
                                        read_word_url = read_word_url1 + quote(arr[indx]) + read_word_url2

                                        read_kanzi_arr = []

                                        with urllib.request.urlopen(read_word_url) as respon:
                                            html = respon.read().decode('utf8')
                                            soup = BeautifulSoup(html, 'html.parser')
                                            table = soup.find('table')
                                            reads = table.find_all('span','NetDicTitle')
                                            for read in reads:
                                                read_kanzi_arr.append(remove_tag(str(read)).split(' ')[0])
                                        
                                        read_kanzi_arr = list(set(read_kanzi_arr))
                                        stream = ""
                                        for index in range(0, len(read_kanzi_arr)):      
                                            if index == len(read_kanzi_arr) - 1:
                                                stream += read_kanzi_arr[index]
                                            else:
                                                stream += read_kanzi_arr[index] + ', '
                                        if stream:
                                            query = "INSERT into grade"+str(level)+"(word, read_word) values (?, ?);"
                                            cur.execute(query,(arr[indx].strip(), stream.strip()))

                                        query = "UPDATE download_persent SET persent = "+ str(((level-1)*20)+indx) +" where id = 1;"
                                        cur.execute(query)
                                        screen.fill(blue)
                                        screen.blit(background,(0,0))
                                        title = text_format("Japanese Typing Game", font, 60, blue)
                                        title_rect = title.get_rect()
                                        screen.blit(title, (screen_width/2 - (title_rect[2]/2), 80))
                                        download_persent += (100 / (6 * 20))
                                        download_persent_text = 'Downloading...' + str(round(download_persent,2)) + '%'
                                        download_text = text_format(download_persent_text, font, 60, brown)
                                        download_rect = download_text.get_rect()
                                        screen.blit(download_text, (screen_width/2 - (download_rect[2]/2), 300 + 80 ))
                                        pygame.display.update()
                                        for event in pygame.event.get():
                                            if event.type==pygame.KEYDOWN:
                                                if event.key==pygame.K_ESCAPE:
                                                    escape = True
                                                    conn.commit()
                                                    break
                                            if escape:
                                                break
                                        if escape:
                                            break
                                    if escape:
                                        break
                                    persent[0] = 0 

                                conn.commit()
                                if not escape:
                                    del start_menu[-1]
                                load_table()
                                page_index = 0
                                menu_index = 0
                    elif menus_index == 1:
                        if selected==menus[menus_index][-1]:
                            menus_index = 0
                            page_index = 0
                            menu_index = 0
                        else:
                            cur.execute("delete from recent_game")
                            menus_index = 2
                            page_index = 0
                            menu_index = 0
                            table_name = selected
                    elif menus_index == 2:
                        if selected==menus[menus_index][-1]:
                            menus_index -=1
                            page_index = 0
                            menu_index = 0
                            selected = menus[menus_index][0]
                            break
                        words_reads = [i for i in cur.execute("select word, read_word from "+table_name+" order by random() LIMIT " + str(selected))]
                        if len(words_reads) != int(selected):
                            menus_index = 1
                        else:
                            for i in words_reads:
                                query = "INSERT into recent_game (word, read_word) values (?, ?);"
                                cur.execute(query, (i[0], i[1]))
                            conn.commit()
                            exec(open(('game.py'), encoding='UTF-8').read())
                            for j in [i[0] for i in cur.execute("select word from recent_game")]:
                                print(j)
                            cur.execute("delete from recent_game")
                            conn.commit()
                    selected = menus[menus_index][0]
                            
 
        # Main Menu UI
        screen.fill(blue)
        screen.blit(background,(0,0))
        title = text_format("Japanese Typing Game", font, 60, blue)
       
        for i in range(3):
            menu_text = ''
            if (page_index*3) + i < len(menus[menus_index]):
                if selected == menus[menus_index][(page_index*3) + i]:
                    menu_text = text_format(menus[menus_index][(page_index*3) + i], font, 55, brown)
                else:
                    menu_text = text_format(menus[menus_index][(page_index*3) + i], font, 55, black)
                menu_rect = menu_text.get_rect()
                screen.blit(menu_text, (screen_width/2 - (menu_rect[2]/2), 300 + 70 * (i)))
        

        title_rect = title.get_rect()
        screen.blit(title, (screen_width/2 - (title_rect[2]/2), 80))
            
        pygame.display.update()
        clock.tick(FPS)
        pygame.display.set_caption("Python - Japanese Typing Game")

main_menu()
pygame.quit()
quit()