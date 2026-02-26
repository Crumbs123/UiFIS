import pygame
import math
import random

# Инициализация Pygame
pygame.init()

# Константы экрана
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 69, 0)
GRAY = (128, 128, 128)
BLUE = (65, 105, 225)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
CYAN = (0, 255, 255)
DARK_BLUE = (25, 25, 112)
GOLD = (255, 215, 0)

class Planet:
    def __init__(self, name, orbit_radius, speed, size, color, start_angle=0, has_rings=False, moons=0):
        self.name = name
        self.orbit_radius = orbit_radius  # Относительный радиус орбиты
        self.speed = speed  # Базовая скорость вращения
        self.size = size  # Размер планеты
        self.color = color
        self.angle = math.radians(start_angle)  # Текущий угол в радианах
        self.has_rings = has_rings  # Есть ли кольца (Сатурн)
        self.moons = moons  # Количество спутников
        
    def update(self, speed_multiplier, center_x, center_y, zoom):
        # Обновление угла
        self.angle += self.speed * speed_multiplier
        
        # Вычисление позиции
        actual_radius = self.orbit_radius * 80 * zoom  # Масштабирование радиуса
        x = center_x + math.cos(self.angle) * actual_radius
        y = center_y + math.sin(self.angle) * actual_radius
        
        # Ограничение размера планеты
        display_size = max(4, min(int(self.size * zoom), 40))
        
        return x, y, display_size
    
    def draw_orbit(self, screen, center_x, center_y, zoom):
        # Рисование орбиты
        actual_radius = int(self.orbit_radius * 80 * zoom)
        if actual_radius > 0:
            pygame.draw.circle(screen, (50, 50, 50), (center_x, center_y), actual_radius, 1)
    
    def draw(self, screen, x, y, display_size):
        # Рисование планеты
        pygame.draw.circle(screen, self.color, (int(x), int(y)), display_size)
        
        # Добавление блика для объема
        if display_size > 5:
            highlight_offset = max(1, display_size // 4)
            highlight_size = max(2, display_size // 3)
            highlight_color = tuple(min(255, c + 30) for c in self.color)
            pygame.draw.circle(screen, highlight_color, 
                             (int(x - highlight_offset), int(y - highlight_offset)), 
                             highlight_size)
        
        # Рисование колец для Сатурна
        if self.has_rings and display_size > 4:
            ring_width = int(display_size * 2.5)
            ring_height = int(display_size * 0.6)
            ring_surface = pygame.Surface((ring_width * 2, ring_height * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(ring_surface, (200, 180, 140, 150), 
                              (0, 0, ring_width * 2, ring_height * 2), 2)
            screen.blit(ring_surface, (int(x - ring_width), int(y - ring_height)))
        
        # Подпись планеты
        font = pygame.font.SysFont('Arial', 12)
        label = font.render(self.name, True, WHITE)
        screen.blit(label, (int(x) - label.get_width() // 2, int(y) + display_size + 5))


class SolarSystemApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Солнечная система")
        self.clock = pygame.time.Clock()
        
        # Центр экрана
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
        
        # Параметры управления
        self.speed_multiplier = 1.0
        self.zoom = 1.0
        self.paused = False
        self.show_orbits = True
        self.show_stars = True
        
        # Звезды для фона
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                      random.randint(1, 3)) for _ in range(200)]
        
        # Инициализация планет с научно обоснованными относительными параметрами
        self.planets = [
            Planet("Меркурий", 1.0, 0.04, 6, GRAY, 0),
            Planet("Венера", 1.5, 0.03, 10, ORANGE, 45),
            Planet("Земля", 2.0, 0.025, 11, BLUE, 90),
            Planet("Марс", 2.6, 0.02, 8, RED, 135),
            Planet("Юпитер", 3.8, 0.012, 22, (205, 133, 63), 180),
            Planet("Сатурн", 5.0, 0.009, 18, GOLD, 225, has_rings=True),
            Planet("Уран", 6.0, 0.006, 14, CYAN, 270),
            Planet("Нептун", 7.0, 0.005, 13, DARK_BLUE, 315)
        ]
        
        # Шрифты
        self.font_large = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 18)
        self.font_small = pygame.font.SysFont('Arial', 14)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.speed_multiplier = min(5.0, self.speed_multiplier + 0.5)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.speed_multiplier = max(0.1, self.speed_multiplier - 0.5)
                elif event.key == pygame.K_o:
                    self.show_orbits = not self.show_orbits
                elif event.key == pygame.K_r:
                    # Сброс параметров
                    self.speed_multiplier = 1.0
                    self.zoom = 1.0
                elif event.key == pygame.K_q:
                    return False
            
            elif event.type == pygame.MOUSEWHEEL:
                # Масштабирование колесиком мыши
                if event.y > 0:
                    self.zoom = min(2.0, self.zoom * 1.1)
                else:
                    self.zoom = max(0.3, self.zoom / 1.1)
            
            elif event.type == pygame.VIDEORESIZE:
                # Адаптация к размеру окна
                global WIDTH, HEIGHT
                WIDTH, HEIGHT = event.w, event.h
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                self.center_x = WIDTH // 2
                self.center_y = HEIGHT // 2
                # Перегенерация звезд для нового размера
                self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                              random.randint(1, 3)) for _ in range(200)]
        
        return True
    
    def draw_sun(self):
        # Размер Солнца с ограничением
        sun_size = int(35 * self.zoom)
        sun_size = max(15, min(sun_size, 80))
        
        # Свечение Солнца (градиент)
        for i in range(3, 0, -1):
            glow_size = sun_size + i * 15
            alpha = 100 - i * 25
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 0, alpha), 
                             (glow_size, glow_size), glow_size)
            self.screen.blit(glow_surface, 
                           (self.center_x - glow_size, self.center_y - glow_size))
        
        # Само Солнце
        pygame.draw.circle(self.screen, YELLOW, (self.center_x, self.center_y), sun_size)
        
        # Подпись
        label = self.font_medium.render("СОЛНЦЕ", True, YELLOW)
        self.screen.blit(label, (self.center_x - label.get_width() // 2, 
                                self.center_y - sun_size - 25))
    
    def draw_stars(self):
        if not self.show_stars:
            return
        for x, y, size in self.stars:
            brightness = random.randint(150, 255)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (x, y), size)
    
    def draw_ui(self):
        # Панель управления
        panel_height = 80
        panel = pygame.Surface((WIDTH, panel_height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        self.screen.blit(panel, (0, 0))
        
        # Заголовок
        title = self.font_large.render("Солнечная система", True, YELLOW)
        self.screen.blit(title, (20, 10))
        
        # Статус
        status_color = (0, 255, 0) if not self.paused else (255, 0, 0)
        status_text = "▶ Играет" if not self.paused else "⏸ Пауза"
        status = self.font_medium.render(status_text, True, status_color)
        self.screen.blit(status, (20, 45))
        
        # Скорость
        speed_text = f"Скорость: {self.speed_multiplier:.1f}x"
        speed_label = self.font_medium.render(speed_text, True, WHITE)
        self.screen.blit(speed_label, (150, 45))
        
        # Масштаб
        zoom_text = f"Масштаб: {self.zoom:.1f}x"
        zoom_label = self.font_medium.render(zoom_text, True, WHITE)
        self.screen.blit(zoom_label, (320, 45))
        
        # Управление (правая сторона)
        controls = [
            "Пробел: Пауза | ↑/↓: Скорость | Колесо мыши: Масштаб",
            "O: Орбиты | R: Сброс | Q: Выход"
        ]
        for i, text in enumerate(controls):
            ctrl_label = self.font_small.render(text, True, (200, 200, 200))
            self.screen.blit(ctrl_label, (WIDTH - ctrl_label.get_width() - 20, 15 + i * 25))
        
        # Информация о планетах (нижняя панель)
        info_panel = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        info_panel.fill((0, 0, 0, 150))
        self.screen.blit(info_panel, (0, HEIGHT - 100))
        
        # Отображение данных о планетах
        planet_info = "Планеты: "
        for i, planet in enumerate(self.planets[:4]):  # Первые 4 планеты
            planet_info += f"{planet.name} "
        planet_info += "| "
        for planet in self.planets[4:]:  # Внешние планеты
            planet_info += f"{planet.name} "
        
        info_text = self.font_small.render(planet_info, True, WHITE)
        self.screen.blit(info_text, (20, HEIGHT - 80))
        
        # Подсказка
        hint = self.font_small.render("Наведите на планету для информации | Реальные пропорции орбит и скоростей", 
                                     True, (150, 150, 150))
        self.screen.blit(hint, (20, HEIGHT - 40))
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            # Очистка экрана
            self.screen.fill(BLACK)
            
            # Отрисовка звезд
            self.draw_stars()
            
            # Отрисовка орбит
            if self.show_orbits:
                for planet in self.planets:
                    planet.draw_orbit(self.screen, self.center_x, self.center_y, self.zoom)
            
            # Отрисовка Солнца
            self.draw_sun()
            
            # Обновление и отрисовка планет
            for planet in self.planets:
                if not self.paused:
                    x, y, size = planet.update(self.speed_multiplier, self.center_x, self.center_y, self.zoom)
                else:
                    # Если пауза, просто пересчитываем позицию без обновления угла
                    actual_radius = planet.orbit_radius * 80 * self.zoom
                    x = self.center_x + math.cos(planet.angle) * actual_radius
                    y = self.center_y + math.sin(planet.angle) * actual_radius
                    size = max(4, min(int(planet.size * self.zoom), 40))
                
                planet.draw(self.screen, x, y, size)
            
            # Отрисовка интерфейса
            self.draw_ui()
            
            # Обновление экрана
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()


def main():
    print("=" * 50)
    print("СОЛНЕЧНАЯ СИСТЕМА - Интерактивная симуляция")
    print("=" * 50)
    print("\nУправление:")
    print("  Пробел      - Пауза/Продолжить")
    print("  ↑ / W       - Увеличить скорость")
    print("  ↓ / S       - Уменьшить скорость")
    print("  Колесо мыши - Масштабирование")
    print("  O           - Показать/скрыть орбиты")
    print("  R           - Сбросить параметры")
    print("  Q           - Выход")
    print("\n" + "=" * 50)
    
    app = SolarSystemApp()
    app.run()
    print("\nПрограмма завершена.")


if __name__ == "__main__":
    main()