import pymunk
import pymunk.pygame_util
import pygame
from pygame.locals import *

# Initialize Pygame and Pymunk
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = (0, -900)  # Gravity in y-direction


# Helper function to create a segment of the rope
def create_segment(space, position, length, mass):
    body = pymunk.Body(mass, pymunk.moment_for_segment(mass, (0, 0), (length, 0), 1))
    body.position = position
    shape = pymunk.Segment(body, (0, 0), (length, 0), 5)
    shape.friction = 0.5
    space.add(body, shape)
    return body


# Create the rope
def create_rope(space, start_pos, segment_length, num_segments, mass):
    segments = []
    prev_body = None

    for i in range(num_segments):
        position = start_pos[0] + i * segment_length, start_pos[1]
        body = create_segment(space, position, segment_length, mass)
        segments.append(body)

        if prev_body is not None:
            joint = pymunk.DampedSpring(
                prev_body,
                body,
                (segment_length / 2, 0),
                (-segment_length / 2, 0),
                segment_length,
                stiffness=1000,
                damping=10,
            )
            space.add(joint)
        prev_body = body

    # Anchor the first segment
    static_body = space.static_body
    anchor = pymunk.PinJoint(
        static_body, segments[0], (start_pos[0], start_pos[1]), (-segment_length / 2, 0)
    )
    space.add(anchor)

    return segments


# Parameters for the rope
start_position = (300, 400)
segment_length = 30
num_segments = 10
mass = 1

# Create the rope
rope = create_rope(space, start_position, segment_length, num_segments, mass)

# Pygame loop to visualize the rope
draw_options = pymunk.pygame_util.DrawOptions(screen)
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen.fill((255, 255, 255))
    space.step(1 / 60.0)
    space.debug_draw(draw_options)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
