import pygame
import random
import tkinter as tk
from tkinter import *
from tkinter import messagebox


#########################################
## Constants
#########################################

# Define colors by RGB color code
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
PURPLE = (128,0,128)

# This sets the wdith of the screeen and number of rows and columns in the grid
WIDTH = 800
WINDOW_SIZE = [WIDTH, WIDTH]
ROWS = 50       # This is both the number of rows and columns

# This sets the margin between each cell
MARGIN = 2

# Side length of grid square
LENGTH = (WIDTH - ROWS*MARGIN) // ROWS

# Percent of grid spaces to make obstacles when randomly generating terrain (choose number 0-1)
PERCENT = 0.3

# Tkinter window
ROOT = Tk()


#########################################
## Helper Functions
#########################################

def drawGrid(grid):
    '''
    This function takes a 2D list of nodes and draws the grid in pygame

    '''

    # Set the screen background
    screen.fill(BLACK)

    # Draw the grid
    for row in range(ROWS):
        for column in range(ROWS):
            # 
            color = grid[row][column].color
            pygame.draw.rect(screen,
                             color,
                             [(MARGIN + LENGTH) * column + MARGIN,
                              (MARGIN + LENGTH) * row + MARGIN,
                              LENGTH,
                              LENGTH])

        # Limit to 60 frames per second
    clock.tick(60)
 
    # Update the screen with what we've drawn.
    pygame.display.flip()

def getSuccessors(node):
    '''
    This function takes a node and returns its possible successors (surrounding 8 nodes)
    '''

    rows = [node.x,node.x-1,node.x+1]
    cols = [node.y,node.y-1,node.y+1]
    
    successors = []
    for i in rows:
        if i >= 0 and i < ROWS:
            for j in cols:
                if j>= 0 and j < ROWS:
                    successor = grid[i][j]
                    if not successor.obstacle:
                        successors.append(successor)

    return successors 

def updateColors(open,closed,end_path):
    '''
    This function takes the open list, closed list, and final node of the proposed optimal path and colors the 
    nodes accordingly.

    Variables: 
    open - A* algorithm open list
    closed - A* algorithm closed list
    end_path - Newest node to be evaluated/added to the path

    Colors:
    Green - Belongs to the open list
    Red - Belongs to the closed list
    Purple - Part of the proposed optimal path

    '''

    # Color nodes in open list 
    for node in open_list:
        if node == start or node == end:
            continue
        node.color = GREEN
        node.open = True

    # Color nodes in closed list
    for node in closed_list:
        if node == start or node == end:
            continue
        node.color = RED
        node.closed = True

    # Color/display current proposed optimal path
    while end_path.path != False:
        end_path.color = PURPLE
        end_path = end_path.path

def nodeDist(node1,node2):
    '''
    This function calculates the euclidian distance between two nodes
    '''

    dist = ((node1.x-node2.x)**2 + (node1.y-node2.y)**2)**.5
    return dist

#########################################
##  Setup Node Class
#########################################

class Node:
    '''
    This is the node class, which contains useful information about each node in the map/grid
    '''

    def __init__(self,x,y):

        # Positional information
        self.x = x
        self.y = y

        # Cost information
        self.g = 0
        self.h = 0
        self.f = 0

        # Is this the start/finish?
        self.start = False
        self.end = False

        # Color of Node
        self.color = WHITE

        # Is an obstacle?
        self.obstacle = False

        # In the closed/open list or path
        self.open  = False
        self.closed = False
        self.path = False

#########################################
## Visualization Setup
#########################################

# User input to specify random or manual setup

# Create interface
Label(ROOT,text="Would you like to build the grid randomly or manually:").grid(row=0, sticky=W)
randomly = IntVar()
Checkbutton(ROOT, text="Randomly", variable=randomly).grid(row=1, sticky=W)
manually = IntVar()
Checkbutton(ROOT, text="Manually", variable=manually).grid(row=2, sticky=W)

Button(ROOT, text='Okay', command=ROOT.quit).grid(row=3, sticky=W, pady=4)
mainloop()

# Assign setup variable based on user input
setup = ''
if manually.get() < randomly.get():
    setup = 'R'
else:
    setup = 'M'

# Create a 2 dimensional array for the grid containing all of the nodes
grid = []
for row in range(ROWS):
    grid.append([])
    for column in range(ROWS):
        # Create a node for that position in the grid
        newNode = Node(row,column)
        # Make random obstacles 
        if PERCENT > random.random() and setup == 'R':
            newNode.obstacle = True
            newNode.color = BLACK
        grid[row].append(newNode)  # Append the node
 

# Provide User Instructions
ROOT.withdraw()
instructions = ''
if setup == 'M':
    instructions = ("Left click to add a start and then an end. Once start and end points "
                    "have been specfied, left click to add obstacles. Right click to remove"
                    " start, end, or obstacles. Press spacebar to run algorithm")
elif setup == 'R':
    instructions = ("Left click to add a start and then an end. Right click to remove"
                    " start or end points. Press spacebar to run the algorithm")

messagebox.showinfo("Instructions",instructions)

# Initialize pygame
pygame.init()
 
# Set the size of the screen
screen = pygame.display.set_mode(WINDOW_SIZE)
 
# Set title of screen
pygame.display.set_caption("A* Pathfinding Algorithm")
 
# Define visualization variables
done = False        # Algorithm in process if False
start = False       # Start position has been chosen
end = False         # End position has been chosen
Started = False     # Has algorithm started?
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()


#########################################
## Main Program Loop
#########################################

# Initialize the A* open list
open_list = []

# Initialize the A* closed list
closed_list = []

while not done:

    # -------------- Setup the Map -------------- 

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

        # If user presses the spacebar, the algorithm starts.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and start != False and end != False:
                Started = True
        if Started:
            break

        # User grid component setup/creation
        if pygame.mouse.get_pressed()[0]:
            # User clicks the mouse. Get the position
            pos = pygame.mouse.get_pos()
            # Change the x/y screen coordinates to grid coordinates
            column = pos[0] // (LENGTH + MARGIN)
            row = pos[1] // (LENGTH + MARGIN)
            node = grid[row][column]

            # Create start node and add to open list
            if start == False and node.end == False and node.obstacle == False:
                node.color = BLUE
                node.start = True
                start = node
                start.open = True
                open_list.append(start)
            
            # Create end node
            elif end == False and node.start == False and node.obstacle == False:
                node.color = PURPLE
                node.end = True
                end = node
            
            # Create obstacle nodes
            elif node.start == False and node.end == False and setup == 'M':
                node.color = BLACK
                node.obstacle = True

        # User grid component removal/modificatoin
        elif pygame.mouse.get_pressed()[2]:
            # User clicks the mouse. Get the position
            pos = pygame.mouse.get_pos()
            # Change the x/y screen coordinates to grid coordinates
            column = pos[0] // (LENGTH + MARGIN)
            row = pos[1] // (LENGTH + MARGIN)
            node = grid[row][column]

            # Remove start node and remove from open list
            if node.start == True:
                node.color = WHITE
                node.start = False
                start = False
                open_list = []
            
            # Remove end node
            elif node.end == True:
                node.color = WHITE
                node.end = False
                end = False
            
            # Remove barrier nodes
            elif node.obstacle == True:
                node.color = WHITE
                node.obstacle = False

    # -------------- A* Algorithm -------------- 

    if Started:

        # Quit if open list is empty
        if not open_list:
            print('No Path Found!')
            continue
        
        # Find the node with the lowest f-value in the open list, current_node
        current_node = open_list[0]
        for node in open_list:
            if node.f < current_node.f:
                current_node = node
    
        # If current_node is the destination, then we are done.
        if current_node == end:
            continue

        # Remove current_node from the open_list 
        open_list.remove(current_node)

        # Add current_node to closed list
        closed_list.append(current_node)

        # Get successors of current node, successors are the next nodes to be checked
        successors = getSuccessors(current_node)

        # Evaluate successor nodes
        for next_node in successors:
            # If already evaluated completely (in closed list) skip the node
            if next_node in closed_list:
                continue
            
            # Calculate g score for this node on this current path
            tempG = current_node.g + nodeDist(current_node,next_node)

            # If node is new, add it to the open list. If the node is note new but is already part
            # of a better path, skip the node.
            if next_node not in open_list:
                open_list.append(next_node)
            elif tempG >= next_node.g:
                continue

            # The node is either new or can create a shorter path, so we add it to the path and 
            # update its cost
            next_node.path = current_node
            next_node.g = tempG
            next_node.h = nodeDist(next_node,end)
            next_node.f = next_node.g + next_node.h

            updateColors(open_list,closed_list,current_node)

    # Draw the grid
    drawGrid(grid)
 

# End the pygame instance
pygame.quit()