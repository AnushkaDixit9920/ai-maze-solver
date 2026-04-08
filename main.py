import pygame
import random
from queue import PriorityQueue, Queue

pygame.init()

WIDTH = 600
HEIGHT = 700
ROWS = 20

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Maze Solver")

FONT = pygame.font.SysFont("Arial", 18)

WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
LIGHT_GREY = (230, 230, 230)

gap = WIDTH // ROWS

grid = [[WHITE for _ in range(ROWS)] for _ in range(ROWS)]

start = None
end = None

astar_count = 0
bfs_count = 0
path_length = 0


# ---------------- BUTTON CLASS ----------------
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        pygame.draw.rect(WIN, LIGHT_GREY, self.rect)
        pygame.draw.rect(WIN, BLACK, self.rect, 2)
        txt = FONT.render(self.text, True, BLACK)
        WIN.blit(txt, (self.rect.x + 10, self.rect.y + 10))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# Buttons
btn_astar = Button(10, 620, 120, 40, "Run A*")
btn_bfs = Button(140, 620, 120, 40, "Run BFS")
btn_reset = Button(270, 620, 120, 40, "Reset")
btn_maze = Button(400, 620, 180, 40, "Generate Maze")


def draw_grid():
    for i in range(ROWS):
        pygame.draw.line(WIN, GREY, (0, i * gap), (WIDTH, i * gap))
        pygame.draw.line(WIN, GREY, (i * gap, 0), (i * gap, WIDTH))


def draw_stats():
    text = f"A*: {astar_count}   BFS: {bfs_count}   Path: {path_length}"

    if bfs_count > 0:
        eff = ((bfs_count - astar_count) / bfs_count) * 100
        text += f"   Efficiency: {eff:.1f}%"

    render = FONT.render(text, True, BLACK)
    WIN.blit(render, (10, 580))


def draw():
    WIN.fill(WHITE)

    for i in range(ROWS):
        for j in range(ROWS):
            pygame.draw.rect(WIN, grid[i][j], (j * gap, i * gap, gap, gap))

    draw_grid()
    draw_stats()

    btn_astar.draw()
    btn_bfs.draw()
    btn_reset.draw()
    btn_maze.draw()

    pygame.display.update()


def get_clicked_pos(pos):
    x, y = pos
    return y // gap, x // gap


def get_neighbors(pos):
    row, col = pos
    neighbors = []

    if row < ROWS - 1 and grid[row + 1][col] != BLACK:
        neighbors.append((row + 1, col))
    if row > 0 and grid[row - 1][col] != BLACK:
        neighbors.append((row - 1, col))
    if col < ROWS - 1 and grid[row][col + 1] != BLACK:
        neighbors.append((row, col + 1))
    if col > 0 and grid[row][col - 1] != BLACK:
        neighbors.append((row, col - 1))

    return neighbors


def h(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


# 🔥 GUARANTEED SOLVABLE MAZE
def generate_maze():
    global grid, start, end
    grid = [[WHITE for _ in range(ROWS)] for _ in range(ROWS)]

    start = (random.randint(0, ROWS - 1), random.randint(0, ROWS - 1))
    end = (random.randint(0, ROWS - 1), random.randint(0, ROWS - 1))

    while end == start:
        end = (random.randint(0, ROWS - 1), random.randint(0, ROWS - 1))

    path = []
    current = start

    while current != end:
        path.append(current)
        row, col = current

        directions = []
        if row < end[0]: directions.append((row + 1, col))
        if row > end[0]: directions.append((row - 1, col))
        if col < end[1]: directions.append((row, col + 1))
        if col > end[1]: directions.append((row, col - 1))

        current = random.choice(directions)

    path.append(end)

    for i in range(ROWS):
        for j in range(ROWS):
            if (i, j) not in path:
                if random.random() < 0.3:
                    grid[i][j] = BLACK

    grid[start[0]][start[1]] = GREEN
    grid[end[0]][end[1]] = RED


def astar(draw, start, end):
    global astar_count, path_length
    astar_count = 0
    path_length = 0

    open_set = PriorityQueue()
    open_set.put((0, 0, start))

    came_from = {}
    g_score = {(i, j): float("inf") for i in range(ROWS) for j in range(ROWS)}
    g_score[start] = 0

    f_score = {(i, j): float("inf") for i in range(ROWS) for j in range(ROWS)}
    f_score[start] = h(start, end)

    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)
        astar_count += 1

        if current == end:
            while current in came_from:
                current = came_from[current]
                path_length += 1

                if current != start:
                    grid[current[0]][current[1]] = PURPLE
                draw()
            return True

        for neighbor in get_neighbors(current):
            temp_g = g_score[current] + 1

            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                f_score[neighbor] = temp_g + h(neighbor, end)

                if neighbor not in open_set_hash:
                    open_set.put((f_score[neighbor], 0, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end:
                        grid[neighbor[0]][neighbor[1]] = BLUE

        draw()
        if current != start:
            grid[current[0]][current[1]] = GREY

    return False


def bfs(draw, start, end):
    global bfs_count, path_length
    bfs_count = 0
    path_length = 0

    queue = Queue()
    queue.put(start)

    came_from = {}
    visited = {start}

    while not queue.empty():
        current = queue.get()
        bfs_count += 1

        if current == end:
            while current in came_from:
                current = came_from[current]
                path_length += 1

                if current != start:
                    grid[current[0]][current[1]] = YELLOW
                draw()
            return True

        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.put(neighbor)
                if neighbor != end:
                    grid[neighbor[0]][neighbor[1]] = BLUE

        draw()
        if current != start:
            grid[current[0]][current[1]] = GREY

    return False


run = True
while run:
    draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if btn_astar.clicked(pos) and start and end:
                astar(draw, start, end)

            elif btn_bfs.clicked(pos) and start and end:
                bfs(draw, start, end)

            elif btn_reset.clicked(pos):
                start = None
                end = None
                path_length = 0
                grid = [[WHITE for _ in range(ROWS)] for _ in range(ROWS)]

            elif btn_maze.clicked(pos):
                path_length = 0
                generate_maze()

            elif pos[1] < WIDTH:
                row, col = get_clicked_pos(pos)

                if not start:
                    start = (row, col)
                    grid[row][col] = GREEN

                elif not end:
                    end = (row, col)
                    grid[row][col] = RED

                else:
                    if (row, col) != start and (row, col) != end:
                        grid[row][col] = BLACK

pygame.quit()