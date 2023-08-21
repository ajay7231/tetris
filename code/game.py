from settings import *
from panel import Panel
from random import choice
from timer import Timer
from os.path import join

class Game(Panel):
    def __init__(self,get_next_shape,update_score) -> None:
        super().__init__(GAME_WIDTH, GAME_HEIGHT)
        self.rect.topleft = (PADDING, PADDING)
        self.sprites = pygame.sprite.Group()
        self.score = 0

        self.get_next_shape = get_next_shape
        self.update_score = update_score


        self.line_surface = self.surface.copy()
        self.line_surface.fill((0, 255, 0))
        self.line_surface.set_colorkey((0, 255, 0))
        self.line_surface.set_alpha(120)

        self.field_data = [[0] * COLUMNS for _ in range(ROWS)]
        self.score = 0
        self.tetromino = Tetromino(self.get_next_shape(), self.sprites, self.create_new_tetromino, self.field_data)

        self.down_speed = UPDATE_START_SPEED
        self.down_speed_fast = self.down_speed * 0.25
        self.down_pressed = False

        self.timers = {
            "vertical move": Timer(UPDATE_START_SPEED, True, self.move_down),
            "horizontal move": Timer(MOVE_WAIT_TIME),
            "rotate": Timer(ROTATE_WAIT_TIME)
        }
        self.timers["vertical move"].activate()

        # score
        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0

        self.landing_sound = pygame.mixer.Sound(join('sound', 'landing.wav'))
        self.landing_sound.set_volume(0.2)

    def calculate_score(self, num_lines):
        self.current_lines += num_lines
        self.current_score += SCORE_DATA[num_lines] * self.current_level

        if self.current_lines / 2 > self.current_level:
            self.current_level += 1
            self.down_speed *= 0.8
            self.down_speed_fast = self.down_speed * 0.25
        
        self.update_score(self.current_lines, self.current_score, self.current_level)
    
    def check_game_over(self):
        for block in self.tetromino.blocks:
            if block.pos.y < 0:
                exit()

    def create_new_tetromino(self):
        self.landing_sound.play()
        self.check_game_over()
        self.check_finished_rows()
        self.tetromino = Tetromino(self.get_next_shape(), self.sprites, self.create_new_tetromino, self.field_data)

    def draw_grid(self):
        for col in range(1, COLUMNS):
            x = col * CELL_SIZE
            pygame.draw.line(self.line_surface, LINE_COLOR, (x, 0), (x, self.surface.get_height()), 1)

        for row in range(1, ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(self.line_surface, LINE_COLOR, (0, y), (self.surface.get_width(), y))

        self.surface.blit(self.line_surface, (0, 0))

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.timers["horizontal move"].active:
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                direction = -1 if keys[pygame.K_LEFT] else 1
                self.tetromino.move_horizontal(direction)
                self.timers["horizontal move"].activate()

        if not self.timers["rotate"].active and keys[pygame.K_UP]:
            self.tetromino.rotate()
            self.timers["rotate"].activate()
        
        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.timers["vertical move"].duration = self.down_speed_fast
            self.down_pressed = True
        elif self.down_pressed and not keys[pygame.K_DOWN]:
            self.timers["vertical move"].duration = self.down_speed
            self.down_pressed = False

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def run(self):
        self.input()
        self.timer_update()
        self.sprites.update()

        self.surface.fill(GRAY)
        self.sprites.draw(self.surface)

        self.draw_grid()
        self.display_surface.blit(self.surface, (PADDING, PADDING))
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)

    def move_down(self):
        self.tetromino.move_down()

    def check_finished_rows(self):
        deleted_rows = [index for index, row in enumerate(self.field_data) if all(row)]
        if deleted_rows:
            for deleted_row in deleted_rows:
                for block in self.field_data[deleted_row]:
                    block.kill()
                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < deleted_row:
                            block.pos.y += 1
            self.field_data = [[0] * COLUMNS for _ in range(ROWS)]
            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
            self.score += SCORE_DATA[len(deleted_rows)]
            print(self.score)
            self.calculate_score(len(deleted_rows))

class Tetromino:
    def __init__(self, shape, group, create_new_tetromino, field_data) -> None:
        self.shape = shape
        tetromino_data = TETROMINOS[shape]
        self.block_positions = tetromino_data['shape']
        self.color = tetromino_data['color']
        self.create_new_tetromino = create_new_tetromino
        self.field_data = field_data
        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

    def update(self):
        for block in self.blocks:
            block.update()

    def next_move_horizontal_collision(self, direction):
        return any(block.horizontal_collide(int(block.pos.x + direction), self.field_data) for block in self.blocks)

    def next_move_vertical_collision(self, direction):
        return any(block.vertical_collide(int(block.pos.y + direction), self.field_data) for block in self.blocks)

    def move_down(self):
        if not self.next_move_vertical_collision(1):
            for block in self.blocks:
                block.pos.y += 1
            self.update()
        else:
            self.store_blocks_in_field()
            self.create_new_tetromino()

    def move_horizontal(self, direction):
        if not self.next_move_horizontal_collision(direction):
            for block in self.blocks:
                block.pos.x += direction
            self.update()

    def rotate(self):
        if self.shape != 'O':
            pivot = self.blocks[0].pos
            new_block_positions = [block.rotate(pivot) for block in self.blocks]
            if all(0 <= pos.x < COLUMNS and 0 <= pos.y < ROWS and not self.field_data[int(pos.y)][int(pos.x)] for pos in new_block_positions):
                for i, block in enumerate(self.blocks):
                    block.pos = new_block_positions[i]

    def store_blocks_in_field(self):
        for block in self.blocks:
            self.field_data[int(block.pos.y)][int(block.pos.x)] = block

class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color) -> None:
        super().__init__(group)
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)
        self.pos = pygame.Vector2(pos) + BLOCK_OFFSET
        self.rect = self.image.get_rect(topleft=self.pos * CELL_SIZE)

    def horizontal_collide(self, x, field_data):
        return not 0 <= x < COLUMNS or field_data[int(self.pos.y)][x]

    def vertical_collide(self, y, field_data):
        return y >= ROWS or (0 <= y < ROWS and field_data[y][int(self.pos.x)])

    def update(self):
        self.rect.topleft = self.pos * CELL_SIZE

    def rotate(self, pivot):
        return pivot + (self.pos - pivot).rotate(90)
