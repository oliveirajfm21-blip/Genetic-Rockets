import pygame
import random
import math

HEIGHT = 800
WIDTH = 600
LIFE = 300
MAX_THRUST = 0.35
MAX_SPEED = 4
POPULATION = 300
TARGET_X = WIDTH / 2
TARGET_Y = 50
MUTATION_RATE = 0.01
PAREDE = pygame.Rect(150, 400, 300, 20)


def gene_aleatorio():
    theta = random.uniform(0, 2 * math.pi)
    thrust = random.uniform(0, MAX_THRUST)
    ax = thrust * math.cos(theta)
    ay = thrust * math.sin(theta)
    return [ax, ay]


class Rocket:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT - 20
        self.Speed_x = 0
        self.Speed_y = 0
        self.fitness = 0
        self.vivo = True
        self.DNA = []
        for _ in range(LIFE):
            self.DNA.append(gene_aleatorio())

    def update(self, frame):
        if not self.vivo:
            return
        ax, ay = self.DNA[frame]
        self.Speed_x += ax
        self.Speed_y += ay
        modulo = math.hypot(self.Speed_x, self.Speed_y)
        if modulo > MAX_SPEED:
            fator = MAX_SPEED / modulo
            self.Speed_x *= fator
            self.Speed_y *= fator
        self.x += self.Speed_x
        self.y += self.Speed_y
        if PAREDE.collidepoint(self.x, self.y):
            self.vivo = False

    def calc_fitness(self):
        d = math.hypot(self.x - TARGET_X, self.y - TARGET_Y)
        self.fitness = 1 / max(d, 1)
        if not self.vivo:
            self.fitness /= 10


def cruzar(mae, pai):
    corte = random.randint(0, LIFE)
    filho = Rocket()
    filho.DNA = mae.DNA[:corte] + pai.DNA[corte:]
    return filho


def mutar(filho):
    for i in range(LIFE):
        if random.random() < MUTATION_RATE:
            filho.DNA[i] = gene_aleatorio()


pygame.init()
tela = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Darwin Launchpad")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 28)

rodando = True
frame = 0
geracao = 1

rockets = []
for _ in range(POPULATION):
    rockets.append(Rocket())

while rodando:
    # 1. eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # 2. atualizar
    if frame < LIFE:
        for r in rockets:
            r.update(frame)
        frame += 1
    else:
        # avaliar
        weights = []
        for r in rockets:
            r.calc_fitness()
            weights.append(r.fitness)
        best = max(weights)
        print("geração:", geracao, "| melhor nota:", round(best, 4))

        # reproduzir
        nova_geracao = []
        for _ in range(POPULATION):
            mae, pai = random.choices(rockets, weights=weights, k=2)
            filho = cruzar(mae, pai)
            mutar(filho)
            nova_geracao.append(filho)

        # recomeçar
        rockets = nova_geracao
        frame = 0
        geracao += 1

    # 3. desenhar
    tela.fill((20, 20, 30))
    pygame.draw.rect(tela, (120, 120, 140), PAREDE)
    pygame.draw.circle(tela, (255, 0, 0), (TARGET_X, TARGET_Y), 6)
    for r in rockets:
        cor = (255, 255, 255) if r.vivo else (200, 60, 60)
        pygame.draw.circle(tela, cor, (r.x, r.y), 3)
    texto = fonte.render(f"Geração {geracao}", True, (200, 200, 200))
    tela.blit(texto, (10, 10))
    pygame.display.flip()

    # 4. esperar
    relogio.tick(60)

pygame.quit()