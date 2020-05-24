from math import floor, factorial
import random

#TODO: in get_NL round the p? so that 0.49999999 is not rejected as not being 0.5

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

    print('New function use.')

    # Loop for different values of NL to find those that work
    for possible_NL in range(num_tokens):

        p_r = get_prob(NC, possible_NL, num_tokens)

        print('P:' + str(p_r))

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


def make_sequence(sequence, format='letter'):
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

    if format=='letter':
        pass
    elif format=='digit':
        text_sequence = alpha_digit_switch(text_sequence)

    return text_sequence


def alpha_digit_switch(text_sequence):

    # Check if digits or letters
    if text_sequence.isdigit(): 
        switched_sequence = text_sequence.replace('1', 'l')
        switched_sequence = text_sequence.replace('2', 'r')
        new_format = 'letter'

    elif text_sequence.isalpha():
        switched_sequence  = text_sequence.replace('l', '1')
        switched_sequence  = text_sequence.replace('r', '2')
        new_format = 'digit'

    return reversed_sequence, new_format


def winning_side(text_sequence):

    if text_sequence.isdigit(): 
        code_left = '1'
        code_right = '2'
    elif text_sequence.isalpha():
        code_left = 'l'
        code_right = 'r'

    nr_left = token_sequence_str.count(code_left)
    winning_side = code_left if (nr_left > len(text_sequence)-nr_left) else code_right

    return winning_side

def replace_all(text_sequence, dic):
    for i, j in dic.iteritems():
        text_sequence = text_sequence.replace(i, j)
    return text_sequence

def left_right_switch(text_sequence):

    # Check if digits or letters
    if text_sequence.isdigit(): 
        codes = [ ['1', '1-'], ['2', '1'], ['1-', '2']]  # 3 steps with placeholder as a little hack

    elif text_sequence.isalpha():
        codes = [ ['l', 'l-'], ['r', 'l'], ['l-', 'r']]

    for x,y in (codes): 
        text_sequence = text_sequence.replace(x, y)

    return text_sequence 


def experiment_sequences(templates, num_tokens, nr_per_type, nr_random=0, 
    randomisation='random', format='letter'):

    #Input: dict with label and template

    # templates = {
    # 'e' : [(.6,1),  (), (.7,1), (), (.8,1), (), (), (), (), (.8,1), (), (), (.9,1), (), ()],
    # 'a' : [(),  (.5,1), (.55,.65), (.5,1), (.55,.65), (.5,1), (.55,.65), (.5,1), (0,.6), (.5,1), (.65,1), (.5,1), (.75,1), (), ()]
    # 'm' : [(),  (0,.3),  (0,.4), (0,.5), (), (), (), (), (), (.5,1), (), (), (), (.75,1), (), ()] 
    # }

    exp_sequences = []
    trial_keys = []

    for trial_type in templates:
        for i in range(nr_per_type):
            # Add key to list with all trials
            trial_keys += [trial_type]

    # Add random sequences
    if nr_random > 0:
        for i in range(nr_random):
            # Add (random) key to list with all trials
            trial_keys += random.sample(templates.keys(),1)

    
    # For the whole experiment, set 1/2 trials to Left-winning, and 1/2 to Right-winning
    nr_l = round(len(trial_keys)/ 2)
    nr_r = len(trial_keys) - nr_l
    exp_winning_side = random.sample(['l'] * nr_l + ['r'] * nr_r, len(trial_keys))

    # For each key:template transform into the corresponding sequence
    for i, x in enumerate(trial_keys):

        template = templates[x[0]]

        # 1. Extend if necessary
        extended_template = get_extended_template(template, new_length=num_tokens)
        # 2. From template calculate plausible ranges
        ranges = get_ranges(extended_template)
        # 3. Fill in empty information with what we know from ranges
        filled_ranges = fill_in(ranges)
        # 4. Create a sequences of right tokens
        nr_sequence = make_NR_sequence(filled_ranges)
        # 5. Create a text sequence in the format expected
        final_sequence = make_sequence(nr_sequence, format=format)
        # 6. Change to winning side

        # By default all sequences are made with 2 or 'r' winning.
        #If 'r', no change. If 'l', use function to invert.
        if exp_winning_side[i] == 'l':
            final_sequence = left_right_switch(final_sequence)

        # 7. Add to an experimental structure

        exp_sequences += [{'trial_type'     : x,
                           'token_sequence' : final_sequence, 
                           'winning_side'   : exp_winning_side[i]}]

    # Re-order according to need
    if randomisation == 'random':
        exp_sequences[:] = random.sample(exp_sequences, len(exp_sequences))

    return exp_sequences
#---------
num_tokens = 15
nr_per_type = 3
nr_random = 3
templates = {
    'e' : [(.6,1),  (), (.7,1), (), (.8,1), (), (), (), (), (.8,1), (), (), (.9,1), (), ()],
    'a' : [(),  (.49,.51), (.55,.65), (.49,.51), (.55,.65), (.49,.51), (.55,.65), (.49,.51), (0,.66), (.49,1), (.65,1), (.49,1), (.75,1), (), ()],
    'm' : [(),  (0,.3),  (0,.4), (0,.5), (), (), (), (), (), (.5,1), (), (), (), (.75,1), (), ()] 
    }

exp_sequences = experiment_sequences(templates, num_tokens=num_tokens, 
    nr_per_type=nr_per_type, nr_random=nr_random, randomisation='random', 
    format='letter')

print(exp_sequences)