import random
from math import floor, factorial


def letters_or_digits(s):
    return 'letters' if s.isalpha() else 'digits'


def get_quantities(sequence, length = None, stop = None):
    """
    Function for calculating NC, NR, and NL from a given sequence.
    :param str sequence: sequence of left-right movements
    :param int length: the full length of the sequence (optional, default is len(sequence))
    :param int length: moment of the sequence where qtes are taken (optional, default is at the end)
    """
    # Check if sequence entered correctly
    try: isinstance(sequence, str)
    except AssertionError: print("The sequence should be in `string` format.")

    if stop is not None:
        try: length is not None
        except AssertionError:
            print("If an optional `stop` is provided, the full sequence `length` is required.")

    if length is None: length = len(sequence)
    if stop is None: stop = len(sequence)

    NC = length - stop  # Number of tokens remaining is equal to total number - stop TODO: stop+1?
    if letters_or_digits(sequence) == 'digits':
        NR = sequence.count('2')
    elif letters_or_digits(sequence) == 'letters': 
        NR = sequence.count('r')

    NL = length - (NC + NR)
    return NC, NR, NL


def get_prob(NC, NL, num_tokens):
    """Function for calculating the success probability of guessing right 
    (Cisek et al. 2009). Given a total number of tokens, the number of remaining 
    tokens in the center, moved tokens to the LEFT, calculate the probability 
    that RIGHT response is correct"""

    # First part of the formula
    first_part = factorial(NC)/(2**NC)
    # Summation part of the formula
    high_bound = min(NC, floor(num_tokens/2)-NL)  #the higher bound for the summation
    summation = sum([1/(factorial(k)*factorial(NC - k)) for k in range(0, high_bound+1)])
    # Probability that 'Right' response is correct given the sequence history
    p_r = round(first_part * summation, 2)
    return p_r


def get_prob_vector(sequence, num_tokens):
    """Function to calculate the p(r)) at each step of a given
    sequence."""

    probs = []
    # Calculate the success probability after each token movement
    for stop in range(0, len(sequence) + 1):
        # Take part of the sequence
        sequence_part = sequence[:stop]
        # Obtain the variables for the formula
        NC, NR, NL = get_quantities(sequence=sequence_part, length=num_tokens, stop=stop)
        # Formula
        p_r = get_prob(NC, NL, num_tokens)
        #print('center:' + str(NC) + ', right:' + str(NR) + ', left:' + str(NL) + ', P(R):' + str(round(P_R, 2)))
        probs += [p_r]
    return probs


def extend_template(template, t_type, new_length):
    """Function for extending the size of each template.
    :param list template: a list of  min_p_r, max_p_r tuples
    :param str t_type: the type of trial ('e', 'a' or 'm')
    :param int new_length: the new length of the template"""

    old_length = len(template)
    extended_template = [tuple()] * new_length  #output

    if t_type == 'e' or t_type == 'm' : 
        """Similar to an interpolation"""

        # Find pos of each filled item
        old_pos = [i for i,x in enumerate(template) if x is not tuple()]
        # Calculate normalized [0-1] position
        adj_pos = [old_pos / old_length for old_pos in old_pos]
        # New positions
        new_pos = [round(pos * new_length) for pos in adj_pos]

        for i in range(new_length):
            if i in new_pos:
                #find idx of i in new_pos (and old_pos)
                idx = new_pos.index(i)
                # that gives the pos
                pos = old_pos[idx]
                # we take value corresponding to pos
                extended_template[i] = template[pos]

        # Manually adjust some p values depending on num_tokens 
        # For instance in easy, first movement gives a p = get_prob(num_tokens-1,0,num_tokens)
        extended_template[0] = (get_prob(new_length-1, 0, new_length), 1)

    elif t_type == 'a': 
        #Ambiguous sequence. Hits p=0.5 in alternate trials for 2/3 of the trial.
        #Then it starts increasing to one side.

        flip_point_1 = round((new_length/3)*2) #find pos of 2/3 start
        flip_point_2 = round((new_length/6)*5) #find pos of 5/6 start
        # For the 1st part:
        for pos in range(0, flip_point_1):
            # if pos%2:  # Even
            NC = new_length-(pos+1)
            NL = floor((pos+1)/2)
            extended_template[pos] = (get_prob(NC, NL, new_length), 
                                        get_prob(NC, NL, new_length))
            # if not pos%2:  # Odd
            #     extended_template[pos] = (.5, .5)
        # For the 2nd part:
        #for pos in range(flip_point, new_length):
            # increase by the factor allowed by the n_tokens/p calculation
            # NC = new_length-(pos+1)
            # NL = floor((pos+1)/2)  # Min
        extended_template[flip_point_1] = (.5, 1)
        extended_template[flip_point_2] = (.75, 1)
        extended_template[new_length-1] = (1, 1)

    return extended_template


def get_NL(num_tokens, NC, prob_min, prob_max):
    """Returns which NL values provide a p(r) contained within a 
    p(r) range.
    :param int num_tokens: length of the sequence
    :param int NC: tokens remaining at the center
    :param float prob_min: minimum p(r)
    :param float prob_max: maximum p(r)
    """

    accepted_NL_values = []
    # Loop for different values of NL to find those that work
    for possible_NL in range(num_tokens):
        p_r = get_prob(NC, possible_NL, num_tokens)
       # print('p_r: ' + str(p_r) + ',  not higher than ' + str(prob_min) + ' and lower than ' + str(prob_max) +' : ' + str(p_r >= prob_min and p_r <= prob_max) )
        if p_r >= prob_min and p_r <= prob_max:
            accepted_NL_values += [possible_NL]
        else: 
            continue
    #count NLs to get valid range of min,max
    NL_min = min(accepted_NL_values)
    NL_max = max(accepted_NL_values)
    return NL_min, NL_max


def get_ranges(extended_template):
    """Function to translate the probability template into actual token 
    quantity ranges (of NR)"""

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
    print(ranges)
    return ranges


def look_right(start, list):
    """Function to find inside the list the nearest item on the right
    :param int start: leftmost value to start search
    :param list list: a list of NR_min,NR_max ranges"""

    for next_index in range(start, len(list)):
        if list[next_index] is tuple():
            continue
        else:
            right_min = list[next_index][0]
            right_max = list[next_index][1]
            break
    return next_index, right_min, right_max


def look_left(end, list):
    """Function to find inside the list the nearest item on the left
    :param int end: rightmost value to end search
    :param list list: a list of NR_min,NR_max ranges"""

    left_min = list[end-1][0]
    left_max = list[end-1][1]
    return left_min, left_max


def fill_in(ranges):
    """A function to fill empty tuples inbetween known ranges.
    :params list ranges: a list of empty and non-empty ranges/tuples
    
    1) A given minimum cannot be lower than a previous minimum.
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
                left_min, left_max = look_left(end=i, list=filled_ranges)
                found_left = True
            except: 
                pass
            try:
                next_index, right_min, right_max = look_right(start=i, list=ranges)
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
            elif not found_left and not found_right: 
                print('WARNING: The list of ranges is probably empty...')
           
            filled_ranges += [(new_min, new_max)]
    return filled_ranges


def make_NR_sequence(filled_ranges):
    """A function to create a sequence of NR values.
    :params filled_ranges list: list with ranges from fill_in()
    """
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


def switch_alpha_digit(text_sequence):
    """A function to invert letters and digits.
    :params str text_sequence: a left/right sequence in text format
    """
    # Check if digits or letters
    codes=[]
    if text_sequence.isdigit(): 
        codes = [['1', 'l'], ['2', 'r']]  # 3 steps with placeholder as a little hack
    elif text_sequence.isalpha():
        codes = [['l', '1'], ['r', '2']]
    for x,y in (codes): 
        switched_sequence = text_sequence.replace(x, y)
    return switched_sequence


def make_sequence(nr_sequence, format_to='letters'):
    """Given a sequence with the number of NR, create a sequence indicating
    whether a token goes left or right (e.g. lrrlrlrrl).
    :params str nr_sequence: a sequence of NR values
    :params str format_to: output the sequence as 'letters' (default) or 'digits'
    """

    text_sequence = ''
    counter = 0
    for i, x in enumerate(nr_sequence):
        NC = len(nr_sequence) - (i+1)
        NL = len(nr_sequence) - (NC+x)
        if i is 0 and x is 1:
            text_sequence += 'r'
        elif i is 0 and x is not 1:
            text_sequence += 'l'
        if i>0:
            if nr_sequence[i-1]+1 == x:
                text_sequence += 'r'
            elif nr_sequence[i-1] == x:
                text_sequence += 'l'
    # If asked for digit format, we convert to digit, otherwise do nothing
    if format_to=='letters':
        pass
    elif format_to=='digits':
        text_sequence = switch_alpha_digit(text_sequence)
    return text_sequence


def winning_side(text_sequence):
    """A function to determine the winning side of a sequence (left or right)
    :params str text_sequence: a sequence in text format (can be letters or digits)
    """

    if text_sequence.isdigit(): 
        code_left = '1'
        code_right = '2'
    elif text_sequence.isalpha():
        code_left = 'l'
        code_right = 'r'
    nr_left = token_sequence_str.count(code_left)
    winning_side = code_left if (nr_left > len(text_sequence)-nr_left) else code_right
    return winning_side


def left_right_switch(text_sequence):
    """A function to invert to make the right left and the left right.
    :params str text_sequence: a sequence in text, can be letters or digits
    """
    codes=[]
    # Check if digits or letters
    if text_sequence.isdigit(): 
        codes = [['1', '_'], ['2', '1'], ['_', '2']]  # 3 steps with placeholder as a little hack

    elif text_sequence.isalpha():
        codes = [['l', '_'], ['r', 'l'], ['_', 'r']]

    for x,y in (codes): 
        text_sequence = text_sequence.replace(x, y)

    return text_sequence 


def experiment_sequences(templates, num_tokens, nr_per_type, nr_random=0, 
    randomisation='random', format_to='letters'):
    """A function to create a trial list.

    :params dict templates: a dictionary with trial_type as key and the template (list of tuples) as value 
    :params int num_tokens: the number of tokens (the length of the sequence)
    :params int nr_per_type: number of repetitions of each template
    :params int nr_random: number of trials sampled randomly from the templates
    :params str randomisation: whether trials are shuffled ('random') or not 
    :params str format_to: 'letters' (default) or 'digits'
    """

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
        extended_template = extend_template(template, t_type=x[0], new_length=num_tokens)
        # 2. From template calculate plausible ranges
        ranges = get_ranges(extended_template)
        # 3. Fill in empty information with what we know from ranges
        filled_ranges = fill_in(ranges)
        # 4. Create a sequences of right tokens
        nr_sequence = make_NR_sequence(filled_ranges)
        # 5. Create a text sequence in the format expected
        text_sequence = make_sequence(nr_sequence, format_to=format)
        # 6. Change to winning side
        # By default all sequences are made with 2 or 'r' winning.
        #If 'r', no change. If 'l', use function to invert.
        if exp_winning_side[i] == 'l':
            text_sequence = left_right_switch(text_sequence)
        # 7. Add to an experimental structure
        exp_sequences += [{'trial_type'     : x,
                           'token_sequence' : text_sequence, 
                           'winning_side'   : exp_winning_side[i]}]

    # Re-order according to need
    if randomisation == 'random':
        exp_sequences[:] = random.sample(exp_sequences, len(exp_sequences))

    return exp_sequences