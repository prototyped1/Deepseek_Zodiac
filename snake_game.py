import pygame
import sys
import random
import math

# 初始化pygame
pygame.init()

# 游戏常量
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# 颜色定义
BACKGROUND = (15, 20, 25)
GRID_COLOR = (30, 40, 50)
SNAKE_HEAD_COLOR = (0, 200, 150)
SNAKE_BODY_START = (50, 180, 120)
SNAKE_BODY_END = (100, 220, 180)
FOOD_COLOR = (220, 80, 60)
TEXT_COLOR = (220, 220, 220)
PARTICLE_COLORS = [(255, 210, 80), (255, 120, 80), (80, 200, 255)]

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("炫彩贪食蛇")
clock = pygame.time.Clock()

# 字体
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.score = 0
        self.grow_to = 3
        self.particles = []
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_position = (((head[0] + x) % GRID_WIDTH), ((head[1] + y) % GRID_HEIGHT))
        
        if new_position in self.positions[1:]:
            self.reset()
            return False
        
        self.positions.insert(0, new_position)
        
        if len(self.positions) > self.grow_to:
            self.positions.pop()
            
        # 添加移动粒子
        if random.random() < 0.3:
            self.particles.append({
                'pos': [head[0] * GRID_SIZE + GRID_SIZE//2, head[1] * GRID_SIZE + GRID_SIZE//2],
                'color': random.choice(PARTICLE_COLORS),
                'size': random.randint(2, 5),
                'life': 15
            })
            
        # 更新粒子
        for p in self.particles[:]:
            p['life'] -= 1
            p['pos'][0] += random.randint(-3, 3)
            p['pos'][1] += random.randint(-3, 3)
            if p['life'] <= 0:
                self.particles.remove(p)
                
        return True
    
    def render(self, surface):
        # 渲染粒子
        for p in self.particles:
            pygame.draw.circle(surface, p['color'], (int(p['pos'][0]), int(p['pos'][1])), p['size'])
        
        # 渲染蛇身（带渐变效果）
        for i, pos in enumerate(self.positions):
            # 计算渐变颜色
            ratio = i / max(len(self.positions), 1)
            r = SNAKE_BODY_START[0] + (SNAKE_BODY_END[0] - SNAKE_BODY_START[0]) * ratio
            g = SNAKE_BODY_START[1] + (SNAKE_BODY_END[1] - SNAKE_BODY_START[1]) * ratio
            b = SNAKE_BODY_START[2] + (SNAKE_BODY_END[2] - SNAKE_BODY_START[2]) * ratio
            color = (int(r), int(g), int(b))
            
            # 绘制圆角矩形
            rect = pygame.Rect((pos[0] * GRID_SIZE, pos[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect, border_radius=8)
            
            # 蛇头特殊样式
            if i == 0:
                eye_size = GRID_SIZE // 5
                eye_offset = GRID_SIZE // 3
                # 眼睛位置根据方向变化
                if self.direction == (1, 0):  # 向右
                    pygame.draw.circle(surface, (0, 0, 0), (rect.centerx + eye_offset, rect.centery - eye_offset), eye_size)
                    pygame.draw.circle(surface, (0, 0, 0), (rect.centerx + eye_offset, rect.centery + eye_offset), eye_size)
                elif self.direction == (-1, 0):  # 向左
                    pygame.draw.circle(surface, (0, 0, 0), (rect.centerx - eye_offset, rect.centery - eye_offset), eye_size)
                    pygame.draw.circle(surface, (0, 0, 0), (rect.centerx - eye_offset, rect.centery + eye_offset), eye_size)
                elif self.direction == (0, 1):  # 向下
                    pygame.draw.circle(surface, (0, 0, 0), (rect.centerx - eye_offset, rect.centery + eye_offset), eye_size)
                    pygame.draw.circle(surface, (0, 0, 0), (rect.centerx + eye_offset, rect.centery + eye_offset), eye_size)
                elif self.direction == (0, -1):  # 向上
                    pygame.draw.circle(surface, (0, 0, 0), (rect.centerx - eye_offset, rect.centery - eye_offset), eye_size)
                    pygame.draw.circle(surface, (0, 0, 0), (rect.centerx + eye_offset, rect.centery - eye_offset), eye_size)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = FOOD_COLOR
        self.randomize_position()
        self.pulse = 0
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        
    def render(self, surface):
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        pulse_size = int(3 * math.sin(self.pulse))
        
        rect = pygame.Rect(
            (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE),
            (GRID_SIZE, GRID_SIZE)
        )
        
        # 绘制食物（带脉动效果）
        pygame.draw.circle(surface, self.color, rect.center, GRID_SIZE // 2 + pulse_size)
        pygame.draw.circle(surface, (255, 255, 255), rect.center, GRID_SIZE // 4 + pulse_size // 2)

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)

def main():
    snake = Snake()
    food = Food()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != (0, 1):
                    snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                    snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                    snake.direction = (1, 0)
        
        # 更新蛇的位置
        if not snake.update():
            continue
        
        # 检查是否吃到食物
        if snake.get_head_position() == food.position:
            snake.grow_to += 1
            snake.score += 10
            food.randomize_position()
            # 确保食物不出现在蛇身上
            while food.position in snake.positions:
                food.randomize_position()
        
        # 绘制
        screen.fill(BACKGROUND)
        draw_grid(screen)
        food.render(screen)
        snake.render(screen)
        
        # 显示分数
        score_text = font.render(f'分数: {snake.score}', True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        
        # 显示操作提示
        controls_text = small_font.render('方向键控制移动 | 碰到自己会重新开始', True, (180, 180, 180))
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()