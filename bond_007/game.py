import pygame
from persistent.const import *
from persistent.game_class import Player, Enemy, Bullet, Ammo
from db.connect import save_score


# Основная игра
class Game:
    def __init__(self, username: str, d1_on: bool):
        pygame.init()

        self.running: bool = True
        self.score_is_writed: bool = False
        self.paused: bool  = False
        
        self.username: str = username

        self.screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shooter Game")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        # игрок и очки
        self.player: Player = Player()
        self.score: int = 0

        # списки для врагов, патронов и пуль
        self.enemies: list = []
        self.bullets: list = []
        self.ammo: list = []
        self.enemy_bullets: list = []

        self.enemy_count: int = INITIAL_ENEMY_COUNT  # количество врагов на текущую волну
        # атрибут для подсчета уже заспавненных врагов в рамках текущей волны
        self.current_enemies: int = INITIAL_ENEMY_COUNT

        # атрибуты для смены волн
        self.last_increase_time: int = 0
        self.last_wave_increasing: int = 0
        self.wave: int = 1

        # увеличение размера и здоровья врагов
        self.increase_enabled: bool = True
        self.increasing: int = 0
        self.last_enemy_increasing: int = 0

        # булевые атрибуты для реализации стрельбы и спавна врагов
        self.shoot_enabled: bool = False
        self.spawn_enabled: bool = True

        # Инициализация и воспроизведение музыки
        pygame.mixer.init()
        pygame.mixer.music.load('jingle.mp3')
        pygame.mixer.music.play(-1)

        # Таймер для спавна врагов и патронов
        self.enemy_spawn_timer: int = pygame.time.get_ticks()
        self.ammo_spawn_timer: int = pygame.time.get_ticks()

        # Чит-коды
        self.infinite_ammo: bool = d1_on
        self.infinite_health: bool = False
        self.multi_shot: bool = False

        # 1D режим
        self.one_dimension: bool = d1_on
        
        if d1_on:
            self.spawn_cooldown: int = 900
        else:
            self.spawn_cooldown: int = 1500

    # конец игры и запись очков в бд
    def game_over(self) -> None:
        print("Game Over! Final Score:", self.score)
        save_score(self.username, self.score)
        self.running = False

    # увеличение размера врагов по мере продвижения
    def increase_enemy_size(self) -> None:
        if self.wave in INCREASING_WAVES and self.wave != self.last_enemy_increasing:
            if not (self.one_dimension and (self.wave == 14 or self.wave == 17 or self.wave == 20)):
                self.increasing += 1
                self.last_enemy_increasing = self.wave
                print("size increased")

    # запуск

    def run(self) -> None:
        print(f"Game started! Wave 1, total enemies: {INITIAL_ENEMY_COUNT}")
        while self.running:
            self.increase_enemy_size()
            self.handle_events()
            if not self.paused:
                self.update()
            self.render()
            self.clock.tick(60)

    # нажатие клавиш

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    self.paused = not self.paused
                # Активация чит-кодов
                if event.key == pygame.K_1:  # Бесконечные патроны
                    self.infinite_ammo = not self.infinite_ammo
                    print("Infinite Ammo:", self.infinite_ammo)
                if event.key == pygame.K_2:  # Бесконечное здоровье
                    self.infinite_health = not self.infinite_health
                    print("Infinite Health:", self.infinite_health)
                if event.key == pygame.K_3:  # Многократная стрельба
                    self.multi_shot = not self.multi_shot
                    print("Multi-Shot:", self.multi_shot)

        # Движение игрока (стрелки или WASD)
        keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.move('UP', self.paused, self.one_dimension)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.move('DOWN', self.paused, self.one_dimension)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.move('LEFT', self.paused, self.one_dimension)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.move('RIGHT', self.paused, self.one_dimension)

        # Стрельба
        if pygame.mouse.get_pressed()[0] and not self.paused:
            if not self.shoot_cooldown:  # Проверяем, можем ли мы стрелять
                if self.infinite_ammo or self.player.bullets > 0:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    bullet_start_pos = (self.player.rect.centerx,
                                        self.player.rect.top)
                    direction = (mouse_x - bullet_start_pos[0],
                                 mouse_y - bullet_start_pos[1])
                    bullet = Bullet(bullet_start_pos, direction)
                    self.bullets.append(bullet)
                    if not self.infinite_ammo:
                        self.player.bullets -= 1

                    # Дополнительные пули в стороны
                    if self.multi_shot:
                        angles = [-30, -18, -15, -10, -4, 5, 9, 15,
                                  20, 30]  # Углы отклонения в градусах
                        for angle in angles:
                            rotated_direction = self.rotate_vector(
                                direction, angle)
                            self.bullets.append(
                                Bullet(bullet_start_pos, rotated_direction))

                    # Устанавливаем флаг временем стрельбы
                    self.shoot_cooldown = True

        # Если левая кнопка мыши не нажата, сбрасываем флаг
        if not pygame.mouse.get_pressed()[0]:
            self.shoot_cooldown = False

    # функция отклонения выстрела на заданный угол
    def rotate_vector(self, vector, angle):
        import math
        rad = math.radians(angle)
        x, y = vector
        return (
            x * math.cos(rad) - y * math.sin(rad),
            x * math.sin(rad) + y * math.cos(rad)
        )

    # Обновление и проверка всей информации в процессе игры

    def update(self) -> None:
        if self.infinite_health:
            self.player.health = MAX_HEALTH

        # Обновление пуль игрока
        for bullet in self.bullets[:]:
            bullet.move()
            if (bullet.rect.bottom < 0 or bullet.rect.left < 0 or
                    bullet.rect.right > WIDTH or bullet.rect.top > HEIGHT):
                self.bullets.remove(bullet)

        # Проверка на столкновения пуль с врагами
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= 1  # Уменьшаем здоровье врага (1 попадание)
                    self.bullets.remove(bullet)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 1
                    break

        # Движение врагов и стрельба
        for enemy in self.enemies:
            enemy.move(self.player)
            if enemy.rect.colliderect(self.player.rect):
                if not self.infinite_health:
                    self.player.health -= ENEMY_HIT_DAMAGE
                if self.player.health <= 0:
                    self.game_over()

            # Стрельба врагов
            current_time: int = pygame.time.get_ticks()
            if not self.one_dimension and current_time - enemy.last_shot_time > 2000:  # Враги стреляют каждые 2 секунды
                # Передаем игрока для корректного направления пули
                bullet = enemy.shoot(self.player)
                self.enemy_bullets.append(bullet)
                enemy.last_shot_time = current_time

        # Обновление пуль от врагов
        for enemy_bullet in self.enemy_bullets[:]:
            enemy_bullet.move()
            if (enemy_bullet.rect.bottom < 0 or enemy_bullet.rect.left < 0 or
                    enemy_bullet.rect.right > WIDTH or enemy_bullet.rect.top > HEIGHT):
                self.enemy_bullets.remove(enemy_bullet)

            # Проверка на столкновение пули врага с игроком
            if not self.infinite_health and enemy_bullet.rect.colliderect(self.player.rect):
                self.player.health -= BULLET_HIT_DAMAGE
                self.enemy_bullets.remove(enemy_bullet)
                if self.player.health <= 0:
                    self.game_over()

        # Спавн врагов
        current_time = pygame.time.get_ticks()
        if len(self.enemies) < self.enemy_count and self.spawn_enabled and current_time - self.enemy_spawn_timer > self.spawn_cooldown:
            enemy = Enemy(self.increasing, self.one_dimension)
            if MIN_SPAWN_DISTANCE <= ((self.player.rect.y - enemy.rect.x)**2 + (self.player.rect.y - enemy.rect.y)**2)**(1/2):
                self.enemies.append(enemy)
                self.current_enemies -= 1
                self.enemy_spawn_timer = current_time
                if self.current_enemies == 0:
                    self.spawn_enabled = False
            else:
                print('cancel spawn')

        # Проверка на конец волны
        if len(self.enemies) == 0 and self.score > 0 and current_time - self.last_wave_increasing > 5000:
            self.enemy_count += ENEMY_INCREASE_PER_WAVE  # Увеличиваем количество врагов
            self.wave += 1
            self.increase_enemy_size()
            print(f"Wave {self.wave}, total enemies: {self.enemy_count}")
            self.spawn_enabled = True
            self.last_wave_increasing = current_time
            self.current_enemies = self.enemy_count

        # Спавн патронов
        if not self.one_dimension and current_time - self.ammo_spawn_timer > AMMO_SPAWN_RATE:
            self.ammo.append(Ammo())
            self.ammo_spawn_timer = current_time

        # Проверка на столкновения патронов с игроком
        for ammo in self.ammo[:]:
            if ammo.rect.colliderect(self.player.rect):
                self.player.bullets += 100  # Игрок получает 100 патронов
                self.ammo.remove(ammo)

    # Отображение на экране

    def render(self):
        if self.one_dimension:
            self.screen.fill(GRAY)

            white_strip_height = 50

            pygame.draw.rect(self.screen, WHITE,
                             (0, 375, WIDTH, white_strip_height))

            pygame.draw.rect(self.screen, GRAY, (0, 425, WIDTH, 375))

        else:
            self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, GREEN, self.player.rect)  # Игрок
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, RED, enemy.rect)  # Враги
            enemy.draw_health(self.screen)  # Рисуем здоровье врага
        for bullet in self.bullets:
            if self.one_dimension and 374 <= bullet.rect.y <= 426:
                pygame.draw.rect(self.screen, BLUE, bullet.rect)  # Пули игрока
            elif not self.one_dimension:
                pygame.draw.rect(self.screen, BLUE, bullet.rect)
        for ammo in self.ammo:
            pygame.draw.rect(self.screen, (255, 215, 0), ammo.rect)  # Патроны
        for enemy_bullet in self.enemy_bullets:  # Рисуем пули от врагов
            pygame.draw.rect(self.screen, (255, 0, 255),
                             enemy_bullet.rect)  # Пули будут фиолетовыми

        # Отображение очков и здоровья
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (0, 0, 0))
        health_text = font.render(
            f'Health: {self.player.health}', True, (0, 0, 0))
        if not self.one_dimension:
            bullets_text = font.render(
                f'Bullets: {self.player.bullets}', True, (0, 0, 0))
            self.screen.blit(bullets_text, (10, 70))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(health_text, (10, 40))

        pygame.display.flip()
