import gcode


def test_z_levels_even_multiple():
    r = gcode._compute_steps(start=0, target=-.2,step=0.1)
    assert r == [0, -0.1, -0.2 ]

def test_z_levels_not_even_multiple():
    r = gcode._compute_steps(start=0, target=-.21,step=0.1)
    assert r == [0, -0.1, -0.2, -0.21 ]

def test_positive_range():
    r = gcode._compute_steps(start=0, target=0.21,step=0.1)
    assert r == [0, 0.1, 0.2, 0.21 ]

"""
def test_circular_plug():
    p = gcode.Program()
    p.g01(x=0,y=0, z=0)
    p.safe_z = 0.2
    p.goto_safe_z()
    p.set_cutter_comp(gcode.CutterComp.LEFT, 1)
    centers = gcode._linear_pattern(0,0,4.0,4.0,2,2)
    for c in centers:
        p.circular_plug(center_x=c[0], center_y=c[1], radius=0.375, finish_allowance=0.005, clockwise=False ,z_depth=-0.75, z_step=0.2, final_z=p.safe_z)

    r = p.to_gcode()
    print(r)
"""

def test_circular_pocket():
    p = gcode.Program()
    p.g01(x=0,y=0, z=0)
    p.safe_z = 0.2
    p.goto_safe_z()
    p.set_cutter_comp(gcode.CutterComp.LEFT, 1)
    centers = gcode._linear_pattern(0,0,4.0,4.0,2,2)
    #p.circular_pocket(center_x=0.0, center_y=0.0, radius=0.375, finish_allowance=0.005, clockwise=False,
    #                  z_depth=-0.75, z_step=0.2, final_z=p.safe_z, stepover=0.1)
    for c in centers:
        p.circular_pocket(center_x=c[0], center_y=c[1], radius=0.375, finish_allowance=0.005, clockwise=False ,z_depth=-0.75, z_step=0.2, final_z=p.safe_z,stepover=0.1)
    #for c in centers:
    #   p.circular_plug(center_x=c[0], center_y=c[1], radius=0.375, finish_allowance=0.005, clockwise=False ,z_depth=-0.75, z_step=0.2, final_z=p.safe_z)

    r = p.to_gcode()
    print(r)

def test_linear_pattern():

    assert [
        (1.0,1.0),
        (1.0,3.0),
        (3.0,1.0),
        (3.0,3.0)
    ] == gcode._linear_pattern(1.0, 1.0, 2.0, 2.0, 2, 2)