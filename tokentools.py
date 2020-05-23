from math import floor, factorial
import random


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


def look_right(i, ranges):
    for next_index in range(i, len(ranges)):
        if ranges[next_index] is tuple():
            continue
        else:
            right_min = ranges[next_index][0]
            right_max = ranges[next_index][1]
            break
    return next_index, right_min, right_max

def look_left(i, filled_ranges):

    left_min = filled_ranges[i-1][0]
    left_max = filled_ranges[i-1][1]

    return left_min, left_max


def fill_in(ranges):
    """1) A given minimum cannot be lower than a previous minimum.
    We set all unknown item's minima to the previous known minimum.
    2) An unknown maximum cannot be more than +1 of a previous known maximum.
    We set all unknown maxima to +1 of the previous known maximum."""

    filled_ranges = []

    for i, x in enumerate(ranges):

        found_left = False
        found_right = False

        if x:  #continue until finding empty slot

            filled_ranges += [x]

        if x is tuple():  # if empty

            try: 
                left_min, left_max = look_left(i, filled_ranges)
                found_left = True
            except: 
                pass
            try:
                next_index, right_min, right_max = look_right(i, ranges)
                found_right = True
            except: 
                pass

            if not found_left and found_right:
                new_min = right_min - (next_index-i)  #  bc only 1 jump per timepoint allowed
                new_max = right_max  # cannot be more than the following max

            elif found_left and not found_right:
                new_min = left_min
                new_max = left_max + 1

            elif found_left and found_right:

                # Find new_min 
                # Take the highest value between
                val_1 = left_min  #at least the previous min
                val_2 = right_min-(next_index-i)  #  only 1 jump per timepoint allowed
                new_min = max(val_1, val_2)  #take highest value

                # Find new_max 
                # Take the highest value between
                val_3 = left_max + 1  # maximum +1 from previous maximum
                val_4 = right_max  # cannot be more than the following max
                new_max = min(val_3, val_4)  #take highest value

            filled_ranges += [(new_min, new_max)]

    return filled_ranges


def make_NR_sequence(filled_ranges):

    sequence = []

    for i, x in enumerate(filled_ranges):

        if x[0] == x[1]:
            value = x[0]
        else:
            if i is 0:
                value = random.randint(0, 1)

            if i is not 0:
                previous_value = sequence[i-1]
                #If previous_value is lower than the current minimum, mandatory to add 1
                if previous_value == (x[0] - 1):
                    value = previous_value + 1
                # If previous value is within the current range, then it's random
                elif previous_value in range(x[0], x[1]):
                    # Coin toss 
                    value = previous_value + random.randint(0, 1)

        sequence += [value] 

    return sequence


def make_sequence(sequence):
    """Given a sequence with the number of NR, create a sequence indicating
    whether a token goes left or right (e.g. 21212121)."""

    text_sequence = ''
    counter = 0

    for i, x in enumerate(sequence):

        NC = len(sequence) - (i+1)
        NL = len(sequence) - (NC+x)

        if i is 0 and x is 1:
            text_sequence += '2'
        elif i is 0 and x is not 1:
            text_sequence += '1'

        if i>0:
            if sequence[i-1]+1 == x:
                text_sequence += '2'
            elif sequence[i-1] == x:
                text_sequence += '1'

    return text_sequence


#----------


# sequence for example (almost all tokens go to right, so P(R) increases steadily)
sequence = '222221211222212'  #sequence of tokens, going left (1) or right (2)
num_tokens = 15  #total number of tokens

#example
template = [(.6, 1),  (), (.7, 1), (), (.8, 1), (), (), (), (), (.8, 1), (), (), (.9, 1), (), ()]  # all >=
# ambi = [],  .5, .55-0.65, .5, .55-0.65, .5, .55-0.65, .5, <.6, >.5, .65, >.5, .75, [], []  # 

# i    =  1,    2,    3,  4,  5,  6,  7,  8,  9,   10, 11, 12, 13,  14, 15
# misl = [],  <.3,  <.4, <.5, [], [], [], [], [], >.5, [], [], [], .75, [], []  # 


extended_template = get_extended_template(template, new_length=num_tokens)
ranges = get_ranges(extended_template)
print(ranges)
# adjusted_ranges = adjust_min_max(ranges)
# print(adjusted_ranges)

filled_ranges = fill_in(ranges)
print(filled_ranges)

comp = make_NR_sequence(filled_ranges)
print(comp)

text = make_sequence(comp)
print(text)


#TODO:
# FIll-in sequences