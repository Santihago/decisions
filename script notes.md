# Script notes

First goal: scatter n tokens pseudo-randomly inside a bigger circle

## 1. Make a grid using ElementArrayStim

I ultimately want to place tokens inside a circle, but I will start by drawing 
tokens using a **square grid** using PsychoPy's ELementArrayStim option. I will
later remove the tokens from the grid that fall outside the circle line.

### 1.1 Defining the target n of tokens

```python
#set the number of desired tokens inside the main circle
wanted_tokens = 20
```

### 1.2 Finding the grid size

To obtain the desired number of tokens, the formula from a perfect square grid
comes from `wanted_tokens = m x m`.

```python
# now set the grid parameters to approximate the wanted number of tokens
# this will adjust the number of grid lines and therefore the token size. 
# it will provide a grid that overshoot the `wanted_tokens` number slightly
# (those extra tokens can be remove later)
alt_grid_side = ceil(sqrt(wanted_tokens))
```

### 1.3 Increase the grid size

This step doubles the number of grid lines (that will be removed) to allow
for space between tokens.
We first **double** the grid size:

```python
grid_side = alt_grid_side*2
```

Later, I will remove tokens from the square that fellow outside of the circle
borders. The circle diameter is the same length as the square. To account for
the tokens that will be removed, I multiply the `grid_side` value by a constant,
1.3. I checked that it works by providing a final number of tokens above the
`wanted_tokens` in most cases.

### 1.4 Grid position

I also set where the grid is positioned on the screen (center).

```python
#set where the grid is positioned
location = [0, 0]
loc = np.array(location) + np.array(token_size) // 2
```

## 2. Create trial-specific scattered tokens

I create an array `xys` of coordinates `xys` = [(`x_pos`,`y_pos`),  ...]
I loop though each alternate line and column and set the location.
I add jitter: maximum jitter is the size of removed alternate lines, so there
is no overlap between tokens.

Also removes out of circle tokens using Pythagora's formula with each `x_pos`.

```python
# SETTING UP COORDINATES FOR EACH TOKEN
    #array of coordinates
    xys = []
    #set lower and higher token id on each side
    low, high = side_tokens // -2, side_tokens // 2
    #populate xys
    for y in range(low, high, 2):  # by steps of 2 to remove alternate lines
        for x in range(low, high, 2):
            x_pos = token_size[0] * x
            y_pos = token_size[1] * y
            # ADD JITTER
            x_pos = x_pos + np.random.uniform(-token_size[0]/2, token_size[0]/2)
            y_pos = y_pos + np.random.uniform(-token_size[0]/2, token_size[1]/2)
            # REMOVE OUT OF CIRCLE ELEMENTS
            #for a given x_pos, we find a max y_pos that remains within the circle using Pythagora's theorem
            try: max_y_pos = sqrt((circle_radius-(token_size[0]))**2 - x_pos**2)
            except: max_y_pos = 0
            if (y_pos+loc[0]) > max_y_pos or (y_pos+loc[0]) < -max_y_pos : continue
            else: xys.append((x_pos, y_pos))
```
