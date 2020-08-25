import pygame
import random
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox

#########################################
## Helper Functions
#########################################

def drawGrid():

    'This function draws the node grid'

    # Set the screen background
    screen.fill(BLACK)

    # Draw the grid
    for row in range(ROWS):
        for column in range(ROWS):
            color = grid[row][column].color
            pygame.draw.rect(screen,
                             color,
                             [(MARGIN + LENGTH) * column + MARGIN,
                              (MARGIN + LENGTH) * row + MARGIN,
                              LENGTH,
                              LENGTH])

        # Limit to 60 frames per second
    clock.tick(60)
 
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

def getSuccessors(node):

    'This function takes a node and returns its possible successors'

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

def nodeDist(node1,node2):

    'This function calculates the euclidian distance between two nodes'

    dist = ((node1.x-node2.x)**2 + (node1.y-node2.y)**2)**.5
    return dist

#########################################
##  Setup Node Class
#########################################

class Node:

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.f = 0
        self.start = False
        self.end = False
        self.color = WHITE
        self.obstacle = False
        self.open  = False
        self.closed = False
        self.path = False

#########################################
## Visualization Setup
#########################################

# Uer input to specify random or manual setup
ROOT = tk.Tk()
ROOT.withdraw()

setup = simpledialog.askstring(title="Grid Setup",
                                  prompt="Would you like to build the grid randomly or manually? [R/M]")


# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
PURPLE = (128,0,128)

# This sets the number of rows and columns in the grid
WIDTH = 800
ROWS = 50

# This sets the margin between each cell
MARGIN = 2

# Side length of grid square
LENGTH = (WIDTH - ROWS*MARGIN) // ROWS
 
# Create a 2 dimensional array for the grid.
grid = []
for row in range(ROWS):
    grid.append([])
    for column in range(ROWS):
        newNode = Node(row,column)
        if 0.3 > random.random() and setup == 'R':
            newNode.obstacle = True
            newNode.color = BLACK
        grid[row].append(newNode)  # Append a node
 

# Provide User Instructions

if setup == 'M':
    messagebox.showinfo("Instructions", "Left click to add a start and then an end. Once start and end points "
                                    "have been specfied, left click to add obstacles. Right click to remove"
                                    " start, end, or obstacles. Press spacebar to run algorithm")
elif setup == 'R':
    messagebox.showinfo("Instructions", "Left click to add a start and then an end. Right click to remove"
                                    " start or end points. Press spacebar to run the algorithm")

# Initialize pygame
pygame.init()
 
# Set the size of the screen
WINDOW_SIZE = [WIDTH, WIDTH]
screen = pygame.display.set_mode(WINDOW_SIZE)
 
# Set title of screen
pygame.display.set_caption("A* Pathfinding Algorithm")
 
# Define visualization variables
done = False        # Algorithm in process if False
start = False       # Start position has been chosen
end = False         # End position has been chosen
Started = False     # Has algorithm
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()


#########################################
## A* Algorithm Setup
#########################################

# Initialize the open list
open_list = []

# Initialize the closed list
closed_list = []
 
#########################################
## Main Program Loop
#########################################

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
            continue

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

    if Started == True:

        # Quit if open list is empty
        if not open_list:
            done = True
            print('No Path Found!')
        
        # Find the node with the lowest f-value in the open list, q
        q = open_list[0]
        for i in open_list:
            if i.f < q.f:
                q = i
    
        # If q is the destination, then we are done.
        if q == end:
            done = True

        # Remove q from the open_list 
        open_list.remove(q)

        # Add q to closed list
        closed_list.append(q)

        # Get successors of node q, successors are the next nodes to be checked
        successors = getSuccessors(q)

        # Evaluate successor nodes
        for i in successors:
            # If already evaluated completely (in closed list) skip the node
            if i in closed_list:
                continue
            
            # Calculate g score for this node on this current path
            tempG = q.g + nodeDist(q,i)

            # If node is new, add it to the open list. If the node is note new but is already part
            # of a better path, skip the node.
            if i not in open_list:
                open_list.append(i)
            elif tempG >= i.g:
                continue

            # The node is either new or can create a shorter path, so we add it to the path and 
            # update its cost
            i.path = q
            i.g = tempG
            i.h = nodeDist(i,end)
            i.f = i.g + i.h

           
        # Color nodes in open list 
        for i in open_list:
            if i == start or i == end:
                continue
            i.color = GREEN
            i.open = True

        # Color nodes in closed list
        for i in closed_list:
            if i == start or i == end:
                continue
            i.color = RED
            i.closed = True

        # Color/display current proposed optimal path
        while q.path != False:
            q.color = PURPLE
            q = q.path


    # Draw the grid
    drawGrid()
 

# This is my weak way to keep the final path displayed until the user closes the window
finished = False   
while not finished:

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            finished = True  # Flag that we are done so we exit this loop

# End the pygame instance
pygame.quit()