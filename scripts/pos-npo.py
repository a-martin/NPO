# -*- coding: utf-8 -*-


from psychopy import core, gui, misc, data, visual, event, sound
import pandas as pd
import numpy as np
import codecs # for utf-8 file handling
import random

##########################
## FUNCTION DEFINITIONS ##

def instructies(x):
    'Display instructions on screen and wait for participant to press button'
    win.flip()
    visual.TextStim(win, text=x, color="black", wrapWidth=800).draw()
    win.flip()
    event.waitKeys()
    win.flip()
    return

def playStim(x):
    # play sound and do not allow other processes to continue until sound finished
    x.play()
    core.wait(x.getDuration())
    return

def drawSquare(pos, colour):

    square = visual.Rect(
        win,
        lineWidth=6,
        lineColor=colour,
        lineColorSpace='rgb',
        pos=pos,
        size=(550,350)
    )
    
    return square

def drawBigSquare(pos, colour):

    square = visual.Rect(
        win,
        lineWidth=6,
        lineColor=colour,
        lineColorSpace='rgb',
        pos=pos,
        size=(1050,650)
    )
    
    return square

    
def doNounExposureTrial(noun):

    # Prepare objects
    npo = vocab['nouns'][noun] # fetch npo from eng
    npoAudio = sound.Sound(cheminAudio+npo+'.wav') # prepare sound obj
    
    npoImage = visual.ImageStim( # prepare image obj
        win,
        image=cheminImages+noun+'.png'
    )
    npoImage.draw()

    # Do trial
    win.flip() # display image
    core.wait(0.500) # wait 500 ms
    playStim(npoAudio) # play label
    # event.waitKeys() # wait for participant key press
    mouse.setVisible(True) # activate mouse

    clicked = False
    while not clicked:
        if mouse.isPressedIn(npoImage):
            mouse.setVisible(False)
            clicked = True

    win.flip() # erase screen
    
    return

def doNounExposure():
    repetitions = 6
    eng = vocab['nouns'].keys() * repetitions
    random.shuffle(eng) # NOT BLOCKED

    for noun in eng:
        doNounExposureTrial(noun)
    return
    
def doNounTestTrial(noun):

    # Prepare all objects
    correctNpo = vocab['nouns'][noun]
    correctAudio = sound.Sound(cheminAudio+correctNpo+'.wav')

    allNouns = vocab['nouns'].keys()
    random.shuffle(allNouns)
    nounImages = [visual.ImageStim(win, image=cheminImages+nom+'.png', pos=quadPos[n], name=nom) for n,nom in enumerate(allNouns)]

    # Do trial
    win.flip()
    core.wait(0.500)
    playStim(correctAudio)
    core.wait(0.100)

    squares = []
    
    for pic in nounImages:
        pic.setAutoDraw(True)
        squares.append(drawSquare(pic.pos, 'lightgrey'))
        
    win.flip()
    mouse.setVisible(True)

    clicked = False
    while not clicked:
        for n,image in enumerate(nounImages):
            square = squares[n]
            if image.contains(mouse):
                square.setAutoDraw(True)
            else:
                square.setAutoDraw(False)
            win.flip()

            if mouse.isPressedIn(image):
                response = image.name
                if response == noun:
                    correct = 1
                else:
                    correct = 0

                clicked = True
                
    for n,image in enumerate(nounImages):
        if correct==0: 
            frameColor = None
        else:
            frameColor = 'green'
            
        square = squares[n]
        square.setLineColor(frameColor)

        if image.name != noun:
            image.setOpacity(0.15)

        win.flip()

    if correct==0:
        playStim(sound.Sound(cheminAudio+'wrong-short.wav'))
        core.wait(0.100)
        playStim(correctAudio)
    else:
        playStim(sound.Sound(cheminAudio+'correct-short.wav'))
    core.wait(1.000)
    

    for image in nounImages: image.setAutoDraw(False)
    for square in squares: square.setAutoDraw(False)
    mouse.setVisible(False)

    win.flip()
    
    return noun, correctNpo, response, correct
    
def doNounTest():
    global nounTestDf
    repetitions = 6
    eng = vocab['nouns'].keys() * repetitions
    random.shuffle(eng) # NOT BLOCKED
    print eng
    for trialNo,noun in enumerate(eng):
        noun, correctNpo, response, correct = doNounTestTrial(noun)

        dico = {
            'suj':sujet,
            'trial':trialNo,
            'engNoun':noun,
            'correctNpo':correctNpo,
            'response':response,
            'correct':correct
        }
        trial = pd.DataFrame([dico])
        nounTestDf = nounTestDf.append(trial)
        
    return

def doModExposureTrial(mod, noun):

    # Prepare objects
    modType = 'inner' if mod in vocab[inner].keys() else 'outer'
    modCats = inner if modType=='inner' else outer
    npoMod = vocab[modCats][mod]
    npoNoun = vocab['nouns'][noun]

    npoAudio = [
        sound.Sound(cheminAudio+npoNoun+'.wav'),
        sound.Sound(cheminAudio+npoMod+'.wav'),
    ]

    npoImage = visual.ImageStim( # prepare image obj
        win,
        image=cheminImages+mod+'-'+noun+'.png'
    )
    npoImage.draw()

    # Do trial
    win.flip() # display image
    core.wait(0.500) # wait 500 ms

    for stim in npoAudio:
        playStim(stim) # play label

    mouse.setVisible(True) # activate mouse

    clicked = False
    while not clicked:
        if mouse.isPressedIn(npoImage):
            mouse.setVisible(False)
            clicked = True

    win.flip() # erase screen

    return
    
def doModExposure():

    # first do 2x each modifier type in a random order, blocked
    innerOuter = [vocab[inner].keys(), vocab[outer].keys()]
    random.shuffle(innerOuter)

    mods = []
    for modType in innerOuter:
         mods += modType * 2

    # then do 4x each modifier type, non-blocked 
    repetitions = 4
       
    innerEng = vocab[inner].keys() * repetitions
    outerEng = vocab[outer].keys() * repetitions
    engL = innerEng + outerEng
    random.shuffle(engL)
    mods += engL
    nouns = vocab['nouns'].keys()

    for mod in mods:
        noun = random.choice(nouns)
        doModExposureTrial(mod, noun)
    return


def doModTestTrial(mod, noun):

    # Prepare all objects 
    modType = 'inner' if mod in vocab[inner].keys() else 'outer'
    modCats = inner if modType=='inner' else outer
    npoMod = vocab[modCats][mod]
    npoNoun = vocab['nouns'][noun]

    npoAudio = [
        sound.Sound(cheminAudio+npoNoun+'.wav'),
        sound.Sound(cheminAudio+npoMod+'.wav'),
    ]

    modOther = otherMods[mod]
    allPhrases = [mod+'-'+noun, modOther+'-'+noun]
    
    images = [visual.ImageStim(win, image=cheminImages+phrase+'.png', pos=duoPos[n], name=phrase) for n,phrase in enumerate(allPhrases)]

    # Do trial
    win.flip()
    core.wait(0.500)
    for audio in npoAudio: playStim(audio)
    core.wait(0.100)
    squares = []
    
    for pic in images:
        pic.setAutoDraw(True)
        squares.append(drawBigSquare(pic.pos, 'lightgrey'))
    win.flip()
    mouse.setVisible(True)

    clicked = False
    while not clicked:
        for n,image in enumerate(images):
            square = squares[n]
            if image.contains(mouse):
                square.setAutoDraw(True)
            else:
                square.setAutoDraw(False)
            win.flip()

            if mouse.isPressedIn(image):
                response = image.name.split('-')[0] # recover mod
                if response == mod:
                    correct = 1
                else:
                    correct = 0

                clicked = True
                
    for n,image in enumerate(images):
        if correct==0: 
            frameColor = None
        else:
            frameColor = 'green'
            
        square = squares[n]
        square.setLineColor(frameColor)

        if image.name.split('-')[0] != mod:
            image.setOpacity(0.15)

        win.flip()

    core.wait(1.000)
    

    for image in images: image.setAutoDraw(False)
    for square in squares: square.setAutoDraw(False)
    mouse.setVisible(False)

    win.flip()

    
    return mod, noun, modType, npoMod, response, correct


def doModTest():
     global modTestDf
     repetitions = 6
     i = vocab[inner].keys()
     o = vocab[outer].keys()
     eng = i * 6 + o * 6
     random.shuffle(eng)
     for trialNo,mod in enumerate(eng):
          noun = random.choice(vocab['nouns'].keys())
          mod, noun, modType, npoMod, response, correct = doModTestTrial(mod, noun)

          dico = {
               'suj':sujet,
               'trial':trialNo,
               'engNoun':noun,
               'engMod':mod,
               'modType':modType,
               'npoMod':npoMod,
               'response':response,
               'correct':correct
          }
          trial = pd.DataFrame([dico])
          modTestDf = modTestDf.append(trial)
          
     return
    
############################
## GLOBAL FIXED VARIABLES ##

cheminAudio =  '../stimuli/audio/'
cheminImages = '../stimuli/images/'

quadPos = [
    (-300, 200),   # upper left
    (300, 200),    # upper right
    (-300, -200),  # lower left
    (300, -200)    # lower right
]

duoPos = [
     (-300, 0), # left
     (300, 0),  # right
]

sujetRaw = '001'
boothCode = 1
sujet = 'ENG{}{}'.format(boothCode, sujetRaw)

conds = ['dems', 'nums']
outer = conds[int(sujetRaw) % 2]
inner = 'adjs'

nounTestFileName = '../data/{}-nounTest.csv'.format(sujet)
nounTestDfCols = [
    'engNoun',
    'correctNpo',
    'response',
    'correct'
]
nounTestDf = pd.DataFrame(columns=nounTestDfCols)

modTestFileName = '../data/{}-modTest.csv'.format(sujet)
modTestDfCols = [
]
modTestDf = pd.DataFrame(columns=modTestDfCols)


welcome = u'''Welcome!

This is an experiment about learning a small part of a new language. It will take about 30 minutes to complete and you will be paid £5.00 for your time. This experiment is part of a series of studies being conducted by Dr Jennifer Culbertson at the University of Edinburgh, and has been approved by the Linguistics and English Language Ethics Committee. 

Proceeding indicates that:

- you are a native speaker of English, at least 18 years old
- you have read the information letter
- you voluntarily agree to participate, and understand you can stop your participation at any time
- you agree that your anonymous data may be kept permanently in Edinburgh University archives and may used by qualified researchers for teaching and research purposes

If you do not agree to all of these, please inform the experimenter now.

If you agree, press the spacebar.'''

nounExpoConsigne = u'''You will now hear nouns in the language.  Click on the picture after you hear its name.
'''

nounTestConsigne = u'''You will now be tested on your retention of nouns in the language.
'''

modExpoConsigne = u'''You will now hear nouns with modifiers in the language.  Click on the picture after you hear its description.
'''

modTestConsigne = u'''Mod test.'''

merci = u'''Thank you for your participation!'''


#######################
## GENERATE LANGUAGE ##


engNouns = ['book', 'mug', 'pencil', 'scissors']
npoNouns = ['monu1', 'wato1', 'kipi2', 'teno2']
random.shuffle(npoNouns)

engDems = ['this', 'that']
npoDems = ['hig2', 'hog1']
random.shuffle(npoDems)

engNums = ['two', 'three']
npoNums = ['pem1', 'jo1']
random.shuffle(npoNums)

engAdjs = ['blue', 'red']
npoAdjs = ['wun1', 'kim2']
random.shuffle(npoAdjs)


vocab = {
    'nouns':{x:npoNouns.pop() for x in engNouns},
    'dems':{x:npoDems.pop() for x in engDems},
    'nums':{x:npoNums.pop() for x in engNums},
    'adjs':{x:npoAdjs.pop() for x in engAdjs}
}

vocabFlat = {}
for cat in vocab:
    vocabFlat.update(vocab[cat])

vocabDf = pd.DataFrame.from_dict(vocabFlat, orient='index')
vocabDf.columns = ['NPO']
vocabDf.index.rename('ENG', inplace=True)
vocabDf.to_csv('../data/'+sujet+'-lg.csv')

otherMods = {}
for cat in [engDems, engNums, engAdjs]:
     otherMods.update({cat[0]:cat[1]})
     otherMods.update({cat[1]:cat[0]})


########################
#### RUN EXPERIMENT ####

# PROPOSE FULLSCR
pec = {'Full screen':'y'}
dlg = gui.DlgFromDict(pec, title=u'Démarrage')
if dlg.OK:
    if pec['Full screen'] == 'y':
        plein_ecran = True
    else:
        plein_ecran = False
else:
    core.quit()


# DRAW WINDOW
if plein_ecran:
    win = visual.Window(
        fullscr=True,
        allowGUI=False,
        color="white",
        colorSpace="rgb",
        units="pix"
    )
else:
    win = visual.Window(
        [1200,800],
        color="white",
        colorSpace="rgb",
        units="pix"
    )
win.flip()

# MAKE MOUSE
mouse = event.Mouse(visible=False)


# RUN EXPERIMENT

# Display welcome
instructies(welcome)

# Noun exposure
# instructies(nounExpoConsigne)
# doNounExposure()

# Noun test
# instructies(nounTestConsigne)
# doNounTest()
# nounTestDf.to_csv(nounTestFileName, index=None)

# Mod exposure
# instructies(modExpoConsigne)
# doModExposure()

# Mod test
instructies(modTestConsigne)
doModTest()
modTestDf.to_csv(modTestFileName, index=None)

# Thank you
instructies(merci)

core.quit()


