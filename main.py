# -----------------------------------------------
# #Projet : Kung-Fu PandaRoux
#Auteurs : Maxence Andrivon, Hugo Dupuis, Anais Najac, Come de La Serre
# -----------------------------------------------


import pyxel
import pygame
import random
import math

# -----------------------------------------------
# Sons (pygame.mixer)
# -----------------------------------------------
pygame.mixer.init()
musique         = pygame.mixer.Sound("default_theme.wav")
son_collectible = pygame.mixer.Sound("item_collected.mp3")
son_victoire    = pygame.mixer.Sound("game_bonus.mp3")
son_game_over   = pygame.mixer.Sound("game_over.mp3")
son_portail     = pygame.mixer.Sound("portal.mp3")

# -----------------------------------------------
# Fenêtre Pyxel
# -----------------------------------------------
LARGEUR = 256
HAUTEUR = 160
SOL_Y   = 128

pyxel.init(LARGEUR, HAUTEUR, title="Kung Fu Panda Roux")
pyxel.load("nsi.pyxres")

# -----------------------------------------------
# Animations panda (bank 1)
# -----------------------------------------------
FRAMES_MARCHE = [(0,0),(40,0),(80,0),(120,0),(160,0),(200,0)]
FRAMES_SAUT   = [(0,32),(40,32)]

# -----------------------------------------------
# Sprites dans mon pyxres (positions)
# bank1 y=97 x=0  : coeur plein  (8x8)
# bank1 y=97 x=8  : coeur vide   (8x8)
# bank1 y=97 x=16 : braconnier gauche (32x32)
# bank1 y=105 x=16: monstre   (32x32)
# bank0 y=161 x=0 : Mont Fuji (256x95)
# -----------------------------------------------

# -----------------------------------------------
# Monde - NIVEAU 1 
# -----------------------------------------------
MONDE_N1       = 2000
PORTAIL_X      = 1880   # position du portail en fin de niveau

# Plateformes niveau 1 : plus jolies, collant au décor
PLAT_N1 = [
    [180,  SOL_Y-28, 48],
    [340,  SOL_Y-52, 48],
    [520,  SOL_Y-36, 32],
    [690,  SOL_Y-62, 64],
    [900,  SOL_Y-42, 48],
    [1070, SOL_Y-70, 48],
    [1250, SOL_Y-48, 32],
    [1430, SOL_Y-74, 64],
    [1620, SOL_Y-55, 48],
    [1800, SOL_Y-38, 32],
]

BAMBOUS_N1 = [60,110,200,260,360,440,540,620,730,820,960,1050,
              1180,1290,1410,1520,1650,1770,1900]

# -----------------------------------------------
# Monde - NIVEAU 2 (forêt sombre + monstres)
# -----------------------------------------------
MONDE_N2 = 1600

PLAT_N2 = [
    [160,  SOL_Y-32, 48],
    [380,  SOL_Y-55, 48],
    [600,  SOL_Y-40, 32],
    [800,  SOL_Y-65, 48],
    [1050, SOL_Y-48, 64],
    [1300, SOL_Y-60, 32],
]

# Positions des monstres chapeaux
MONSTRES_POS_N2 = [400, 700, 1000, 1350]

# Arbres sombres pour le fond niveau 2
random.seed(77)
ARBRES_N2 = [random.randint(0, MONDE_N2) for _ in range(40)]
ARBRES_N2.sort()

# Étoiles fixes pour le ciel niveau 2
random.seed(55)
ETOILES = [(random.randint(0, LARGEUR-1), random.randint(2, 85)) for _ in range(60)]

# -----------------------------------------------
# Dialogues d'intro
# -----------------------------------------------
DIALOGUES = [
    "ROUX : Hmmm... ou suis-je ?",
    "       Je crois que je suis perdu...",
    "       Ou est ma famille ? Je dois la retrouver !",
    "ENNEMI : Ou est le dernier panda roux ?",
    "ROUX : Parfois il faut se battre !"
]

# -----------------------------------------------
# Variables globales
# -----------------------------------------------
etat       = "titre"
niveau     = 1
score      = 0
titre_cpt  = 0

# Joueur
joueur_x       = 50.0
joueur_y       = float(SOL_Y - 32)
joueur_vit_y   = 0.0
joueur_sol     = True
joueur_dir     = 1
joueur_vies    = 3
joueur_invinc  = 0
joueur_ani_cpt = 0
joueur_frame   = 0
griffe_cd      = 0

# Caméra
camera_x = 0.0

# Braconnier (niveau 1)
brac_x      = 600.0
brac_y      = float(SOL_Y - 32)
brac_vies   = 5
brac_invinc = 0
brac_mort   = False
brac_mort_t = 0
brac_tir_cd = 0

# Monstres chapeau (niveau 2) : [x, y, hp, invinc, mort, mort_t, dir]
monstres = []

# Projectiles
griffes = []   # [x, y, vx]
balles  = []   # [x, y, vx]

# Pommes de soin
pommes_n1 = [[350.0,float(SOL_Y-20),False],[800.0,float(SOL_Y-20),False],
             [1200.0,float(SOL_Y-20),False],[1600.0,float(SOL_Y-20),False]]
pommes = []

# Portail
portail_traverse = False

# Dialogues
dia_index = 0
dia_char  = 0
dia_texte = ""
dia_cpt   = 0

# -----------------------------------------------
# Fonctions utilitaires
# -----------------------------------------------
def get_plateformes():
    return PLAT_N1 if niveau == 1 else PLAT_N2

def get_monde_larg():
    return MONDE_N1 if niveau == 1 else MONDE_N2

def collision_plateformes():
    global joueur_y, joueur_vit_y, joueur_sol
    bas = joueur_y + 32
    gau = joueur_x + 4
    droi = joueur_x + 28
    for plat in get_plateformes():
        px, py, pl = plat[0], plat[1], plat[2]
        if (droi > px and gau < px+pl and
                bas >= py and bas <= py+10 and joueur_vit_y >= 0):
            joueur_y     = float(py - 32)
            joueur_vit_y = 0
            joueur_sol   = True

def init_niveau_1():
    """Initialise ou réinitialise le niveau 1"""
    global joueur_x,joueur_y,joueur_vit_y,joueur_sol,joueur_dir
    global joueur_vies,joueur_invinc,joueur_ani_cpt,joueur_frame,griffe_cd
    global brac_x,brac_y,brac_vies,brac_invinc,brac_mort,brac_mort_t,brac_tir_cd
    global camera_x,score,portail_traverse,pommes
    joueur_x=50.0; joueur_y=float(SOL_Y-32); joueur_vit_y=0.0
    joueur_sol=True; joueur_dir=1; joueur_vies=3
    joueur_invinc=0; joueur_ani_cpt=0; joueur_frame=0; griffe_cd=0
    brac_x=600.0; brac_y=float(SOL_Y-32); brac_vies=5
    brac_invinc=0; brac_mort=False; brac_mort_t=0; brac_tir_cd=0
    camera_x=0.0; portail_traverse=False
    griffes.clear(); balles.clear()
    pommes.clear()
    for p in pommes_n1: pommes.append([p[0],p[1],False])

def init_niveau_2():
    """Initialise ou réinitialise le niveau 2"""
    global joueur_x,joueur_y,joueur_vit_y,joueur_sol,joueur_dir
    global joueur_vies,joueur_invinc,joueur_ani_cpt,joueur_frame,griffe_cd
    global camera_x,score
    joueur_x=50.0; joueur_y=float(SOL_Y-32); joueur_vit_y=0.0
    joueur_sol=True; joueur_dir=1; joueur_vies=3
    joueur_invinc=0; joueur_ani_cpt=0; joueur_frame=0; griffe_cd=0
    camera_x=0.0
    griffes.clear(); balles.clear(); pommes.clear()
    monstres.clear()
    for x in MONSTRES_POS_N2:
        monstres.append([float(x), float(SOL_Y-32), 3, 0, False, 0, 1])

# -----------------------------------------------
# Dessin du décor niveau 1 (Fuji + bambous)
# -----------------------------------------------
def dessiner_decor_n1():
    # Ciel
    for y in range(SOL_Y):
        c = 6 if y < 60 else 12
        pyxel.line(0, y, LARGEUR, y, c)

    # Mont Fuji depuis le pyxres (bank0, x=0, y=161, 256x95)
    pyxel.blt(0, SOL_Y-95, 0, 0, 161, 256, 95, 12)

    # Bambous
    for bx in BAMBOUS_N1:
        sx = int(bx - camera_x)
        if -32 < sx < LARGEUR+32:
            pyxel.blt(sx, SOL_Y-32, 0, 80, 80, 32, 32, 12)

    # Sol
    dec = int(camera_x) % 16
    for tx in range(-dec, LARGEUR+16, 16):
        pyxel.blt(tx, SOL_Y, 0, 0, 120, 16, 16, 12)

    # Plateformes (tuiles d'herbe/terre)
    for plat in PLAT_N1:
        sx = int(plat[0] - camera_x)
        py = plat[1]
        larg = plat[2]
        if -larg < sx < LARGEUR+larg:
            pyxel.rect(sx, py+4, larg, 12, 4)   # terre brune
            pyxel.rect(sx, py,   larg,  4, 3)    # herbe verte
            pyxel.rect(sx, py,   larg,  1, 11)   # ligne herbe claire

# -----------------------------------------------
# Dessin du décor niveau 2 (forêt sombre)
# -----------------------------------------------
def dessiner_decor_n2():
    # Ciel très sombre
    for y in range(SOL_Y):
        c = 1 if y < 75 else 5
        pyxel.line(0, y, LARGEUR, y, c)

    # Lune croissante
    pyxel.circ(200, 18, 14, 7)
    pyxel.circ(206, 14, 10, 1)

    # Étoiles fixes
    for ex, ey in ETOILES:
        if (pyxel.frame_count // 30 + ex) % 7 != 0:
            pyxel.pset(ex, ey, 7)

    # Arbres sombres en fond
    for i, tx in enumerate(ARBRES_N2):
        sx = int(tx - camera_x * 0.4)
        if -30 < sx < LARGEUR+30:
            h_arbre = 40 + (i % 5)*8
            pyxel.rect(sx-3, SOL_Y-h_arbre, 6, h_arbre, 0)
            pyxel.tri(sx-16, SOL_Y-h_arbre,
                      sx+16, SOL_Y-h_arbre,
                      sx,    SOL_Y-h_arbre-32, 1)
            pyxel.tri(sx-11, SOL_Y-h_arbre-10,
                      sx+11, SOL_Y-h_arbre-10,
                      sx,    SOL_Y-h_arbre-38, 0)

    # Sol
    dec = int(camera_x) % 16
    for tx in range(-dec, LARGEUR+16, 16):
        pyxel.blt(tx, SOL_Y, 0, 0, 120, 16, 16, 12)

    # Brume au sol
    for tx in range(0, LARGEUR, 3):
        if (tx + pyxel.frame_count//4) % 5 < 3:
            pyxel.pset(tx, SOL_Y-2, 6)
            pyxel.pset(tx+1, SOL_Y-3, 5)

    # Plateformes niveau 2 (plus sombres)
    for plat in PLAT_N2:
        sx = int(plat[0] - camera_x)
        py = plat[1]
        larg = plat[2]
        if -larg < sx < LARGEUR+larg:
            pyxel.rect(sx, py+4, larg, 12, 1)   # pierre sombre
            pyxel.rect(sx, py,   larg,  4, 0)    # dessus noir
            pyxel.rect(sx, py,   larg,  1, 5)    # ligne sombre

# -----------------------------------------------
# Dessin du portail (animé, en code)
# -----------------------------------------------
def dessiner_portail():
    if portail_traverse: return
    sx = int(PORTAIL_X - camera_x)
    if not (-25 < sx < LARGEUR+25): return

    t = pyxel.frame_count
    cy = SOL_Y - 25

    # Piliers
    pyxel.rect(sx,    cy-20, 5, 45, 2)
    pyxel.rect(sx+15, cy-20, 5, 45, 2)
    pyxel.rect(sx+1,  cy-20, 3, 45, 13)
    pyxel.rect(sx+16, cy-20, 3, 45, 13)

    # Arche
    pyxel.circb(sx+10, cy-20, 10, 13)
    pyxel.circb(sx+10, cy-20,  9, 2)

    # Tourbillon animé (cercles concentriques qui pulsent)
    couleurs = [13, 2, 1, 13, 2]
    for i in range(5):
        r = 3 + i*2 + int(pyxel.sin(t*20 + i*45) * 1.5)
        pyxel.circb(sx+10, cy, r, couleurs[i % len(couleurs)])

    # Centre brillant
    pyxel.pset(sx+10, cy, 7)
    pyxel.pset(sx+9,  cy, 13)
    pyxel.pset(sx+11, cy, 13)

    # Texte indicatif
    if (t // 20) % 2 == 0:
        pyxel.text(sx-12, cy-35, "PORTAIL", 13)

# -----------------------------------------------
# Dessin du joueur
# -----------------------------------------------
def dessiner_joueur():
    if joueur_invinc > 0 and (joueur_invinc//4)%2 == 1:
        return
    if not joueur_sol:
        u, v = FRAMES_SAUT[0]
    elif (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_RIGHT) or
          pyxel.btn(pyxel.KEY_A)    or pyxel.btn(pyxel.KEY_D)):
        u, v = FRAMES_MARCHE[joueur_frame]
    else:
        u, v = FRAMES_MARCHE[0]
    sx = int(joueur_x - camera_x)
    sy = int(joueur_y)
    w  = 40 * joueur_dir
    ox = 40 if joueur_dir == -1 else 0
    pyxel.blt(sx+ox, sy, 1, u, v, w, 32, 12)

# -----------------------------------------------
# Dessin du braconnier (avec 2 faces)
# bank1 x=0  y=64 : face droite (original)
# bank1 x=16 y=97 : face gauche (miroir)
# -----------------------------------------------
def dessiner_braconnier():
    if brac_mort:
        if brac_mort_t < 30 and (brac_mort_t//5)%2 == 0:
            sx = int(brac_x - camera_x)
            pyxel.blt(sx, int(brac_y), 1, 0, 64, 32, 32, 12)
        return
    sx = int(brac_x - camera_x)
    if not (-32 < sx < LARGEUR+32): return
    if brac_invinc > 0 and (brac_invinc//4)%2 == 1: return

    dx = joueur_x - brac_x
    if dx >= 0:
        # Joueur à droite → face droite (original)
        pyxel.blt(sx, int(brac_y), 1, 0, 64, 32, 32, 12)
    else:
        # Joueur à gauche → face gauche (sprite miroir)
        pyxel.blt(sx, int(brac_y), 1, 16, 97, 32, 32, 12)

    # Barre de vie
    barre_y = int(brac_y) - 7
    pyxel.rect(sx, barre_y, 32, 4, 0)
    pyxel.rect(sx, barre_y, int(32*brac_vies/5), 4, 8)

# -----------------------------------------------
# Dessin des monstres chapeau (niveau 2)
# bank1 x=16 y=105 : sprite 32x32
# -----------------------------------------------
def dessiner_monstres():
    for m in monstres:
        mx, my, mhp, minv, mmort, mmt, mdir = m
        sx = int(mx - camera_x)
        if not (-32 < sx < LARGEUR+32): continue
        if mmort:
            if mmt < 28 and (mmt//5)%2 == 0:
                pyxel.blt(sx, int(my), 1, 16, 105, 32, 32, 12)
            continue
        if minv > 0 and (minv//4)%2 == 1: continue
        # Flip selon direction
        w  = 32 if mdir > 0 else -32
        ox = 0  if mdir > 0 else 32
        pyxel.blt(sx+ox, int(my), 1, 16, 105, w, 32, 12)
        # Barre de vie
        barre_y = int(my) - 7
        pyxel.rect(sx, barre_y, 32, 4, 0)
        pyxel.rect(sx, barre_y, int(32*mhp/3), 4, 8)

# -----------------------------------------------
# Dessin des griffes et balles
# -----------------------------------------------
def dessiner_griffes():
    for g in griffes:
        sx = int(g[0] - camera_x)
        if -22 < sx < LARGEUR+22:
            w  = 22 if g[2] > 0 else -22
            ox = 22 if g[2] < 0 else 0
            pyxel.blt(sx+ox, int(g[1]), 0, 16, 64, w, 16, 12)

def dessiner_balles():
    for b in balles:
        sx = int(b[0] - camera_x)
        if -10 < sx < LARGEUR+10:
            pyxel.circ(sx+4, int(b[1])+4, 4, 9)
            pyxel.circ(sx+4, int(b[1])+4, 2, 10)

def dessiner_pommes():
    for p in pommes:
        if not p[2]:
            sx = int(p[0] - camera_x)
            if -16 < sx < LARGEUR+16:
                pyxel.blt(sx, int(p[1]), 0, 0, 64, 16, 16, 12)

# -----------------------------------------------
# HUD avec cœurs Zelda
# bank1 y=97 x=0: plein, x=8: vide
# -----------------------------------------------
def dessiner_hud():
    for i in range(3):
        cx = 5 + i*11
        if i < joueur_vies:
            pyxel.blt(cx, 4, 1, 0, 97, 8, 8, 12)   # coeur plein
        else:
            pyxel.blt(cx, 4, 1, 8, 97, 8, 8, 12)   # coeur vide

    pyxel.text(LARGEUR-52, 4, f"Score:{score}", 7)

    niv_txt = f"N{niveau}"
    pyxel.text(LARGEUR//2-8, 4, niv_txt, 10)

    if griffe_cd == 0:
        pyxel.text(4, HAUTEUR-8, "X:Griffe  Fleches:Bouger", 6)
    else:
        pyxel.text(4, HAUTEUR-8, "X:Griffe  Fleches:Bouger", 5)

# -----------------------------------------------
# Écran titre
# -----------------------------------------------
def dessiner_titre():
    pyxel.cls(1)
    pyxel.blt(0, 100-95, 0, 0, 161, 256, 95, 12)
    pyxel.rect(0, 100, LARGEUR, HAUTEUR-100, 3)
    bob = int(pyxel.sin(titre_cpt*6)*3)
    pyxel.blt(LARGEUR//2-20, 72+bob, 1, 0, 0, 40, 32, 12)
    pyxel.text(LARGEUR//2-44,  8,  "KUNG FU PANDA ROUX", 10)
    pyxel.text(LARGEUR//2-40, 18,  "Retrouve ta famille !",  7)
    pyxel.text(LARGEUR//2-48,108,  "Fleches ou WASD : Bouger", 7)
    pyxel.text(LARGEUR//2-36,116,  "Haut / Espace : Sauter",  7)
    pyxel.text(LARGEUR//2-20,124,  "X : Attaquer",            7)
    pyxel.text(LARGEUR//2-28,134,  "Recupere les pommes",    14)
    pyxel.text(LARGEUR//2-24,142,  "pour regagner des PV",   14)
    if (titre_cpt//20)%2 == 0:
        pyxel.text(LARGEUR//2-44,152, "[ ESPACE ] pour jouer", 10)

# -----------------------------------------------
# Écran dialogue
# -----------------------------------------------
def dessiner_dialogue():
    dessiner_decor_n1()
    dessiner_joueur()
    pyxel.rect(4, 96, LARGEUR-8, 52, 1)
    pyxel.rectb(4, 96, LARGEUR-8, 52, 7)
    pyxel.rectb(5, 97, LARGEUR-10, 50, 6)
    pyxel.text(10, 104, dia_texte, 7)
    if dia_index < len(DIALOGUES) and dia_char >= len(DIALOGUES[dia_index]):
        if (pyxel.frame_count//15)%2 == 0:
            pyxel.text(LARGEUR-46, 138, "[ESPACE]", 10)
    if dia_index >= len(DIALOGUES):
        pyxel.text(LARGEUR//2-44, 118, "Bonne chance, Roux !", 10)
        if (pyxel.frame_count//15)%2 == 0:
            pyxel.text(LARGEUR-46, 138, "[ESPACE]", 10)

# -----------------------------------------------
# Écran de fin (victoire ou game over)
# -----------------------------------------------
def dessiner_fin():
    if etat == "victoire":
        pyxel.rect(35, 50, 186, 60, 0)
        pyxel.rectb(35, 50, 186, 60, 10)
        pyxel.text(78, 60, "VICTOIRE !", 10)
        pyxel.text(65, 75, "Ta famille est sauvee !", 7)
    else:
        pyxel.rect(43, 50, 170, 60, 0)
        pyxel.rectb(43, 50, 170, 60, 8)
        pyxel.text(88, 60, "PERDU...", 8)
    pyxel.text(72, 90, f"Score : {score}", 7)
    pyxel.text(58, 104, "[R] pour rejouer", 6)

# -----------------------------------------------
# UPDATE titre
# -----------------------------------------------
def update_titre():
    global etat, titre_cpt
    titre_cpt += 1
    if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
        musique.play(loops=-1)
        etat = "dialogue"

# -----------------------------------------------
# UPDATE dialogue
# -----------------------------------------------
def update_dialogue():
    global dia_index, dia_char, dia_texte, dia_cpt, etat
    dia_cpt += 1
    if dia_index < len(DIALOGUES):
        if dia_cpt % 2 == 0 and dia_char < len(DIALOGUES[dia_index]):
            dia_char += 1
            dia_texte = DIALOGUES[dia_index][:dia_char]
    if pyxel.btnp(pyxel.KEY_SPACE):
        if dia_index < len(DIALOGUES):
            if dia_char >= len(DIALOGUES[dia_index]):
                dia_index += 1; dia_char = 0; dia_texte = ""; dia_cpt = 0
            else:
                dia_char = len(DIALOGUES[dia_index])
                dia_texte = DIALOGUES[dia_index]
        else:
            init_niveau_1()
            etat = "jeu"

# -----------------------------------------------
# UPDATE jeu (niveau 1 et 2)
# -----------------------------------------------
def update_jeu():
    global joueur_x,joueur_y,joueur_vit_y,joueur_sol,joueur_dir
    global joueur_vies,joueur_invinc,joueur_ani_cpt,joueur_frame,griffe_cd
    global brac_x,brac_vies,brac_invinc,brac_mort,brac_mort_t,brac_tir_cd
    global camera_x,score,etat,niveau,portail_traverse

    # ── Déplacement joueur ────────────────────────────────
    deplacement = False
    if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
        joueur_x -= 2; joueur_dir = -1; deplacement = True
    if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
        joueur_x += 2; joueur_dir =  1; deplacement = True

    if (pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W) or
            pyxel.btnp(pyxel.KEY_SPACE)) and joueur_sol:
        joueur_vit_y = -6; joueur_sol = False

    joueur_vit_y += 0.4
    joueur_y     += joueur_vit_y
    joueur_sol    = False

    if joueur_y >= SOL_Y-32:
        joueur_y=float(SOL_Y-32); joueur_vit_y=0; joueur_sol=True

    collision_plateformes()

    lm = get_monde_larg()
    joueur_x = max(0, min(joueur_x, lm-32))

    if deplacement and joueur_sol:
        joueur_ani_cpt += 1
        if joueur_ani_cpt >= 6:
            joueur_ani_cpt = 0
            joueur_frame = (joueur_frame+1) % len(FRAMES_MARCHE)
    else:
        joueur_ani_cpt = 0

    if joueur_invinc > 0: joueur_invinc -= 1
    if griffe_cd > 0:     griffe_cd -= 1

    # ── Lancer une griffe ─────────────────────────────────
    if pyxel.btnp(pyxel.KEY_X) and griffe_cd == 0:
        vx = 4 if joueur_dir == 1 else -4
        ox = 30 if joueur_dir == 1 else -22
        griffes.append([joueur_x+ox, joueur_y+10, vx])
        griffe_cd = 18

    # ── Caméra ────────────────────────────────────────────
    cible = joueur_x - LARGEUR//2
    camera_x = max(0, min(cible, lm-LARGEUR))

    # ── Griffes ───────────────────────────────────────────
    for g in griffes[:]:
        g[0] += g[2]
        if g[0]<camera_x-30 or g[0]>camera_x+LARGEUR+30:
            griffes.remove(g)

    # ── Balles ────────────────────────────────────────────
    for b in balles[:]:
        b[0] += b[2]
        if b[0]<camera_x-20 or b[0]>camera_x+LARGEUR+20:
            balles.remove(b)

    # ── Ramasser les pommes ───────────────────────────────
    for p in pommes:
        if not p[2] and abs(joueur_x-p[0])<20 and abs(joueur_y-p[1])<20:
            p[2]=True; joueur_vies=min(3,joueur_vies+1); score+=20
            son_collectible.play()

    # ════════════════════════════════════════════════════════
    # NIVEAU 1 : braconnier + portail
    # ════════════════════════════════════════════════════════
    if niveau == 1:

        # Portail : vérifier si le joueur le traverse
        if not portail_traverse:
            if joueur_x+16 > PORTAIL_X and joueur_x < PORTAIL_X+20:
                portail_traverse = True
                musique.stop()
                son_portail.play()
                # Transition vers niveau 2
                niveau = 2
                init_niveau_2()
                musique.play(loops=-1)
                return

        if not brac_mort:
            if brac_invinc > 0: brac_invinc -= 1
            if brac_tir_cd > 0: brac_tir_cd -= 1

            dx = joueur_x - brac_x
            dist = abs(dx)

            if dist > 140:
                brac_x += 0.7*(1 if dx>0 else -1)
            elif dist < 55:
                brac_x -= 0.9*(1 if dx>0 else -1)
            else:
                if brac_tir_cd == 0:
                    # Tir dans la bonne direction
                    vx_balle = 2.5 if dx>0 else -2.5
                    # Spawn balle du bon côté selon direction
                    bx_spawn = brac_x+28 if dx>0 else brac_x
                    balles.append([bx_spawn, brac_y+14, vx_balle])
                    brac_tir_cd = 80

            brac_x = max(0, min(brac_x, MONDE_N1-32))

            # Griffes → braconnier
            if brac_invinc == 0:
                for g in griffes[:]:
                    if abs(g[0]-brac_x)<28 and abs(g[1]-brac_y)<28:
                        griffes.remove(g); brac_vies-=1
                        brac_invinc=30; score+=10
                        if brac_vies <= 0:
                            brac_mort=True; score+=50
                            musique.stop(); son_victoire.play()
                            etat="victoire"
                        break

            # Balles → joueur
            if joueur_invinc == 0:
                for b in balles[:]:
                    if abs(b[0]-joueur_x)<24 and abs(b[1]-joueur_y)<24:
                        balles.remove(b); joueur_vies-=1
                        joueur_invinc=70
                        if joueur_vies<=0:
                            musique.stop(); son_game_over.play()
                            etat="game_over"
                        break

            # Contact braconnier → joueur
            if joueur_invinc==0 and abs(joueur_x-brac_x)<26 and abs(joueur_y-brac_y)<26:
                joueur_vies-=1; joueur_invinc=90
                if joueur_vies<=0:
                    musique.stop(); son_game_over.play(); etat="game_over"

        else:
            brac_mort_t += 1

    # ════════════════════════════════════════════════════════
    # NIVEAU 2 : monstres chapeaux
    # ════════════════════════════════════════════════════════
    else:
        tous_morts = True
        for i, m in enumerate(monstres):
            mx, my, mhp, minv, mmort, mmt, mdir = m
            if not mmort:
                tous_morts = False
                if minv > 0: monstres[i][3] -= 1

                dx = joueur_x - mx
                dist = abs(dx)
                monstres[i][6] = 1 if dx>0 else -1  # direction

                if dist > 90:
                    monstres[i][0] += 0.9*(1 if dx>0 else -1)
                elif dist < 35:
                    monstres[i][0] -= 0.7*(1 if dx>0 else -1)
                # Dans la zone intermédiaire : reste en place

                monstres[i][0] = max(0, min(monstres[i][0], MONDE_N2-32))

                # Griffes → monstre
                if minv == 0:
                    for g in griffes[:]:
                        if abs(g[0]-mx)<28 and abs(g[1]-my)<28:
                            griffes.remove(g)
                            monstres[i][2] -= 1  # hp
                            monstres[i][3] = 28   # invincible
                            score += 10
                            if monstres[i][2] <= 0:
                                monstres[i][4] = True   # mort
                                monstres[i][5] = 0       # timer mort
                                score += 40
                            break

                # Contact monstre → joueur
                if joueur_invinc==0 and abs(joueur_x-mx)<26 and abs(joueur_y-my)<26:
                    joueur_vies-=1; joueur_invinc=90
                    if joueur_vies<=0:
                        musique.stop(); son_game_over.play(); etat="game_over"
            else:
                monstres[i][5] += 1  # timer mort

        # Balles → joueur (monstres n'en ont pas, mais au cas où)
        if joueur_invinc==0:
            for b in balles[:]:
                if abs(b[0]-joueur_x)<24 and abs(b[1]-joueur_y)<24:
                    balles.remove(b); joueur_vies-=1; joueur_invinc=70
                    if joueur_vies<=0:
                        musique.stop(); son_game_over.play(); etat="game_over"
                    break

        if tous_morts:
            musique.stop(); son_victoire.play(); etat="victoire"

# -----------------------------------------------
# UPDATE fin (victoire ou game over)
# -----------------------------------------------
def update_fin():
    global etat, niveau, score
    if pyxel.btnp(pyxel.KEY_R):
        score = 0
        # Game over : recommence le niveau actuel SANS dialogues
        if niveau == 1:
            init_niveau_1()
        else:
            init_niveau_2()
        musique.play(loops=-1)
        etat = "jeu"

# ════════════════════════════════════════════════════════════
# BOUCLES PYXEL
# ════════════════════════════════════════════════════════════
def update():
    if   etat == "titre":    update_titre()
    elif etat == "dialogue": update_dialogue()
    elif etat == "jeu":      update_jeu()
    else:                    update_fin()

def draw():
    pyxel.cls(12)

    if etat == "titre":
        dessiner_titre()

    elif etat == "dialogue":
        dessiner_dialogue()

    elif etat == "jeu":
        if niveau == 1:
            dessiner_decor_n1()
            dessiner_portail()
        else:
            dessiner_decor_n2()

        dessiner_pommes()
        dessiner_griffes()
        dessiner_balles()

        if niveau == 1:
            dessiner_braconnier()
            # Indicateur si le braconnier est hors écran
            if not brac_mort:
                sx_b = int(brac_x - camera_x)
                if sx_b < 0:
                    pyxel.text(4, HAUTEUR//2, "< ENNEMI", 8)
                elif sx_b > LARGEUR:
                    pyxel.text(LARGEUR-52, HAUTEUR//2, "ENNEMI >", 8)
        else:
            dessiner_monstres()
            # Indicateur pour les monstres hors écran
            for m in monstres:
                if not m[4]:
                    sx_m = int(m[0]-camera_x)
                    if sx_m < 0:
                        pyxel.text(4, HAUTEUR//2, "< ENNEMI", 8); break
                    elif sx_m > LARGEUR:
                        pyxel.text(LARGEUR-52, HAUTEUR//2, "ENNEMI >", 8); break

        dessiner_joueur()
        dessiner_hud()

    else:
        if niveau == 1:
            dessiner_decor_n1()
        else:
            dessiner_decor_n2()
        dessiner_fin()

pyxel.run(update, draw)
