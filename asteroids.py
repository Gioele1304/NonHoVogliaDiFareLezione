import pygame, sys, math, random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()

# Colori
BLACK=(0,0,0); WHITE=(255,255,255)

font = pygame.font.SysFont(None, 32)

# Astronave
ship = pygame.Rect(WIDTH//2, HEIGHT//2, 20, 20)
ship_angle = 0
ship_speed = 0
lives = 3
score = 0

# Liste
bullets=[]
asteroids=[]

def spawn_asteroid():
    size=random.randint(30,60)
    x,y=random.choice([(random.randint(0,WIDTH),0),
                       (random.randint(0,WIDTH),HEIGHT),
                       (0,random.randint(0,HEIGHT)),
                       (WIDTH,random.randint(0,HEIGHT))])
    dx=random.choice([-2,-1,1,2])
    dy=random.choice([-2,-1,1,2])
    asteroids.append([pygame.Rect(x,y,size,size),dx,dy])

def draw_ship():
    # triangolo che ruota
    points=[]
    for i in [0,120,240]:
        ang=math.radians(ship_angle+i)
        x=ship.centerx+math.cos(ang)*15
        y=ship.centery+math.sin(ang)*15
        points.append((x,y))
    # corpo nave
    pygame.draw.polygon(screen, WHITE, points, 2)

    # punta evidenziata con arco
    tip_angle = math.radians(ship_angle)
    tip_x = ship.centerx + math.cos(tip_angle)*15
    tip_y = ship.centery + math.sin(tip_angle)*15

    # rettangolo che contiene l'arco
    arc_rect = pygame.Rect(tip_x-8, tip_y-8, 16, 16)

    # angoli dell'arco (in radianti)
    start_angle = tip_angle - math.pi/4   # 45° prima
    end_angle   = tip_angle + math.pi/4   # 45° dopo

    # disegna arco giallo
    pygame.draw.arc(screen, (255,255,0), arc_rect, start_angle, end_angle, 3)
                    
def move_ship():
    global ship
    ship.centerx+=math.cos(math.radians(ship_angle))*ship_speed
    ship.centery+=math.sin(math.radians(ship_angle))*ship_speed
    ship.centerx%=WIDTH
    ship.centery%=HEIGHT

def shoot():
    ang=math.radians(ship_angle)
    dx=math.cos(ang)*6; dy=math.sin(ang)*6
    bullets.append([pygame.Rect(ship.centerx,ship.centery,4,4),dx,dy])

def update_bullets():
    global score
    for b in bullets[:]:
        b[0].x+=b[1]; b[0].y+=b[2]
        if b[0].x<0 or b[0].x>WIDTH or b[0].y<0 or b[0].y>HEIGHT:
            bullets.remove(b)
        else:
            for a in asteroids[:]:
                if b[0].colliderect(a[0]):
                    bullets.remove(b)
                    asteroids.remove(a)
                    score+=10
                    if a[0].width>20:
                        # frammenta
                        for _ in range(2):
                            new_size=a[0].width//2
                            dx=random.choice([-2,-1,1,2])
                            dy=random.choice([-2,-1,1,2])
                            rect=pygame.Rect(a[0].x,a[0].y,new_size,new_size)
                            asteroids.append([rect,dx,dy])
                    break

def update_asteroids():
    global lives
    for a in asteroids:
        a[0].x+=a[1]; a[0].y+=a[2]
        a[0].x%=WIDTH; a[0].y%=HEIGHT
        if a[0].colliderect(ship):
            lives-=1
            asteroids.remove(a)
            if lives<=0:
                game_over()

def game_over():
    while True:
        screen.fill(BLACK)
        text1=font.render("GAME OVER",True,WHITE)
        text2=font.render("Q=Quit  E=Restart",True,WHITE)
        screen.blit(text1,(WIDTH//2-80,HEIGHT//2-40))
        screen.blit(text2,(WIDTH//2-100,HEIGHT//2))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_q: pygame.quit(); sys.exit()
                if e.key==pygame.K_e: restart_game(); return

def restart_game():
    global ship,ship_angle,ship_speed,lives,score,bullets,asteroids
    ship=pygame.Rect(WIDTH//2,HEIGHT//2,20,20)
    ship_angle=0; ship_speed=0
    lives=3; score=0
    bullets=[]; asteroids=[]
    for _ in range(5): spawn_asteroid()

# Inizio
restart_game()

# Loop principale
while True:
    for e in pygame.event.get():
        if e.type==pygame.QUIT: pygame.quit(); sys.exit()
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_SPACE: shoot()

    keys=pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: ship_angle-=5
    if keys[pygame.K_RIGHT]: ship_angle+=5
    if keys[pygame.K_UP]: ship_speed=min(ship_speed+0.2,6)
    if keys[pygame.K_DOWN]: ship_speed=max(ship_speed-0.2,0)

    move_ship()
    update_bullets()
    update_asteroids()

    screen.fill(BLACK)
    draw_ship()
    for b in bullets: pygame.draw.rect(screen,WHITE,b[0])
    for a in asteroids: pygame.draw.circle(screen,WHITE,a[0].center,a[0].width//2,1)
    hud=font.render(f"Score:{score} Lives:{lives}",True,WHITE)
    screen.blit(hud,(10,10))
    pygame.display.flip()
    clock.tick(60)
