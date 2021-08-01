import time
import pygame
import os
import random
from numpy import *
import copy
import types
import weakref
from copyreg import dispatch_table

INITIAL_NUMBER_PROBABILITY = 0 #Difficulty
INDIVIDUAL_NUMBER_PROBABILITY = 50
POPULATION_SIZE = 200
GENERATION_LIMIT = 20000

pygame.font.init()

WIDTH, HEIGHT = 100, 100
THICK_LINE_WIDTH = 10
THIN_LINE_WIDTH = 2

WINDOW_WIDTH = WIDTH * 9 + THICK_LINE_WIDTH * 1 + THIN_LINE_WIDTH * 3
WINDOW_HEIGHT = HEIGHT * 9 + THICK_LINE_WIDTH * 1 + THIN_LINE_WIDTH * 3

WIN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

THIN_LINES = []
THICK_LINES = []
H_SPACE = 0
V_SPACE = 0

for i in range(9):
    if i % 3 == 2:
        THICK_LINES.append(pygame.Rect(0, HEIGHT - THICK_LINE_WIDTH / 2 + H_SPACE, WINDOW_WIDTH,
                                       THICK_LINE_WIDTH))  # Horizontal thick lines
        THICK_LINES.append(pygame.Rect(WIDTH - THICK_LINE_WIDTH / 2 + V_SPACE, 0, THICK_LINE_WIDTH,
                                       WINDOW_WIDTH))  # Vertical thick lines
    else:
        THIN_LINES.append(pygame.Rect(0, HEIGHT - THIN_LINE_WIDTH / 2 + H_SPACE, WINDOW_WIDTH,
                                      THIN_LINE_WIDTH))  # Horizontal thin lines
        THIN_LINES.append(
            pygame.Rect(WIDTH - THIN_LINE_WIDTH / 2 + V_SPACE, 0, THIN_LINE_WIDTH, WINDOW_WIDTH))  # Vertical thin lines

    H_SPACE += HEIGHT + THIN_LINE_WIDTH
    V_SPACE += WIDTH + THIN_LINE_WIDTH

pygame.display.set_caption("Sudoku Solver")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

FPS = 60

NUMBER_FONT = pygame.font.SysFont('comics', 40)
WINNER_FONT = pygame.font.SysFont('comics', 100)



class Individual():
    brd = []
    fitness = -1


def contains(list, element):
    present = False
    for i in range(len(list)):
        if list[i] == element:
            present = True

    return present

def draw_board(board, ind):
    # Draw initial numbers
    V_offset = 0
    for i in range(len(ind.brd)):
        H_offset = 0
        for j in range(len(ind.brd[i])):
            if constraints_broken(i, j, ind.brd[i][j], ind.brd):
                number_text = NUMBER_FONT.render(str(ind.brd[i][j]), 1, RED)
            else:
                number_text = NUMBER_FONT.render(str(ind.brd[i][j]), 1, BLACK)

            WIN.blit(number_text, (
                WIDTH / 2 - number_text.get_width() / 2 + H_offset,
                HEIGHT / 2 - number_text.get_height() / 2 + V_offset))
            if j % 3 == 2:
                H_offset += THICK_LINE_WIDTH / 2 + WIDTH
            else:
                H_offset += THIN_LINE_WIDTH / 2 + HEIGHT
        if i % 3 == 2:
            V_offset += THICK_LINE_WIDTH / 2 + WIDTH
        else:
            V_offset += THIN_LINE_WIDTH / 2 + HEIGHT

    pygame.display.update()

def draw_window(board, ind):
    WIN.fill(WHITE)

    # Draw gridlines
    for line in THIN_LINES:
        pygame.draw.rect(WIN, BLACK, line)
    for line in THICK_LINES:
        pygame.draw.rect(WIN, BLACK, line)

    pygame.display.update()


def generate_board():
    board = []
    for i in range(9):
        row = []
        for j in range(9):
            row.append(" ")
        board.append(row)
    for i in range(len(board)):
        for j in range(len(board[0])):
            randomNumber = random.randint(1, 100)
            if randomNumber <= INITIAL_NUMBER_PROBABILITY:
                counter = 0
                boardNumber = random.randint(1, 9)
                # print(check_constraints(i, j, boardNumber, board))
                while constraints_broken(i, j, boardNumber, board) and counter < 10:
                    boardNumber = random.randint(1, 9)
                    counter += 1
                if not constraints_broken(i, j, boardNumber, board):
                    board[i][j] = boardNumber

    return board


def is_original_number(x, y, board):
    if board[x][y] != " ":
        return True
    else:
        return False


def constraints_broken(x, y, num, board):
    broken = False
    for a in range(3):
        for b in range(3):
            if board[(x // 3) * 3 + a][(y // 3) * 3 + b] == num and str(num) != " ":
                broken = True

    for c in range(9):
        if (board[x][c] == num or board[c][y] == num) and str(num) != " ":
            broken = True

    return broken

def evaluate_constraints_broken(x, y, num, board):
    broken = 0
    #for a in range(3):
    #    for b in range(3):
    #        if board[(y // 3) * 3 + a][(x // 3) * 3 + b] == num and str(num) != " ":
    #            broken += 1

    for c in range(9):
        if ((board[x][c] == num and c!= y) or (board[c][y] == num and c!= x)) and str(num) != " ":
            broken += 1


    return broken

def print_constraints_broken(board):
    print("Number: " + str(num) + "| X: " + str(x) + "| Y: " + str(y))
    print("-" + str(board[x]) + "-")
    print("-------------------------")
    for row in board:
        print(row)

    print(" ")

def generate_individual(board):
    ind = Individual()
    ind.brd = copy.deepcopy(board)
    for i in range(len(ind.brd)):
        for j in range(len(ind.brd[i])):
            if not is_original_number(i, j, board):
                if random.randint(0, 100) <= INDIVIDUAL_NUMBER_PROBABILITY:
                    counter = 0
                    boardNumber = random.randint(1, 9)
                    while constraints_broken(i, j, boardNumber, ind.brd) and counter < 10:
                        boardNumber = random.randint(1, 9)
                        counter += 1
                    if not constraints_broken(i, j, boardNumber, ind.brd):
                        ind.brd[i][j] = boardNumber

    ind.fitness = evaluate_individual(ind)

    #print_individual(ind)
    return ind

def generate_individual_full(board):
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    ind = Individual()
    ind.brd = copy.deepcopy(board)
    for x in range(9):
        numbers_temp = []
        for i in range(9):
            if not contains(board[x], i+1):
                numbers_temp.append(i+1)
        random.shuffle(numbers_temp)
        for i in range(9):
            if ind.brd[x][i] == " " and not contains(ind.brd[x][i], numbers_temp[0]):
                ind.brd[x][i] = numbers_temp[0]
                numbers_temp.pop(0)
    ind.fitness = evaluate_individual(ind)
    return ind


def print_individual(ind):
    for row in ind.brd:
        print(row)
    print(ind.fitness)


def evaluate_individual(ind):
    fitness = 0
    for i in range(len(ind.brd)):
        for j in range(len(ind.brd[i])):
            fitness += evaluate_constraints_broken(i, j, ind.brd[i][j], ind.brd)

    return fitness


def average_fitness(pop):
    total = 0
    for ind in pop:
        total += ind.fitness
    avg = total / len(pop)
    print(avg)


# Selection
def select(pop):
    parent = Individual()
    #for i in range(len(pop)):
    #    if random.randint(0, 100) < 30 and parent.fitness == -1:
    #        parent = copy.deepcopy(pop[i])
    parent = copy.deepcopy(pop[random.randint(0, POPULATION_SIZE // 5)])

    return parent

def select_random(pop):
    parent = copy.deepcopy(pop[random.randint(0, len(pop) - 1)])

    return parent

# Mutation
def mutate(ind, board):

    for i in range(len(ind.brd)):
        for j in range(len(ind.brd[i])):
            if random.randint(0, 100) < 10 or ind.brd[i][j] == " ":
                new_chromosome = 1

                while constraints_broken(i, j, new_chromosome, ind.brd) and new_chromosome < 10:
                    new_chromosome += 1

                if not constraints_broken(i, j, new_chromosome, ind.brd) and new_chromosome < 10:
                    ind.brd[i][j] = copy.deepcopy(new_chromosome)
                    #print("Mutated: " + str(new_chromosome))
                    #time.sleep(1)
    return ind

def mutate_swap(ind, board):

    for i in range(3):
        row = random.randint(0, 9)
        column1 = random.randint(0, 9)
        column2 = random.randint(0, 9)
        while is_original_number(column1, row, board):
            column1 = random.randint(0, 9)
        while is_original_number(column2, row, board):
            column2 = random.randint(0, 9)

        temp = copy.deepcopy(ind.brd[row][column1])
        ind.brd[row][column1] = copy.deepcopy(ind.brd[row][column2])
        ind.brd[row][column2] = copy.deepcopy(temp)

    return ind

# Replacement
def replace(ind, pop):
    if ind.fitness < pop[len(pop) - 1].fitness:
        pop[len(pop) - 1] = ind
    return pop

def sort_population(pop):
    n = len(pop)
    temp = Individual()

    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if pop[j].fitness > pop[j + 1].fitness:
                temp = copy.deepcopy(pop[j])
                pop[j] = copy.deepcopy(pop[j + 1])
                pop[j + 1] = copy.deepcopy(temp)
        print("Sorting: " + str(i * 100 / n) + "%", end="\r")
    #for i in range(3):
        #print(pop[i].fitness)
    return pop


def one_point_crossover(parent1, parent2, board):
    cxPoint = random.randint(0, 9)
    child = generate_individual(board)
    for i in range(cxPoint):
        child.brd[i] = copy.deepcopy(parent1.brd[i])
    for i in range(len(child.brd) - cxPoint):
        child.brd[i + cxPoint] = copy.deepcopy(parent2.brd[i + cxPoint])

    return child


def initialise_population(pop_size, board):
    population = []
    for i in range(pop_size):
        #print("Loading: " + str(i*100/pop_size) + "%")
        population.append(generate_individual_full(board))

    return population

def display_evo_stats(generations, best, initial_best, worst, initial_worst):
    print("Generations: " + str(generations) + " | Best: " + str(best.fitness) + " | Initial best: " + str(initial_best.fitness) + " | Worst: " + str(worst.fitness) + " | Initial worst: " + str(initial_worst.fitness))



def evolutionary_main_loop(board):

    parents = []
    children = []
    population = sort_population(initialise_population(POPULATION_SIZE, board))
    initial_best = population[0]
    initial_worst = population[len(population)-1]
    best = population[0]
    worst = population[len(population)-1]
    generations = 0

    while best.fitness != 0 and generations < GENERATION_LIMIT:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        best = population[0]
        worst = population[len(population)-1]

        parents.clear()
        children.clear()
        #for i in range(10):
            #children.append(select(population))

        #children.append(one_point_crossover(parents[0], parents[1], board))
        #children.append(parents[0])
        #children[0] = mutate_swap(children[0], board)

        parent1 = Individual()
        parent1 = copy.deepcopy(mutate_swap(select(population), board))
        parent1.fitness = evaluate_individual(parent1)
        population = sort_population(replace(parent1, population))
        parent2 = copy.deepcopy(mutate_swap(parent1, board))
        parent2.fitness = evaluate_individual(parent2)
        population = sort_population(replace(parent2, population))
        parent3 = copy.deepcopy(mutate_swap(parent2, board))
        parent3.fitness = evaluate_individual(parent3)
        population = sort_population(replace(parent3, population))
        parent4 = copy.deepcopy(mutate_swap(parent3, board))
        parent4.fitness = evaluate_individual(parent4)
        population = sort_population(replace(parent4, population))
        parent5 = copy.deepcopy(mutate_swap(parent4, board))
        parent5.fitness = evaluate_individual(parent5)
        population = sort_population(replace(parent5, population))
        parent6 = copy.deepcopy(mutate_swap(parent5, board))
        parent6.fitness = evaluate_individual(parent6)
        population = sort_population(replace(parent6, population))
        parent7 = copy.deepcopy(mutate_swap(parent6, board))
        parent7.fitness = evaluate_individual(parent7)
        population = sort_population(replace(parent7, population))
        parent8 = copy.deepcopy(mutate_swap(parent7, board))
        parent8.fitness = evaluate_individual(parent8)
        population = sort_population(replace(parent8, population))

        generations += 1
        if population[0].fitness < best.fitness:
            draw_window(board, best)
            draw_board(board, best)
        display_evo_stats(generations, best, initial_best, worst, initial_worst)

    display_evo_stats(generations, best, initial_best, worst, initial_worst)
    time.sleep(10000)
    pygame.quit()

def main():
    basic_sudoku = Individual()
    basic_sudoku.brd = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8]
    ]
    board = generate_board()
    clock = pygame.time.Clock()
    run = True
    print("Basic: " + str(evaluate_individual(basic_sudoku)))

    evolutionary_main_loop(board)
    #while run:
        #clock.tick(FPS)
        #for event in pygame.event.get():
            #if event.type == pygame.QUIT:
                #run = False
    time.sleep(10000)
    pygame.quit()
        #pygame.display.update()



if __name__ == "__main__":
    main()
