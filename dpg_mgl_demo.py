import moderngl as mgl
from pyrr import Matrix44

import numpy

import dearpygui.dearpygui as dpg

dpg.enable_docking(dock_space=True)


with dpg.font_registry():

    # add font (set as default for entire app)
    dpg.add_font(
        "/usr/share/fonts/adobe-source-han-sans/SourceHanSansCN-Regular.otf",
        40,
        default_font=True)


import numpy as np
import threading

width = 800
height = 800
grid_arr = np.ones((width, height, 4), dtype=np.float32)

rng = np.random.default_rng()

should_continue = True


def setter():
    import time

    while should_continue:
        rng.standard_normal(out=grid_arr, dtype=np.float32)

        # dpg.set_value(image_id, grid_arr)
        time.sleep(0.01)


t = threading.Thread(target=setter)
t.start()

def exit_handler():
    global should_continue
    print("EXIT!")
    should_continue = False

dpg.set_exit_callback(exit_handler)

class MGLPlotter:
    width, height = 800, 800

    def __init__(self, mgl_context, texture) -> None:

        self.theta = 0.0

        self.ctx = mgl_context
        self.texture = texture

        self.prog = ctx.program(vertex_shader="""
            #version 330
            uniform mat4 model;
            in vec2 in_vert;
            in vec3 in_color;
            out vec3 color;
            void main() {
                gl_Position = model * vec4(in_vert, 0.0, 1.0);
                color = in_color;
            }
            """,
            fragment_shader="""
            #version 330
            in vec3 color;
            out vec4 fragColor;
            void main() {
                fragColor = vec4(color, 1.0);
            }
        """)

        self.vertices = np.array([
            -0.6, -0.6,
            1.0, 0.0, 0.0,
            0.6, -0.6,
            0.0, 1.0, 0.0,
            0.0, 0.6,
            0.0, 0.0, 1.0,
        ], dtype='f4')
        
        self.vbo = ctx.buffer(self.vertices)
        self.vao = ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')
        self.fbo = ctx.framebuffer(color_attachments=[texture])
    
    def paintGL(self):
        self.fbo.use()
        self.ctx.clear()
        self.prog['model'].write(Matrix44.from_eulers((self.theta, 0.1, 0.0), dtype='f4'))
        self.vao.render(mgl.TRIANGLES)
        # self.fbo
        self.ctx.screen.use()

checked = False

def checkbox_callback():
    pass

if __name__ == "__main__":
    dpg.setup_viewport()
    ctx = mgl.create_context()

    texture_id = ctx.texture((800, 800), 4)
    
    print(f"MGL Context: {ctx}")

    with dpg.texture_registry():
        image_id = dpg.add_raw_texture(width,
                                    height,
                                    grid_arr,
                                    textureid=texture_id.glo,
                                    format=dpg.mvFormat_Float_rgba)

    from dearpygui.logger import mvLogger

    logger = mvLogger()
    logger.log_level = 0

    # dpg.add_clicked_handler(cb, 0, callback=lambda s, a, u: logger.log(f"clicked_handler: {s} '\t' {a} '\t' {u}"))
    # dpg.add_hover_handler(cb, callback=lambda s, a, u: logger.log(f"hover_handler: {s} '\t' {a} '\t' {u}"))

    glp = MGLPlotter(ctx, texture_id)

    with dpg.window(label="Tutorial"):
        # with dpg.drawlist(width=width, height=height):
        def drop_callback(sender, app_data, user_data):
            glp.theta = app_data

        dpg.add_slider_float(label = "theta", min_value=-numpy.pi, max_value=numpy.pi, callback=drop_callback)
        dpg.add_checkbox(label="Radio Button1", source=checked, callback=checkbox_callback)

        def clicked_callback(sender, app_data, user_data):
            logger.log_error(f"[{sender}]: {app_data}, {user_data}")
            print(f"[{sender}]: {app_data}, {user_data}")

        img_widget = dpg.add_image(image_id)
        with dpg.handler_registry():
            dpg.add_clicked_handler(img_widget, label="3D clicked", user_data = "click", callback=clicked_callback)
            dpg.add_mouse_down_handler(label="3D dragged", user_data = "down", callback=clicked_callback)
            # dpg.add_hover_handler(img_widget, user_data="hover", callback=clicked_callback)
            # dpg.add_mouse_release_handler(img_widget, user_data="release", callback=clicked_callback)
            # dpg.add_mouse_move_handler(img_widget, user_data="move", callback=clicked_callback)

        with dpg.drawlist(width=800, height=800): # or you could use dpg.add_drawlist and set parents manually
            # dpg.draw_image(image_id, (0, 0), (800, 800))
            dpg.draw_line((10, 10), (100, 100), color=(255, 0, 0, 255), thickness=5)
            dpg.draw_text((300, 300), "Origin", color=(250, 250, 250, 255), size=45)
            dpg.draw_arrow((50, 70), (400, 265), color=(0, 200, 255), thickness=1, size=40)

    # show_demo()
    from dearpygui.demo import show_demo
    show_demo()

    while dpg.is_dearpygui_running():
        glp.paintGL()

        dpg.render_dearpygui_frame()

    dpg.cleanup_dearpygui()