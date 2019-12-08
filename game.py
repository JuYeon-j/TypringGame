# -*- coding: utf-8 -*-
import pygame
import pygame_textinput
import random 
import sqlite3
from pygame import mixer




pygame.init()

screen = pygame.display.set_mode((800,600))


background = pygame.image.load('mountain.png')

pygame.display.set_caption("Python - Japanese Typing Game")

icon = pygame.image.load('books.png')
pygame.display.set_icon(icon)


textinput = pygame_textinput.TextInput(font_family='ipaexm.ttf')


playerX = 350
playerY = 530

#일본어

conn = sqlite3.connect('words.db')
cur = conn.cursor()
text_and_read =[ i for i in cur.execute("select word, read_word from recent_game")]

text = [i[0] for i in text_and_read]

readtext = []

for i in range(0, len(text_and_read)):
    arr = []
    for j in text_and_read[i][1].split(','):
        arr.append(j.strip())
    readtext.append(arr)
print(readtext)


textX=[]
textY=[]
textY_change=[]
j_text=[]
up = 0
index=0
state = "false"
music = "false"


score_value = 0

scoreX = 320
scoreY = 10

font = pygame.font.Font('Gumbo DEMO.otf', 50)

game_font  = pygame.font.Font('Gumbo DEMO.otf', 90)

scorefont = pygame.font.Font('Bubblegum.ttf',40)


def show_score(x,y):
    global scorefont 
    global score_value
    score = scorefont.render("Score :" + str(score_value), True, (156, 117, 110))
    screen.blit(score, (x, y))


def game_over_text():
    global game_font
    over_text = game_font.render("GAME OVER", True,(156, 117, 110))
    screen.blit(over_text, (190,250))

def game_finish_text():
    global game_font
    finish_text = game_font.render("FINISH", True, (156, 117, 110))
    screen.blit(finish_text,(300,250))

def jj():
    global textX 
    global textY
    global textY_change
    global j_text
    global text
    textX.append(random.randint(0,700))
    textY.append(50)
    textY_change.append(0)
    j_text.append(range(len(text)))
    
text_font = pygame.font.Font('ipaexm.ttf',32)


def player(x,y):
    global textinput
    screen.blit(textinput.get_surface(), (x,y))


def jtext(x,y,i):
    global j_text
    global text
    global text_font
    j_text[i] = text_font.render(text[i],True,(156, 117, 110))
    screen.blit(j_text[i], (x,y))


running = True
while running:
    screen.blit(background, (0, 0))
     
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                state = "true"               
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                textinput.clear_text()
                state = "false"

    jj()

    up += 1
    if up > 200:
        jj()
        up = 0
        index += 1

    if index - 1 >= len(text):
        index -=  1
    
    if state is "true":  
        input_text = textinput.get_text()
        hira = ''
        hira_true = "false"
        for i in readtext:
            hira = [j for j in i]
            if  input_text in hira:
                hira_true = "true"
                break

        if hira_true is "true":

            textinput.clear_text() 

            answerIndex = readtext.index(hira)
            sound = mixer.Sound('musicbell.wav')
            sound.play()
            

            score_value += 1

            del text[answerIndex]
            del readtext[answerIndex]
            del textX[answerIndex]
            del textY[answerIndex]
      
            
            

            index -= 1

            

    if len(text) == 0:
        game_finish_text()


    for i in range(0, index):

        if textY[i] > 485:
            game_over_text()
            readtext = []
            break


        textY_change[i]  = 0.2
        textY[i] += textY_change[i]

        jtext(textX[i], textY[i], i)

    show_score(scoreX, scoreY)
    player(playerX,playerY)
    textinput.update(events)      
    pygame.display.update()