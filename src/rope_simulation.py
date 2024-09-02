import pymunk
import pymunk.pygame_util
import pygame
from pygame.locals import *

# Initialize Pygame and Pymunk
pygame.init()
screen = pygame.display.set_mode((1200, 700))
clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = (0, 900)  # Gravity in y-direction


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
                stiffness=2000,
                damping=20,
            )
            space.add(joint)
        prev_body = body

    # Anchor the first segment
    static_body = space.static_body
    anchor = pymunk.PinJoint(
        static_body, segments[0], (start_pos[0], start_pos[1]), (-segment_length / 2, 0)
    )
    end_anchor = pymunk.PinJoint(
        static_body,
        segments[-1],
        (start_pos[0] + num_segments * segment_length, start_pos[1]),
        (segment_length / 2, 0),
    )
    space.add(anchor)
    space.add(end_anchor)

    return segments, end_anchor


# Function to draw gridlines
def draw_gridlines(screen, color, width, height, spacing):
    for x in range(0, width, spacing):
        pygame.draw.line(screen, color, (x, 0), (x, height))
    for y in range(0, height, spacing):
        pygame.draw.line(screen, color, (0, y), (width, y))


# Parameters for the rope
start_position = (400, 100)
segment_length = 10
num_segments = 30
mass = 0.25

# Create the rope
rope, end_anchor = create_rope(
    space, start_position, segment_length, num_segments, mass
)

# Pygame loop to visualize the rope
draw_options = pymunk.pygame_util.DrawOptions(screen)
running = True
dragging_anchor = False

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                if (
                    end_anchor.a.position.get_distance(mouse_pos) < 100
                ):  # Increase the clickable area
                    dragging_anchor = True
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                dragging_anchor = False
        elif event.type == MOUSEMOTION:
            if dragging_anchor:
                mouse_pos = pygame.mouse.get_pos()
                end_anchor.anchor_a = (
                    mouse_pos  # Update the position of the second anchor
                )

    screen.fill((255, 255, 255))
    draw_gridlines(screen, (200, 200, 200), 1200, 700, 50)  # Draw gridlines
    space.step(1 / 60.0)
    space.debug_draw(draw_options)

    # Draw a circle around the second anchor for visual feedback
    pygame.draw.circle(
        screen,
        (255, 0, 0),
        (int(end_anchor.a.position.x), int(end_anchor.a.position.y)),
        10,
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
