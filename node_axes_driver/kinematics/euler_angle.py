import math as m


def is_close(x, y, rtol=1.e-5, atol=1.e-8):
    return abs(x - y) <= atol + rtol * abs(y)


# input data: rotation matrix from direct kinematic
def angles_euler(matrix):
    pfi = 0.0
    if is_close(matrix[2][0], -1.0):
        theta = m.pi / 2.0
        psi = m.atan2(matrix[0][1], matrix[0][2])
    elif is_close(matrix[2][0], 1.0):
        theta = -m.pi / 2.0
        psi = m.atan2(-matrix[0][1], -matrix[0][2])
    else:
        theta = -m.asin(matrix[2][0])
        cos_theta = m.cos(theta)
        psi = m.atan2(matrix[2][1] / cos_theta, matrix[2][2] / cos_theta)
        pfi = m.atan2(matrix[1][0] / cos_theta, matrix[0][0] / cos_theta)

    return m.degrees(pfi), m.degrees(theta), m.degrees(psi)

