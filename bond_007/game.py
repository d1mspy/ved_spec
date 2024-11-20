import pygame
from persistent.const import *
from persistent.game_class import Player, Enemy, Bullet, Ammo

# Основная игра
class Game:
    def __init__(self) :
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH , HEIGHT))
        pygame.display.set_caption("Shooter Game")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.ammo = []
        self.score = 0
        self.enemy_spawn_timer = pygame.time.get_ticks ( )
        self.ammo_spawn_timer = pygame.time.get_ticks ( )
        self.wave_time = pygame.time.get_ticks ( )
        self.spawn_delay = ENEMY_SPAWN_RATE
        self.running = True

    def run(self) :
        while self.running :
            self.handle_events ( )
            self.update ( )
            self.render ( )
            self.clock.tick ( 60 )

    def handle_events(self) :
        for event in pygame.event.get ( ) :
            if event.type == pygame.QUIT :
                self.running = False

        keys = pygame.key.get_pressed ( )
        if keys[pygame.K_UP] :
            self.player.move ( 'UP' )
        if keys[pygame.K_DOWN] :
            self.player.move ( 'DOWN' )
        if keys[pygame.K_LEFT] :
            self.player.move ( 'LEFT' )
        if keys[pygame.K_RIGHT] :
            self.player.move ( 'RIGHT' )
        if keys[pygame.K_SPACE] and self.player.bullets > 0 :
            mouse_x , mouse_y = pygame.mouse.get_pos ( )
            bullet_start_pos = (self.player.rect.centerx , self.player.rect.top)
            direction = (mouse_x - bullet_start_pos[0] , mouse_y - bullet_start_pos[1])
            bullet = Bullet ( bullet_start_pos , direction )
            self.bullets.append ( bullet )
            self.player.bullets -= 1

    def update(self) :
        # Обновление пуль
        for bullet in self.bullets[:] :
            bullet.move ( )
            if bullet.rect.bottom < 0 or bullet.rect.left < 0 or bullet.rect.right > WIDTH or bullet.rect.top > HEIGHT :
                self.bullets.remove ( bullet )

        # Проверка на столкновения пуль с врагами
        for bullet in self.bullets[:] :
            for enemy in self.enemies[:] :
                if bullet.rect.colliderect ( enemy.rect ) :
                    enemy.health -= BULLET_HIT_DAMAGE
                    self.bullets.remove ( bullet )
                    if enemy.health <= 0 :
                        self.enemies.remove ( enemy )
                        self.score += 1
                    break

        # Движение врагов
        for enemy in self.enemies :
            enemy.move ( self.player )
            if enemy.rect.colliderect ( self.player.rect ) :
                self.player.health -= ENEMY_HIT_DAMAGE
                if self.player.health <= 0 :
                    print ( "Game Over! Final Score:" , self.score )
                    self.running = False

            # Стрельба врагов
            current_time = pygame.time.get_ticks ( )
            if current_time - enemy.last_shot_time > 2000 :  # Враги стреляют каждые 2 секунды
                bullet = enemy.shoot ( )
                self.bullets.append ( bullet )
                enemy.last_shot_time = current_time

        # Спавн врагов
        current_time = pygame.time.get_ticks ( )
        if current_time - self.enemy_spawn_timer > self.spawn_delay :
            for _ in range ( ENEMY_COUNT_PER_WAVE ) :
                self.enemies.append ( Enemy ( ) )
            self.enemy_spawn_timer = current_time

        # Проверка волны врагов
        if current_time - self.wave_time > WAVE_DELAY :
            self.enemy_spawn_timer = current_time
            self.spawn_delay -= 1  # Уменьшаем интервал спавна врагов после каждой волны

        # Спавн патронов
        if current_time - self.ammo_spawn_timer > AMMO_SPAWN_RATE :
            self.ammo.append ( Ammo ( ) )
            self.ammo_spawn_timer = current_time

        # Проверка на столкновения патронов с игроком
        for ammo in self.ammo[:] :
            if ammo.rect.colliderect ( self.player.rect ) :
                self.player.bullets += 10  # игрок получает 10 патронов
                self.ammo.remove ( ammo )

        # Проверка выхода патронов за границы
        for ammo in self.ammo[:] :
            if ammo.rect.left < 0 or ammo.rect.right > WIDTH or ammo.rect.top < 0 or ammo.rect.bottom > HEIGHT :
                self.ammo.remove ( ammo )

    def render(self) :
        self.screen.fill ( WHITE )
        pygame.draw.rect ( self.screen , GREEN , self.player.rect )
        for enemy in self.enemies :
            pygame.draw.rect ( self.screen , RED , enemy.rect )
        for bullet in self.bullets :
            pygame.draw.rect ( self.screen , BLUE , bullet.rect )
        for ammo in self.ammo :
            pygame.draw.rect ( self.screen , (255 , 215 , 0) , ammo.rect )  # Золотистый цвет для патронов

        # Отображение очков и здоровья
        font = pygame.font.SysFont ( None , 36 )
        score_text = font.render ( f'Score: {self.score}' , True , (0 , 0 , 0) )
        health_text = font.render ( f'Health: {self.player.health}' , True , (0 , 0 , 0) )
        bullets_text = font.render ( f'Bullets: {self.player.bullets}' , True , (0 , 0 , 0) )
        self.screen.blit ( score_text , (10 , 10) )
        self.screen.blit ( health_text , (10 , 40) )
        self.screen.blit ( bullets_text , (10 , 70) )

        pygame.display.flip ( )
