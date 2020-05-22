from math import floor, factorial


def get_quantities(sequence, length = None, end = None, digits=True):
    """Sequence example: '222221211222212' or 'rrrrrlrllrrrrrlr """
    # Check if sequence entered correctly
    try: isinstance(sequence, str)
    except AssertionError: print("The sequence should be in `string` format.")

    # Other checks
    if end is not None:
        try: length is not None
        except AssertionError:
            print("If an optional `end` is provided, need also the full sequence `length`.")

    # Defaults: If not optional end or length, then we assume it is a full sequence
    if length is None: length = len(sequence)
    if end is None: end = len(sequence)  #if no high limit, then the entire sequence is considered

    # Unfold sequence
    NC = length - end  # Number of tokens remaining is equal to total number - end
    if digits: NR = sequence.count('2')
    elif not digits: NR = sequence.count('r')
    NL = length - (NC + NR)

    return NC, NR, NL


def get_prob(NC, NL, num_tokens):
    """Formula for calculating the success probability of guessing right 
    (Cisek 2009). Given a total number of tokens, the number of remaining 
    tokens in the center, moved tokens to the LEFT, calculate the probability 
    that RIGHT response is correct"""

    # First part of the formula
    first_part = factorial(NC) / (2**NC)

    # Summation part of the formula
    high_bound = min(NC, floor(num_tokens/2)-NL)  #the higher bound for the summation NOTE: Not sure if floor() for even numbers
    summation = sum([1/(factorial(k)*factorial(NC - k)) for k in range(0, high_bound+1)])

    # Probability that 'Right' response is correct given the sequence history
    p_r = first_part * summation

    return p_r


def get_prob_vector(sequence, num_tokens):
    """Given a sequence, get a vector of probabilities at each timepoint."""

    probs = []

    # Calculate the success probability after each token movement
    for end in range(0, len(sequence) + 1):

        # Take part of the sequence
        sequence_part = sequence[:end]

        # Obtain the variables for the formula
        NC, NR, NL = get_quantities(sequence=sequence_part, length=num_tokens, end=end, digits=True)

        # Formula
        p_r = get_prob(NC, NL, num_tokens)

        #print('center:' + str(NC) + ', right:' + str(NR) + ', left:' + str(NL) + ', P(R):' + str(round(P_R, 2)))

        probs += [p_r]

    return probs


def get_extended_template(template, new_length):

    old_length = len(template)

    # Find pos of each filled item
    old_pos = [i for i,x in enumerate(template) if x is not tuple()]
    # Normalize
    adj_pos = [old_pos / old_length for old_pos in old_pos]
    # New positions
    new_pos = [round(pos * new_length) for pos in adj_pos]

    # New extended_template
    extended_template = [tuple()] * new_length
    for i in range(new_length):
        if i in new_pos:
            #find idx of i in new_pos (and old_pos)
            idx = new_pos.index(i)
            # that gives the pos
            pos = old_pos[idx]
            # we take value corresponding to pos
            extended_template[i] = template[pos]

    return extended_template


def get_NL(num_tokens, NC, prob_min, prob_max):
    """Reversing the formula"""

    accepted_NL_values = []

    # Loop for different values of NL to find those that work
    for possible_NL in range(num_tokens):

        p_r = get_prob(NC, possible_NL, num_tokens)

        if p_r >= prob_min and p_r <= prob_max:
            accepted_NL_values += [possible_NL]
        else: continue

    #count NLs to get valid range of min,max
    NL_min = min(accepted_NL_values)
    NL_max = max(accepted_NL_values)

    return NL_min, NL_max


def get_ranges(extended_template):  #type='easy'
    """Translate prob template into token quantity ranges"""

    ranges = []

    num_tokens = len(extended_template)

    for i, x in enumerate(extended_template):  #start backwards [::-1]
        if not x: # If x==[]
            ranges += [tuple()]  #[((),)]  #empty tuple
            continue
        else:
            NC = num_tokens - (i+1)
            #we have NC, find NL so that get_prob()> x < 1 
            #(find range of NL min and NR max), and take a value in range randomly
            NL_min, NL_max = get_NL(num_tokens=num_tokens, NC=NC, prob_min=x[0], prob_max=x[1])

            NR_min = num_tokens - (NC + NL_max) 
            NR_max = num_tokens - (NC + NL_min) 

            #Save tuple in vector
            ranges += [(NR_min, NR_max)]

    return ranges


# def adjust_min_max(ranges):
# """A minimum cannot be lower than a previous minimum.
# A maximum cannot be lower than a previous maximum."""

#     for i, x in enumerate(ranges):

#         latest_valid_idx = []

#         if x == tuple(): # If empty
#             continue
        
#         else:
#             idx = i  #latest index of non-empty item
#             if i == 0: #no adjustment needed for first item
#                 continue
#             elif i>0:
#                 previous_min = ranges[idx][0]
#                 previous_max = ranges[idx][1]

#                 #min: a min[i] cannot be lower than previous minima
#                 #max: a max[i] cannot be higher than previous maxima
#                 new_min = previous_min if (previous_min > x[0]) else x[0]
#                 new_max = previous_max if (previous_max < x[1]) else x[1]

#                 # Change the range value if necessary
#                 ranges[i] = (new_min, new_max)

#         return ranges 


# def fillin_template(ranges):

#     filled_template = []

#     for i, x in enumerate(ranges):

#         latest_valid_idx = []
        
#         if x is tuple():  #empty

#             if i==0:
#                 # Random side selection
#                 # 1 or 0
#                 NR = random.int(0, 1, 1)
#             else:
#                 # Take min and max from previous range

#         elif x is not tuple():

#             idx = i  #latest index of non-empty item

#             # Take min and max from range
#             # Take into account previous item for the min and max
            
#             previous_min = ranges[idx][0]
#             previous_max = ranges[idx][1]

#             # Merge
#             new_min = previous_min if (previous_min > x[0]) else x[0]
#             new_max = previous_max if (previous_max < x[1]) else x[1]

#             # If equal values, then no question
#             if new_min == new_max:
#                 NR = new_min
#             # If range, then sample a value between the two
#             elif new_min is not new_max:
#                 NR = random.int(new_min, new_max, 1)

#             completed_template[i] = 

#         return complete_template

# def make_sequence(complete_template):

#     # Starting from the complete_template, we haveNC and the NR

#     # Find NL for each timepoint

#     # Translate into 212121 or lrlrlrl


# def exp_sequence_maker():

#     # Given predefined


#----------


# sequence for example (almost all tokens go to right, so P(R) increases steadily)
sequence = '222221211222212'  #sequence of tokens, going left (1) or right (2)
num_tokens = 8  #total number of tokens

#example
template = [(.6, 1),  (), (.7, 1), (), (.8, 1), (), (), (), (), (.8, 1), (), (), (.9, 1), (), ()]  # all >=
# ambi = [],  .5, .55-0.65, .5, .55-0.65, .5, .55-0.65, .5, <.6, >.5, .65, >.5, .75, [], []  # 

# i    =  1,    2,    3,  4,  5,  6,  7,  8,  9,   10, 11, 12, 13,  14, 15
# misl = [],  <.3,  <.4, <.5, [], [], [], [], [], >.5, [], [], [], .75, [], []  # 


extended_template = get_extended_template(template, new_length = 8)
ranges = get_ranges(extended_template)
print(ranges)
adjusted_ranges = adjust_min_max(ranges)
print(adjusted_ranges)

#TODO:
# FIll-in sequences