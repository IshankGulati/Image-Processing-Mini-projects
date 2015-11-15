import cv2
import numpy as np
import heapq

# no of rows and columns in grid
rows = 10
columns = 10


def grid_map(img):
    # create a 2d array
    grid = np.zeros((rows, columns))
    for i in range(rows):
        for j in range(columns):
            # white blocks
            if (np.array_equal(img[20+(i*40), 20+(j*40)], [255, 255, 255])):
                grid[i][j] = 0
            # start -> orange block
            elif (np.array_equal(img[20+(i*40), 20+(j*40)], [39, 127, 255])):
                grid[i][j] = 2
            # end -> pink block
            elif (np.array_equal(img[20+(i*40), 20+(j*40)], [201, 174, 255])):
                grid[i][j] = 3
            # obstacles ->black blocks
            else:
                grid[i][j] = 1
    return grid


class Cell(object):
    def __init__(self, x, y, reachable):
        # setting some parameters for each cell
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.cost = 0
        self.heuristic = 0
        # net_cost=cost+heuristic
        self.net_cost = 0


class Astar(object):
    def __init__(self):
        # list of unchecked neighbour cells
        self.open = []
        # keeps cells with lowest total_cost at top
        heapq.heapify(self.open)
        # list of already checked cells
        self.closed = set()
        # list of neighbour cells
        self.cells = []

    def init_grid(self, grid):
        for i in range(rows):
            for j in range(columns):
                # detecting the obstacles
                if grid[i][j] == 1:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(i, j, reachable))
                # detecting the start and end
                if(grid[i][j] == 2):
                    self.start = self.cell(i, j)
                if(grid[i][j] == 3):
                    self.end = self.cell(i, j)

    def cell(self, x, y):
        # returns the location to identify each cell
        return self.cells[x*columns+y]

    def cell_heuristic(self, cell):
        # returns the heuristic for astar algo
        return abs(cell.x-self.end.x)+abs(cell.y-self.end.y)

    def neighbour(self, cell):
        cells = []
        # returns a list of neigbours of a cell
        if cell.x < columns - 1:
            cells.append(self.cell(cell.x+1, cell.y))
        if cell.x > 0:
            cells.append(self.cell(cell.x-1, cell.y))
        if cell.y < rows-1:
            cells.append(self.cell(cell.x, cell.y+1))
        if cell.y > 0:
            cells.append(self.cell(cell.x, cell.y-1))
        return cells

    def update_cell(self, adj, cell):
        # update the details about the selected neigbour cell
        adj.cost = cell.cost + 1
        adj.heuristic = self.cell_heuristic(adj)
        adj.parent = cell
        adj.net_cost = adj.cost + adj.heuristic

    def display_path(self):
        # list for storing the path
        route_path = []
        # flag to determine length of path
        count = 0
        cell = self.end
        while cell.parent is not None:
            # storing the parents in list from end to start
            route_path.append([(cell.y)+1, (cell.x)+1])
            cell = cell.parent
            count += 1
        return route_path, count

    def search(self):
        # pushing the first element in open queue
        heapq.heappush(self.open, (self.start.net_cost, self.start))
        while(len(self.open)):
            net_cost, cell = heapq.heappop(self.open)
            # adding the checked cell to closed list
            self.closed.add(cell)
            if cell is self.end:
                # store path and path legth
                route_path, route_length = self.display_path()
                route_path.reverse()
                break
            # getting the adjoint cells
            neighbours = self.neighbour(cell)
            for path in neighbours:
                # if cell is not an obstacle and has not been already checked
                if path.reachable and path not in self.closed:
                    if (path.net_cost, path) in self.open:
                        # selecting the cell with least cost
                        if path.cost > cell.cost + 1:
                            self.update_cell(path, cell)
                    else:
                        self.update_cell(path, cell)
                        heapq.heappush(self.open, (path.net_cost, path))
        return route_path, route_length


def play(img):
    # map the grid in an array
    grid = grid_map(img)

    # executing A*
    solution = Astar()
    solution.init_grid(grid)
    route_path, route_length = solution.search()

    return route_length, route_path


if __name__ == "__main__":
    # code for checking output for single image
    img = cv2.imread('SampleImages/test_image1.png')
    route_length, route_path = play(img)
    print "OUTPUT FOR SINGLE IMAGE (IMAGE 1)..."
    print "route length = ", route_length
    print "route path   = ", route_path
    # code for checking output for all images
    route_length_list = []
    route_path_list = []
    for file_number in range(1, 6):
        file_name = "SampleImages/test_image"+str(file_number)+".png"
        pic = cv2.imread(file_name)
        route_length, route_path = play(pic)
        route_length_list.append(route_length)
        route_path_list.append(route_path)
    print "OUTPUT FOR ALL IMAGES..."
    for i in range(5):
        print "route length for image ", i+1, " = ", route_length_list[i]
        print "route path for image ", i+1, " = ", route_path_list[i]
