import pygame # type: ignore
from persistent.const import *
from persistent.game_class import Player, Enemy, Bullet, Ammo
from db.connect import save_score


# Основная игра


class Game:
    def __init__(self):
        pygame.init()
        
        self.running = True
        self.game_over = False
        self.score_is_writed = False
        self.paused = False
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shooter Game")
        self.clock = pygame.time.Clock()
        
        # игрок и очки
        self.player = Player()
        self.score = 0
        
        # списки для врагов, патронов и пуль
        self.enemies = []
        self.bullets = []
        self.ammo = []
        self.enemy_bullets = []

        self.enemy_count = INITIAL_ENEMY_COUNT # количество врагов на текущую волну
        self.current_enemies = INITIAL_ENEMY_COUNT # атрибут для подсчета уже заспавненных врагов в рамках текущей волны
        
        # атрибуты для смены волн
        self.last_increase_time = 0
        self.last_wave_increasing = 0
        
        # интервал увеличения размера и здоровья врагов
        self.increase_interval = 10000
        self.increasing = 0
        
        # булевые атрибуты для реализации стрельбы и спавна врагов
        self.shoot_enabled = False
        self.spawn_enabled = True

        # Инициализация и воспроизведение музыки
        pygame.mixer.init()
        pygame.mixer.music.load('FUNKA_JANA.mp3')
        pygame.mixer.music.play(-1)

        # Таймер для спавна врагов и патронов
        self.enemy_spawn_timer = pygame.time.get_ticks()
        self.ammo_spawn_timer = pygame.time.get_ticks()


    # конец игры и запись очков в бд
    def game_over(self) -> None:
        print("Game Over! Final Score:", self.score)
        save_score(self.score)
        self.running = False

    # увеличение размера врагов по мере продвижения
    def increase_enemy_size(self) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_increase_time > self.increase_interval:
            self.increasing += 1
            self.last_increase_time = current_time
            print("size increased")
    
    
    # запуск
    def run(self) -> None:
        while self.running:
            self.increase_enemy_size( )
            self.handle_events()
            if not self.paused:
                self.update()
            self.render()
            self.clock.tick(60)
    
    
    # нажатие клавиш
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.running=False
            if event.type==pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    self.paused = not self.paused

        # Движение игрока (стрелки или WASD)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.move('UP')
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.move('DOWN')
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.move('LEFT')
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.move('RIGHT')

        # Стрельба
        if pygame.mouse.get_pressed()[0]:
            if not self.shoot_cooldown:  # Проверяем, можем ли мы стрелять
                    if self.player.bullets > 0:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        bullet_start_pos = (self.player.rect.centerx, 
                                            self.player.rect.top)
                        direction = (mouse_x - bullet_start_pos[0], 
                                     mouse_y - bullet_start_pos[1])
                        bullet = Bullet(bullet_start_pos, direction)
                        self.bullets.append(bullet)
                        self.player.bullets -= 1
                        
                        # Устанавливаем флаг временем стрельбы
                        self.shoot_cooldown = True

        # Если левая кнопка мыши не нажата, сбрасываем флаг
        if not pygame.mouse.get_pressed()[0]:
            self.shoot_cooldown = False
      
      
    # Обновление и проверка всей информации в процессе игры 
    def update(self) -> None:
        
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
                self.player.health -= ENEMY_HIT_DAMAGE
                if self.player.health <= 0:
                    self.game_over()

            # Стрельба врагов
            current_time = pygame.time.get_ticks()
            if current_time - enemy.last_shot_time > 2000:  # Враги стреляют каждые 2 секунды
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
            if enemy_bullet.rect.colliderect(self.player.rect):
                self.player.health -= BULLET_HIT_DAMAGE
                self.enemy_bullets.remove(enemy_bullet)
                if self.player.health <= 0:
                    self.game_over()
                    
        # Спавн врагов
        current_time = pygame.time.get_ticks()
        if len(self.enemies) < self.enemy_count and self.spawn_enabled:
            if current_time - self.enemy_spawn_timer > 1000:  # Спавн врагов каждые 1 секунду
                enemy = Enemy(self.increasing)
                if MIN_SPAWN_DISTANCE <= ((self.player.rect.y - enemy.rect.x)**2 + (self.player.rect.y - enemy.rect.y)**2)**(1/2):
                    self.enemies.append(enemy)
                    self.current_enemies -= 1
                    self.enemy_spawn_timer = current_time
                    if self.current_enemies == 0:
                        self.spawn_enabled = False
                    
        # Проверка на конец волны
        if len(self.enemies) == 0 and self.score > 0 and current_time - self.last_wave_increasing > 5000:
            self.enemy_count += ENEMY_INCREASE_PER_WAVE  # Увеличиваем количество врагов
            print(f"Next wave! Total enemies: {self.enemy_count}")
            self.spawn_enabled = True
            self.last_wave_increasing = current_time
            self.current_enemies = self.enemy_count
            
        # Спавн патронов
        if current_time - self.ammo_spawn_timer > AMMO_SPAWN_RATE:
            self.ammo.append(Ammo())
            self.ammo_spawn_timer = current_time

        # Проверка на столкновения патронов с игроком
        for ammo in self.ammo[:]:
            if ammo.rect.colliderect(self.player.rect):
                self.player.bullets += 100  # Игрок получает 10 патронов
                self.ammo.remove(ammo)


    # Отображение на экране
    def render(self):
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, GREEN, self.player.rect)  # Игрок
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, RED, enemy.rect)  # Враги
            enemy.draw_health(self.screen)  # Рисуем здоровье врага
        for bullet in self.bullets:
            pygame.draw.rect(self.screen, BLUE, bullet.rect)  # Пули игрока
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
        bullets_text = font.render(
            f'Bullets: {self.player.bullets}', True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(health_text, (10, 40))
        self.screen.blit(bullets_text, (10, 70))

        pygame.display.flip()
