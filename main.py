import pygame
import os

# Pygameの初期化
pygame.init()

# 画面のサイズ
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# ウィンドウのタイトル
pygame.display.set_caption("Mario tekina Game")

# 画像の読み込み
try:
    player_img_orig = pygame.image.load(os.path.join("assets", "player.png")).convert_alpha()
    platform_img_orig = pygame.image.load(os.path.join("assets", "platform.png")).convert_alpha()
    coin_img_orig = pygame.image.load(os.path.join("assets", "coin.png")).convert_alpha()
    enemy_img_orig = pygame.image.load(os.path.join("assets", "enemy.png")).convert_alpha()

    # 画像のリサイズ
    player_image = pygame.transform.scale(player_img_orig, (60, 90))
    platform_image = pygame.transform.scale(platform_img_orig, (20, 30))
    coin_image = pygame.transform.scale(coin_img_orig, (50, 50))
    enemy_image = pygame.transform.scale(enemy_img_orig, (45, 45))

except pygame.error as e:
    print("画像の読み込みまたはリサイズに失敗しました。assetsフォルダに画像ファイルがあるか確認してください。")
    print(e)
    pygame.quit()
    exit()

# 色の定義 (RGB)
WHITE = (255, 255, 255)

# プレイヤーの初期設定
player_rect = player_image.get_rect(topleft=(50, 370))
player_speed = 4
GRAVITY = 1
JUMP_STRENGTH = -20
JUMP_STRENGTH_CLEAR = -10  # クリア時のジャンプ力
player_y_velocity = 0
is_jumping = False
player_facing_left = False

# スコア
score = 0
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)
game_over = False
game_clear = False

# 足場の設定
platform_rects = [
    pygame.Rect(0, 570, screen_width, 30), # 地面（長いまま）
    pygame.Rect(120, 450, 200, 30),
    pygame.Rect(500, 350, 200, 30),
    pygame.Rect(300, 250, 200, 30)
]

# コインの設定
coin_rects = [
    coin_image.get_rect(topleft=(285, 400)),
    coin_image.get_rect(topleft=(575, 300)),
    coin_image.get_rect(topleft=(300, 200))
]

# 敵の設定
# 1つ目の空中足場の上に敵を配置
second_platform = platform_rects[2]
enemies = [
    {
        "rect": enemy_image.get_rect(topleft=(second_platform.left + 20, second_platform.top - enemy_image.get_height())),
        "speed": 2,
    }
]

# ゲームループのフラグ
running = True

# フレームレート制御のためのClockオブジェクト
clock = pygame.time.Clock()

ENEMY_GRAVITY = 1

state = 'title'  # タイトル画面から開始

def reset_game():
    global player_rect, player_y_velocity, is_jumping, player_facing_left, score, coin_rects, enemies, game_over, game_clear
    player_rect.x = 50
    player_rect.y = 400
    player_y_velocity = 0
    is_jumping = False
    player_facing_left = False
    score = 0
    coin_rects = [
        coin_image.get_rect(topleft=(285, 400)),
        coin_image.get_rect(topleft=(575, 300)),
        coin_image.get_rect(topleft=(300, 200))
    ]
    # 敵を2つ目の足場の上に再配置
    second_platform = platform_rects[2]
    enemies.clear()
    enemies.append({
        "rect": enemy_image.get_rect(topleft=(second_platform.left + 20, second_platform.top - enemy_image.get_height())),
        "speed": 2,
    })
    game_over = False
    game_clear = False

# ゲームループ
while running:
    if state == 'title':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    state = 'playing'
                    reset_game()
        # タイトル画面の描画
        screen.fill((0, 0, 255))
        title_text = game_over_font.render("Mario tekina Game", True, WHITE)
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 2 - 100))
        start_text = font.render("Press SPACE to Start", True, WHITE)
        screen.blit(start_text, (screen_width // 2 - start_text.get_width() // 2, screen_height // 2))
        pygame.display.flip()
        clock.tick(60)
        continue
    # ゲームクリア判定
    if not enemies and not coin_rects:
        game_clear = True
        game_over = False
    if game_over:
        state = 'gameover'
    if game_clear:
        state = 'clear'
    if state == 'gameover':
        # ゲームオーバー時のイベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    state = 'playing'
    elif state == 'clear':
        # ゲームクリア時のイベント処理（R以外無効）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    state = 'playing'
        # プレイヤーを自動でぴょんぴょん跳ねさせる（弱め）
        if player_rect.bottom >= platform_rects[0].top:
            player_y_velocity = JUMP_STRENGTH_CLEAR
        player_y_velocity += GRAVITY
        player_rect.y += player_y_velocity
        # 地面との衝突判定
        if player_rect.bottom >= platform_rects[0].top:
            player_rect.bottom = platform_rects[0].top
            player_y_velocity = 0
    elif state == 'playing':
        # ゲームプレイ中の処理
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_jumping:
                    player_y_velocity = JUMP_STRENGTH
                    is_jumping = True

        # キーボードの状態を取得
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
            player_facing_left = True
        if keys[pygame.K_RIGHT]:
            player_rect.x += player_speed
            player_facing_left = False

        # 物理演算
        player_y_velocity += GRAVITY
        player_rect.y += player_y_velocity

        # on_ground フラグをリセット
        on_ground = False

        # 地面と足場との衝突判定
        for plat in platform_rects:
            if player_rect.colliderect(plat) and player_y_velocity >= 0:
                if player_rect.bottom >= plat.top:
                    player_rect.bottom = plat.top
                    player_y_velocity = 0
                    is_jumping = False
                    on_ground = True
                    break

        # コインとの衝突判定
        for coin in coin_rects[:]:
            if player_rect.colliderect(coin):
                coin_rects.remove(coin)
                score += 10

        # 敵の移動と重力
        for enemy in enemies:
            # 重力で落下
            enemy["rect"].y += ENEMY_GRAVITY

            # 足場の上にいるか判定（両足が足場の範囲内にある場合のみ）
            on_platform = False
            for plat in platform_rects:
                left_foot = enemy["rect"].left + 1
                right_foot = enemy["rect"].right - 1
                if (plat.left <= left_foot <= plat.right or plat.left <= right_foot <= plat.right) and abs(enemy["rect"].bottom - plat.top) <= ENEMY_GRAVITY * 2:
                    enemy["rect"].bottom = plat.top
                    on_platform = True
                    break

            # 横移動（足場の上にいるときだけ）
            if on_platform:
                enemy["rect"].x += enemy["speed"]
                # 足場の端で折り返し
                if enemy["rect"].left < plat.left or enemy["rect"].right > plat.right:
                    enemy["speed"] *= -1

        # 敵との衝突判定
        for enemy in enemies[:]:
            if player_rect.colliderect(enemy["rect"]):
                # 上から踏んだ場合
                if player_y_velocity > 0 and player_rect.bottom < enemy["rect"].centery:
                    enemies.remove(enemy)
                    score += 50
                    player_y_velocity = -10 # 小さく跳ねる
                # 横から当たった場合
                else:
                    game_over = True

    # 描画処理
    screen.fill((0, 0, 255))

    # 足場を描画 (透明な余白を考慮した最終修正)
    tile_bounding_rect = platform_image.get_bounding_rect()
    tile_step = tile_bounding_rect.width
    if tile_step == 0: # 画像が真っ白などの場合
        tile_step = platform_image.get_width()

    for plat in platform_rects:
        x = plat.left
        while x < plat.right:
            screen.blit(platform_image, (x, plat.y))
            x += tile_step

    # コインを描画
    for coin in coin_rects:
        screen.blit(coin_image, coin)

    # 敵を描画
    for enemy in enemies:
        screen.blit(enemy_image, (enemy["rect"].x, enemy["rect"].y + 12))

    # プレイヤーを描画
    if player_facing_left:
        flipped_player = pygame.transform.flip(player_image, True, False)
        screen.blit(flipped_player, (player_rect.x - 10, player_rect.y + 30))
    else:
        screen.blit(player_image, (player_rect.x - 10, player_rect.y + 30))

    # スコアを表示
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    if state == 'gameover':
        game_over_text = game_over_font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - game_over_text.get_height() // 2))
        restart_font = pygame.font.Font(None, 36)
        restart_text = restart_font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (
            screen_width // 2 - restart_text.get_width() // 2,
            screen_height // 2 - game_over_text.get_height() // 2 + game_over_text.get_height() + 20
        ))
    elif state == 'clear':
        game_clear_text = game_over_font.render("GAME CLEAR", True, WHITE)
        screen.blit(game_clear_text, (screen_width // 2 - game_clear_text.get_width() // 2, screen_height // 2 - game_clear_text.get_height() // 2))
        restart_font = pygame.font.Font(None, 36)
        restart_text = restart_font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (
            screen_width // 2 - restart_text.get_width() // 2,
            screen_height // 2 - game_clear_text.get_height() // 2 + game_clear_text.get_height() + 20
        ))

    # 画面を更新
    pygame.display.flip()

    # フレームレートを60に設定
    clock.tick(60)

# Pygameの終了
pygame.quit() 