from OpenGL import platform as gl_platform

import moderngl as mgl
from pyrr import Matrix44

from simple_3dviz import Scene, Mesh

import numpy

import dearpygui.dearpygui as dpg
from simple_3dviz.renderables.base import Renderable

dpg.enable_docking(dock_space=True)


with dpg.font_registry():

    # add font (set as default for entire app)
    dpg.add_font(
        "/usr/share/fonts/adobe-source-han-sans/SourceHanSansCN-Regular.otf",
        40,
        default_font=True)


import numpy as np
import threading

rng = np.random.default_rng()

should_continue = True

def exit_handler():
    global should_continue
    print("EXIT!")
    should_continue = False

dpg.set_exit_callback(exit_handler)

def render(renderables, scene,
           background=(1,)*4, camera_position=(-2, -2, -2),
           camera_target=(0, 0, 0), up_vector=(0, 0, 1), light=None):
    """Render a list of primitives for a given number of frames calling the
    passed behaviours after every frame.
    Arguments
    ---------
        renderables: list[Renderable] the renderables to be displayed in the
                     scene
        size: (w, h) the size of the window
        background: (r, g, b, a) the rgba tuple for the background
        camera_position: (x, y, z) the position of the camera
        camera_target: (x, y, z) the point that the camera looks at
        up_vector: (x, y, z) defines the floor and sky
        light: (x, y, z) defines the position of the light source
        scene: An optional scene to reuse
    """
    # Create the scene or clear it if it is provided
    scene.clear()

    # Set up the scene
    scene.background = background
    scene.camera_position = camera_position
    scene.camera_target = camera_target
    scene.up_vector = up_vector
    scene.light = light if light is not None else camera_position

    # Add the primitives
    if not isinstance(renderables, (list, tuple)):
        renderables = [renderables]
    if not all(isinstance(r, Renderable) for r in renderables):
        raise ValueError(("render() expects one or more renderables as "
                          "parameters not {}").format(renderables))
    for r in renderables:
        scene.add(r)


class MGLPlotter:
    width, height = 800, 800

    @property
    def size(self):
        return (self.width, self.height)

    def __init__(self, mgl_context) -> None:

        self.theta = 0.0
        self.texture: mgl.Texture = ctx.texture((800, 800), 4)

        self.ctx = mgl_context

        dphi, dtheta = np.pi/250.0, np.pi/250.0
        [phi, theta] = np.mgrid[0:np.pi+dphi*1.5:dphi, 0:2*np.pi+dtheta*1.5:dtheta]
        m0 = 4; m1 = 3; m2 = 2; m3 = 3; m4 = 6; m5 = 2; m6 = 6; m7 = 4;
        r = np.sin(m0 * phi)**m1 + np.cos(m2 * phi)**m3
        r = r + np.sin(m4 * theta)**m5 + np.cos(m6 * theta)**m7
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.cos(phi)
        z = r * np.sin(phi) * np.sin(theta)
        self.mesh = Mesh.from_xyz(x, y, z)
        self.mesh.colors = (0.4, 0.1, 0.0, 1.0)
        self.scene = Scene(self.size, ctx = self.ctx)
        
        render([self.mesh],self.scene, camera_position=(3, 3, 3),
        background=(0,)*4)

        self.dbo = ctx.depth_texture(self.size)
        self.fbo = ctx.framebuffer(color_attachments=[self.texture], depth_attachment=self.dbo)
    
    def resize(self, width, height):
        self.width, self.height = width, height

    def rotate_camera(self, delta):
        actual_x, actual_y = delta[1]/self.width, delta[0]/self.height

        self.scene.rotate_x(actual_x)
        self.scene.rotate_z(actual_y)

    def paintGL(self):
        if self.texture.width != self.width or self.texture.height != self.height:
            # print(f"release! {self.texture.width} {self.width}, {self.texture.height} {self.height}")
            self.texture.release()
            self.texture = ctx.texture(self.size, 4)
            self.dbo.release()
            self.dbo = ctx.depth_texture(self.size)
            self.fbo.release()
            self.fbo = ctx.framebuffer(color_attachments=[self.texture], depth_attachment=self.dbo)

        # self.scene.rotate_x(0.01)

        self.scene.camera_matrix = Matrix44.perspective_projection(45., self.width/self.height, 0.1, 1000.)

        self.fbo.use()
        self.ctx.clear()
        self.scene.render()
        # self.fbo
        self.ctx.screen.use()

checked = False

def checkbox_callback():
    pass

if __name__ == "__main__":
    dpg.setup_viewport()

    dpg_context = gl_platform.GetCurrentContext()

    print(f"DPG context: {dpg_context}")

    ctx = mgl.create_context()
    
    print(f"MGL Context: {ctx}")

    from dearpygui.logger import mvLogger

    logger = mvLogger()
    logger.log_level = 0

    # dpg.add_clicked_handler(cb, 0, callback=lambda s, a, u: logger.log(f"clicked_handler: {s} '\t' {a} '\t' {u}"))
    # dpg.add_hover_handler(cb, callback=lambda s, a, u: logger.log(f"hover_handler: {s} '\t' {a} '\t' {u}"))

    glp = MGLPlotter(ctx)

    with dpg.window(label="Tutorial"):

        def set_theta(s, a, u):
            glp.theta = a

        dpg.add_slider_float(label = "theta", min_value=-numpy.pi, max_value=numpy.pi, callback=set_theta)

        def canvas_callback(source, app_data, user_data):
            if app_data[0] == 0:
                width, height = app_data[1]
                glp.resize(width, height)
                dpg.set_item_width(source, width)
                dpg.set_item_height(source, height)
            else:
                glp.rotate_camera(app_data[1])

        img_widget = dpg.add_raw_canvas(glp.texture.glo, callback=canvas_callback)
        # with dpg.handler_registry():
        #     dpg.add_clicked_handler(img_widget, label="3D clicked", user_data = "click", callback=clicked_callback)
        #     dpg.add_mouse_down_handler(label="3D dragged", user_data = "down", callback=clicked_callback)
            # dpg.add_hover_handler(img_widget, user_data="hover", callback=clicked_callback)
            # dpg.add_mouse_release_handler(img_widget, user_data="release", callback=clicked_callback)
            # dpg.add_mouse_move_handler(img_widget, user_data="move", callback=clicked_callback)

        with dpg.drawlist(width=800, height=800): # or you could use dpg.add_drawlist and set parents manually
            # dpg.draw_image(canvas_id, (0, 0), (800, 800))
            dpg.draw_line((10, 10), (100, 100), color=(255, 0, 0, 255), thickness=5)
            dpg.draw_text((300, 300), "Origin", color=(250, 250, 250, 255), size=45)
            dpg.draw_arrow((50, 70), (400, 265), color=(0, 200, 255), thickness=1, size=40)

    # show_demo()
    from dearpygui.demo import show_demo
    show_demo()

    while dpg.is_dearpygui_running():
        glp.paintGL()
        dpg.set_value(img_widget, glp.texture.glo)

        dpg.render_dearpygui_frame()

    dpg.cleanup_dearpygui()