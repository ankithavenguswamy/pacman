# To start the game, click "Play" or "Run"
import random


SPEED = 2
GHOST_SPEED = 1
TITLE = 'Pac-Man'
WORLD_SIZE = 20
BLOCK_SIZE = 32
WIDTH = WORLD_SIZE*BLOCK_SIZE
HEIGHT = WORLD_SIZE*BLOCK_SIZE

#Our sprites
pacman = Actor('pacman_o.png')
pacman.food_left = None #variable for pacman object saying whether there is food left
pacman.x = pacman.y = 1.5*BLOCK_SIZE
pacman.banner = None #no initial words on screen
pacman.banner_counter = 0
pacman.score = 0
pacman.lives = 3 #pacman starts out with 3 lives
#Direction we are going in
pacman.dx, pacman.dy = 0,0
ghosts = []
ghost_start_pos = []

#this is a dictionary mapping characters to the images
char_to_image = {
    '.': 'dot.png',
    '=': 'wall.png',
    '*': 'power.png',
    'g': 'ghost1.png',
    'G': 'ghost2.png',
}

#An array containing the world tiles, non-trivial list
world = []

def load_level(number): #takes in a number dictating which level to open
    file = "level-%s.txt" % number
    pacman.food_left = 0
    with open(file) as f: #opens and reads board file
        for line in f:
            row = []
            for block in line:
                row.append(block) #adds each block to the row list
                if block == '.': pacman.food_left += 1 #counts up how many pellets of food are present, adds it to the food left variable
            world.append(row) #adds the list row into the list world

def set_random_dir(sprite, speed): #allows the sprite to randomly move backwards or forwards at a speed up to what we defined
    sprite.dx = random.choice([-speed, speed])
    sprite.dy = random.choice([-speed, speed])

def make_ghost_actors():
    for y, row in enumerate(world): #for each x and y position, if there is a 'g' or 'G', we create a ghost actor
        for x, block in enumerate(row):
            if block == 'g' or block == 'G':
                g = Actor(char_to_image[block], (x*BLOCK_SIZE, y*BLOCK_SIZE), anchor=('left', 'top')) #mapping the image of the ghost to the character
                g.dx = random.choice([-GHOST_SPEED,GHOST_SPEED]) #the ghost is allowed to move randomly at the ghost speed in both x and y directions
                g.dy = random.choice([-GHOST_SPEED,GHOST_SPEED])
                ghosts.append(g)
                ghost_start_pos.append((x,y)) #list that records x,y coordinates of each ghost
                world[y][x] = None #now that we have the ghost moving, we delete the block was in the world (otherwise there would be two ghosts -- one moving, and one standing still)


def draw(): #draws the world, pacman, and ghosts
    screen.clear()
    for y, row in enumerate(world): #iterates through the rows in the world
        for x, block in enumerate(row): #iterates through each block in the row, associating each block to the image
            image = char_to_image.get(block, None)
            if image:
                screen.blit(char_to_image[block], (x*BLOCK_SIZE, y*BLOCK_SIZE)) #draws the right image
    pacman.draw() #draws the pacman
    for g in ghosts: g.draw() #draws the ghost
    if pacman.banner and pacman.banner_counter > 0: #draws the banners for both score and lives in the corners of the game
        screen.draw.text(pacman.banner, center = (WIDTH/2, HEIGHT/2), fontsize = 120)
    screen.draw.text("Score: %s" % pacman.score, topleft=(8,4), fontsize = 40)
    screen.draw.text("Lives: %s" % pacman.lives, topright=(WIDTH-8,4), fontsize = 40)


def blocks_ahead_of(sprite, dx, dy): #Takes in position of sprite, returns a list of tiles at this position + (dx, dy)
    #What we want to move to, bit of rounding to get the exact pixel position
    x = int(round(sprite.left))+dx
    y = int(round(sprite.top))+dy
    #Find integer block pos, using floor
    ix,iy = int(x // BLOCK_SIZE), int(y // BLOCK_SIZE) #converts x,y to block position (using integers only)
    #Remainder lets us check adjacent blocks
    rx, ry = x % BLOCK_SIZE, y % BLOCK_SIZE
    #Keeps in bounds of world
    if ix == WORLD_SIZE-1: rx = 0
    if iy == WORLD_SIZE-1: ry = 0

    blocks = [world[iy][ix]] #checks blocks at world[iy][ix] and to the right, below, diagonally depending on remainders
    if rx: blocks.append(world[iy][ix+1])
    if ry: blocks.append(world[iy+1][ix])
    if rx and ry: blocks.append(world[iy+1][ix+1])

    return blocks #returns the blocks ahead of the sprite

def wrap_around(mini, val, maxi): #takes in a minimum and maximum value (edges of map), and position of sprite
    if val < mini: return maxi #if the sprite goes below the minimum, it will wrap around to the maximum side (and vice versa)
    elif val > maxi: return mini
    else: return val #if the sprite is within the map, it will stay there

def move_ahead(sprite):
    #Record current position so we can see if the sprite moved
    oldx, oldy = sprite.x, sprite.y
    #In order to go in direction dx, dy there must be no wall that way
    if '=' not in blocks_ahead_of(sprite, sprite.dx, 0):
        sprite.x += sprite.dx
    if '=' not in blocks_ahead_of(sprite, 0, sprite.dy):
        sprite.y += sprite.dy
    #Keep sprite on screen
    sprite.x = wrap_around(0, sprite.x, WIDTH-BLOCK_SIZE)
    sprite.y = wrap_around(0, sprite.y, HEIGHT-BLOCK_SIZE)

    #Return whether we moved
    moved = (oldx != sprite.x or oldy != sprite.y)

    #Costume change for pacman depending on if we turn a certain direction (will rotate pacman)
    if moved and sprite == pacman:
        a = 0
        if oldx < sprite.x: a = 0
        elif oldy > sprite.y: a = 90
        elif oldx > sprite.x: a = 180
        elif oldy < sprite.y: a = 270
        sprite.angle = a
    return moved

def eat_food(): #function that allows pacman to eat food
    ix,iy = int(pacman.x / BLOCK_SIZE), int(pacman.y / BLOCK_SIZE)
    if world[iy][ix] == '.':
        world[iy][ix] = None #when pacman moves over '.' block (aka food), it deletes the food there
        pacman.food_left -= 1 #decreases number in food left variable by 1
        print("Food left: ", pacman.food_left) #prints how much food is left
        pacman.score += 1 #increases the pacman score by 1 for eating the food

def reset_sprites():
    pacman.x = pacman.y = 1.5*BLOCK_SIZE
    #Move ghosts back to their start positions
    for g, (x, y) in zip(ghosts, ghost_start_pos):
        g.x = x * BLOCK_SIZE
        g.y = y * BLOCK_SIZE

def set_banner(message, count): #inputs are the message displayed and how long it will be displayer, output is the banners in the left and right corners of the screen
    pacman.banner = message
    pacman.banner_counter = count

def update(): #updates position using the function move_ahead, which verifies there is no wall that way
    move_ahead(pacman)
    eat_food()
    for g in ghosts:
        if not move_ahead(g): #if the ghost is unable to move ahead in that direction (i.e., there is a wall), it will turn in a random direction and continue moving
            set_random_dir(g, GHOST_SPEED)
        if g.colliderect(pacman): #if the ghost and pacman collide, it will...
            reset_sprites() #move the sprites back to starting position,
            set_banner('Ouch!', 5) #display an "Ouch!" banner
            pacman.lives -= 1 #pacman will lose one life
            reset_sprites()
            if pacman.lives == 0: #if the pacman has no more lives left, the game will be over
                quit()

def on_key_down(key): #takes in key pressed down, outputs movement in certain direction
    if key == keys.LEFT:
        pacman.dx = -1
    if key == keys.RIGHT:
        pacman.dx = 1
    if key == keys.UP:
        pacman.dy = -1
    if key == keys.DOWN:
        pacman.dy = 1

def on_key_up(key): #takes in release of key as input, outputs no movement in x and y direction
    if key in (keys.LEFT, keys.RIGHT):
        pacman.dx = 0
    if key in (keys.UP, keys.DOWN):

        pacman.dy = 0
def periodic(): #allows the banner to not remain on the screen indefinitely, will be called on to decrease the banner counter
    if pacman.banner_counter > 0:
        pacman.banner_counter -= 1
clock.schedule_interval(periodic, 0.2) #this makes it so that the "Ouch!" sign is on the screen for one second and not more than that


#Game set up
load_level(1)
make_ghost_actors()
for row in world: print(world)
