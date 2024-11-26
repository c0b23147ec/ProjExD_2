import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {pg.K_UP:(0, -5), pg.K_DOWN:(0, +5), pg.K_LEFT:(-5, 0), pg.K_RIGHT:(+5, 0)}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数はこうかとんRect or ばくだんRect
    戻り値はタプル（横方向判定結果, 縦方向判定結果)
    画面内ならTrue, 画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def game_over(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に，半透明の黒い画面上に「Game Over」と表示し，
    泣いているこうかとん画像を貼り付ける関数
    引数:screen
    戻り値:なし
    """
    kk8_img = pg.image.load("fig/8.png")
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))

    black_img = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(black_img, (0, 0, 0), (0, 0, WIDTH, HEIGHT), 1)
    black_img.set_alpha(150)
    screen.blit(black_img, [0, 0])  # 背景を黒色に

    screen.blit(txt, [WIDTH / 2 - txt.get_width() / 2, HEIGHT / 2 - txt.get_height() / 2])  # GameOverの表示
    screen.blit(kk8_img, [WIDTH / 2 - txt.get_width() / 2 - kk8_img.get_width() / 2 - 30, HEIGHT / 2 + txt.get_height() / 2 - kk8_img.get_height()])  #こうかとんの表示(左)
    screen.blit(kk8_img, [WIDTH / 2 + txt.get_width() / 2 + kk8_img.get_width() / 2, HEIGHT / 2 + txt.get_height() / 2 - kk8_img.get_height()])  #工科トンの表示(右)
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceを要素としたリストと加速度リストを返す
    引数はなし
    戻り値：tuple[list[pg.Surface], list[int]]
    """
    accs = [a for a in range(1, 11)]

    bb_circle = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_circle.append(bb_img)

    return bb_circle, accs

def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    kk_img = pg.image.load("fig/3.png")
    kk_imgs = {(-5, 0): pg.transform.rotozoom(kk_img, 0, 0.9),
               (-5, +5): pg.transform.rotozoom(kk_img, 45, 0.9),
               (0, 5):pg.transform.rotozoom(pg.transform.flip(kk_img,True, False), 270, 0.9),
               (5, 5):pg.transform.rotozoom(pg.transform.flip(kk_img,True, False), 315, 0.9),
               (5, 0):pg.transform.rotozoom(pg.transform.flip(kk_img,True, False), 0, 0.9),
               (5, -5):pg.transform.rotozoom(pg.transform.flip(kk_img,True, False), 45, 0.9),
               (0, -5):pg.transform.rotozoom(pg.transform.flip(kk_img,True, False), 90, 0.9),
               (-5, -5): pg.transform.rotozoom(kk_img, 315, 0.9),}
    return kk_imgs[sum_mv]



def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))  # 爆弾用の空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10) 
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect() # 爆弾Rectの抽出
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)  # 爆弾のセンター座標
    vx , vy = 5, 5  # 爆弾の移動
    clock = pg.time.Clock()
    tmr = 0

    bb_imgs, bb_accs = init_bb_imgs()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            game_over(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key,tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_rct.move_ip(sum_mv)
        if tuple(sum_mv) != (0, 0):
            kk_img = get_kk_img(tuple(sum_mv))
        if check_bound(kk_rct) != (True, True):  # こうかとんの画面内判定
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        avx = vx*bb_accs[min(tmr//500, 9)]  # こうかとんの加速(x)
        avy = vy*bb_accs[min(tmr//500, 9)]  # こうかとんの加速(y)

        bb_rct.move_ip(avx, avy)  # 加速度の変更
        
        bb_img = bb_imgs[min(tmr//500, 9)]  # ばくだんの拡大
        
        yoko, tate = check_bound(bb_rct)  # ばくだんの画面内判定
        if not yoko:
            vx *= -1
        if not tate:
            vy *=-1

        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
