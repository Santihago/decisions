from psychopy import core, visual, event, logging, gui, data
import numpy as np
import random
from math import sqrt, ceil, sin
import csv, datetime, glob, os

"""

# Author: Santiago Muñoz Moldes, University of Cambridge
# Email: sm2115@cam.ac.uk
# Start date: March 2020
"""

""" 
# TODO
# - save stgs to log file (and add seed)
"""

#=====================
# 1. GENERAL SETTINGS
#=====================

# 1.1

win = visual.Window(units='pix', color='#1e1e1e')
slow_speed = 60//5  #normal moving speed
fast_speed = 60//20
frames_per_token = slow_speed
num_trials = 3
num_tokens = 30 #set the number of *desired* tokens inside the main circle

# 1.2 Experiment information

exp_name = 'Decisions'

#------------------------------
# Experiment session GUI dialog
#------------------------------

#get values from dialog
my_dlg = gui.Dlg(title=exp_name, pos = (860,340))
my_dlg.addField(label='id',initial=0, tip='Participant name or code'),
my_dlg.addField(label='age',initial=0, tip='Participant age'),
my_dlg.addField(label='gender', choices=('female','male', 'Other/Prefer no to say'))
my_dlg.addField(label='screen', choices=(60, 144), tip='Refresh Rate')
my_dlg.addField(label='triggers', initial='No', choices=['Yes', 'No'], tip='Send EEG Triggers')
dlg_data = my_dlg.show()
if my_dlg.OK==False: core.quit()  #user pressed cancel

#store values from dialog
exp_info = {
    'id':dlg_data[0],
    'age':dlg_data[1],
    'gender':dlg_data[2], 
    'screen':dlg_data[3],
    'triggers':dlg_data[4]
    }

exp_info['date']=data.getDateStr()  #get a simple timestamp for filename
exp_info['exp_name']=exp_name

#-----------------------
#setup files for saving
#-----------------------

# 1.3 File saving
"""Create functions to handle trial logging"""

dir = 'data'
filename = dir + os.path.sep + exp_name + '_' + '%s_%s' %(exp_info['id'], exp_info['date']) + '.csv' #generate file name with name of the experiment
logfile = logging.LogFile(filename[:-3] + 'log', level=logging.EXP)

def write_trial(correct, resp, acc, rt, x_values, t_values):
    # check if file and folder already exist
    if not os.path.isdir(dir):
        os.makedirs(dir) #if this fails (e.g. permissions) you will get an error

    # open file
    with open(filename, 'a') as save_file: #'a' = append; 'w' = writing; 'b' = in binary mode
        file_writer = csv.writer(save_file, delimiter=',') #generate file_writer object # delimiter='\t'
        if os.stat(filename).st_size == 0: #if file is empty, insert header
            file_writer.writerow(('exp_name', 'id', 'gender', 'trial', 'correct', 'resp', 'acc', 'rt', 'x_values', 't_values', 'timestamp', ))

        # write trial
        file_writer.writerow((exp_name, exp_info['id'], exp_info['gender'], trl, correct, resp, acc, rt, x_values, t_values, get_timestamp()))


def get_timestamp(time="", format='%Y-%m-%d %H:%M:%S'): 
    if time=="": return get_timestamp(core.getAbsTime(), format)
    return datetime.datetime.fromtimestamp(time).strftime(format)

# Logfile settings
#logfile = logging.LogFile(filename + '.log', level=logging.EXP)
#logging.console.setLevel(logging.WARNING)  #this outputs to the screen, not a file

#=====================
# 2. STIMULI CREATION
#=====================

#-------------------------
# 2.1 MAIN VISUAL STIMULI
#-------------------------

# 2.1.1 Colors for darktheme
blackish = "#1e1e1e"
greenish = "#52D273"
redish = "#E94F64"
yellowish = "#EAD15D"
whitish = "#F2F2F2"

# 2.1.2 Create 3 big circles
circle_size = 130  #set the circle diameter
circle_radius = circle_size/2
line_color = whitish  #color of the circle border
line_width = 2.5  #width of the circle border
line_edges = 256  #number of edges to create the circle
c_offset = 200  #offset from the center in the x axis for the 2 periph circles
c_y_pos = 200
circles = []
for pos in -c_offset, 0, c_offset:
    circles += [visual.Circle(win, 
        radius=circle_radius, lineColor=line_color, lineWidth=line_width,
        pos=(pos, c_y_pos), edges=line_edges, interpolate=True)]

#------------------
# 2.2 TOKEN ARRAYS
#------------------
"""Inspired by: https://discourse.psychopy.org/t/changing-colors-of-tiles-in-a-grid-psychopy-help/4616/6

Now set the grid parameters to approximate the wanted number of tokens
this will adjust the number of grid lines and therefore the token size. 
it will provide a grid that overshoot the `num_tokens` number slightly
(those extra tokens can be remove later)"""
alt_grid_side = ceil(sqrt(num_tokens))
grid_side = alt_grid_side*2
side_tokens = ceil(grid_side*1.3) #constant is abritrary (NOTE: got 1 error with n=15 now)
#set the size of a token
token_size = [circle_size / side_tokens, circle_size / side_tokens]
#set where the grid is positioned
location = [0, c_y_pos]
loc = np.array(location) + np.array(token_size) // 2


def make_tokens(xys, indices, pos):
    """Creates an elementArrayStim based on given parameters"""
    # Select xys
    if len(xys)==len(indices): this_xys = xys #no need to select indices
    else: this_xys = [xys[i] for i in indices] #find corresponding x's,y's
    # Create the central ElementArrayStim array 
    tokens = visual.ElementArrayStim(win,
        xys=this_xys, fieldShape='circle', fieldPos=pos,  
        colors=whitish, nElements=len(this_xys), elementMask='circle',
        elementTex=None, sizes=(token_size[0], token_size[1]))
    return tokens

def clip(val, min_, max_):
    return min_ if val < min_ else max_ if val > max_ else val

#- - - - - - - - - -
# PRELOADING ARRAYS
#- - - - - - - - - -
"""Here I create all central token arrays with randomly jittered tokens.
I first define all positions and then create stimuli arrays."""

# Create empty arrays beforehand
stgs = []
stim = []

for trl in range(num_trials):

    # SETTING UP COORDINATES FOR EACH TOKEN
    xys = [] #empty array of coordinates
    # Set the lowest and highest token ID on each side
    low, high = side_tokens // -2, side_tokens // 2
    # Populate xys
    for y in range(low, high, 2):  #by steps of 2 to remove alternate lines
        for x in range(low, high, 2):
            x_pos = token_size[0] * x
            y_pos = token_size[1] * y
            # ADD JITTER
            x_pos = x_pos + np.random.uniform(-token_size[0]/2, token_size[0]/2)
            y_pos = y_pos + np.random.uniform(-token_size[0]/2, token_size[1]/2)
            # REMOVE OUT OF CIRCLE ELEMENTS
            #for a given x_pos, we find a max y_pos that remains within the circle using Pythagora's theorem
            try: max_y_pos = sqrt((circle_radius-(token_size[0]))**2 - x_pos**2)
            except: max_y_pos = 0  #to avoid error with sqrt(0)
            if (y_pos+loc[0]) > max_y_pos or (y_pos+loc[0]) < -max_y_pos : continue
            else: xys.append((x_pos, y_pos))

    # NOTE: Not sure what the following does...:
    #tokens.size = (token_size[0] * side_tokens,
    #               token_size[1] * side_tokens)

    #Set L/R assignment for each token in this trial
    #TODO: Extended this with trial difficulty, types, etc
    token_sequence = ['l']*(len(xys)//2) + ['r']*(len(xys)//2)
    token_sequence = random.sample(token_sequence, len(token_sequence))

    # Reduce xys length to the initially desired number of tokens
    shortlist = random.sample(range(len(xys)), num_tokens)
    xys = [xys[i] for i in shortlist]

    # SETTINGS
    # `pos`: main position: central, left or right
    # `i_all`: indices for all tokens that will go either left or right
    # `i_now`: indices of tokens that will be shown at a given moment
    #TODO: stgs[trial]
    stgs += [{'c' : {
        'pos'  : loc,
        'i_all': random.sample(range(len(xys)), num_tokens),  # Shuffle list of indices for the new shortlisted xys list
        'i_now': [ [] for i in range(num_tokens) ]  #TODO: Extend for each `this_token`, maybe make this an indexed list
        }, 
            'l'   : {
        'pos'  : (loc - (c_offset, 0)),
        'i_all': [i for i, x in enumerate(token_sequence) if x == 'l'],
        'i_now': [ [] for i in range(num_tokens) ] 
        },
            'r'  : {
        'pos'  : (loc + (c_offset, 0)),
        'i_all': [i for i, x in enumerate(token_sequence) if x == 'r'],
        'i_now': [ [] for i in range(num_tokens) ] 
        }
    }]

    # STIMULI. ElementArrays will be stored here.
    stim += [{'c' : [ [] for i in range(num_tokens) ],
              'l' : [ [] for i in range(num_tokens) ],
              'r' : [ [] for i in range(num_tokens) ]}]

    # Create and store stim at each side at each moment in time
    for this_token in range(num_tokens):
        # 1. Update array indices
        for side in 'l', 'r':
            stgs[trl][side]['i_now'][this_token] = [t for t in stgs[trl][side]['i_all'] if t <= this_token]
        # Now remove the sides indices from the center indices
        sides = stgs[trl]['l']['i_now'][this_token] + stgs[trl]['r']['i_now'][this_token]
        stgs[trl]['c']['i_now'][this_token] = [x for x in stgs[trl]['c']['i_all'] if x not in sides]
        # 2. Set each side's array stim using the indices
        for i_pos in stgs[trl]:
            if stgs[trl][i_pos]['i_now'][this_token]:  #test whether list is not empty
                stim[trl][i_pos][this_token] = make_tokens(
                    xys=xys, 
                    indices=stgs[trl][i_pos]['i_now'][this_token], 
                    pos=stgs[trl][i_pos]['pos'])

    # Add also the full array at the end of each trial list  # `trl` will always give the +1
    stim[trl]['c'] += [make_tokens(xys=xys, 
                              indices=stgs[trl]['c']['i_all'], 
                              pos=stgs[trl]['c']['pos'])]

    # Save stgs to file
    # NOTE: TODO.

#----------------------
# 2.3 RESPONSE STIMULI
#----------------------

#- - - - - - - - - -
# Mouse and cursor
#- - - - - - - - - -

mouse = event.Mouse(visible=True, win=win)
cursor_start_y_pos = -200
cursor_rad = 5
cursor = visual.Circle(win, 
        radius=cursor_rad, lineColor=line_color, fillColor=line_color,
        lineWidth=line_width, interpolate=False)

#Time window for mouse velocity calculation
#TODO: change depending on initial hz
t_in_frames = 15

#stimuli for cursor shadow
shadow_length = 10
shadow_stim = []
for i in range(shadow_length):
    shadow_rad = cursor_rad/shadow_length*(i+1)
    shadow_stim += [visual.Circle(win, 
        radius=shadow_rad, lineColor=line_color, fillColor=line_color,
        lineWidth=line_width, interpolate=False)]

#- - - - - - - - - - -
# Moving drawing area
#- - - - - - - - - - -

draw_area_coord = (cursor_start_y_pos, location[1]-circle_radius)  # top, bottom
draw_rect_height = abs(abs(draw_area_coord[1]) - draw_area_coord[0])  # top - bottom
draw_rect_x = 0
draw_rect_y = draw_area_coord[1] - draw_rect_height/2
#we calulate vertical step that is added each frame
y_step = draw_rect_height/(num_tokens*frames_per_token)
#stimuli list for drawing area
area = visual.Rect(win, width=500, height=draw_rect_height, 
                    fillColor = whitish, lineColor = whitish, 
                    pos = (draw_rect_x, draw_rect_y),
                    opacity = .75)

#- - - - - - - - - - -
# Static text and other
#- - - - - - - - - - -

txt_size = 20  #text height in dva
title_pos = -150  # y position for the text
pretrl_stims = []
pretrl_stims += [visual.Polygon(win, edges=3, radius=10, fillColor = yellowish,
            lineColor = yellowish, pos = (0, cursor_start_y_pos))]
pretrl_stims += [visual.TextStim(win, 
            text=u"Bring mouse to bottom shape to start", 
            height=txt_size, pos = [0, title_pos], color = whitish)]

#===============
# 3. TRIAL LOOP
#===============

for trl in range(num_trials):

    # 3.1 Reset some values at each trial
    trl_path  = []  #continuous rating vector: tuples for pos, and time (variable length each trial)
    trl_times = []  #timestamp for each recorded position
    for side in 0, 2: 
        circles[side].setLineColor(line_color)  #reset colors
        circles[side].setLineWidth(line_width)  #reset line width

    moving = True  #mouse
    show_shadow = True
    show_cursor = True
    show_area = True
    responded = False
    last_token = False
    last_frame = False
    frames_per_token = slow_speed
    #mouse.setPos([0, cursor_start_y_pos])
    mouse.clickReset()
    lower_bound = draw_area_coord[0]  #restart the value each trial

    event.Mouse(visible=True)  #make mouse visible (again)
    timer = core.Clock()  #start a trial timer

    # 3.2 Set some trial information
    correct_side = 'l' #TODO: change to get from sequences

    # 3.3 Draw on screen pre-trial stimuli until mouse reaches start position
    while not pretrl_stims[0].contains(mouse):  # [] indexes the target shape
        
        #make the starting space blink
        pretrl_stims[0].setOpacity(abs(sin(timer.getTime()*2)))
        #draw titles and other
        for s in pretrl_stims:
            s.draw()
        #draw big circles
        for c in circles:
            c.draw()
        #draw the full central array
        stim[trl]['c'][num_tokens].draw()

        #flip to the screen while mouse not on position
        win.flip()

        #allow to quit if necessary TODO: add quit confirmation
        if event.getKeys(['escape']): core.quit()

    #===============
    # 4. TOKEN LOOP
    #===============
    """Mouse is on position, start moving tokens!"""

    event.Mouse(visible=False)  #make mouse disappear
    timer.reset()  #restart the trial timer
    for this_token in range(num_tokens):
        #detect whether this is the last token for special case
        if this_token == num_tokens-1: 
            last_token = True

        #===============
        # 5. FRAME LOOP
        #===============
        """Each token is presented for multiple screen refreshes (frames)
        Cursor and other visual stimuli are updated simultaneously"""

        for this_frame in range(frames_per_token):
            # 5.0 Detect whether this is the last token (for special case)
            if this_frame == frames_per_token-1 and last_token: 
                last_frame = True

            # 5.1 Update drawing area
            #draw an area for drawing with a moving lower bound
            #we calulate the vertical step that is added each frame
            if show_area:
                lower_bound += y_step
                new_height = abs(abs(draw_area_coord[1]) - lower_bound)
                new_y = draw_area_coord[1] - new_height/2
                area.height = new_height
                area.setPos((draw_rect_x, new_y))
                area.draw()

            # 5.2 Update mouse and cursor
            #5.2.1 Get mouse position and, if needed, set within limits
            m_x, m_y = mouse.getPos()
            #5.2.2 Store mouse position
            trl_path.append((m_x, m_y))  # record current mouse positions
            trl_times.append(round(timer.getTime(), 2))  # record time of mouse position

            #5.2.3 Calculate mouse velocity
            #distance between last and previous recorded coordiantes (between two frames)
            # time in frames for the duration of the travel
            if len(trl_path) > t_in_frames:  # start measuring after a time minimum
                m_velocity = sqrt((trl_path[-1][0] - trl_path[-t_in_frames][0])**2 + 
                                  (trl_path[-1][1] - trl_path[-t_in_frames][1])**2)
                if m_velocity > 0:
                    moving = True
                    #cursor.setFillColor('white')
                    area.setFillColor(whitish)
                else:
                    moving = False
                    #cursor.setFillColor('red')
                    area.setFillColor(redish)

            #5.2.4 Prepare cursor visualisation

            # a. cursor shadow
            if show_shadow:
                if len(trl_path) > shadow_length:
                    shadow_pos = trl_path[-shadow_length:]
                    for i, pos in enumerate(shadow_pos):
                        shadow_stim[i].setPos(pos) 
                        shadow_stim[i].setOpacity(1/shadow_length*(i+1))
                        shadow_stim[i].draw()

            # b. Current cursor
            #horizontal limits
            #if m_x < -c_offset: m_x = -c_offset  #clipped -X position
            #if m_x > c_offset: m_x = c_offset  #clipped +X position
            # TODO: cannot go down vertically
            # OR better: there is minimum upward motion if speed <= 0? (but problem of mismatch finger/cursor)
            #set new position
            cursor.setPos([m_x, m_y])
            if show_cursor: cursor.draw()

            # 5.3 Update the current token array
            for s in stim[trl]:
                if stim[trl][s][this_token]:  #test whether list is not empty
                    stim[trl][s][this_token].draw()

            # 5.4 Special case after response or missed response
            # if responded, go through all remaining tokens but faster
            #break will skip all planned frames, but we can add another short delay
            if responded:
                if not last_token:
                    frames_per_token = fast_speed
                    show_cursor = False
                    show_shadow = False
                    show_area = False
                if last_token and last_frame: #last token, feedback and record something
                    #display feedback
                    if sel_side_letter == correct_side: 
                        circles[sel_side_num].setLineColor(greenish)
                    else:
                        circles[sel_side_num].setLineColor(redish)
                        
            if not responded and last_token:
                #no response, "too slow" message or similar
                continue

            # 5.5 Draw static big circles
            #change appearance if mouse reaches side cicles
            for side in 0, 2:
                if circles[side].contains(mouse): 
                    circles[side].setLineWidth(line_width*3)
                    responded = True
                    sel_side_num = side
                    sel_side_letter = 'l' if side == 0 else 'r'
                    rt = round(timer.getTime(), 3)  #timestamp
                else: circles[side].setLineWidth(line_width)
            for c in circles:
                c.draw()

            # 5.6 Flip everything that has been drawn on screen
            win.flip()

            # 5.7 Ask for manual input if trial ended
            if last_token and last_frame:
                #save trial information
                write_trial(correct='l', 
                            resp='sel_side_letter', 
                            acc= 1 if 'l'=='sel_side_letter' else 0,
                            rt=rt, 
                            x_values=trl_path, 
                            t_values=trl_times)

                #require manual input to continue
                keypress = event.waitKeys(keyList=['space', 'escape'])

            # 5.8 Continously allow to quit if escape is pressed
            if event.getKeys(['escape']): core.quit()