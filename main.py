import gcode

# in machine coordinates
X_MIN = 0
Y_MIN = 0
X_MAX = 48.4
Y_MAX = 87.3
STEPOVER = 0.625
FAST_FEED = 300.0
CUT_FEED = 300.0
PLUNGE_FEED = 10.0

def machine_dogholes():
    p = gcode.Program()
    p.literal("G54 G90")
    p.goto_safe_z()

    SPACING=4.0
    DIAMETER=0.75
    X_COUNT=2
    Y_COUNT=1

    centers = gcode._linear_pattern(0, 0, SPACING, SPACING, X_COUNT,Y_COUNT)
    p.literal("GO1 X0 Y0 F150.")
    p.literal("G01 Z0.1")
    p.literal("M3 S20000")
    for c in centers:
       p.circular_plug(center_x=c[0], center_y=c[1],
                       radius=DIAMETER/2.0,
                       finish_allowance=0.01,
                       clockwise=False ,z_depth=-0.75,
                       z_step=0.05, final_z=p.safe_z,xy_feed=100.0,plunge_feed=10.0)

    return p.to_gcode()

def machine_spoilboard():

    p = gcode.Program()

    #p.safe_z = 0.2
    #p.comment("Home the machine first, and set x&y zero at machine zero!")
    #p.literal("G90 G54")
    #p.goto_safe_z()

    # initial region
    p.literal("M03 S20000")
    p.zigzag(-0.005, X_MIN, X_MAX, Y_MIN, Y_MAX, STEPOVER, FAST_FEED, CUT_FEED, PLUNGE_FEED)

    p.goto_safe_z()
    p.literal("M05")
    p.literal("M02")

    return p.to_gcode()


if __name__ == '__main__':
    #print(machine_spoilboard())
    print(machine_dogholes())

