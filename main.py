import pgzrun
from pygame import Rect

WIDTH = 600
HEIGHT = 600
TITLE = "Sky Jumper"

MENU = 'menu'
GAME = 'game'
GAME_OVER = 'game_over'
VICTORY = 'victory'
EXIT = 'exit'
current_state = MENU

sound_on = True

# Plataformas: chão e plataformas suspensas
platforms = [
    Rect(0, 540, WIDTH, 60),          # chão — ajustado para encostar no personagem
    Rect(100, 450, 150, 20),
    Rect(200, 400, 150, 20),
    Rect(300, 350, 150, 20),
    Rect(350, 300, 50, 20),
    Rect(450, 240, 50, 20)
]

GROUND_Y = platforms[0].top

class Hero:
    def __init__(self):
        self.images_idle = ["hero_idle1", "hero_idle2", "hero_idle3", "hero_idle4"]
        self.images_walk = ["hero_walk1", "hero_walk2", "hero_walk3", "hero_walk4", "hero_walk5", "hero_walk6"]
        self.actor = Actor(self.images_idle[0])
        self.actor.x = 100
        self.frame = 0
        self.anim_timer = 0
        self.walking = False
        self.vy = 0
        self.on_ground = False
        self.direction = 0
        self.align_to_ground()

    def align_to_ground(self):
        self.actor.y = GROUND_Y - self.actor.height // 2

    def update(self):
        self.anim_timer += 1
        self.walking = (self.direction != 0)
        
        if self.walking:
            if self.anim_timer % 30 == 0:
                self.frame = (self.frame + 1) % len(self.images_walk)
                self.actor.image = self.images_walk[self.frame]
        else:
            if self.anim_timer % 10 == 0:
                self.frame = (self.frame + 1) % len(self.images_idle)
                self.actor.image = self.images_idle[self.frame]

        # Movimento horizontal
        if self.direction != 0:
            self.actor.x += self.direction * 2

        # Aplicar gravidade
        self.vy += 0.5
        self.actor.y += self.vy
        self.on_ground = False

        hero_rect = Rect(
            self.actor.x - (self.actor.width - 40) // 2,
            self.actor.y - (self.actor.height - 10) // 2,
            (self.actor.width - 40),
            (self.actor.height - 10)
        )

        # Verificar colisão com plataformas
        for plat in platforms:
            if self.vy >= 0 and \
            hero_rect.bottom >= plat.top and \
            hero_rect.bottom - self.vy < plat.top and \
            hero_rect.right > plat.left and \
            hero_rect.left < plat.right:
                self.actor.y = plat.top - (self.actor.height - 10) // 2
                self.vy = 0
                self.on_ground = True
                break
        
    def move(self, direction):
        self.direction = direction

    def stop(self):
        self.direction = 0
        self.frame = 0
        self.actor.image = self.images_idle[self.frame]

    def jump(self):
        if self.on_ground:
            self.vy = -10
            self.on_ground = False
            if sound_on:
                sounds.jump.play()

class Enemy:
    def __init__(self, x, y):
        self.images = ["enemy_walk1", "enemy_walk2"]
        self.actor = Actor(self.images[0])
        self.actor.x = x
        self.frame = 0
        self.timer = 0
        self.direction = 1
        self.align_to_ground(y)

    def align_to_ground(self, ground_y):
        self.actor.y = ground_y - self.actor.height // 2

    def update(self):
        self.actor.x += self.direction * 2
        if self.actor.left < 100 or self.actor.right > 500:
            self.direction *= -1

        self.timer += 1
        if self.timer % 20 == 0:
            self.frame = (self.frame + 1) % len(self.images)
            self.actor.image = self.images[self.frame]

hero = Hero()
enemies = [Enemy(400, GROUND_Y)]
menu_options = ["Start Game", "Toggle Sound", "Exit"]
game_over_options = ["Try Again", "Exit"]
victory_options = ["Play Again", "Exit"]
victory_index = 0
game_over_index = 0
menu_index = 0
music_started = False

def draw():
    screen.clear()
    if current_state == MENU:
        draw_menu()
    elif current_state == GAME:
        draw_game()
    elif current_state == GAME_OVER:
        draw_game_over()
    elif current_state == VICTORY:
        draw_victory()

def draw_menu():
    screen.fill((30, 30, 60))
    for i, text in enumerate(menu_options):
        color = "white" if i != menu_index else "yellow"
        screen.draw.text(text, center=(WIDTH // 2, 200 + i * 60), fontsize=50, color=color)

def draw_game_over():
    screen.fill((20, 0, 0))
    screen.draw.text("GAME OVER", center=(WIDTH // 2, 150), fontsize=80, color="red")
    for i, text in enumerate(game_over_options):
        color = "white" if i != game_over_index else "yellow"
        screen.draw.text(text, center=(WIDTH // 2, 300 + i * 60), fontsize=50, color=color)

def draw_victory():
    screen.fill((0, 80, 0))
    screen.draw.text("YOU WIN!", center=(WIDTH // 2, 150), fontsize=80, color="lime")
    for i, text in enumerate(game_over_options):
        color = "white" if i != game_over_index else "yellow"
        screen.draw.text(text, center=(WIDTH // 2, 300 + i * 60), fontsize=50, color=color)

def draw_game():
    screen.fill((100, 200, 255))
    
    for plat in platforms:
        screen.draw.filled_rect(plat, (60, 180, 75))

    hero.actor.draw()
    for e in enemies:
        e.actor.draw()

def update():
    global current_state, music_started
    if not music_started:
        music.play("bg")
        music.set_volume(0.4)
        music_started = True

    if current_state == GAME:
        hero.update()
        for e in enemies:
            e.update()
            if hero.actor.colliderect(e.actor):
                if sound_on:
                    sounds.hit.play()
                current_state = GAME_OVER

        last_platform = platforms[-1]
        hero_rect = Rect(hero.actor.x - (hero.actor.width - 40) // 2,
                 hero.actor.y - (hero.actor.height - 10) // 2,
                 hero.actor.width - 40,
                 hero.actor.height - 10)

        if hero.on_ground and \
        hero_rect.bottom <= last_platform.top + 5 and \
        hero_rect.right > last_platform.left and \
        hero_rect.left < last_platform.right:
            current_state = VICTORY

def on_key_down(key):
    global current_state, menu_index, sound_on, game_over_index
    if current_state == MENU:
        if key == keys.DOWN:
            menu_index = (menu_index + 1) % len(menu_options)
        elif key == keys.UP:
            menu_index = (menu_index - 1) % len(menu_options)
        elif key == keys.RETURN:
            selected = menu_options[menu_index]
            if selected == "Start Game":
                reset_game()
                current_state = GAME
            elif selected == "Toggle Sound":
                sound_on = not sound_on
                if not sound_on:
                    music.stop()
                else:
                    music.play("bg")
            elif selected == "Exit":
                exit()
    elif current_state == GAME:
        if key == keys.LEFT or key == keys.A:
            hero.move(-1)
        elif key == keys.RIGHT or key == keys.D:
            hero.move(1)
        elif key == keys.SPACE or key == keys.UP:
            hero.jump()
    elif current_state == GAME_OVER:
        if key == keys.UP:
            game_over_index = (game_over_index - 1) % len(game_over_options)
        elif key == keys.DOWN:
            game_over_index = (game_over_index + 1) % len(game_over_options)
        elif key == keys.RETURN:
            selected = game_over_options[game_over_index]
            if selected == "Try Again":
                reset_game()
                current_state = GAME
            elif selected == "Exit":
                exit()
    elif current_state == VICTORY:
        global victory_index
        if key == keys.UP:
            victory_index = (victory_index - 1) % len(victory_options)
        elif key == keys.DOWN:
            victory_index = (victory_index + 1) % len(victory_options)
        elif key == keys.RETURN:
            selected = victory_options[victory_index]
            if selected == "Play Again":
                reset_game()
                current_state = GAME
            elif selected == "Exit":
                exit()


def on_key_up(key):
    if current_state == GAME:
        if key in (keys.LEFT, keys.RIGHT, keys.A, keys.D):
            hero.stop()

def reset_game():
    global hero, enemies
    hero = Hero()
    enemies = [Enemy(400, GROUND_Y)]

pgzrun.go()
