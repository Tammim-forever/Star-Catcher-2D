
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

WIDTH, HEIGHT = 800, 600
player_x = WIDTH / 2
player_y = 75
player_speed = 8
objects = []
score = 0
lives = 3
paused = False
game_over = False
frame = 0
keys_down = set()
last_tick = time.perf_counter()


def draw_circle(cx, cy, radius, color, segments=32):
    glColor3f(*color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        glVertex2f(cx + radius * math.cos(angle), cy + radius * math.sin(angle))
    glEnd()


def draw_text(x, y, text, color=(1, 1, 1)):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))


def draw_background():
    # Deep blue space and small twinkling stars
    glClearColor(0.025, 0.035, 0.11, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    glPointSize(2)
    glBegin(GL_POINTS)
    for i in range(85):
        x = (i * 137 + 31) % WIDTH
        y = (i * 211 + 47) % HEIGHT
        brightness = 0.45 + 0.45 * (0.5 + 0.5 * math.sin(frame * 0.08 + i))
        glColor3f(brightness, brightness, 1.0)
        glVertex2f(x, y)
    glEnd()
    # Horizon glow
    glColor3f(0.12, 0.19, 0.36)
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(WIDTH, 0)
    glVertex2f(WIDTH, 8); glVertex2f(0, 8)
    glEnd()


def draw_ship():
    # Engine flame animates between two sizes
    flame = 15 + 5 * math.sin(frame * 0.35)
    glColor3f(1.0, 0.48, 0.08)
    glBegin(GL_TRIANGLES)
    glVertex2f(player_x - 9, player_y - 15)
    glVertex2f(player_x + 9, player_y - 15)
    glVertex2f(player_x, player_y - 15 - flame)
    glEnd()
    glColor3f(0.15, 0.75, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(player_x, player_y + 27)
    glVertex2f(player_x - 24, player_y - 16)
    glVertex2f(player_x - 10, player_y - 12)
    glVertex2f(player_x, player_y + 27)
    glVertex2f(player_x + 24, player_y - 16)
    glVertex2f(player_x + 10, player_y - 12)
    glEnd()
    glColor3f(0.72, 0.94, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(player_x, player_y + 29)
    glVertex2f(player_x - 13, player_y - 13)
    glVertex2f(player_x + 13, player_y - 13)
    glEnd()
    draw_circle(player_x, player_y + 3, 6, (0.08, 0.18, 0.45), 20)
    draw_circle(player_x, player_y + 4, 3, (0.3, 0.9, 1.0), 16)


def draw_star(x, y, radius):
    glColor3f(1.0, 0.82, 0.13)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(11):
        angle = math.pi / 2 + i * math.pi / 5
        r = radius if i % 2 == 0 else radius * 0.43
        glVertex2f(x + math.cos(angle) * r, y + math.sin(angle) * r)
    glEnd()
    draw_circle(x, y, 2.2, (1.0, 1.0, 0.75), 12)


def draw_asteroid(x, y, radius):
    draw_circle(x, y, radius, (0.58, 0.29, 0.25), 12)
    draw_circle(x - radius * 0.28, y + radius * 0.2, radius * 0.2, (0.35, 0.2, 0.22), 10)
    draw_circle(x + radius * 0.35, y - radius * 0.24, radius * 0.14, (0.35, 0.2, 0.22), 10)


def draw_hud():
    draw_text(18, HEIGHT - 28, "STAR CATCHER", (0.4, 0.85, 1.0))
    draw_text(18, HEIGHT - 51, "Score: " + str(score))
    draw_text(WIDTH - 105, HEIGHT - 28, "Lives: " + str(lives), (1.0, 0.55, 0.55))
    draw_text(205, 20, "Move: arrows / A D     Pause: P     Restart: R", (0.68, 0.74, 0.9))


def draw_scene():
    draw_background()
    for item in objects:
        if item["kind"] == "star":
            draw_star(item["x"], item["y"], item["r"])
        else:
            draw_asteroid(item["x"], item["y"], item["r"])
    draw_ship()
    draw_hud()
    if paused and not game_over:
        draw_text(355, 315, "PAUSED", (1.0, 0.9, 0.3))
    if game_over:
        glColor3f(0.055, 0.075, 0.17)
        glBegin(GL_QUADS)
        glVertex2f(145, 220); glVertex2f(655, 220)
        glVertex2f(655, 390); glVertex2f(145, 390)
        glEnd()
        draw_text(352, 345, "GAME OVER", (1.0, 0.42, 0.42))
        draw_text(320, 315, "Final score: " + str(score))
        draw_text(290, 278, "Press R to play again")
    glutSwapBuffers()


def spawn_object():
    # Asteroids are the obstacles to dodge; stars are optional score pickups.
    kind = "rock" if random.random() < 0.58 else "star"
    radius = random.randint(12, 19) if kind == "star" else random.randint(16, 23)
    objects.append({"kind": kind, "x": random.randint(radius + 8, WIDTH - radius - 8),
                    "y": HEIGHT + radius, "r": radius,
                    "speed": random.uniform(3.0, 5.0) + min(score * 0.015, 2.0),
                    "drift": random.uniform(-0.6, 0.6)})


def reset_game():
    global player_x, objects, score, lives, paused, game_over, frame
    player_x = WIDTH / 2
    objects = []
    score = 0
    lives = 3
    paused = False
    game_over = False
    frame = 0


def update(value):
    global player_x, frame, lives, score, game_over, objects
    frame += 1
    if not paused and not game_over:
        if b"a" in keys_down or b"A" in keys_down:
            player_x -= player_speed
        if b"d" in keys_down or b"D" in keys_down:
            player_x += player_speed
        if GLUT_KEY_LEFT in keys_down:
            player_x -= player_speed
        if GLUT_KEY_RIGHT in keys_down:
            player_x += player_speed
        player_x = max(28, min(WIDTH - 28, player_x))

        spawn_interval = max(22, 48 - score // 4)
        if frame % spawn_interval == 0:
            spawn_object()
        # Reward surviving so the score visibly changes even when no star is caught.
        if frame % 60 == 0:
            score += 1

        remaining = []
        for item in objects:
            item["y"] -= item["speed"]
            item["x"] += item["drift"]
            caught = item["y"] < player_y + 10 and item["y"] > player_y - 28 and abs(item["x"] - player_x) < item["r"] + 16
            if caught:
                if item["kind"] == "star":
                    score += 3
                else:
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                continue
            if item["y"] < -item["r"]:
                # Missing a star is harmless. Only hitting an asteroid costs a life.
                continue
            remaining.append(item)
        objects = remaining
    glutPostRedisplay()


def idle():
    """Drive animation at about 60 updates per second without GLUT timers."""
    global last_tick
    now = time.perf_counter()
    if now - last_tick >= 1.0 / 60.0:
        last_tick = now
        update(0)


def keyboard_down(key, x, y):
    global paused, player_x
    if key == b'\x1b':
        raise SystemExit
    if key in (b'a', b'A'):
        player_x = max(28, player_x - player_speed * 3)
        keys_down.add(key)
    elif key in (b'd', b'D'):
        player_x = min(WIDTH - 28, player_x + player_speed * 3)
        keys_down.add(key)
    elif key in (b'p', b'P') and not game_over:
        paused = not paused
    elif key in (b'r', b'R'):
        reset_game()
    else:
        keys_down.add(key)
    glutPostRedisplay()


def keyboard_up(key, x, y):
    keys_down.discard(key)


def special_down(key, x, y):
    global player_x
    if key == GLUT_KEY_LEFT:
        player_x = max(28, player_x - player_speed * 3)
    elif key == GLUT_KEY_RIGHT:
        player_x = min(WIDTH - 28, player_x + player_speed * 3)
    keys_down.add(key)


def special_up(key, x, y):
    keys_down.discard(key)


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(100, 60)
    glutCreateWindow(b"Star Catcher - 2D OpenGL Game")
    glutDisplayFunc(draw_scene)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
