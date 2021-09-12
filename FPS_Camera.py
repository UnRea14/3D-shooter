from ursina import *


class FPS_camera(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.running = False
        self.crouching = False
        self.speed = 5
        self.origin_y = -.5
        self.camera_pivot = Entity(parent=self, y=2)
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)

        camera.parent = self.camera_pivot
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_duration = .5
        self.jumping = False
        self.air_time = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self, up_recoil=0):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0] + up_recoil
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(self.forward * (held_keys['w'] - held_keys['s']) + self.right * (held_keys['d'] - held_keys['a'])).normalized()

        origin = self.world_position + (self.up * .5)
        hit_info = raycast(origin, self.direction, ignore=(self,), distance=.5, debug=False)
        if not hit_info.hit:
            self.position += self.direction * self.speed * time.dt

        if self.gravity:
            # # gravity
            ray = raycast(self.world_position + (0, 2, 0), self.down, ignore=(self,))
            # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

            if ray.distance <= 2.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5:  # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, ray.distance - .05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity

    def input(self, key):
        if key == 'space':
            self.jump()
        if key == 'left shift' and not self.running:
            self.run()
        elif self.running:
            self.stop_run()
        elif key == 'left control' and not self.crouching:
            self.crouch()
        elif self.crouching:
            self.stop_crouch()

    def jump(self):
        if not self.grounded:
            return

        self.grounded = False
        self.animate_y(self.y + self.jump_height, self.jump_duration, resolution=int(1 // time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.jump_duration)

    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        self.air_time = 0
        self.grounded = True

    def run(self):
        self.speed += 10
        self.running = True

    def stop_run(self):
        self.speed -= 10
        self.running = False

    def crouch(self):
        self.y -= 1
        self.crouching = True

    def stop_crouch(self):
        self.y += 1
        self.crouching = False
