import pygame
from pygame.locals import *
from numpy import array
from numpy.linalg import norm
from numpy.random import binomial
from random import randint
from maze_gen import *

pygame.init()
font = pygame.font.SysFont('arial', 25)

rat_up = pygame.image.load("../assets/spr_rat_up.png")
rat_down = pygame.image.load("../assets/spr_rat_down.png")
rat_left = pygame.image.load("../assets/spr_rat_left.png")
rat_right = pygame.image.load("../assets/spr_rat_right.png")

class Rat_Game:

    """

    Autor: Moisés Filipe
    Descrição: Classe principal que contem o estado e comportamento do jogo.
    
    """

    def __init__(self, w=1000, h=700):
        self.width = w
        self.height = h

        self.screen = pygame.display.set_mode((self.width, self.height)) # inicializa o display com a largura e altura especificada
        pygame.display.set_caption("Rat")
        self.clock = pygame.time.Clock()

        self.reset() # inicializa o jogador e o grid

        self.rect_width = self.width//self.grid.n_cols
        self.rect_height = self.height//self.grid.n_rows

    def reset(self):
        self.player = player()
        self.grid = Grid(self.player, n_cols = 30, n_rows = 30)

    def game_step(self, action):

        """

        Recebe como entrada uma ação e realiza as mudanças de estado necessárias dentro do jogo. Uma vez realizadas tais mudanças, renderiza tudo na em self.screen.
        A acao deve ser uma lista binaria de forma que seus elementos representem as direções da seguinte maneira:

        [1,0,0,0] -> Cima

        [0,1,0,0] -> Baixo

        [0,0,1,0] -> Esquerda

        [0,0,0,1] -> Direita

        """
        self.grid.frame_iteration += 1 # O grid armazena a informacao de quantos steps foram realizados. 

        self.screen.fill((200, 200, 200))                                       # Preenche a tela de cinza
        text = font.render("Score: " + str(self.player.score), True, (0,0,0))   # Salva o score como uma string a ser exibida
        self.screen.blit(text, [0, 0])                                          # Renderiza o score no canto superior esquerdo

        # Encerra o jogo quando a janela e fechada
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        current_distance_from_goal = norm(array((self.player.x, self.player.y)) - array((self.grid.goal_x, self.grid.goal_y))) # Computa a distancia do jogador ao objetivo. Formula usada: numpy.norm(a-b)

        if action[0] == 1:
            if self.grid.is_valid_position(self.player.x, self.player.y - 1):   # Se a posicao que o agente deseja se mover e valida
                self.grid.clear_player_position()                               # Preencha a atual posicao do agente no grid com 0
                self.player.direction = "Up"
                self.player.move("Up")                                          # Atualize a posicao do agente
            else:
                self.player.current_reward = -1
                self.player.score += -1
        
        if action[1] == 1:
            if self.grid.is_valid_position(self.player.x, self.player.y + 1):
                self.grid.clear_player_position()
                self.player.direction = "Down"
                self.player.move("Down")
            else:
                self.player.current_reward = -1
                self.player.score += -1

        if action[2] == 1:
            if self.grid.is_valid_position(self.player.x - 1, self.player.y):
                self.grid.clear_player_position()
                self.player.direction = "Left"
                self.player.move("Left")
            else:
                self.player.current_reward = -1
                self.player.score += -1

        if action[3] == 1:
            if self.grid.is_valid_position(self.player.x + 1, self.player.y):
                self.grid.clear_player_position()
                self.player.direction = "Right"
                self.player.move("Right")
            else:
                self.player.current_reward = -1
                self.player.score += -1

        # Se a distancia do agente ao objetivo aumentou, o puna. Caso contrario, o recompense.    
        if norm(array((self.player.x, self.player.y)) - array((self.grid.goal_x, self.grid.goal_y))) >=  current_distance_from_goal:
             self.player.current_reward = self.player.penalty_amount
             self.player.score += self.player.penalty_amount
        else:
            self.player.current_reward = 1
            self.player.score += 1

        self.grid.update()               # Atualiza o grid com as mudancas realizadas nesse step
        self.draw_grid(self.screen) # Renderiza o grid em self.screen 

        pygame.display.update()
        self.clock.tick(1000)

        return self.player.current_reward, self.grid.done, self.player.score # Retorna os dados importantes desse step
    
    def draw_grid(self, screen):
        for x in range(0, self.grid.n_cols):
            for y in range(0, self.grid.n_rows):
                rect = pygame.Rect(x * self.rect_width,  y * self.rect_height, self.rect_width, self.rect_height)
                if self.grid.grid[x][y] == 1:
                    if self.player.direction == "Up":
                        self.screen.blit(rat_up, ((x*self.rect_width) - 32 + self.rect_width//2, (y*self.rect_height)-32+self.rect_height//2))
                    elif self.player.direction == "Down":
                        self.screen.blit(rat_down, ((x*self.rect_width) - 32 + self.rect_width//2, (y*self.rect_height)-32+self.rect_height//2))
                    elif self.player.direction == "Right":
                        self.screen.blit(rat_right, ((x*self.rect_width) - 32 + self.rect_width//2, (y*self.rect_height)-32+self.rect_height//2))
                    else:
                        self.screen.blit(rat_left, ((x*self.rect_width) - 32 + self.rect_width//2, (y*self.rect_height)-32+self.rect_height//2))

                    # pygame.draw.circle(screen, pygame.Color("#ab58a8"), [
                    #                (x*self.rect_width) + self.rect_width//2, (y*self.rect_height)+self.rect_height//2], 10)
                elif self.grid.grid[x][y] == 2:
                    screen.fill((0, 200, 0), rect)
                elif self.grid.grid[x][y] == 3:
                    screen.fill((0,200,200), rect)

                pygame.draw.rect(screen, (0, 0, 0), rect, 1)    

class player:
    
    def __init__(self):
        # Atual posicao no grid
        self.x = 1
        self.y = 1

        self.direction = "Right"

        self.score = 0

        self.penalty_amount = -1 # Quantidade a ser subtraida quando o agente se distancia do objetivo
        self.reward_amount = 20  # Quantidade a ser somada quando o agente alcanca o objetivo

        self.current_reward = 0  # Recompensa do step atual
    
    def move(self, direction):
        if direction == "Right":
            self.x += 1

        elif direction == "Left":
            self.x -= 1

        elif direction == "Down":
            self.y += 1

        elif direction == "Up":
            self.y -= 1

class Grid:

    """
    
    Aqui e armazenado todo o estado do jogo. Esta classe recebe uma instancia de Player em sua inicializacao.

    O estado do jogo e representado em uma matriz NxM, de forma que seus elementos representem diferentes entidades do jogo.
    Esta forma de representacao nos permite adicionar novas entidades arbitrariamente com relativa facilidade.

    1 -> Representa o jogador
    2 -> Representa o objetivo
    3 -> Representa um obstaculo
    TODO: 4 -> Queijo

    Exemplo:

    Um grid onde o jogador está no canto superior esquerdo mas não consegue alcançar o objetivo, pois esta cercado de obstaculos.

    [1,0,3,0]
    [0,0,3,0]
    [3,3,3,0]
    [0,0,0,2]
    
    """
    
    def __init__(self, player, n_rows = 10, n_cols = 10, screen_width = 500, screen_height = 500):

        self.player = player

        # Dimensoes do grid
        self.n_cols = n_cols
        self.n_rows = n_rows
        
        # Dimensoes da tela, importante para renderizar o grid.
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.frame_iteration = 0 # Quantidade de steps realizados
        self.done = False        # Variavel que determina se o jogo acabou

        #self.grid = [[0]*n_cols for i in range(n_rows)] # Matriz que representa o grid.
        self.grid = wilson(np.zeros(shape=(n_cols,n_cols)),n_cols)
        
        # Posicao do objetivo
        self.goal_x = randint(0, n_cols-1)
        self.goal_y = randint(0, n_rows-1)

        while self.grid[self.goal_x][self.goal_y] != 2:
            if self.grid[self.goal_x][self.goal_y] == 0:
                self.grid[self.goal_x][self.goal_y] = 2 # Popula a posicao do objetivo com um objetivo
            else:
                self.goal_x = randint(0, n_cols-1)
                self.goal_y = randint(0, n_rows-1)
    
    def is_valid_position(self, x, y):
        """Checa se a posicao atual esta populada com um obstaculo ou esta out of bounds"""
        if x > self.n_cols-1 or y > self.n_rows-1:
            return False
        if x < 0 or y < 0:
            return False
        
        if self.grid[x][y] == 3:
            return False

        return True  

    def update(self):
        """Atualiza o grid com as mudancas de estado realizadas."""
        if self.grid[self.player.x][self.player.y] == 2:   # Se a posicao do jogador eh a mesma do objetivo
            self.player.score += self.player.reward_amount # Some a recompensa ao score
            self.done = True                               # Jogo encerrado

        if self.frame_iteration > 500: # Se foram realizados 20 steps
            self.done = True          # Jogo encerrado

        self.grid[self.player.x][self.player.y] = 1 # Popule a atual posicao do jogador com 1
    
    def clear_player_position(self):
        self.grid[self.player.x][self.player.y] = 0


if __name__ == "__main__":
    game = Rat_Game()

    while True:
        game.game_step()