
class CutterComp:
    LEFT="left"
    RIGHT="right"
    NONE="none"


def _linear_pattern(start_x=0, start_y=0, x_spacing=0, y_spacing=0, x_count=1, y_count=1, ):
    r = []
    for y in range(y_count):
        for x in range(x_count):
            r.append((start_x + x*x_spacing,start_y + y*y_spacing))

    return r


def _compute_steps( start=0, target=0, step=0):
    steps=[]
    current = start

    if target > start:
        while current < target:
            steps.append(current)
            current = current + step
            last = steps[-1]

        if last < target:
            steps.append(target)
    else:
        while current > target:
            steps.append(current)
            current = current - step
            last = steps[-1]

        if last > target:
            steps.append(target)

    return steps

class Program(object):
    def __init__(self):
        self.cmds=[]
        self.safe_z = 0.0
        self.tool_diameter=0.0
        self.cutterComp = None
        self.tool_number = 0
        self.current_z = 0
        self.current_y = 0
        self.current_x = 0

    def set_cutter_comp(self, cutter_comp, tool_number=None):
        if cutter_comp == CutterComp.LEFT:
            self.cmds.append("G41 D%d" % tool_number)
        elif cutter_comp == CutterComp.RIGHT:
            self.cmds.append("G42 D%d" % tool_number)
        else:
            self.cmds.append("G40")

    def goto_safe_z(self):
        self.g01(z=self.safe_z)

    def literal(self, gcode_line):
        self.cmds.append(gcode_line)

    def to_gcode(self):
        return "\n".join(self.cmds)

    def comment(self, comment_text):
        self.cmds.append("( " + comment_text + ")")

    def g02_xy_radius(self, x=None, y=None, r=None):
        cmd = "G17 G02"
        if x is not None:
            cmd += " X%0.3f" % x
        if y is not None:
            cmd += " Y%0.3f" % y
        cmd += " R%0.3f" % r
        self.cmds.append(cmd)

    def g03_xy_radius(self, x=None, y=None, r=None):
        cmd = "G17 G03"
        if x is not None:
            cmd += " X%0.3f" % x
        if y is not None:
            cmd += " Y%0.3f" % y
        cmd += " R%0.3f" % r
        self.cmds.append(cmd)

    def g02_xy_center(self, x=None, y=None, i=None, j=None,f=100.0):
        cmd = "G17 G02 "
        if x is not None:
            cmd += (" X%0.3f" % x)
        if y is not None:
            cmd += (" Y%0.3f" % y)
        cmd += (" I%0.3f" % i)
        cmd += (" J%0.3f" % j)
        cmd += (" F%0.3f" % f)
        self.cmds.append(cmd)

    def g03_xy_center(self, x=None, y=None, i=None, j=None,f=100.0):
        cmd = "G17 G03 "
        if x is not None:
            cmd += (" X%0.3f" % x)
        if y is not None:
            cmd += (" Y%0.3f" % y)
        cmd += (" I%0.3f" % i)
        cmd += (" J%0.3f" % j)
        cmd += (" F%0.3f" % f)
        self.cmds.append(cmd)

    def g01(self, x=None, y=None, z=None, f=None):
        g = "G01"
        if x is not None:
            g += (" X %0.3f" % x)
            self.current_x = x
        if y is not None:
            g += ( " Y %0.3f" % y)
            self.current_y = y
        if z is not None:
            g += ( " Z %0.3f" % z)
            self.current_z = z
        if f is not None:
            g += ( " F %0.3f" % f)

        self.cmds.append(g)

    def circular_pocket(self, center_x=0, center_y=0, radius=0.0, clockwise=False, finish_allowance=0.0, stepover=0.1, z_depth=0.0, z_step=0.0, final_z=None):
        """
        Same as circular plug, only we machine all material out of the pocket at each level
        """
        self.comment("Circular Pocket: center=(%0.3f, %0.3f, z_depth=%0.3f, z_step=%0.3f, finish_allow=%0.3f, stepover=%0.3f" % (center_x, center_y, z_depth, z_step,finish_allowance,stepover))
        original_z = self.current_z
        if clockwise:
            arc_f = self.g02_xy_center
        else:
            arc_f = self.g03_xy_center

        r_rough = (radius - finish_allowance)
        r_finish = radius
        start_x_finish = center_x - r_finish

        self.set_cutter_comp(CutterComp.NONE)
        self.g01(x=center_x, y=center_y)

        z_levels = _compute_steps( start=original_z, target=z_depth, step=z_step)
        pocket_steps = _compute_steps(start=0,target=r_rough, step=stepover)

        for z in z_levels:
            self.g01(z=z)

            # relative coordinates

            for pocket_start in pocket_steps:
                start_x = center_x - pocket_start

                self.set_cutter_comp(CutterComp.NONE)
                self.g01(start_x)

                self.set_cutter_comp(CutterComp.LEFT, tool_number=1)
                arc_f(i=pocket_start, j=0)

        if finish_allowance > 0:
            self.set_cutter_comp(CutterComp.NONE)
            self.g01(x=start_x_finish)

            self.set_cutter_comp(CutterComp.LEFT, tool_number=1)
            arc_f(i=r_finish, j=0)

        self.set_cutter_comp(CutterComp.NONE)
        self.g01(x=center_x, y=center_y)

        if final_z is not None:
            self.g01(z=final_z)

    def circular_plug(self, center_x=0, center_y=0, radius=0.0,
                      clockwise=False, finish_allowance=0.0,
                      z_depth=0.0, z_step=0.0, final_z=None,
                      xy_feed=150, plunge_feed=10.0):
        """
        Machines a circular plug, with a full depth finishing pass if finish_allowance> 0
        """
        self.comment("Circular Plug: center=(%0.3f, %0.3f, z_depth=%0.3f, z_step=%0.3f, finish_allow=%0.3f" % (center_x, center_y, z_depth, z_step,finish_allowance))
        original_z = self.current_z
        if clockwise:
            arc_f = self.g02_xy_center
        else:
            arc_f = self.g03_xy_center

        r_rough = (radius - finish_allowance)
        r_finish = radius
        start_x_rough = center_x - r_rough
        start_x_finish = center_x - r_finish

        self.set_cutter_comp(CutterComp.NONE)
        self.g01(x=center_x, y=center_y)

        z_levels = _compute_steps( start=original_z, target=z_depth, step=z_step)


        # roughing passes
        self.g01(x=start_x_rough,f=plunge_feed)
        self.set_cutter_comp(CutterComp.LEFT, tool_number=1)
        for z in z_levels:
            self.g01(z=z,f=plunge_feed)
            # relative coordinates
            arc_f(i=r_rough, j=0)

        if finish_allowance > 0:
            self.g01(x=start_x_finish)
            arc_f(i=r_finish, j=0)

        self.set_cutter_comp(CutterComp.NONE)
        self.g01(x=center_x, y=center_y)

        if final_z is not None:
            self.g01(z=final_z)


    def zigzag (self, zlevel, xmin, xmax, ymin, ymax, x_spacing, f_inital, f_rest, f_plunge):
        self.comment("zigzag: zlevel=%0.2f, x=[%0.3f,%0.3f], y=[%0.3f,%03.f]" % (zlevel, xmin, xmax, ymin, ymax))
        self.goto_safe_z()
        self.g01(x=xmin, y=ymin, f=f_inital)
        cx = xmin
        at_min=True

        self.g01(z=zlevel,f=f_plunge)
        self.g01(x=xmin, y=ymin, f=f_rest)
        while cx < xmax:
            if at_min:
                self.g01(y=ymax)
            else:
                self.g01(y=ymin)
            at_min = not at_min
            cx += x_spacing
            self.g01(x=cx)



