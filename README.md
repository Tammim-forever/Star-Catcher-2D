# Star Catcher

An interactive 2D arcade game built with Python, OpenGL, and GLUT. Steer your ship through space, collect stars to increase your score, and avoid asteroids.

## Features

- Animated starfield, spaceship, stars, and asteroids
- Keyboard controls for smooth movement
- Score, lives, pause, and game-over display
- Increasing challenge as your score grows

## Controls

| Key | Action |
| --- | --- |
| Left / Right Arrow or `A` / `D` | Move the ship |
| `P` | Pause or resume |
| `R` | Restart the game |
| `Esc` | Quit |

## Run locally

1. Install Python 3.
2. Install the Python graphics packages:

   ```bash
   python -m pip install PyOpenGL PyOpenGL_accelerate
   ```

3. Run the game:

   ```bash
   python the_star_catcher.py
   ```

The game uses GLUT. If startup reports that GLUT or its shared library is missing, install a GLUT/FreeGLUT runtime for your operating system.
