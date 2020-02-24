#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Decision-Making Token Task
 
Author: Santiago Muñoz-Moldes
Date started: 02-2020
University of Cambridge
santimz@gmail.com
"""

#========================
# Importing used modules
#========================

from psychopy import monitors, gui, visual, core, data, event, logging
import numpy as np
from numpy.random import random, randint, normal, uniform
from random import shuffle
#from math import ceil, floor
import glob, os

#==========================================
# Store info about the experiment session
#==========================================
#------------------------------
# Experiment session GUI dialog
#------------------------------

#get values from dialog
expName='Decisions'
myDlg = gui.Dlg(title=expName, pos = (860,340))
myDlg.addField(label='participant',initial=0, tip='Participant name or code'),
myDlg.addField(label='age',initial=0, tip='Participant age'),
myDlg.addField(label='sex', choices=('female','male', 'Other/Prefer no to say'))
myDlg.addField(label='screen', choices=(60, 144), tip='Refresh Rate')
myDlg.addField(label='triggers', initial='No', choices=['Yes', 'No'], tip='Send EEG Triggers')
dlg_data = myDlg.show()
if myDlg.OK==False: core.quit()  #user pressed cancel

#store values from dialog
expInfo = {
    'participant':dlg_data[0],
    'age':dlg_data[1],
    'sex':dlg_data[2], 
    'screen':dlg_data[3],
    'triggers':dlg_data[4]
    }

expInfo['date']=data.getDateStr()  #get a simple timestamp for filename
expInfo['expName']=expName

#-----------------------
#setup files for saving
#-----------------------

if not os.path.isdir('data'):
    os.makedirs('data')  #if this fails (e.g. permissions) we will get an error
filename='data' + os.path.sep + '%s_%s' %(expInfo['participant'], expInfo['date'])
logFile=logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  #this outputs to the screen, not a file

#====================================================================
# Setting some static variables that we might want to tweak later on
#====================================================================

#determine screen's refresh rate
# hz = int(expInfo['screen'])

# #experiment time durations in seconds
# times= {"REST" : 1., 
#         "CS" : 4., 
#         "US" : 0.5, 
#         "POST_RATING" : 3., 
#         "RATING_MAX" : 10.,
#         "ITI_MIN" : 7., 
#         "ITI_MAX" : 11.}

# #adjust times in seconds to frames depending on screen's refresh rate
# #choose 'ceil' for rounding up, 'floor' for rounding down (no half frames)
# timeInFrames= {  # choose 'ceil' for rounding up, 'floor' for rounding down
#         "REST" : int(ceil(hz * times["REST"])),
#         "CS" : int(ceil(hz * times["CS"])),
#         "US" : int(ceil(hz * times["US"])),
#         "POST_RATING" : int(ceil(hz * times["POST_RATING"])),
#         "RATING_MAX" : int(ceil(hz * times["RATING_MAX"])),
#         "ITI_MIN" : int(ceil(hz * times["ITI_MIN"])),
#         "ITI_MAX" : int(ceil(hz * times["ITI_MAX"]))
#         }

#=====================
# Open parallel port
#=====================
# Parallel port drivers need to be installed before
# Note: the file inpout32.dll needs to be in the same folder

#triggers can be turned On or Off
if expInfo['triggers']=='Yes': triggers = True
else: triggers = False

if triggers:

    # More info on EGI triggers on the next link
    # https://discourse.psychopy.org/t/egi-netstation-visual-timing-latencies/2888/10
    # original code: https://github.com/gaelen/python-egi/
    import egi.simple as egi
    ms_localtime = egi.ms_localtime  

    ns = egi.Netstation()
    ns.connect('11.0.0.42', 55513) # sample address and port -- change according to your network settings
    ## ns.initialize('11.0.0.42', 55513)
    ns.BeginSession()     

    # "Connected to PC" 
    # log: 'NTEL' \n     

    ns.sync()     

    # log: the timestamp     

    ns.StartRecording()
    # I do not recommend to use this feature, as my experience is that Netstation
    # [ the version _we_ use, may be not the latest one ] may sometimes crash
    # on this command ; so I'd rather click the 'record' and 'stop' buttons manually.

    time.sleep(5) # NS removes "too short" session files on exit  

#===============================
# Creation of window and stimuli
#===============================

#-------------------
# Monitor and screen
#-------------------

# Monitor ('Macbook Pro 15')
widthPix = 2880  #screen width in px
heightPix = 1800  #screen height in px
monitorwidth = 33  #monitor width in cm
viewdist = 60.  #viewing distance in cm
monitorname = 'test'
scrn = 0  #0 to use main screen, 1 to use external screen
mon = monitors.Monitor(monitorname, width=monitorwidth, distance=viewdist)
mon.setSizePix((widthPix, heightPix))
mon.save()

#Initialize window
# win = visual.Window(
#     monitor=mon,
#     size=(widthPix,heightPix),
#     color=[0,0,0],  #'#B9B9B9' in hex
#     #color=[0,0,.7255],  #'#B9B9B9' in hex
#     colorSpace='hsv',  # !
#     units='deg',
#     screen=scrn,
#     allowGUI=False,
#     fullscr=True)

win = visual.Window(monitor=mon,
                    size=[1200, 800], 
                    color=[0,0,70], 
                    units='deg', 
                    colorSpace='hsv', 
                    screen=scrn)  # For testing only

#-------
# MOUSE
#-------

mouse = event.Mouse(visible=True, win=win)

#-----------------
# VISUAL ELEMENTS
#-----------------

# create 3 big circles
c_rad = 2 # radius size in dva
line_color = 'black'
line_width = 8  # thicker for side circles

circle_left  = visual.Circle(win, 
                             radius=c_rad, 
                             lineColor=line_color,
                             lineWidth=line_width, 
                             pos=(-4,0),
                             edges=256)
circle_mid   = visual.Circle(win, 
                             radius=c_rad, 
                             lineColor=line_color, 
                             lineWidth=line_width/2,
                             pos=(0,0),
                             edges=256)
circle_right = visual.Circle(win, 
                             radius=c_rad, 
                             lineColor = line_color,
                             lineWidth=line_width ,
                             pos=(4,0),
                             edges=256)

# create list of small circle stimuli
nr_tokens = 50  # the total number of "numbers" displayed
token_rad = .15 # in pixels or degrees of visual angle or whatever
token_color = 'black'
token_fill  = 'grey'
token_line_width = .05
min_pos = -(c_rad) # minimum value for both X and Y axis
max_pos = c_rad    # maximum value for both X and Y axis

stims = []  #stimuli list
for this_token in range(nr_tokens):
    x_pos = uniform(min_pos, max_pos) # set the x pos for this element in particular
    y_pos = uniform(min_pos, max_pos) # set the y pos for this element in particular
    stims += [visual.Circle(win, 
                            radius=token_rad, 
                            lineColor=token_color,
                            lineWidth=token_line_width,
                            fillColor=token_fill,
                            pos=(x_pos, y_pos))]

#---------------
# TEXT ELEMENTS
#---------------

# # Instructions text
# instruction_list = []
# text_size = 1  #in degrees of visual angle (dva)
# #fixcross_size = 4  #in degrees of visual angle (dva)
# text_color = 'white'
# text_font = 'arial'

# Merci = visual.TextStim(win,
#     text=u"Merci!",
#     color=text_color ,
#     height=text_size,
#     font=text_font)


#============================================
# Start main loop that goes through all trials
#============================================

#for this_trial in trials:

for this_trial in range(3):

    #draw big circles
    circle_left.draw()
    circle_mid.draw()
    circle_right.draw()

    #draw all elements
    for stim in stims:
        stim.draw()
    win.flip() # Flip everything

    #Send EEG marker
    ## # optionally can perform additional synchronization     
    ## ns.sync() 
    # if triggers:
    #     ns.send_event('evt_', 
    #                 label="event", 
    #                 timestamp=egi.ms_localtime(), 
    #                 table = {'fld1' : 123, 
    #                         'fld2' : "abc", 
    #                         'fld3' : 0.042}) 

    # Wait for a response

    core.wait(3)


#================
# Save and close
#================

# # Save response data
# trials.saveAsWideText(filename+'.csv')

# # Stop  EEG recording
# if triggers:

#     ns.send_event('stop')

#     time.sleep(5)

#     ns.StopRecording()

#     ns.EndSession()     
#     ns.disconnect()

#=======
# Close
#=======

# # Show 'Merci!' message
# Merci.draw()
# win.flip()
# core.wait(2)

win.close()
core.quit()