# NAME: Terminal
# AUTH: Burritossss
# VERS: 1.0.0
# DESC: Allows rendering of basic text to a terminal

import core.hardwareapi as API

class HardwareMod(API.hardwareAPI):
    def setup(self):
        return super().setup()
    
    def cpu_tick(self):
        return super().cpu_tick()
    
    def tick(self, canvas: API.Canvas):
        canvas.draw_text(4, 6, "I'm at 4, 6!")