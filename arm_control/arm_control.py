
curr_x = 0
curr_y = 0

# Main method
def start_drawing(instructions):

    # Initialize robot arm stuffs
    curr_x = 0
    curr_y = 0
    
    # Process lines in each instruction
    print "Number of instructions received:", len(instructions)
    for line in instructions:
        draw_line(line)
        pass
        
    # pen-up when done
    pass
    
    
def draw_line(line):
    #print 'Drawing line with color:', line.color, '\tStart:', line.points[0], '\tEnd:', line.points[-1]
    # pen-up and select correct color
    
    # move to starting point
    move_to(line.points[0])
    
    # pen-down
    
    # Move pen to coordinate of the line in sequence
    for point in line.points:
        move_to(point)
    
    # pen-up
    
    pass
    
    
def move_to(coordinate):
    x = coordinate[0]
    y = coordinate[1]
    
    # Skip if already on point
    if x == curr_x and y == curr_y:
        return
    
    # Run maths to decide how to move each motors
    pass