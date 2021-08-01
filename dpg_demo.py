import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo
from OpenGL import platform as gl_platform
from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture
from OpenGL.raw.GL.VERSION.GL_1_5 import glBindBuffer
from OpenGL.raw.GL.VERSION.GL_3_0 import GL_COLOR_ATTACHMENT0, glBindFramebuffer, glGenFramebuffers
from OpenGL.raw.GL.VERSION.GL_3_2 import glFramebufferTexture

from vispy import gloo

import numpy

import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo
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

with dpg.texture_registry():
    image_id = dpg.add_raw_texture(width,
                                   height,
                                   grid_arr,
                                   format=dpg.mvFormat_Float_rgba)
    image_id_1 = dpg.add_raw_texture(width,
                                     height,
                                     grid_arr,
                                     format=dpg.mvFormat_Float_rgba)

with dpg.window(label="Tutorial"):
    # with dpg.drawlist(width=width, height=height):
    dpg.add_image(image_id)  # , (0, 0), (width, height))

should_continue = True


def setter():
    import time

    while dpg.get_raw_texture(image_id) == 0:
        time.sleep(0.01)

    texture_id = dpg.get_raw_texture(image_id)
    dpg.set_update_enable(image_id, 0)

    # fbo = gl.glGenFramebuffers(1)
    # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
    # gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    # glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, 400, 400, 0, gl.GL_RGBA, gl.GL_FLOAT, 0)
    # glTextureParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    # glTextureParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    # glFramebufferTexture2D(
    #     GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, texture_id, 0
    # )

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

class GLPlotter:
    width, height = 800, 800

    def __init__(self, texture_id) -> None:

        self.data = np.array(.2*numpy.random.randn(100000,2),dtype=np.float32)
        self.vbo = glvbo.VBO(self.data)
        self.texture_id = texture_id
        self.fbo = gl.GLuint()

        glGenFramebuffers(1, self.fbo)
    
    def paintGL(self):
        self.data = np.array(.2*numpy.random.randn(100000,2),dtype=np.float32)
        glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo)
        glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        self.vbo[:] = self.data
        self.vbo.bind()
        self.vbo.copy_data()
        # gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, width, height, gl.GL_RGBA, gl.GL_FLOAT, 0)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.texture_id, 0)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, self.vbo)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glViewport(0, 0, width, height)
        gl.glColor(1, 1, 0, 1)
        gl.glDrawArrays(gl.GL_POINTS, 0, self.data.shape[0])
        self.vbo.unbind()
        glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)


    

if __name__ == "__main__":
    dpg.setup_viewport()

    dpg_context = gl_platform.GetCurrentContext()

    print(f"DPG context: {dpg_context}")

    show_demo()

    glp = None
    while dpg.is_dearpygui_running():

        if glp is None:
            texture_id = dpg.get_raw_texture(image_id)
            if texture_id != 0:
                dpg.set_update_enable(image_id, 0)
                glp = GLPlotter(texture_id)
                print("Got Painter")
        else:
            glp.paintGL()

        dpg.render_dearpygui_frame()

    dpg.cleanup_dearpygui()