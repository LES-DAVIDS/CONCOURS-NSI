# -----------------------------------------------
# #Projet : Kung-Fu PandaRoux
#Auteurs : Maxence Andrivon, Hugo Dupuis, Anais Najac, Come de La Serre
# -----------------------------------------------

"""
generer_pyxres.py - Lance UNE SEULE FOIS pour créer le nsi.pyxres amélioré
"""
import tomllib, zipfile, os, random, math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Charger l'original ──────────────────────────────────────
def charger():
    for nom in ['nsi.pyxres']:
        p = os.path.join(SCRIPT_DIR, nom)
        if os.path.exists(p):
            with zipfile.ZipFile(p) as z:
                return tomllib.loads(z.read('pyxel_resource.toml').decode())
    raise FileNotFoundError("nsi.pyxres introuvable")

# ── Placer un sprite dans un bank ───────────────────────────
def placer(data, bank, x0, y0, sprite):
    d = data['images'][bank]['data']
    besoin = y0 + len(sprite)
    while len(d) < besoin:
        d.append([12]*256)
    for i in range(len(d)):
        while len(d[i]) < 256:
            d[i].append(12)
    for dy, ligne in enumerate(sprite):
        for dx, c in enumerate(ligne):
            d[y0+dy][x0+dx] = c

# ── Sérialiser exactement comme Pyxel attend ───────────────
def sauvegarder(data, chemin):
    def row_s(r): return '[' + ','.join(map(str,r)) + ']'
    lignes = [f"format_version = {data['format_version']}", '']
    for img in data['images']:
        lignes += ['[[images]]', f"width = {img['width']}", f"height = {img['height']}",
                   'data = [' + ', '.join(row_s(r) for r in img['data']) + ']', '']
    for tm in data['tilemaps']:
        imgsrc = tm.get('imgsrc', tm.get('image', 0)) or 0
        lignes += ['[[tilemaps]]', f"width = {tm.get('width',256)}",
                   f"height = {tm.get('height',256)}", f"imgsrc = {imgsrc}",
                   'data = [' + ', '.join(row_s(r) for r in tm.get('data',[[0]])) + ']', '']
    for s in data['sounds']:
        lignes += ['[[sounds]]',
                   f"notes = {s.get('notes',[])}",   f"tones = {s.get('tones',[])}",
                   f"volumes = {s.get('volumes',[])}",f"effects = {s.get('effects',[])}",
                   f"speed = {s.get('speed',30)}", '']
    for m in data['musics']:
        lignes.append('[[musics]]')
        for k,v in m.items(): lignes.append(f"{k} = {v}")
        lignes.append('')
    with zipfile.ZipFile(chemin, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('pyxel_resource.toml', '\n'.join(lignes))

T,K,D,G,W,R,P,V,B,Y,L = 12,0,5,6,7,8,14,2,1,10,13

# ════════════════════════════════════════════════════════════
# MONT FUJI amélioré (bank0, y=161, 256x95)
# ════════════════════════════════════════════════════════════
def gen_fuji():
    random.seed(42)
    larg, haut = 256, 95
    px, py, by = 127, 8, 94
    limite_neige = py + int((by-py)*0.26)
    fuji = [[T]*larg for _ in range(haut)]

    # Décalages irréguliers pour crête réaliste
    dec = [0]*haut
    for y in range(py+4, haut, 5):
        d = random.randint(-3,3)
        for k2 in range(3):
            if y+k2 < haut: dec[y+k2] = d//(k2+1)

    for y in range(py, haut):
        t = (y-py)/max(1,by-py)
        # Flanc gauche légèrement plus irrégulier (réalisme Fuji)
        bg = int(px - t*px*0.95) + dec[y]
        bd = int(px + t*(larg-1-px)) + dec[y]//3
        bg = max(0, bg); bd = min(larg-1, bd)
        lz = max(1, bd-bg)

        for x in range(bg, bd+1):
            dc = abs(x-px)/(lz/2+0.01)  # 0=centre,1=bord

            if y <= limite_neige:
                # Calotte neigeuse texturée
                if dc < 0.12:
                    fuji[y][x] = W  # blanc pur sommet
                elif (x+y*2)%5 == 0:
                    fuji[y][x] = G  # grain neige
                else:
                    fuji[y][x] = W

            elif y <= limite_neige+10:
                # Transition neige→roche avec irrégularité
                if dc < 0.22:
                    fuji[y][x] = W if (x+y)%4!=0 else G
                elif dc < 0.48:
                    fuji[y][x] = G if (x*3+y)%3==0 else D
                else:
                    fuji[y][x] = D

            else:
                # Corps rocheux
                if x < px:
                    # Flanc gauche (ombragé)
                    if dc > 0.85: fuji[y][x] = B         # bord très sombre
                    elif dc > 0.6: fuji[y][x] = B if (x-y)%9==0 else D
                    else: fuji[y][x] = D
                else:
                    # Flanc droit (légèrement éclairé)
                    if dc > 0.85: fuji[y][x] = D
                    elif (x+y)%7==0 and dc<0.55: fuji[y][x] = G  # reflet
                    else: fuji[y][x] = D

                # Traînées neigeuses sur les flancs
                if y < limite_neige+20:
                    if (x*2+y*3)%13==0 and dc<0.5:
                        fuji[y][x] = G

    # Rochers à la base
    for rx in range(25, larg-25, 28):
        rh = random.randint(3,7); rw = random.randint(5,10)
        for dy2 in range(-rh,0):
            for dx2 in range(-rw//2, rw//2+1):
                if abs(dx2) <= rw//2-abs(dy2)//2:
                    yy,xx = by+dy2, rx+dx2
                    if 0<=yy<haut and 0<=xx<larg and fuji[yy][xx]!=T:
                        fuji[yy][xx] = 4

    # Ligne de neige supplémentaire sur crête droite
    for y in range(limite_neige, limite_neige+8):
        t2 = (y-py)/max(1,by-py)
        centre_droit = int(px + t2*(larg-1-px)*0.15)
        for x in range(centre_droit-2, centre_droit+3):
            if 0<=x<larg and fuji[y][x]!=T:
                fuji[y][x] = G if (x+y)%2==0 else W

    return fuji

# ════════════════════════════════════════════════════════════
# COEUR PLEIN style Zelda (bank1, y=97, x=0, 8x8)
# ════════════════════════════════════════════════════════════
def gen_coeur_plein():
    return [
        [T, R, R, T, T, R, R, T],
        [R, R, R, R, R, R, R, T],
        [R, W, R, R, R, R, R, R],
        [R, R, R, R, R, R, R, R],
        [T, R, R, R, R, R, R, T],
        [T, T, R, R, R, R, T, T],
        [T, T, T, R, R, T, T, T],
        [T, T, T, T, T, T, T, T],
    ]

# ════════════════════════════════════════════════════════════
# COEUR VIDE style Zelda (bank1, y=97, x=8, 8x8)
# ════════════════════════════════════════════════════════════
def gen_coeur_vide():
    O = D  # contour gris
    return [
        [T, O, O, T, T, O, O, T],
        [O, O, T, T, T, T, O, T],
        [O, T, T, T, T, T, T, O],
        [O, T, T, T, T, T, T, O],
        [T, O, T, T, T, T, O, T],
        [T, T, O, T, T, O, T, T],
        [T, T, T, O, O, T, T, T],
        [T, T, T, T, T, T, T, T],
    ]

# ════════════════════════════════════════════════════════════
# BRACONNIER FACE GAUCHE (bank1, y=97, x=16, 32x32)
# Mirror du braconnier (bank1 x=0 y=64) mais avec fusil à gauche
# ════════════════════════════════════════════════════════════
def gen_braconnier_gauche():
    # On fait le miroir horizontal du sprite original
    import tomllib, zipfile
    p = os.path.join(SCRIPT_DIR, 'nsi.pyxres')
    with zipfile.ZipFile(p) as z:
        data = tomllib.loads(z.read('pyxel_resource.toml').decode())
    d = data['images'][1]['data']
    sprite = []
    for row_i in range(64, 96):
        if row_i < len(d):
            row = d[row_i][0:32]
            while len(row) < 32: row.append(12)
            sprite.append(list(reversed(row)))  # miroir horizontal
        else:
            sprite.append([12]*32)
    return sprite

# ════════════════════════════════════════════════════════════
# MONSTRE CHAPEAU (bank1, y=105, x=16, 32x32)
# Silhouette noire avec grand chapeau, yeux blancs
# ════════════════════════════════════════════════════════════
def gen_monstre():
    return [
        # 0: vide
        [T]*32,
        # 1-3: bord de chapeau très large
        [T,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,T],
        [D,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,D],
        [D,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,D],
        # 4: transition bord → calotte
        [T,D,D,D,D,D,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,D,D,D,D,D,T,T],
        # 5-9: calotte du chapeau
        [T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,D,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,D,T,T,T,T,T,T,T,T],
        # 10-11: tête
        [T,T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T],
        # 12-13: yeux blancs brillants
        [T,T,T,T,T,T,T,K,K,W,W,K,K,K,K,K,K,K,W,W,K,K,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,K,K,W,W,K,K,K,K,K,K,K,W,W,K,K,T,T,T,T,T,T,T,T,T,T],
        # 14-16: reste de la tête
        [T,T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,K,D,D,D,D,D,D,D,D,D,D,D,K,K,K,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T,T,T,T],
        # 17-25: corps cape (s'élargit puis rétrécit)
        [T,T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,K,K,D,K,K,K,K,K,K,K,K,K,K,K,D,K,K,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,T,T,K,K,K,K,K,K,K,K,K,T,T,T,T,T,T,T,T,T,T,T,T,T,T],
        # 26-31: jambes et pieds
        [T,T,T,T,T,T,T,T,T,K,K,K,T,T,T,T,T,T,K,K,K,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,T,T,K,K,K,T,T,T,T,T,T,K,K,K,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,T,T,K,K,K,T,T,T,T,T,T,K,K,K,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,T,T,K,K,K,T,T,T,T,T,T,K,K,K,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,T,K,K,K,K,T,T,T,T,T,K,K,K,K,T,T,T,T,T,T,T,T,T,T,T],
        [T,T,T,T,T,T,T,T,K,K,K,K,T,T,T,T,T,K,K,K,K,T,T,T,T,T,T,T,T,T,T,T],
    ]

# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
print("Chargement du pyxres original...")
data = charger()

print("Dessin du Mont Fuji amélioré (bank0, y=161)...")
placer(data, 0, 0, 161, gen_fuji())

print("Dessin des cœurs Zelda (bank1, y=97)...")
placer(data, 1, 0,  97, gen_coeur_plein())
placer(data, 1, 8,  97, gen_coeur_vide())

print("Dessin braconnier face gauche (bank1, y=97, x=16)...")
placer(data, 1, 16, 97, gen_braconnier_gauche())

print("Dessin du monstre chapeau (bank1, y=105, x=16)...")
placer(data, 1, 16, 105, gen_monstre())

sortie = os.path.join(SCRIPT_DIR, 'nsi.pyxres')
print(f"Sauvegarde → {sortie}")
sauvegarder(data, sortie)

# Vérification rapide
import tomllib, zipfile
with zipfile.ZipFile(sortie) as z:
    dv = tomllib.loads(z.read('pyxel_resource.toml').decode())
b1 = dv['images'][1]['data']
print(f"Vérif: bank1 a {len(b1)} lignes")
print(f"  Coeur plein [97][0]={b1[97][0]} (attendu 12)")
print(f"  Coeur plein [98][0]={b1[98][0]} (attendu 8=rouge)")
print(f"  Monstre [105][16]={b1[105][16]} (attendu 12)")
print(f"  Monstre [108][22]={b1[108][22]} (attendu 0=noir)")
print("✓ Terminé ! Lance maintenant : python kung_fu_panda_roux.py")
