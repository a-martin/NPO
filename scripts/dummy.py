# -*- coding: utf-8 -*-


from psychopy import core, visual, sound
import os, re, random


def playStim(x):
    x.play()
    core.wait(x.getDuration())
    return


cheminI = '../stimuli/images/'
cheminA = '../stimuli/audio/'    



engNouns = ['book', 'mug', 'pencil', 'scissors']
npoNouns = ['monu1', 'wato1', 'kipi2', 'teno2']
random.shuffle(npoNouns)

nouns = {x:npo.pop() for x in eng}
        
win = visual.Window(
    [800,800],
    color="white",
    colorSpace="rgb",
    units="pix",
)

win.flip()


for item in d:
    t = visual.ImageStim(
        win,
        image=cheminI+item+'.png'
    )
    t.draw()
    win.flip()
    core.wait(0.500)

    stimAudio = sound.Sound(cheminA+d[item]+'.wav')
    
    playStim(stimAudio)

    core.wait(0.500)

core.quit()


