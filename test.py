import heapq
import numpy as np
from math import sqrt

# Define the matrix dimensions and the starting and target points
MATRIX_SIZE = 10
START = (2, 5)
TARGET = (8, 8)

# Define a helper function to calculate the Manhattan distance between two points
def distance(x1, y1, x2, y2):
    dist = sqrt(pow(abs(x1 - x2), 2) + pow(abs(y1 - y2), 2))
    formatted_dist = round(dist, 2)
    return formatted_dist

def manhattan(x1, y1, x2, y2):
    return abs(x1-x2)+abs(y1 - y2)

# Initialize the matrix with zeros
matrix = np.zeros((MATRIX_SIZE, MATRIX_SIZE))

# Mark the starting point with a value of 1
matrix[START] = 1

# Define the A* expansion boundary
boundary = set()

# Define the A* algorithm function
def a_star(matrix, start, target):
    heap = [(0, start)]  # Start with the starting point in the heap
    visited = set()  # Keep track of visited nodes
    step = 1  # Initialize the step counter
    while heap:
        (f, (x, y)) = heapq.heappop(heap)
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if (x, y) == target:  # If we have reached the target point, return the step value and the boundary
            boundary.add((x, y))
            return g, boundary
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # Explore north, south, east, west neighbors
            nx, ny = x + dx, y + dy
            if nx >= 0 and nx < MATRIX_SIZE and ny >= 0 and ny < MATRIX_SIZE:  # Check if neighbor is within matrix bounds
                if matrix[nx, ny] == 0:  # Check if neighbor has not been visited
                    boundary.add((nx, ny))
                    g = manhattan(nx, ny, start[0], start[1])  # Assign the step value to the neighbor
                    h = distance(nx, ny, target[0], target[1])  # Calculate the heuristic distance to the target
                    heapq.heappush(heap, (g + h, (nx, ny)))  # Add the neighbor to the heap with the total distance
                    matrix[nx, ny] = g  # Mark the neighbor with the step value
        step += 1  # Increment the step counter
    return None

# Run the A* algorithm from the starting point to the target point
step, boundary = a_star(matrix, START, TARGET)

# Expand from the A* boundary to the rest of the matrix
while boundary:
    x, y = boundary.pop()
    value = matrix[x, y]
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # Explore north, south, east, west neighbors
        nx, ny = x + dx, y + dy
        if nx >= 0 and nx < MATRIX_SIZE and ny >= 0 and ny < MATRIX_SIZE:  # Check if neighbor is within matrix bounds
            if matrix[nx, ny] == 0:  # Check if neighbor has not been visited
                matrix[nx, ny] = value + 1  # Mark the neighbor with the updated value
                boundary.add((nx, ny))  # Add the neighbor to the boundary for further exploration

# Print the resulting matrix
print(matrix)