#Andra 2020 11/02/2020
#Help from https://www.youtube.com/channel/UCYNrBrBOgTfHswcz2DdZQFA "DaFluffyPotato"

import pygame, random, sys, os

clock = pygame.time.Clock()

from pygame.locals import*
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(64)


vertical_momentum = 0
air_timer = 0
Window_size = (600,400)
display = pygame.Surface((300,200))
pygame.display.set_caption("GameV2")

screen = pygame.display.set_mode(Window_size, 0, 32)

grass = pygame.image.load("Sprites/GroundGrass.png")
dirt = pygame.image.load("Sprites/Ground.png")

player_location = [50,50]
player_y_momentum = 0

grass_sound_timer = 0


true_scroll = [0,0]

jump_sound = pygame.mixer.Sound("jump.wav")
grass_sounds = [pygame.mixer.Sound("grass_0.wav"),pygame.mixer.Sound("grass_1.wav")]
grass_sounds[0].set_volume(0.2)
grass_sounds[1].set_volume(0.2)
jump_sound.set_volume(0.1)

pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)

player_rect = pygame.Rect(100,100,18,52)
moving_left = False
moving_right = False
background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]


def load_map(path):
    f = open(path + ".txt", "r")
    data = f.read()
    f.close()
    data = data.split("\n")
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

game_map = load_map("world")

global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split("/")[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + "_" + str(n)
        img_loc = path + "/" + animation_frame_id + ".png"
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((0,0,0))
        animation_frames [animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        
        n += 1
    return animation_frame_data

animation_database = {}

animation_database["Walk"] = load_animation ("Sprites/Walk",[5,5,5,5])
animation_database["Idle"] = load_animation ("Sprites/Idle",[40,7,40,7])
animation_database["Attack"] = load_animation ("Sprites/Attack",[5,5,5])
animation_database["Crawl"] = load_animation ("Sprites/Crawl",[5,5,5,5])
animation_database["Crouch"] = load_animation ("Sprites/Crouch",[20,7])
animation_database["Stab"] = load_animation ("Sprites/Stab",[6,5])

def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame

player_action = "Idle"
player_frame = 0
player_flip = False

def collision_test (rect,tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect,movement,tiles):
    collision_types = {"top":False,"bottom":False,"right":False,"left":False}
    rect.x += movement[0]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types["right"] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types["left"] = True
    rect.y += movement[1]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types["bottom"] = True
        elif movement[1] <0:
            rect.top = tile.bottom
            collision_types["top"] = True
    return rect, collision_types
ATK = 0
Crouch = 0
Crawl = 0
Crawl_key_1 = 0
Crawl_key_2 = 0
Crawl_key_3 = 0



        
while True:
    display.fill((146,244,255)) # clear screen by filling it with blue

    if grass_sound_timer > 0:
        grass_sound_timer -= 1

    true_scroll[0] += (player_rect.x-true_scroll[0]-159)/20
    true_scroll[1] += (player_rect.y-true_scroll[1]-123)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    pygame.draw.rect(display, (7,80,75), pygame.Rect(0,120,300,80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0]-scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14,222,150),obj_rect)
        else:
            pygame.draw.rect(display, (9,91,85),obj_rect)
                            
                            
    
    tile_rects = []
    y = 0
    for layer in game_map:
        x = 0
        for tile in layer:
            if tile == '1':
                display.blit(dirt,(x*16-scroll[0],y*16-scroll[1]))
            if tile == '2':
                display.blit(grass,(x*16-scroll[0],y*16-scroll[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect(x*16,y*16,16,16))
            x += 1
        y += 1

    player_movement = [0,0]
    if moving_right == True:
        player_movement[0] += 2
    if moving_left == True:
        player_movement[0] -= 2
    player_movement[1] += vertical_momentum
    vertical_momentum += 0.2
    if vertical_momentum > 3:
        vertical_momentum = 3

    if player_movement[0] > 0:
        if Crawl_key_1 == 0:
            player_action,player_frame = change_action(player_action,player_frame,"Walk")
            player_flip = False
        elif Crawl_key_1 == 1:
            if Crawl_key_2 == 1:
                player_action,player_frame = change_action(player_action,player_frame,"Crawl")
                player_flip = False
            else:
                player_action,player_frame = change_action(player_action,player_frame,"Walk")
                player_flip = False
            
    if player_movement[0] == 0:
        if Crouch == 0:
            if ATK == 1:
                player_action,player_frame = change_action(player_action,player_frame,"Attack")
            elif ATK == 0:
                player_action,player_frame = change_action(player_action,player_frame,"Idle")
        elif Crouch == 1:
            if ATK == 1:
                player_action,player_frame = change_action(player_action,player_frame,"Stab")
                
            elif ATK == 0:
                player_action,player_frame = change_action(player_action,player_frame,"Crouch")
                
            
    if player_movement[0] < 0:
        if Crawl_key_1 == 0:
            player_action,player_frame = change_action(player_action,player_frame,"Walk")
            player_flip = True
        elif Crawl_key_1 == 1:
            if Crawl_key_3 == 1:
                player_action,player_frame = change_action(player_action,player_frame,"Crawl")
                player_flip = True
            else:
                player_action,player_frame = change_action(player_action,player_frame,"Walk")
                player_flip = True
                


    player_rect,collisions = move(player_rect,player_movement,tile_rects)

    if collisions['bottom'] == True:
        air_timer = 0
        vertical_momentum = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 30
                random.choice(grass_sounds).play()
    else:
        air_timer += 1

        
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img,player_flip,False),(player_rect.x-scroll[0],player_rect.y-scroll[1]))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == KEYDOWN:
            if event.key == K_n:
                pygame.mixer.music.fadeout(1500)
            if event.key == K_m:
                pygame.mixer.music.play(-1)
            if event.key == K_d:
                moving_right = True
                Crawl_key_2 = 1
            if event.key == K_a:
                moving_left = True
                Crawl_key_3 = 1
            if event.key == K_w:
                if air_timer < 6:
                    jump_sound.play()
                    vertical_momentum = -5
            if event.key == K_e:
                ATK = 1
            if event.key == K_LCTRL:
                Crouch = 1
                Crawl_key_1 = 1
                
        if event.type == KEYUP:
            if event.key == K_d:
                moving_right = False
                Crawl_key_2 = 0
            if event.key == K_a:
                Crawl_key_3 = 0
                moving_left = False
            if event.key == K_LCTRL:
                Crouch = 0
                Crawl_key_1 = 0
            if event.key == K_e:
                ATK = 0
                

            
                
    screen.blit(pygame.transform.scale(display,Window_size),(0,0))
    pygame.display.update()
    clock.tick(60)


