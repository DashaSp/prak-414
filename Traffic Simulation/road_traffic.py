import pygame
import numpy as np
import random
from collections import deque


class TrafficSimulation:
    def __init__(self, width=1200, height=500):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Трафик: Управляемое торможение")
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height

        self.road_length = width - 100
        self.road_y = height // 2
        
        self.spawn_rate = 0.6  
        self.next_car_time = 0
        self.cars = []  
        self.next_car_id = 0

        self.desired_distance = 80  
        self.safe_distance = 60     
        self.max_speed = 3.5      
        self.min_speed = 0.1      
        self.acceleration = 2.0   
        self.braking_power = 4.0   

        self.target_speed = 2.8    

        self.selected_car_idx = -1
        self.brake_duration = 180   

        self.color_normal = (100, 200, 100)   
        self.color_too_close = (255, 150, 50)  
        self.color_braking = (255, 50, 50)     
        self.color_far = (50, 150, 255)      
        self.color_selected = (255, 255, 0)    

        self.bg_color = (20, 25, 30)
        self.road_color = (40, 40, 45)
        self.marking_color = (200, 200, 220)

        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.show_distances = True

    def create_car(self):
        speed = self.target_speed * random.uniform(0.8, 1.2)
        speed = np.clip(speed, self.min_speed, self.max_speed)
        
        car_id = self.next_car_id
        self.next_car_id += 1

        start_x = -50 - random.randint(0, 100)
        
        self.cars.append([
            start_x,       
            speed,         
            self.color_normal,  
            False,         
            0,              
            car_id,         
            "едет"        
        ])
        
        self.next_car_time = random.expovariate(self.spawn_rate)

    def update_car_physics(self, i):
        x, v, color, is_braking, brake_timer, car_id, status = self.cars[i]

        if is_braking and brake_timer > 0:
            brake_timer -= 1
            if brake_timer <= 0:
                is_braking = False
            v = max(self.min_speed, v * 0.7)
            color = self.color_braking
            status = "тормозит"

        front_car = None
        front_distance = float('inf')
        
        for j, (x2, v2, _, _, _, _, _) in enumerate(self.cars):
            if j != i and x2 > x: 
                distance = x2 - x
                if distance < front_distance:
                    front_distance = distance
                    front_car = j

        if front_car is not None:
            x_front, v_front, _, _, _, _, _ = self.cars[front_car]
            distance = x_front - x

            if distance < self.safe_distance:
                closeness = 1.0 - (distance / self.safe_distance)
                dv = -self.braking_power * closeness
                color = self.color_too_close
                status = "тормозит"
                
            elif distance < self.desired_distance:
                closeness = 1.0 - (distance / self.desired_distance)
                dv = -self.acceleration * closeness
                color = self.color_normal
                status = "тормозит"
                
            elif distance > self.desired_distance * 1.2:
                farness = (distance - self.desired_distance) / 100
                dv = self.acceleration * min(1.0, farness)
                color = self.color_far
                status = "разгоняется"
                
            else:

                dv = 0
                color = self.color_normal
                status = "едет"

            if v > v_front:
                dv -= self.acceleration * 0.3
                status = "тормозит"
            
        else:
            if v < self.target_speed:
                dv = self.acceleration * 0.5
                status = "разгоняется"
            else:
                dv = -self.acceleration * 0.2
                status = "тормозит"
            color = self.color_normal

        v += dv * 0.05

        v = np.clip(v, self.min_speed, self.max_speed)

        x += v

        if i == self.selected_car_idx:
            color = self.color_selected
        
        self.cars[i] = [x, v, color, is_braking, brake_timer, car_id, status]

    def brake_selected_car(self):
        if 0 <= self.selected_car_idx < len(self.cars):
            x, v, _, _, _, car_id, _ = self.cars[self.selected_car_idx]

            self.cars[self.selected_car_idx][3] = True 
            self.cars[self.selected_car_idx][4] = self.brake_duration
            
            print(f"Машина #{car_id} тормозит на {self.brake_duration/60:.1f} сек!")

            self.selected_car_idx = -1

    def select_next_car(self):
        if not self.cars:
            self.selected_car_idx = -1
            return
            
        if self.selected_car_idx == -1:
            self.selected_car_idx = 0
        else:
            self.selected_car_idx = (self.selected_car_idx + 1) % len(self.cars)

        x, v, _, is_braking, brake_timer, car_id, status = self.cars[self.selected_car_idx]
        print(f"Выбрана машина #{car_id}, скорость: {v:.2f}, статус: {status}")

    def remove_offroad_cars(self):
        self.cars = [car for car in self.cars if car[0] < self.road_length + 200]

    def draw_road(self):
        self.screen.fill(self.bg_color)

        pygame.draw.rect(self.screen, self.road_color, 
                        (50, self.road_y - 25, self.road_length, 50))

        dash_len = 25
        gap_len = 20
        for x in range(60, self.width - 40, dash_len + gap_len):
            pygame.draw.line(self.screen, self.marking_color,
                           (x, self.road_y), 
                           (x + dash_len, self.road_y), 4)

        pygame.draw.line(self.screen, (255, 255, 255),
                        (50, self.road_y - 25), 
                        (self.width - 50, self.road_y - 25), 3)
        pygame.draw.line(self.screen, (255, 255, 255),
                        (50, self.road_y + 25), 
                        (self.width - 50, self.road_y + 25), 3)

    def draw_cars(self):
        for i, (x, v, color, is_braking, brake_timer, car_id, status) in enumerate(self.cars):
            pos_x = int(x) + 50
            pos_y = self.road_y

            radius = int(10 + v * 1.5)

            pygame.draw.circle(self.screen, color, (pos_x, pos_y), radius)
            
            border_color = (255, 255, 255)
            if is_braking:
                border_color = (255, 100, 100) 
                if pygame.time.get_ticks() % 500 < 250:
                    pygame.draw.circle(self.screen, (255, 200, 200), 
                                     (pos_x, pos_y), radius + 3, 2)
            
            pygame.draw.circle(self.screen, border_color, (pos_x, pos_y), radius, 2)
            
            id_text = self.small_font.render(str(car_id), True, (255, 255, 255))
            id_rect = id_text.get_rect(center=(pos_x, pos_y))
            self.screen.blit(id_text, id_rect)
            
            speed_text = self.small_font.render(f"{v:.1f}", True, (255, 255, 255))
            speed_rect = speed_text.get_rect(center=(pos_x, pos_y - radius - 10))
            self.screen.blit(speed_text, speed_rect)
            
            if is_braking and brake_timer > 0:
                bar_width = 30
                bar_height = 4
                progress = brake_timer / self.brake_duration
                
                pygame.draw.rect(self.screen, (200, 200, 200),
                               (pos_x - bar_width//2, pos_y + radius + 5, 
                                bar_width, bar_height), 1)
                pygame.draw.rect(self.screen, (255, 100, 100),
                               (pos_x - bar_width//2, pos_y + radius + 5, 
                                int(bar_width * progress), bar_height))

    def draw_distances(self):
        if not self.show_distances or len(self.cars) < 2:
            return

        sorted_cars = sorted(enumerate(self.cars), key=lambda item: item[1][0])
        
        for idx in range(len(sorted_cars) - 1):
            i, (x1, v1, _, _, _, id1, _) = sorted_cars[idx]
            j, (x2, v2, _, _, _, id2, _) = sorted_cars[idx + 1]
            
            distance = x2 - x1
            pos_x1 = int(x1) + 50
            pos_x2 = int(x2) + 50
            pos_y = self.road_y

            if distance < self.safe_distance:
                line_color = (255, 50, 50, 180) 
                line_width = 3
            elif distance < self.desired_distance:
                line_color = (255, 200, 50, 150) 
                line_width = 2
            else:
                line_color = (50, 200, 50, 120) 
                line_width = 1
            
            line_surf = pygame.Surface((abs(pos_x2 - pos_x1), 4), pygame.SRCALPHA)
            pygame.draw.line(line_surf, line_color, 
                           (0, 2), (abs(pos_x2 - pos_x1), 2), line_width)
            self.screen.blit(line_surf, (min(pos_x1, pos_x2), pos_y - 2))

    def draw_statistics(self):
        stat_width = 320
        stat_height = 180
        stat_x = 20
        stat_y = 20
        
        pygame.draw.rect(self.screen, (0, 0, 0, 200), 
                        (stat_x, stat_y, stat_width, stat_height), border_radius=8)
        
        title = self.font.render("СТАТИСТИКА", True, (255, 200, 100))
        self.screen.blit(title, (stat_x + 20, stat_y + 15))
        
        num_cars = len(self.cars)
        if num_cars > 0:
            speeds = [car[1] for car in self.cars]
            avg_speed = np.mean(speeds)
            min_speed = min(speeds)
            max_speed = max(speeds)
            
            if num_cars > 1:
                positions = [car[0] for car in self.cars]
                positions.sort()
                min_distance = min(positions[i+1] - positions[i] 
                                 for i in range(len(positions)-1))
            else:
                min_distance = float('inf')
        else:
            avg_speed = min_speed = max_speed = 0
            min_distance = 0
        
        stats = [
            f"Машин на дороге: {num_cars}",
            f"Средняя скорость: {avg_speed:.2f}",
            f"Желаемая дистанция: {self.desired_distance}",
            f"Безопасная дистанция: {self.safe_distance}",
            f"Целевая скорость: {self.target_speed:.1f}",
            f"Интенсивность: {self.spawn_rate:.1f}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.small_font.render(stat, True, (220, 220, 220))
            self.screen.blit(stat_text, (stat_x + 20, stat_y + 45 + i * 20))

    def draw_selected_car_info(self):
        if self.selected_car_idx < 0 or self.selected_car_idx >= len(self.cars):
            return
        
        x, v, _, is_braking, brake_timer, car_id, status = self.cars[self.selected_car_idx]
        
        info_width = 280
        info_height = 200
        info_x = 20
        info_y = self.height - info_height - 20
        
        pygame.draw.rect(self.screen, (0, 0, 0, 180), 
                        (info_x, info_y, info_width, info_height), border_radius=8)
        

        title = self.font.render("ВЫБРАННАЯ МАШИНА", True, (255, 255, 100))
        self.screen.blit(title, (info_x + 20, info_y + 15))
        
        if status == "разгоняется":
            status_color = (100, 255, 100) 
        elif status == "тормозит":
            status_color = (255, 100, 100) 
        else:  
            status_color = (100, 200, 255)  
        
        info_lines = [
            f"ID машины: {car_id}",
            f"Скорость: {v:.2f}",
            f"Позиция: {x:.1f}",
            f"Статус: {status}"
        ]
        
        for i, line in enumerate(info_lines):
            color = (220, 220, 220)
            if i == 3:  
                color = status_color
            
            line_text = self.small_font.render(line, True, color)
            self.screen.blit(line_text, (info_x + 20, info_y + 50 + i * 22))
        
        if is_braking and brake_timer > 0:
            remaining_time = brake_timer / 60 
            timer_text = self.small_font.render(f"Торможение: {remaining_time:.1f} сек", 
                                              True, (255, 150, 150))
            self.screen.blit(timer_text, (info_x + 20, info_y + info_height - 30))
            
            bar_width = 240
            bar_height = 6
            bar_x = info_x + 20
            bar_y = info_y + info_height - 15
            
            progress = brake_timer / self.brake_duration
            pygame.draw.rect(self.screen, (100, 100, 100), 
                           (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            pygame.draw.rect(self.screen, (255, 100, 100), 
                           (bar_x, bar_y, int(bar_width * (1 - progress)), bar_height), 
                           border_radius=3)

    def draw_controls(self):
        ctrl_width = 400
        ctrl_height = 220
        ctrl_x = self.width - ctrl_width - 10
        ctrl_y = 0
        
        pygame.draw.rect(self.screen, (0, 0, 0, 100), 
                        (ctrl_x, ctrl_y, ctrl_width, ctrl_height), border_radius=8)
        
        title = self.font.render("УПРАВЛЕНИЕ", True, (100, 255, 100))
        self.screen.blit(title, (ctrl_x + 20, ctrl_y + 15))
        
        controls = [
            ("TAB", "Выбрать машину"),
            ("SPACE", "Тормозить выбранную"),
            ("D", "Показать/скрыть дистанции"),
            ("R", "Сбросить симуляцию"),
            ("ВВЕРХ/ВНИЗ", "Интенсивность трафика"),
            ("ВЛЕВО/ВПРАВО", "Целевая скорость"),
            ("ПЛЮС/МИНУС", "Желаемая дистанция")
        ]
        
        for i, (key, desc) in enumerate(controls):
            y = ctrl_y + 45 + i * 25
            
            # Ключ
            key_text = self.small_font.render(key, True, (100, 255, 100))
            self.screen.blit(key_text, (ctrl_x + 20, y))
            
            # Описание
            desc_text = self.small_font.render(desc, True, (220, 220, 220))
            self.screen.blit(desc_text, (ctrl_x + 140, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.select_next_car()
                elif event.key == pygame.K_SPACE:
                    self.brake_selected_car()
                elif event.key == pygame.K_d:
                    self.show_distances = not self.show_distances
                elif event.key == pygame.K_r:
                    self.cars = []
                    self.selected_car_idx = -1
                elif event.key == pygame.K_UP:
                    self.spawn_rate = min(2.0, self.spawn_rate + 0.1)
                elif event.key == pygame.K_DOWN:
                    self.spawn_rate = max(0.1, self.spawn_rate - 0.1)
                elif event.key == pygame.K_RIGHT:
                    self.target_speed = min(5.0, self.target_speed + 0.2)
                elif event.key == pygame.K_LEFT:
                    self.target_speed = max(1.0, self.target_speed - 0.2)
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.desired_distance = min(150, self.desired_distance + 5)
                    self.safe_distance = min(120, self.safe_distance + 4)
                elif event.key == pygame.K_MINUS:
                    self.desired_distance = max(40, self.desired_distance - 5)
                    self.safe_distance = max(30, self.safe_distance - 4)
        
        return True

    def run(self):
        running = True
        last_time = pygame.time.get_ticks() / 1000.0
        
        while running:
            current_time = pygame.time.get_ticks() / 1000.0
            dt = current_time - last_time
            last_time = current_time
            
            running = self.handle_events()
            
            self.next_car_time -= dt
            if self.next_car_time <= 0:
                self.create_car()
            
            for i in range(len(self.cars)):
                self.update_car_physics(i)
            
            self.remove_offroad_cars()

            self.draw_road()
            self.draw_distances()
            self.draw_cars()
            self.draw_statistics() 
            self.draw_selected_car_info()  
            self.draw_controls()          

            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


if __name__ == "__main__":
    sim = TrafficSimulation(width=1200, height=500)
    sim.run()
