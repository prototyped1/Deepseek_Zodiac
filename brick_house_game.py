
import pygame
import random
import math
import sys

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 250

# 颜色定义
BACKGROUND = (18, 22, 30)
GRID_COLOR = (40, 46, 56)
GRID_BORDER = (60, 70, 85)
TEXT_COLOR = (220, 220, 220)
HIGHLIGHT_COLOR = (100, 180, 255)
PANEL_BG = (30, 35, 45, 180)
PANEL_BORDER = (70, 130, 180)

# 方块颜色（带渐变效果）
BLOCK_COLORS = [
    [(0, 240, 220), (0, 200, 180)],  # Cyan
    [(30, 180, 255), (0, 140, 220)],  # Blue
    [(255, 140, 50), (220, 110, 30)],  # Orange
    [(255, 210, 50), (230, 180, 30)],  # Yellow
    [(150, 220, 90), (120, 190, 70)],  # Green
    [(180, 80, 220), (150, 60, 190)],  # Purple
    [(220, 70, 90), (190, 50, 70)]   # Red
]

# 创建窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("霓虹方块 - 俄罗斯方块")
clock = pygame.time.Clock()

# 字体
# title_font = pygame.font.SysFont("Arial", 48, bold=True)
# font = pygame.font.SysFont("Arial", 28)
# small_font = pygame.font.SysFont("Arial", 20)

title_font = pygame.font.SysFont('simhei', 48, bold=True)
font = pygame.font.SysFont('simhei', 36)
small_font = pygame.font.SysFont('simhei', 24)

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]  # Z
]

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-4, -1)
        self.life = random.randint(20, 40)
        self.gravity = 0.2
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        
    def draw(self, surface):
        alpha = min(255, self.life * 6)
        color = (*self.color, int(alpha))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

class Tetromino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color_idx = self.shape_idx
        self.rotation = 0
        self.particles = []
        
    def rotate(self):
        # 旋转矩阵 (90度顺时针)
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
                
        return rotated
    
    def draw(self, surface, offset_x, offset_y, ghost=False):
        shape = self.get_current_shape()
        color_idx = self.color_idx
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect_x = offset_x + (self.x + x) * GRID_SIZE
                    rect_y = offset_y + (self.y + y) * GRID_SIZE
                    
                    if ghost:
                        # 绘制半透明幽灵方块
                        pygame.draw.rect(surface, (*BLOCK_COLORS[color_idx][0], 80), 
                                        (rect_x, rect_y, GRID_SIZE, GRID_SIZE), 
                                        border_radius=4)
                        pygame.draw.rect(surface, BLOCK_COLORS[color_idx][0], 
                                        (rect_x, rect_y, GRID_SIZE, GRID_SIZE), 
                                        2, border_radius=4)
                    else:
                        # 绘制渐变方块
                        pygame.draw.rect(surface, BLOCK_COLORS[color_idx][0], 
                                        (rect_x, rect_y, GRID_SIZE, GRID_SIZE), 
                                        border_radius=4)
                        pygame.draw.rect(surface, BLOCK_COLORS[color_idx][1], 
                                        (rect_x, rect_y, GRID_SIZE - 4, GRID_SIZE - 4), 
                                        border_radius=3)
                        # 高光效果
                        pygame.draw.line(surface, (255, 255, 255, 100), 
                                        (rect_x + 2, rect_y + 2), 
                                        (rect_x + GRID_SIZE - 4, rect_y + 2), 1)
                        pygame.draw.line(surface, (255, 255, 255, 100), 
                                        (rect_x + 2, rect_y + 2), 
                                        (rect_x + 2, rect_y + GRID_SIZE - 4), 1)
    
    def get_current_shape(self):
        shape = self.shape
        for _ in range(self.rotation % 4):
            shape = self.rotate()
        return shape
    
    def add_particles(self, x, y, count=5):
        for _ in range(count):
            self.particles.append(Particle(x, y, BLOCK_COLORS[self.color_idx][0]))
    
    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class TetrisGame:
    def __init__(self):
        self.reset()
        self.field_offset_x = (SCREEN_WIDTH - SIDEBAR_WIDTH - GRID_WIDTH * GRID_SIZE) // 2 + 20
        self.field_offset_y = 100
        self.particles = []
        
    def reset(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # 方块下落速度（秒）
        self.fall_time = 0
        self.hold_piece = None
        self.can_hold = True
        self.last_move_down_time = 0
        
    def new_piece(self):
        return Tetromino(GRID_WIDTH // 2 - 1, 0)
    
    def valid_position(self, piece, x_offset=0, y_offset=0):
        shape = piece.get_current_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pos_x = piece.x + x + x_offset
                    pos_y = piece.y + y + y_offset
                    
                    if (pos_x < 0 or pos_x >= GRID_WIDTH or 
                        pos_y >= GRID_HEIGHT or 
                        (pos_y >= 0 and self.board[pos_y][pos_x])):
                        return False
        return True
    
    def lock_piece(self):
        shape = self.current_piece.get_current_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pos_x = self.current_piece.x + x
                    pos_y = self.current_piece.y + y
                    if 0 <= pos_y < GRID_HEIGHT:
                        self.board[pos_y][pos_x] = self.current_piece.color_idx + 1
                        # 添加锁定粒子效果
                        self.add_particles(
                            self.field_offset_x + pos_x * GRID_SIZE + GRID_SIZE // 2,
                            self.field_offset_y + pos_y * GRID_SIZE + GRID_SIZE // 2
                        )
        
        # 检查行消除
        self.clear_lines()
        
        # 生成新方块
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.can_hold = True
        
        # 检查游戏结束
        if not self.valid_position(self.current_piece):
            self.game_over = True
    
    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.board[y]):
                lines_to_clear.append(y)
        
        if not lines_to_clear:
            return
        
        # 更新分数
        cleared = len(lines_to_clear)
        self.lines_cleared += cleared
        self.score += [100, 300, 500, 800][min(cleared - 1, 3)] * self.level
        
        # 升级
        self.level = self.lines_cleared // 10 + 1
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
        
        # 消除行
        for line in lines_to_clear:
            del self.board[line]
            self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
            
            # 添加消除特效
            for x in range(GRID_WIDTH):
                self.add_particles(
                    self.field_offset_x + x * GRID_SIZE + GRID_SIZE // 2,
                    self.field_offset_y + line * GRID_SIZE + GRID_SIZE // 2,
                    count=10
                )
    
    def add_particles(self, x, y, count=5):
        for _ in range(count):
            self.particles.append(Particle(x, y, (255, 255, 255)))
    
    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)
    
    def hold_current_piece(self):
        if not self.can_hold:
            return
            
        if self.hold_piece is None:
            self.hold_piece = self.current_piece
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
        else:
            self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
            self.current_piece.x = GRID_WIDTH // 2 - 1
            self.current_piece.y = 0
        
        self.can_hold = False
    
    def draw_board(self, surface):
        # 绘制游戏区域背景
        board_rect = pygame.Rect(
            self.field_offset_x - 10,
            self.field_offset_y - 10,
            GRID_WIDTH * GRID_SIZE + 20,
            GRID_HEIGHT * GRID_SIZE + 20
        )
        pygame.draw.rect(surface, GRID_BORDER, board_rect, border_radius=8)
        pygame.draw.rect(surface, BACKGROUND, board_rect.inflate(-4, -4), border_radius=6)
        
        # 绘制网格
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    self.field_offset_x + x * GRID_SIZE,
                    self.field_offset_y + y * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE
                )
                pygame.draw.rect(surface, GRID_COLOR, rect, 1)
                
                # 绘制已放置的方块
                if self.board[y][x]:
                    color_idx = self.board[y][x] - 1
                    pygame.draw.rect(surface, BLOCK_COLORS[color_idx][0], rect, border_radius=4)
                    pygame.draw.rect(surface, BLOCK_COLORS[color_idx][1], rect.inflate(-8, -8), border_radius=3)
        
        # 绘制幽灵方块（预览位置）
        ghost_y = self.current_piece.y
        while self.valid_position(self.current_piece, 0, ghost_y + 1 - self.current_piece.y):
            ghost_y += 1
        ghost = Tetromino(self.current_piece.x, ghost_y)
        ghost.shape_idx = self.current_piece.shape_idx
        ghost.color_idx = self.current_piece.color_idx
        ghost.rotation = self.current_piece.rotation
        ghost.draw(surface, self.field_offset_x, self.field_offset_y, ghost=True)
        
        # 绘制当前方块
        self.current_piece.draw(surface, self.field_offset_x, self.field_offset_y)
    
    def draw_sidebar(self, surface):
        # 绘制信息面板
        panel_rect = pygame.Rect(
            SCREEN_WIDTH - SIDEBAR_WIDTH + 20,
            self.field_offset_y - 10,
            SIDEBAR_WIDTH - 40,
            SCREEN_HEIGHT - self.field_offset_y - 20
        )
        pygame.draw.rect(surface, PANEL_BORDER, panel_rect, border_radius=10)
        pygame.draw.rect(surface, PANEL_BG, panel_rect.inflate(-4, -4), border_radius=8)
        
        # 标题
        title = title_font.render("霓虹方块", True, HIGHLIGHT_COLOR)
        surface.blit(title, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20 + (SIDEBAR_WIDTH - 40 - title.get_width()) // 2, 20))
        
        # 分数信息
        y_offset = 100
        labels = [
            ("分数", self.score),
            ("等级", self.level),
            ("消除行", self.lines_cleared)
        ]
        
        for label, value in labels:
            text = font.render(f"{label}:", True, TEXT_COLOR)
            value_text = font.render(str(value), True, HIGHLIGHT_COLOR)
            surface.blit(text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 40, y_offset))
            surface.blit(value_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 40 + 120, y_offset))
            y_offset += 50
        
        # 下一个方块预览
        y_offset += 30
        next_label = font.render("下一个:", True, TEXT_COLOR)
        surface.blit(next_label, (SCREEN_WIDTH - SIDEBAR_WIDTH + 40, y_offset))
        y_offset += 50
        
        preview_rect = pygame.Rect(
            SCREEN_WIDTH - SIDEBAR_WIDTH + 40,
            y_offset,
            150,
            150
        )
        pygame.draw.rect(surface, GRID_BORDER, preview_rect, border_radius=8)
        pygame.draw.rect(surface, PANEL_BG, preview_rect.inflate(-4, -4), border_radius=6)
        
        # 绘制下一个方块
        shape = self.next_piece.get_current_shape()
        shape_width = len(shape[0]) * GRID_SIZE
        shape_height = len(shape) * GRID_SIZE
        start_x = preview_rect.centerx - shape_width // 2
        start_y = preview_rect.centery - shape_height // 2
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        start_x + x * GRID_SIZE,
                        start_y + y * GRID_SIZE,
                        GRID_SIZE, GRID_SIZE
                    )
                    pygame.draw.rect(surface, BLOCK_COLORS[self.next_piece.color_idx][0], rect, border_radius=4)
                    pygame.draw.rect(surface, BLOCK_COLORS[self.next_piece.color_idx][1], rect.inflate(-8, -8), border_radius=3)
        
        # Hold 方块预览
        y_offset += 200
        hold_label = font.render("保留:", True, TEXT_COLOR)
        surface.blit(hold_label, (SCREEN_WIDTH - SIDEBAR_WIDTH + 40, y_offset))
        y_offset += 50
        
        hold_rect = pygame.Rect(
            SCREEN_WIDTH - SIDEBAR_WIDTH + 40,
            y_offset,
            150,
            150
        )
        pygame.draw.rect(surface, GRID_BORDER, hold_rect, border_radius=8)
        pygame.draw.rect(surface, PANEL_BG, hold_rect.inflate(-4, -4), border_radius=6)
        
        # 绘制保留的方块
        if self.hold_piece:
            shape = self.hold_piece.get_current_shape()
            shape_width = len(shape[0]) * GRID_SIZE
            shape_height = len(shape) * GRID_SIZE
            start_x = hold_rect.centerx - shape_width // 2
            start_y = hold_rect.centery - shape_height // 2
            
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            start_x + x * GRID_SIZE,
                            start_y + y * GRID_SIZE,
                            GRID_SIZE, GRID_SIZE
                        )
                        pygame.draw.rect(surface, BLOCK_COLORS[self.hold_piece.color_idx][0], rect, border_radius=4)
                        pygame.draw.rect(surface, BLOCK_COLORS[self.hold_piece.color_idx][1], rect.inflate(-8, -8), border_radius=3)
        
        # 操作说明
        y_offset += 200
        controls = [
            "←→ : 左右移动",
            "↑ : 旋转",
            "↓ : 加速下落",
            "空格 : 直接落下",
            "C : 保留方块",
            "P : 暂停游戏",
            "R : 重新开始"
        ]
        
        for control in controls:
            text = small_font.render(control, True, TEXT_COLOR)
            surface.blit(text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 40, y_offset))
            y_offset += 30
    
    def draw_game_over(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        game_over_text = title_font.render("游戏结束", True, (220, 80, 80))
        score_text = font.render(f"最终分数: {self.score}", True, TEXT_COLOR)
        restart_text = font.render("按 R 键重新开始", True, HIGHLIGHT_COLOR)
        
        surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
    
    def draw(self, surface):
        # 绘制背景
        surface.fill(BACKGROUND)
        
        # 绘制网格背景
        for y in range(0, SCREEN_HEIGHT, 40):
            for x in range(0, SCREEN_WIDTH, 40):
                pygame.draw.rect(surface, GRID_COLOR, (x, y, 38, 38), 1)
        
        # 绘制游戏区域
        self.draw_board(surface)
        
        # 绘制侧边栏
        self.draw_sidebar(surface)
        
        # 绘制粒子效果
        self.draw_particles(surface)
        
        # 游戏结束画面
        if self.game_over:
            self.draw_game_over(surface)
        
        # 标题
        title = title_font.render("俄罗斯方块", True, (255, 255, 255))
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

def main():
    game = TetrisGame()
    last_time = pygame.time.get_ticks()
    paused = False
    
    while True:
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0
        last_time = current_time
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if game.game_over and event.key == pygame.K_r:
                    game.reset()
                
                if event.key == pygame.K_r:
                    game.reset()
                
                if event.key == pygame.K_p:
                    paused = not paused
                
                if not paused and not game.game_over:
                    if event.key == pygame.K_LEFT:
                        if game.valid_position(game.current_piece, -1):
                            game.current_piece.x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if game.valid_position(game.current_piece, 1):
                            game.current_piece.x += 1
                    elif event.key == pygame.K_UP:
                        # 旋转
                        game.current_piece.rotation += 1
                        if not game.valid_position(game.current_piece):
                            game.current_piece.rotation -= 1
                    elif event.key == pygame.K_DOWN:
                        # 加速下落
                        if game.valid_position(game.current_piece, 0, 1):
                            game.current_piece.y += 1
                    elif event.key == pygame.K_SPACE:
                        # 硬降（直接落到底部）
                        while game.valid_position(game.current_piece, 0, 1):
                            game.current_piece.y += 1
                        game.lock_piece()
                    elif event.key == pygame.K_c:
                        game.hold_current_piece()
        
        # 游戏逻辑更新
        if not paused and not game.game_over:
            game.fall_time += delta_time
            
            # 方块自动下落
            if game.fall_time >= game.fall_speed:
                game.fall_time = 0
                if game.valid_position(game.current_piece, 0, 1):
                    game.current_piece.y += 1
                    game.last_move_down_time = current_time
                else:
                    game.lock_piece()
            
            # 更新粒子
            game.update_particles()
        
        # 绘制
        game.draw(screen)
        
        # 暂停显示
        if paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            paused_text = title_font.render("游戏暂停", True, (255, 255, 255))
            screen.blit(paused_text, (SCREEN_WIDTH // 2 - paused_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()