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

    # NOTE: Not sure what this does
    #tokens.size = (token_size[0] * side_tokens,
    #               token_size[1] * side_tokens)

    #Set L/R assignment for each token in this trial
    #TODO: Extended this with trial difficulty, types, etc
    token_sequence = ['l']*(len(xys)//2) + ['r']*(len(xys)//2)
    token_sequence = random.sample(token_sequence, len(token_sequence))

    # Reduce xys length to the initially desired number of tokens
    idx_center_all = random.sample(range(len(xys)), wanted_tokens)  #atm only a reshuffle. I could arrange indices by distance to center etc.
    xys = [xys[i] for i in sel_indices]
    # Indices of tokens that will go either left or right
    idx_left_all   = [i for i, x in enumerate(token_sequence) if x == 'l']
    idx_right_all  = [i for i, x in enumerate(token_sequence) if x == 'r']

    # DRAW THE FULL ARRAY TODO: Do better by adding this step inside loop?
    # Find corresponding x,y position of selected indices
    sel_center = [xys[i] for i in idx_center_all]
    # Create the central ElementArrayStim array 
    tokens = visual.ElementArrayStim(win,
        xys=sel_center, fieldShape='circle', fieldPos=loc,  
        colors='white', nElements=len(sel_center), elementMask='circle',
        elementTex=None, sizes=(token_size[0], token_size[1]))

    for this_frame in range(frames_per_token):
        for circle in circles:
            circle.draw()
        tokens.draw()
        win.flip()

    # TODO: ADD SPACEBAR TO START

    for this_token in range(len(xys)):

        # 1. UPDATE ALL ARRAY INDICES
        # TODO: All arrays can and should be previously stored in a list!
        try: stay_in_center = idx_center_all[this_token+1:]
        except: stay_in_center = []
        moved_left = [x for i, x in enumerate(idx_left_all) if x <= this_token]
        moved_right = [x for i, x in enumerate(idx_right_all) if x <= this_token]

        # 2. SELECT THE ARRAY POSITIONS USING THE INDICES

        # 2a. Tokens remaining centered
        if stay_in_center:  # Test whether list is not empty
            # Find corresponding x,y position of selected indices
            sel_center = [xys[i] for i in stay_in_center]
            # Re-create the central ElementArrayStimray
            tokens = visual.ElementArrayStim(win,
                xys=sel_center, fieldShape='circle', fieldPos=loc,  
                colors='white', nElements=len(sel_center), elementMask='circle',
                elementTex=None, sizes=(token_size[0], token_size[1]))
        
        # 2b. Tokens going left
        if moved_left:
            # Find corresponding x,y position of selected indices
            sel_left = [xys[i] for i in moved_left]
            # Modify the token position (mirror) and correct for location bias
            #sel_left = np.array(sel_left)*-1 - token_size
            # Re-create the left ElementArrayStimray
            tokens_left = visual.ElementArrayStim(win,
                xys=sel_left, fieldShape='circle', fieldPos=(loc - (c_offset,0)),  
                colors='white', nElements=len(sel_left), elementMask='circle',
                elementTex=None, sizes=(token_size[0], token_size[1]))

        # 2c. Tokens going right
        if moved_right:
            # Find corresponding x,y position of selected indices
            sel_right = [xys[i] for i in moved_right]
            # Modify the token position (mirror) and correct for location bias
            #sel_right = np.array(sel_right)*-1 - token_size
            # Re-create the left ElementArrayStimray
            tokens_right = visual.ElementArrayStim(win,
                xys=sel_right, fieldShape='circle', fieldPos=(loc + (c_offset,0)),  
                colors='white', nElements=len(sel_right), elementMask='circle',
                elementTex=None, sizes=(token_size[0], token_size[1]))

        # 3. DRAW EVERYTHING
        for this_frame in range(frames_per_token):
            for circle in circles:
                circle.draw()
            if stay_in_center: tokens.draw()   #TODO: tokens[this_circle][this_trial][this_token]
            if moved_left: tokens_left.draw()
            if moved_right: tokens_right.draw()
            win.flip()