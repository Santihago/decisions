from psychopy import visual, event
import numpy as np
import random
from math import sqrt, ceil

#==================
# GENERAL SETTINGS
#==================

win = visual.Window(units='pix', color='#1e1e1e')
frames_per_token = 60//2  #moving speed
num_trials = 3

#==================
# STIMULI CREATION
#==================

#---------------------
# MAIN VISUAL STIMULI
#---------------------

# BIG CIRCLES
# Create 3 big circles
circle_size = 130  #set the circle diameter
circle_radius = circle_size/2
line_color = 'white'  #color of the circle border
line_width = 2.5  #width of the circle border
line_edges = 256  #number of edges to create the circle
c_offset = 200  #offset from the center in the x axis for the 2 periph circles
circles = []
for pos in -c_offset, 0, c_offset:
    circles += [visual.Circle(win, 
        radius=circle_radius, lineColor=line_color, lineWidth=line_width,
        pos=(pos, 0), edges=line_edges, interpolate=False)]

#------------------
# RESPONSE STIMULI
#------------------

# Mouse
mouse = event.Mouse(visible=True, win=win)

# Dynamix text and stimuli
#------------- You can adjust these
rs_size = 400 #scale size in degrees of visual angle (DVA)
scale_max = 8 #maximum rating in the rating scale (int)
rs_col = 'white' # '#373F51'  #charcoal color
rs_txt_col = 'white' # '#373F51'
rs_txt_size = 20  #text height in dva
rs_y_pos = -200
labels_y_pos = -100  #y position (in DVA) of text labels
dyn_txt_y_pos = -90 #y position (in DVA) of dynamic rating text
labels = ["0 %", "100 %"]  #text value of scale labels
labels_pos = [-100, 100]  #pos values from -1 to 1
ticks_pos = [-50, 0, 50]  #pos values of ticks/bands

#------------- No need to adjust these
_rs_max = rs_size/2  #scale rightmost value
_rs_min = (-1 * _rs_max)  #scale leftmost value
rs_stims = []  #scale stimuli list
#horizontal bar
rs_stims += [visual.Rect(win, width=_rs_max*2, height=.1, fillColor = rs_col,
             lineColor = rs_col, pos = (0, rs_y_pos))]
#add text labels
labels_x_pos = [x * _rs_max for x in labels_pos]
for nr, this_x_pos in enumerate(labels_x_pos):
    rs_stims += [visual.TextStim(win, text=labels[nr], height=rs_txt_size,
                 pos = [this_x_pos, labels_y_pos], color = rs_txt_col)]
#add ticks / bands
ticks_x_pos = [x * _rs_max for x in ticks_pos]
for this_x_pos in ticks_x_pos: # Mini-ticks
    rs_stims += [visual.Rect(win, width=5, height=25, pos = [this_x_pos, rs_y_pos], 
                 fillColor = rs_col, opacity = 75)]
#moving slider
rs_slider = visual.Rect(win, width=5, height=10, fillColor = rs_col,
                        lineColor = rs_col)
#moving text
dyn_txt = visual.TextStim(win, text=u"", height=rs_txt_size, color = rs_txt_col)

# Static text (e.g. "Please respond")
title_pos = 200
title_txt_size = 30
rs_stims += [visual.TextStim(win, 
             text=u"Confidence response", 
             height=title_txt_size, pos = [0, title_pos], color = rs_txt_col)]

pretrl_stims = []
pretrl_stims += [visual.TextStim(win, 
             text=u"Bring mouse to center to start", 
             height=title_txt_size, pos = [0, title_pos], color = rs_txt_col)]

#---------------
# TOKEN ARRAYS
#---------------
# Inspired by: https://discourse.psychopy.org/t/changing-colors-of-tiles-in-a-grid-psychopy-help/4616/6

#set the number of desired tokens inside the main circle
wanted_tokens = 30
# now set the grid parameters to approximate the wanted number of tokens
# this will adjust the number of grid lines and therefore the token size. 
# it will provide a grid that overshoot the `wanted_tokens` number slightly
# (those extra tokens can be remove later)
alt_grid_side = ceil(sqrt(wanted_tokens))
grid_side = alt_grid_side*2
side_tokens = ceil(grid_side*1.3) #constant is abritrary (NOTE: got 1 error with n=15 now)
#set the size of a token
token_size = [circle_size / side_tokens, circle_size / side_tokens]
#set where the grid is positioned
location = [0, 0]
loc = np.array(location) + np.array(token_size) // 2


def make_tokens(xys, indices, pos):
    """Creates an elementArrayStim based on given parameters"""
    # Select xys
    if len(xys)==len(indices): this_xys = xys #no need to select indices
    else: this_xys = [xys[i] for i in indices] #find corresponding x's,y's
    # Create the central ElementArrayStim array 
    tokens = visual.ElementArrayStim(win,
        xys=this_xys, fieldShape='circle', fieldPos=pos,  
        colors='white', nElements=len(this_xys), elementMask='circle',
        elementTex=None, sizes=(token_size[0], token_size[1]))
    return tokens

# Create empty arrays beforehand

stgs = []
stim = []

#=====================
# PRE-SETTINGS ARRAYS
#=====================

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

    # NOTE: Not sure what the following does...
    #tokens.size = (token_size[0] * side_tokens,
    #               token_size[1] * side_tokens)

    #Set L/R assignment for each token in this trial
    #TODO: Extended this with trial difficulty, types, etc
    token_sequence = ['l']*(len(xys)//2) + ['r']*(len(xys)//2)
    token_sequence = random.sample(token_sequence, len(token_sequence))

    # Reduce xys length to the initially desired number of tokens
    shortlist = random.sample(range(len(xys)), wanted_tokens)
    xys = [xys[i] for i in shortlist]

    # SETTINGS
    # `pos`: main position: central, left or right
    # `i_all`: indices for all tokens that will go either left or right
    # `i_now`: indices of tokens that will be shown at a given moment
    #TODO: stgs[trial]
    stgs += [{'c' : {
        'pos'  : loc,
        'i_all': random.sample(range(len(xys)), wanted_tokens),  # Shuffle list of indices for the new shortlisted xys list
        'i_now': [ [] for i in range(wanted_tokens) ]  #TODO: Extend for each `this_token`, maybe make this an indexed list
        }, 
            'l'   : {
        'pos'  : (loc - (c_offset, 0)),
        'i_all': [i for i, x in enumerate(token_sequence) if x == 'l'],
        'i_now': [ [] for i in range(wanted_tokens) ] 
        },
            'r'  : {
        'pos'  : (loc + (c_offset, 0)),
        'i_all': [i for i, x in enumerate(token_sequence) if x == 'r'],
        'i_now': [ [] for i in range(wanted_tokens) ] 
        }
    }]

    # STIMULI. ElementArrays will be stored here.
    stim += [{'c' : [ [] for i in range(wanted_tokens) ],
            'l' : [ [] for i in range(wanted_tokens) ],
            'r' : [ [] for i in range(wanted_tokens) ]}]

    # Create and store stim at each side at each moment in time
    for this_token in range(wanted_tokens):
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

    # Add the full stim at the end of each trial list
    stim[trl]['c'] += [make_tokens(xys=xys, 
                              indices=stgs[trl]['c']['i_all'], 
                              pos=stgs[trl]['c']['pos'])]

#=======
# START
#=======

for trl in range(num_trials):

    mouse.setPos([0,-300])
    mouse.clickReset()

    while not circles[1].contains(mouse):  # 1 is central circle
        #draw big circles
        for c in circles:
            c.draw()
        #draw the full central array
        stim[trl]['c'][wanted_tokens].draw()
        #draw titles and other
        for s in pretrl_stims:
            s.draw()
        win.flip()

    # Start moving tokens
    for this_token in range(wanted_tokens):
        for this_frame in range(frames_per_token):

            # STATIC STIMULI
            for c in circles:
                c.draw()

            # RATING SCALE
            #draw all components of the rating scale
            for s in rs_stims:
                s.draw()
            #set slider and dynamic text position to mouse and draw 
            m_x, m_y = mouse.getPos()
            if m_x < _rs_min: m_x = _rs_min  #clipped -X position
            if m_x > _rs_max: m_x = _rs_max  #clipped +X position
            rs_slider.setPos([m_x, rs_y_pos])
            rs_slider.draw()
            #re-scale rating value to given range
            RATING = int(((m_x+_rs_max)/_rs_max)*(scale_max/2))
            #draw value of rating on the screen at mouse position
            dyn_txt.setPos([m_x, dyn_txt_y_pos])
            dyn_txt.setText("CONFIDENCE: " + str(RATING))
            dyn_txt.draw()

            for s in stim[trl]:
                if stim[trl][s][this_token]:  #test whether list is not empty
                    stim[trl][s][this_token].draw()
            win.flip()