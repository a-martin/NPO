# -*- coding: utf-8 -*-


from psychopy import core, gui, misc, data, visual, event, sound, microphone, prefs
import pandas as pd
import numpy as np
import codecs # for utf-8 file handling
import random

prefs.general['audioLib'] = ['pyo']

##########################
## FUNCTION DEFINITIONS ##

def instructies(x):
    'Display instructions on screen and wait for participant to press button'
    win.flip()
    visual.TextStim(win, text=x, color="black", wrapWidth=1.25, height=0.04).draw()
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

def makeRedDot():

    dot = visual.Circle(
        win,
        radius=0.025,
        fillColor='red',
        pos=(0,0.7)
    )

    # dot = visual.Rect(
    #     win,
    #     size=(75,75),
    #     pos=(0,300),
    #     fillColor='red'
    # )


    return dot
    
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
    repetitions = 3 # 12 noun comprehension trials
    eng = vocab['nouns'].keys() * repetitions
    random.shuffle(eng) # NOT BLOCKED
    # print eng
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

def doNounProdTrial(noun, trialNo):

    # Prepare objects
    npo = vocab['nouns'][noun] # fetch npo from eng
    recordFile = '../recordings/{}-noun-{}-{}.wav'.format(sujet, noun, trialNo)
    npoAudio = sound.Sound(cheminAudio+npo+'.wav') # prepare sound obj
    
    npoImage = visual.ImageStim( # prepare image obj
        win,
        image=cheminImages+noun+'.png'
    )
    npoImage.setAutoDraw(True)
    dot = makeRedDot()
    

    # Do trial
    win.flip() # display image
    core.wait(1.000)

    dot.draw()
    win.flip()
    mic.record(sec=5, filename=recordFile)
    core.wait(5)
    win.flip() # erase dot

    core.wait(0.500)
    playStim(npoAudio)
    core.wait(0.500)
    npoImage.setAutoDraw(False)
    win.flip() # erase image
    
    return

def doNounProd():
    nouns = vocab['nouns'].keys() * 3
    random.shuffle(nouns)

    for n,noun in enumerate(nouns):
        doNounProdTrial(noun, n)
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
    random.shuffle(allPhrases)
    
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

    if correct==0:
        playStim(sound.Sound(cheminAudio+'wrong-short.wav'))
        core.wait(0.100)
        for audio in npoAudio: playStim(audio)
    else:
        playStim(sound.Sound(cheminAudio+'correct-short.wav'))
    core.wait(1.000)    

    for image in images: image.setAutoDraw(False)
    for square in squares: square.setAutoDraw(False)
    mouse.setVisible(False)

    win.flip()

    
    return mod, noun, modType, npoMod, response, correct


def doModTest(repetitions=6):
     global modTestDf
     i = vocab[inner].keys()
     o = vocab[outer].keys()
     eng = i * repetitions + o * repetitions
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

def makeBottomNouns():
    nouns = vocab['nouns'].keys()
    nouns.sort()

    nounImages = []
    for n,noun in enumerate(nouns):
        image = visual.ImageStim(
            win,
            image=cheminImages+noun+'.png',
            pos=nounPos[n],
            name=noun,
            # size=(0.15,0.15)
            # height=0.15
        )
        image.units = 'pix'
        image.size = (100, 100)
        image.setAutoDraw(True)
        nounImages.append(image)

    return nounImages

    
def doModProdTrial(mod, noun, trialNo):

    # Prepare objects
    modType = 'inner' if mod in vocab[inner].keys() else 'outer'
    modCats = inner if modType=='inner' else outer
    npoMod = vocab[modCats][mod]
    npoNoun = vocab['nouns'][noun]
    recordFile = '../recordings/{}-1mod-{}_{}-{}.wav'.format(sujet, mod, noun, trialNo)
    
    npoAudio = [
        sound.Sound(cheminAudio+npoNoun+'.wav'),
        sound.Sound(cheminAudio+npoMod+'.wav'),
    ]

    npoImage = visual.ImageStim( # prepare image obj
        win,
        image=cheminImages+mod+'-'+noun+'.png'
    )
    npoImage.setAutoDraw(True)

    # Prepare noun images along bottom
    greyNouns = makeBottomNouns()
    # print greyNouns
        
    
    # dot = makeRedDot()
    dot = makeRedDot()
    dot.setFillColor('lightgrey')
    
    # Do trial
    win.flip() # display main image and greyNouns
    core.wait(1.000)

    mouse.setVisible(True)
    dot.setAutoDraw(True)
    win.flip()

    clicked = False
    while not clicked:
        if mouse.getPressed()[0] == 1:
            print 'left button pressed'
        if mouse.isPressedIn(dot):
            print 'mouse pressed in dot'
            dot.setFillColor('red')
            win.flip()
            clicked = True
        if mouse.isPressedIn(npoImage):
            print 'mouse pressed in central image'
        for n,greyNoun in enumerate(greyNouns):
            if mouse.isPressedIn(greyNoun):
                print 'mouse pressed in {}'.format(n)

                
    mic.record(sec=5, filename=recordFile)
    core.wait(5)
    dot.setFillColor('grey')
    win.flip() # turn dot grey

    core.wait(0.500)
    for stim in npoAudio: playStim(stim)
    core.wait(0.500)
    npoImage.setAutoDraw(False)
    win.flip() # erase image


    return


def doModProd():
    repetitions = 1
       
    innerEng = vocab[inner].keys() * repetitions
    outerEng = vocab[outer].keys() * repetitions
    engL = innerEng + outerEng
    random.shuffle(engL)
    mods = []
    mods += engL
    nouns = vocab['nouns'].keys()
    
    for n,mod in enumerate(mods):
        noun = random.choice(nouns)
        doModProdTrial(mod, noun, n)


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

nounPos = [
    (-0.75,-0.75),
    (-0.25,-0.75),
    (0.25,-0.75),
    (0.75,-0.75)
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

intro = u'''Today, you will learn a small part of a language called Nápíjò. Nápíjò is spoken by around 10,000 people in a rural region of Southeast Asia and has some properties that interest our research team. We are particularly interested in how native English speakers fair when learning Nápíjò words. You will be instructed through a series of short learning and testing tasks.

When you’re ready, press the spacebar, and you will be instructed on the first part of the experiment.
'''

nounExpoConsigne = u'''For this first part of the experiment, you will see pictures of objects, and you will hear a native speaker of Nápíjò say the name of the objects. Simply repeat after the speaker and try to remember as best you can. Once you’ve repeated the name, click on the object, and another object will appear. Objects will repeat, so you’ll have plenty of chances to learn the words!

Press the spacebar when you’re ready to begin.
'''

nounTestConsigne = u'''Now comes your first test. You will hear the speaker say the name of an object, and then you will see all four objects appear on the screen. Your job is to click on the correct object. If you make a mistake, the speaker will say the label again, to help you remember.

Press the spacebar when you’re ready to continue.
'''

nounProdConsigne = u'''Well done. You will now see pictures of objects, and it will be your turn to say their name in Nápíjò. On each trial, you will see the image. Then a red dot will appear above the image. That means the microphone is recording, and you can go ahead and say the name of the object. If you don’t remember the name, simply say so. When the red dot disappears, the microphone is no longer recording. You will then hear the native speaker say the name of the object again, as a wee reminder.

Press the spacebar when you’re ready to continue.
'''

modExpoConsigne = u'''Alright, now that you have learned the names of these objects well, we’ll teach you a couple of ways to describe the objects. Just like in the first part of the experiment, you’ll see a picture and hear the speaker describe it. Simply repeat after the speaker and try to remember the new words you hear. Once you’ve repeated after the speaker, click on the image.

Press the spacebar when you’re ready to continue.
'''

modTestConsigne = u'''Now comes your second test. You will hear the speaker describe objects, and then you will see two possible images. Your job is to click on the image that corresponds to what the speaker says. If you make a mistake, the speaker will repeat the description, to help you remember.

Press the spacebar when you’re ready to continue.
'''

modProdConsigne = u'''Well done. You will now see images, and again it will be your turn to describe them in Nápíjò. On each trial, you will see the image. Then a red dot will appear above the image. That means the microphone is recording, and you can go ahead and give the description in Nápíjò. If you don’t remember some of the words, simply say so. When the red dot disappears, the microphone is no longer recording. You will then hear the native speaker describe the image, as a wee reminder.

Press the spacebar when you’re ready to continue.
'''

twoModProdConsigne = u'''Nicely done. Now comes the hard part! Again, you will need to describe images in Nápíjò, but this time the images will be a little more complex, and you’ll need to combine words in ways you’ve not heard from the native speaker. Just do your best. After a few of these trials, you’ll do a quick round of comprehension again to refresh your memory before a final round of image description.

Press the spacebar when you’re ready to continue.
'''

modTestConsigneBis = u'''Phew, you made it through that. Now once more you’ll hear the native speaker and you’ll have to click on the image that corresponds to their description. If you make a mistake, the speaker will repeat the description.

Press the spacebar when you’re ready to continue.
'''

twoModProdConsigneBis = u'''You have one final task! Again, you’ll see images that you need to describe using all the words of Nápíjò that you’ve learned. Speak only when the red dot appears on the screen, indicating that the microphone is on.

Press the spacebar when you’re ready to continue.
'''

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
        units="norm",
    )
else:
    win = visual.Window(
        [1200,800],
        color="grey",
        colorSpace="rgb",
        units="norm",
        screen=2
    )
win.flip()


# MAKE MOUSE
mouse = event.Mouse(visible=False)

# MAKE MICROPHONE
microphone.switchOn(sampleRate=44100)
mic = microphone.AdvAudioCapture(stereo=False)


# RUN EXPERIMENT

# Display welcome
instructies(welcome)

# Display introduction
instructies(intro)

# Noun exposure
# instructies(nounExpoConsigne)
# doNounExposure()

# Noun test
# instructies(nounTestConsigne)
# doNounTest()
# nounTestDf.to_csv(nounTestFileName, index=None)

# Noun prod
# instructies(nounProdConsigne)
# doNounProd()

# Mod exposure
# instructies(modExpoConsigne)
# doModExposure()

# Mod test
# instructies(modTestConsigne)
# doModTest()
# modTestDf.to_csv(modTestFileName, index=None)

# Mod prod
instructies(modProdConsigne)
doModProd()

# 2-mod prod
# instructies(twoModProdConsigne)
# doTwoModProd()

# Mod prod bis
# instructies(modTestConsigneBis)
# doModTest(repetitions=3)

# 2-mod prod bis
# instructies(twoModProdConsigneBis)
# doTwoModProd()

# Thank you
instructies(merci)

core.quit()


