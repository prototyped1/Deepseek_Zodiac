import pygame
import random
import sys
import math

# 初始化pygame
pygame.init()

# 颜色定义 - 使用更现代的配色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (15, 15, 35)
LIGHT_BLUE = (100, 150, 255)
CYAN = (0, 255, 255)
BLUE = (0, 100, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 100)
PURPLE = (180, 0, 255)
RED = (255, 50, 50)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
GOLD = (255, 215, 0)

# 游戏设置
BLOCK_SIZE = 32
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 10)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GRID_OFFSET_X = 20
GRID_OFFSET_Y = 20

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块 - Tetris")
        self.clock = pygame.time.Clock()
        
        # 尝试加载更好的字体
        try:
            self.title_font = pygame.font.Font("arial.ttf", 48)
            self.font = pygame.font.Font("arial.ttf", 24)
            self.small_font = pygame.font.Font("arial.ttf", 18)
        except:
            self.title_font = pygame.font.Font(None, 48)
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
        
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500
        self.animation_time = 0
        self.particles = []
        
    def new_piece(self):
        """生成新的方块"""
        shape_idx = random.randint(0, len(SHAPES) - 1)
        return {
            'shape': SHAPES[shape_idx],
            'color': COLORS[shape_idx],
            'x': GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
            'y': 0
        }
    
    def valid_position(self, piece, x_offset=0, y_offset=0):
        """检查位置是否有效"""
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x + x_offset
                    new_y = piece['y'] + y + y_offset
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
    
    def rotate_piece(self, piece):
        """旋转方块"""
        rotated = list(zip(*piece['shape'][::-1]))
        rotated = [list(row) for row in rotated]
        
        new_piece = piece.copy()
        new_piece['shape'] = rotated
        
        if self.valid_position(new_piece):
            return new_piece
        return piece
    
    def place_piece(self):
        """将方块放置到网格中"""
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece['y'] + y
                    grid_x = self.current_piece['x'] + x
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_piece['color']
    
    def create_particles(self, x, y, color):
        """创建粒子效果"""
        for _ in range(5):
            self.particles.append({
                'x': x * BLOCK_SIZE + GRID_OFFSET_X + BLOCK_SIZE // 2,
                'y': y * BLOCK_SIZE + GRID_OFFSET_Y + BLOCK_SIZE // 2,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'color': color,
                'life': 30
            })
    
    def update_particles(self):
        """更新粒子效果"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """绘制粒子效果"""
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 30))
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(self.screen, color, 
                             (int(particle['x']), int(particle['y'])), 2)
    
    def clear_lines(self):
        """清除完整的行"""
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        # 创建粒子效果
        for line in lines_to_clear:
            for x in range(GRID_WIDTH):
                if self.grid[line][x]:
                    self.create_particles(x, line, self.grid[line][x])
        
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        # 更新分数
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += len(lines_to_clear) * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)
    
    def draw_gradient_background(self):
        """绘制渐变背景"""
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(DARK_BLUE[0] + (LIGHT_BLUE[0] - DARK_BLUE[0]) * color_ratio)
            g = int(DARK_BLUE[1] + (LIGHT_BLUE[1] - DARK_BLUE[1]) * color_ratio)
            b = int(DARK_BLUE[2] + (LIGHT_BLUE[2] - DARK_BLUE[2]) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_grid_background(self):
        """绘制网格背景"""
        grid_rect = pygame.Rect(GRID_OFFSET_X - 5, GRID_OFFSET_Y - 5,
                               GRID_WIDTH * BLOCK_SIZE + 10, 
                               GRID_HEIGHT * BLOCK_SIZE + 10)
        
        # 绘制阴影
        shadow_rect = grid_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, DARK_GRAY, shadow_rect, border_radius=10)
        
        # 绘制主背景
        pygame.draw.rect(self.screen, BLACK, grid_rect, border_radius=10)
        pygame.draw.rect(self.screen, GRAY, grid_rect, 2, border_radius=10)
    
    def draw_grid(self):
        """绘制游戏网格"""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * BLOCK_SIZE + GRID_OFFSET_X, 
                                 y * BLOCK_SIZE + GRID_OFFSET_Y,
                                 BLOCK_SIZE, BLOCK_SIZE)
                
                color = self.grid[y][x]
                if color:
                    # 绘制方块阴影
                    shadow_rect = rect.copy()
                    shadow_rect.x += 2
                    shadow_rect.y += 2
                    pygame.draw.rect(self.screen, DARK_GRAY, shadow_rect)
                    
                    # 绘制主方块
                    pygame.draw.rect(self.screen, color, rect)
                    
                    # 绘制高光效果
                    highlight_rect = rect.copy()
                    highlight_rect.width = rect.width // 3
                    highlight_rect.height = rect.height // 3
                    highlight_color = tuple(min(255, c + 50) for c in color)
                    pygame.draw.rect(self.screen, highlight_color, highlight_rect)
                    
                    # 绘制边框
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                else:
                    # 绘制空网格线
                    pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)
    
    def draw_piece(self, piece, x_offset=0, y_offset=0):
        """绘制方块"""
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect((piece['x'] + x + x_offset) * BLOCK_SIZE + GRID_OFFSET_X,
                                     (piece['y'] + y + y_offset) * BLOCK_SIZE + GRID_OFFSET_Y,
                                     BLOCK_SIZE, BLOCK_SIZE)
                    
                    # 绘制阴影
                    shadow_rect = rect.copy()
                    shadow_rect.x += 2
                    shadow_rect.y += 2
                    pygame.draw.rect(self.screen, DARK_GRAY, shadow_rect)
                    
                    # 绘制主方块
                    pygame.draw.rect(self.screen, piece['color'], rect)
                    
                    # 绘制高光效果
                    highlight_rect = rect.copy()
                    highlight_rect.width = rect.width // 3
                    highlight_rect.height = rect.height // 3
                    highlight_color = tuple(min(255, c + 50) for c in piece['color'])
                    pygame.draw.rect(self.screen, highlight_color, highlight_rect)
                    
                    # 绘制边框
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def draw_ui_panel(self):
        """绘制UI面板"""
        panel_rect = pygame.Rect(GRID_WIDTH * BLOCK_SIZE + GRID_OFFSET_X + 20, 
                                GRID_OFFSET_Y - 5, 
                                SCREEN_WIDTH - (GRID_WIDTH * BLOCK_SIZE + GRID_OFFSET_X + 25), 
                                SCREEN_HEIGHT - 2 * GRID_OFFSET_Y + 10)
        
        # 绘制面板阴影
        shadow_rect = panel_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, DARK_GRAY, shadow_rect, border_radius=15)
        
        # 绘制主面板
        pygame.draw.rect(self.screen, BLACK, panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, GRAY, panel_rect, 2, border_radius=15)
    
    def draw_ui(self):
        """绘制用户界面"""
        self.draw_ui_panel()
        
        ui_x = GRID_WIDTH * BLOCK_SIZE + GRID_OFFSET_X + 30
        ui_y = GRID_OFFSET_Y + 10
        
        # 绘制标题
        title_text = self.title_font.render("TETRIS", True, GOLD)
        title_rect = title_text.get_rect(centerx=ui_x + 100, y=ui_y)
        self.screen.blit(title_text, title_rect)
        
        ui_y += 80
        
        # 绘制分数
        score_text = self.font.render(f"分数", True, WHITE)
        self.screen.blit(score_text, (ui_x, ui_y))
        score_value = self.font.render(f"{self.score:,}", True, GOLD)
        self.screen.blit(score_value, (ui_x, ui_y + 30))
        
        ui_y += 80
        
        # 绘制等级
        level_text = self.font.render(f"等级", True, WHITE)
        self.screen.blit(level_text, (ui_x, ui_y))
        level_value = self.font.render(f"{self.level}", True, CYAN)
        self.screen.blit(level_value, (ui_x, ui_y + 30))
        
        ui_y += 80
        
        # 绘制消除行数
        lines_text = self.font.render(f"消除行数", True, WHITE)
        self.screen.blit(lines_text, (ui_x, ui_y))
        lines_value = self.font.render(f"{self.lines_cleared}", True, GREEN)
        self.screen.blit(lines_value, (ui_x, ui_y + 30))
        
        ui_y += 100
        
        # 绘制下一个方块预览
        next_text = self.font.render("下一个:", True, WHITE)
        self.screen.blit(next_text, (ui_x, ui_y))
        
        # 绘制预览方块
        preview_x = ui_x + 20
        preview_y = ui_y + 40
        for y, row in enumerate(self.next_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(preview_x + x * 20, preview_y + y * 20, 18, 18)
                    pygame.draw.rect(self.screen, self.next_piece['color'], rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
        
        ui_y += 120
        
        # 绘制控制说明
        controls = [
            "控制说明:",
            "← → : 移动",
            "↓ : 快速下降", 
            "↑ : 旋转",
            "空格 : 暂停",
            "R : 重新开始"
        ]
        
        for i, control in enumerate(controls):
            color = GOLD if i == 0 else WHITE
            control_text = self.small_font.render(control, True, color)
            self.screen.blit(control_text, (ui_x, ui_y + i * 25))
    
    def draw_game_over(self):
        """绘制游戏结束界面"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 游戏结束面板
        panel_width = 400
        panel_height = 300
        panel_rect = pygame.Rect((SCREEN_WIDTH - panel_width) // 2,
                                (SCREEN_HEIGHT - panel_height) // 2,
                                panel_width, panel_height)
        
        # 绘制面板阴影
        shadow_rect = panel_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(self.screen, DARK_GRAY, shadow_rect, border_radius=20)
        
        # 绘制主面板
        pygame.draw.rect(self.screen, BLACK, panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3, border_radius=20)
        
        # 绘制文本
        game_over_text = self.title_font.render("游戏结束!", True, RED)
        score_text = self.font.render(f"最终分数: {self.score:,}", True, WHITE)
        restart_text = self.font.render("按R重新开始", True, GOLD)
        
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                         panel_rect.y + 50))
        self.screen.blit(score_text, 
                        (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                         panel_rect.y + 120))
        self.screen.blit(restart_text, 
                        (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                         panel_rect.y + 180))
    
    def reset_game(self):
        """重置游戏"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500
        self.particles = []
    
    def run(self):
        """主游戏循环"""
        paused = False
        
        while True:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif not self.game_over and not paused:
                        if event.key == pygame.K_LEFT:
                            if self.valid_position(self.current_piece, x_offset=-1):
                                self.current_piece['x'] -= 1
                        elif event.key == pygame.K_RIGHT:
                            if self.valid_position(self.current_piece, x_offset=1):
                                self.current_piece['x'] += 1
                        elif event.key == pygame.K_DOWN:
                            if self.valid_position(self.current_piece, y_offset=1):
                                self.current_piece['y'] += 1
                        elif event.key == pygame.K_UP:
                            self.current_piece = self.rotate_piece(self.current_piece)
            
            if not self.game_over and not paused:
                # 自动下落
                if current_time - self.fall_time > self.fall_speed:
                    if self.valid_position(self.current_piece, y_offset=1):
                        self.current_piece['y'] += 1
                    else:
                        self.place_piece()
                        self.clear_lines()
                        self.current_piece = self.next_piece
                        self.next_piece = self.new_piece()
                        
                        if not self.valid_position(self.current_piece):
                            self.game_over = True
                    
                    self.fall_time = current_time
            
            # 更新粒子
            self.update_particles()
            
            # 绘制
            self.draw_gradient_background()
            self.draw_grid_background()
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_particles()
            self.draw_ui()
            
            if self.game_over:
                self.draw_game_over()
            
            if paused:
                pause_text = self.font.render("游戏暂停", True, WHITE)
                pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(pause_text, pause_rect)
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Tetris()
    game.run() 