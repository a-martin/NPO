from psychopy import microphone, core, prefs

prefs.general['audioLib'] = ['pyo']

microphone.switchOn(sampleRate=44100)
mic = microphone.AdvAudioCapture(stereo=False)

mic.record(sec=2, filename='../recordings/test.wav')

core.quit()


