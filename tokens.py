from psychopy import visual
import numpy as np
import random
from math import sqrt, ceil

#======================
# TODO:
# perhaps add some more space for tokens near border (in pytaghora's formula)
# create probability "curves"/series
#======================

win = visual.Window(units='pix')

# GENERAL

frames_per_token = 60//5  #moving speed

# BIG CIRCLES
# Create 3 big circles
circles = []
circle_size = 130  #set the height of the circle
circle_radius = circle_size/2
line_color = 'white'  #color of the circle border
line_width = 2.5  #width of the circle border
line_edges = 256  #number of edges to create the circle
c_offset = 200  #offset from the center in the x axis
for pos in -c_offset, 0, c_offset:
    circles += [visual.Circle(win, 
        radius=circle_radius, lineColor=line_color, lineWidth=line_width,
        pos=(pos, 0), edges=line_edges, interpolate=False)]

# GENERAL TOKEN ARRAY SETTINGS
#https://discourse.psychopy.org/t/changing-colors-of-tiles-in-a-grid-psychopy-help/4616/6

#set the number of desired tokens inside the main circle
wanted_tokens = 20
# now set the grid parameters to approximate the wanted number of tokens
# this will adjust the number of grid lines and therefore the token size. 
# it will provide a grid that overshoot the `wanted_tokens` number slightly
# (those extra tokens can be remove later)
alt_grid_side = ceil(sqrt(wanted_tokens))
grid_side = alt_grid_side*2
side_tokens = ceil(grid_side*1.3) #constant is abritrary
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

# Create arrays beforehand

stgs = {}
stim = {}

for this_trial in range(1):

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
    stgs = {'c' : {
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
    }

    # STIMULI. ElementArrays will be stored here.
    #TODO: stim[trial]
    stim = {'c' : [ [] for i in range(wanted_tokens) ] ,
            'l' : [ [] for i in range(wanted_tokens) ] ,
            'r' : [ [] for i in range(wanted_tokens) ] }

    # Create and store stim at each side at each moment in time
    for this_token in range(wanted_tokens):

        # 1. Update array indices
        for side in 'l', 'r':
            stgs[side]['i_now'][this_token] = [t for t in stgs[side]['i_all'] if t <= this_token]
        
        # Now remove the sides indices from the center indices
        sides = stgs['l']['i_now'][this_token] + stgs['r']['i_now'][this_token]
        stgs['c']['i_now'][this_token] = [x for x in stgs['c']['i_all'] if x not in sides]
        
        # 2. Set each side's array stim using the indices
        for i_pos in stgs:
            if stgs[i_pos]['i_now'][this_token]:  #test whether list is not empty
                print(i_pos)
                print(stgs[i_pos]['i_now'][this_token])
                stim[i_pos][this_token] = make_tokens(
                    xys=xys, 
                    indices=stgs[i_pos]['i_now'][this_token], 
                    pos=stgs[i_pos]['pos'])

    # START

    # First, show full array TODO: append this to stim[] instead
    tokens = make_tokens(
        xys=xys, 
        indices=stgs['c']['i_all'], 
        pos=stgs['c']['pos'])
    for this_frame in range(frames_per_token):
        for circle in circles:
            circle.draw()
        tokens.draw()
        win.flip()

    # TODO: Add a spacebar here

    # 3. Draw
    for this_token in range(wanted_tokens):
        for this_frame in range(frames_per_token):
            for c in circles:
                c.draw()
            for s in stim:
                if stim[s][this_token]:  #test whether list is not empty
                    stim[s][this_token].draw()
            win.flip()