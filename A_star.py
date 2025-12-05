from random import randint, random
import pygame
import sys


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.f = 0
        self.g = 0
        self.h = 0
        self.neighbors = []
        self.previous = None
        self.obstacle = False  
        self.swamp = False    

    def add_neighbors(self, grid, columns, rows):
        neighbor_x = self.x
        neighbor_y = self.y
    
        if neighbor_x < columns - 1:
            self.neighbors.append(grid[neighbor_x + 1][neighbor_y])
        if neighbor_x > 0:
            self.neighbors.append(grid[neighbor_x - 1][neighbor_y])
        if neighbor_y < rows - 1:
            self.neighbors.append(grid[neighbor_x][neighbor_y + 1])
        if neighbor_y > 0:
            self.neighbors.append(grid[neighbor_x][neighbor_y - 1])


class AStar:
    def __init__(self, cols, rows, start, end, obstacles=None, swamps=None):
        self.cols = cols
        self.rows = rows
        self.start = start
        self.end = end
        self.obstacles = obstacles if obstacles else []
        self.swamps = swamps if swamps else []

    @staticmethod
    def clean_open_set(open_set, current_node):
        for i in range(len(open_set)):
            if open_set[i] == current_node:
                open_set.pop(i)
                break
        return open_set

    @staticmethod
    def h_score(current_node, end):
        distance = abs(current_node.x - end.x) + abs(current_node.y - end.y)
        return distance

    @staticmethod
    def create_grid(cols, rows):
        grid = []
        for _ in range(cols):
            grid.append([])
            for _ in range(rows):
                grid[-1].append(0)
        return grid

    @staticmethod
    def fill_grids(grid, cols, rows, obstacles=None, swamps=None):
        if obstacles is None:
            obstacles = []
        if swamps is None:
            swamps = []
        
        for i in range(cols):
            for j in range(rows):
                grid[i][j] = Node(i, j)
        
        for obstacle in obstacles:
            if 0 <= obstacle[0] < cols and 0 <= obstacle[1] < rows:
                grid[obstacle[0]][obstacle[1]].obstacle = True
        
        for swamp in swamps:
            if 0 <= swamp[0] < cols and 0 <= swamp[1] < rows:
                grid[swamp[0]][swamp[1]].swamp = True
        
        return grid

    @staticmethod
    def get_neighbors(grid, cols, rows):
        for i in range(cols):
            for j in range(rows):
                grid[i][j].add_neighbors(grid, cols, rows)
        return grid
    
    @staticmethod
    def start_path(open_set, closed_set, current_node, end):
        best_way = 0
        for i in range(len(open_set)):
            if open_set[i].f < open_set[best_way].f:
                best_way = i

        current_node = open_set[best_way]
        final_path = []
        if current_node == end:
            temp = current_node
            while temp.previous:
                final_path.append(temp.previous)
                temp = temp.previous

        open_set = AStar.clean_open_set(open_set, current_node)
        closed_set.append(current_node)
        neighbors = current_node.neighbors
        
        for neighbor in neighbors:
            if (neighbor in closed_set) or neighbor.obstacle:
                continue
            else:
                if neighbor.swamp:
                    temp_g = current_node.g + 2  
                else:
                    temp_g = current_node.g + 1 
                    
                control_flag = 0
                for k in range(len(open_set)):
                    if neighbor.x == open_set[k].x and neighbor.y == open_set[k].y:
                        if temp_g < open_set[k].g:
                            open_set[k].g = temp_g
                            open_set[k].h = AStar.h_score(open_set[k], end)
                            open_set[k].f = open_set[k].g + open_set[k].h
                            open_set[k].previous = current_node
                        else:
                            pass
                        control_flag = 1
  
                if control_flag == 1:
                    pass
                else:
                    neighbor.g = temp_g
                    neighbor.h = AStar.h_score(neighbor, end)
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.previous = current_node
                    open_set.append(neighbor)

        return open_set, closed_set, current_node, final_path

    def main(self):
        grid = AStar.create_grid(self.cols, self.rows)
        grid = AStar.fill_grids(grid, self.cols, self.rows, self.obstacles, self.swamps)
        grid = AStar.get_neighbors(grid, self.cols, self.rows)
        
        open_set = []
        closed_set = []
        current_node = None
        final_path = []
        
        open_set.append(grid[self.start[0]][self.start[1]])
        self.end = grid[self.end[0]][self.end[1]]
        
        while len(open_set) > 0:
            open_set, closed_set, current_node, final_path = AStar.start_path(
                open_set, closed_set, current_node, self.end
            )
            if len(final_path) > 0:
                break

        return final_path


def get_integer_input(prompt, min_val=1, max_val=50):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Введите число от {min_val} до {max_val}")
        except ValueError:
            print("Пожалуйста, введите целое число")


def get_coordinate_input(prompt, max_x, max_y):
    while True:
        try:
            coords = input(prompt).strip()
            if ',' in coords:
                x, y = map(int, coords.split(','))
            elif ' ' in coords:
                x, y = map(int, coords.split())
            else:
                print("Введите координаты в формате 'x,y' или 'x y'")
                continue
            
            if 0 <= x < max_x and 0 <= y < max_y:
                return [x, y]
            else:
                print(f"Координаты должны быть в диапазоне: x: 0-{max_x-1}, y: 0-{max_y-1}")
        except ValueError:
            print("Пожалуйста, введите координаты как два целых числа через запятую или пробел")


def main():

    # 1. Размер матрицы
    print()
    print("1. ВВЕДИТЕ РАЗМЕР МАТРИЦЫ")
    cols = get_integer_input("Количество столбцов (ширина): ", 2, 30)
    rows = get_integer_input("Количество строк (высота): ", 2, 30)
    
    print()
    
    # 2. Старт и финиш
    print("2. ВВЕДИТЕ СТАРТ И ФИНИШ")
    print(f"Введите координаты стартовой точки (x: 0-{cols-1}, y: 0-{rows-1}):")
    start = get_coordinate_input("Старт (x,y): ", cols, rows)
    
    print(f"Введите координаты конечной точки (x: 0-{cols-1}, y: 0-{rows-1}):")
    end = get_coordinate_input("Финиш (x,y): ", cols, rows)
    
    if start == end:
        print("Ошибка: старт и финиш не могут быть в одной точке!")
        return
    print()
    
    # 3. Препятствия
    print("3. ВВЕДИТЕ ПРЕПЯТСТВИЯ")
    obstacles = []  # непроходимые
    swamps = []     # "болота"
    
    while True:
        print("\nВыберите тип препятствия:")
        print("1. Добавить НЕПРОХОДИМОЕ препятствие (нельзя пройти)")
        print("2. Добавить 'БОЛОТО' (можно пройти, но стоит, как 2 шага)")
        print("3. Удалить препятствие")
        print("4. Закончить ввод")
        print("5. Случайные препятствия(забывая о предыдущих)")
        
        choice = input("Ваш выбор (1/2/3/4/5): ").strip()
        
        if choice == '1':  # Непроходимое
            obstacle = get_coordinate_input(
                f"Координаты НЕПРОХОДИМОГО препятствия (x,y): ",
                cols, rows
            )
            
            if obstacle in obstacles:
                print("Непроходимое препятствие уже есть здесь")
            elif obstacle in swamps:
                print("Здесь уже есть 'болото'. Заменяю на непроходимое препятствие.")
                swamps.remove(obstacle)
                obstacles.append(obstacle)
            elif obstacle == start:
                print("Нельзя ставить препятствие на старт")
            elif obstacle == end:
                print("Нельзя ставить препятствие на финиш")
            else:
                obstacles.append(obstacle)
                print(f"Добавлено непроходимое препятствие: {obstacle}")
                
        elif choice == '2':  # Болото
            swamp = get_coordinate_input(
                f"Координаты 'БОЛОТА' (x,y): ",
                cols, rows
            )
            
            if swamp in swamps:
                print("'Болото' уже есть здесь")
            elif swamp in obstacles:
                print("Здесь уже есть непроходимое препятствие. Заменяю на 'болото'.")
                obstacles.remove(swamp)
                swamps.append(swamp)
            elif swamp == start:
                print("Нельзя ставить 'болото' на старт")
            elif swamp == end:
                print("Нельзя ставить 'болото' на финиш")
            else:
                swamps.append(swamp)
                print(f"Добавлено 'болото': {swamp}")
                
        elif choice == '3':  
            pos = get_coordinate_input(
                f"Координаты для удаления (x,y): ",
                cols, rows
            )
            
            if pos in obstacles:
                obstacles.remove(pos)
                print(f"Удалено непроходимое препятствие: {pos}")
            elif pos in swamps:
                swamps.remove(pos)
                print(f"Удалено 'болото': {pos}")
            else:
                print("На этой позиции нет препятствий")
                
        elif choice == '4':  
            break
            
        elif choice == '5':  
            try:
                print("\nГенерация случайных препятствий:")
                percent_obstacles = int(input("Процент НЕПРОХОДИМЫХ препятствий (0-50): "))
                percent_swamps = int(input("Процент 'БОЛОТ' (0-50): "))
                
                if 0 <= percent_obstacles <= 50 and 0 <= percent_swamps <= 50:
                    total_cells = cols * rows - 2
                    
                    num_obstacles = int(total_cells * percent_obstacles / 100)
                    for _ in range(num_obstacles):
                        while True:
                            x = randint(0, cols - 1)
                            y = randint(0, rows - 1)
                            pos = [x, y]
                            if (pos not in obstacles and pos not in swamps and 
                                pos != start and pos != end):
                                obstacles.append(pos)
                                break
                    
                    num_swamps = int(total_cells * percent_swamps / 100)
                    for _ in range(num_swamps):
                        while True:
                            x = randint(0, cols - 1)
                            y = randint(0, rows - 1)
                            pos = [x, y]
                            if (pos not in obstacles and pos not in swamps and 
                                pos != start and pos != end):
                                swamps.append(pos)
                                break
                    
                    print(f"Сгенерировано {num_obstacles} непроходимых препятствий и {num_swamps} 'болот'")
                    break
                else:
                    print("Проценты должны быть от 0 до 50")
            except ValueError:
                print("Введите целые числа")
        else:
            print("Неверный выбор")
    
    # Показываем карту
    print("\nКарта:")
    print("S - Старт")
    print("E - Финиш")
    print("█ - Непроходимое препятствие")
    print("~ - 'Болото' (стоит, как 2 шага)")
    print("· - Пусто")
    print()
    
    for y in range(rows):
        row_str = ""
        for x in range(cols):
            if [x, y] == start:
                row_str += " S "
            elif [x, y] == end:
                row_str += " E "
            elif [x, y] in obstacles:
                row_str += " █ "
            elif [x, y] in swamps:
                row_str += " ~ "
            else:
                row_str += " · "
        print(row_str)
    
    print(f"\nНепроходимых препятствий: {len(obstacles)}")
    print(f"'Болот': {len(swamps)}")
    
    # Запуск алгоритма
    a_star = AStar(cols, rows, start, end, obstacles, swamps)
    final_path = a_star.main()
    
    way = []
    total_cost = 0
    if len(final_path) == 0:
        print("Путь не найден!")
    else:
        print("\nПуть найден!")
        prev_node = None
        for i in range(len(final_path)):
            way.append([0] * 2)
            node = final_path[i]
            way[i] = [node.x, node.y]
            if prev_node:
                if node.swamp:
                    step_cost = 2
                else:
                    step_cost = 1
                total_cost += step_cost            
            prev_node = node

        if final_path and final_path[-1].swamp:
            total_cost += 2
        else:
            total_cost += 1
        
        print(f"\nОбщая стоимость пути: {total_cost}")
    
    # Визуализация
    pygame.init()
    size = (50 * cols, 50 * rows)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(f"A* Pathfinding - {cols}x{rows} (стоимость: {total_cost if final_path else 'нет пути'})")
    
    width = 40
    height = 40
    margin = 5
    white = (250, 250, 250)
    black = (0, 0, 0)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    dark_gray = (50, 50, 50)    
    brown = (139, 69, 19)      
    
    grid = AStar.create_grid(cols, rows)
    grid = AStar.fill_grids(grid, cols, rows, obstacles, swamps)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
        
        screen.fill(black)
        
        for col in range(cols):
            for row in range(rows):
                x = col * width + (col + 1) * margin
                y = row * height + (row + 1) * margin
                
                color = white
                
                if [col, row] == start:
                    color = red
                elif [col, row] == end:
                    color = blue
                elif way and [col, row] in way:
                    color = green
                elif grid[col][row].obstacle:
                    color = dark_gray
                elif grid[col][row].swamp:
                    color = brown
                
                pygame.draw.rect(screen, color, (x, y, width, height))
        
        pygame.display.update()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма прервана.")
    except Exception as e:
        print(f"Ошибка: {e}")