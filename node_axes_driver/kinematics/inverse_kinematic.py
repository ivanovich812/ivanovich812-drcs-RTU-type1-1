import numpy as np
import math as m


def take_matrix(matrix):
    result = matrix[0:3, 0:3]
    return result


def take_vector(matrix):
    pos_x = matrix[0][3]
    pos_y = matrix[1][3]
    pos_z = matrix[2][3]
    return [pos_x, pos_y, pos_z]


class InverseKinematic:
    def __init__(self, rotate_matrix, dh_model, tool_frame_offset):
        super().__init__()
        x_offset = tool_frame_offset['offset_X']
        y_offset = tool_frame_offset['offset_Y']
        z_offset = tool_frame_offset['offset_Z']

        trans_matrix = np.array([[1, 0, 0, x_offset],
                                 [0, 1, 0, y_offset],
                                 [0, 0, 1, z_offset],
                                 [0, 0, 0, 1]]).reshape(4, 4)

        new = np.linalg.inv(trans_matrix)

        self.dh = dh_model
        self.vector = take_vector(rotate_matrix @ new)
        self.data = take_matrix(rotate_matrix @ new)

        self.nx_1 = 0.0
        self.k_sq = 0.0
        self.s1_sq = 0.0
        self.s1 = 0.0
        self.s2_sq = 0.0
        self.s2 = 0.0
        self.theta_11 = 0.0
        self.theta_21 = 0.0
        self.theta_31 = 0.0
        self.theta_41 = 0.0
        self.theta_45 = 0.0
        self.theta_51 = 0.0
        self.theta_55 = 0.0
        self.theta_61 = 0.0
        self.theta_65 = 0.0

        self.e_13 = self.data[0][2]
        self.e_23 = self.data[1][2]
        self.e_33 = self.data[2][2]
        self.e_12 = self.data[0][1]
        self.e_22 = self.data[1][1]
        self.e_32 = self.data[2][1]
        self.e_11 = self.data[0][0]
        self.e_21 = self.data[1][0]
        self.e_31 = self.data[2][0]

        self.u_0 = np.array(self.vector).reshape(3, 1)  # [ux_0, uy_0, uz_0] trans

        self.c_0 = self.define_point_c()
        self.calculate_general_parameters()
        self.theta_1()
        self.theta_2()
        self.theta_3()
        self.theta_4_1()
        self.theta_4_5()
        self.theta_5_1()
        self.theta_5_5()
        self.theta_6_1()
        self.theta_6_5()

    def define_point_c(self):
        z_matrix = np.array([0.0, 0.0, 1.0]).reshape(3, 1)
        step_1 = self.dh['6']['d'] * self.data
        step_2 = step_1 @ z_matrix
        step_3 = self.u_0 - step_2  # [cx_0, cy_0, cz_0] trans
        return step_3

    def calculate_general_parameters(self):
        self.nx_1 = m.sqrt((self.c_0[0][0]) ** 2 + (self.c_0[1][0]) ** 2 - 0 ** 2) - self.dh['1']['a']
        self.k_sq = (self.dh['3']['a']) ** 2 + (self.dh['4']['d']) ** 2
        self.s1_sq = self.nx_1 ** 2 + (self.c_0[2][0] - self.dh['1']['d']) ** 2
        self.s1 = m.sqrt(self.s1_sq)
        self.s2_sq = (self.nx_1 + (2 * self.dh['1']['a'])) ** 2 + (self.c_0[2][0] - self.dh['1']['d']) ** 2
        self.s2 = m.sqrt(self.s2_sq)

    def theta_1(self):
        self.theta_11 = m.degrees(m.atan2(self.c_0[1][0], self.c_0[0][0]) - m.atan2(0, (self.nx_1 + self.dh['1']['a'])))

    def theta_2(self):
        a_cos_arg = (self.s1_sq + (self.dh['2']['a']) ** 2 - self.k_sq) / (2 * self.s1 * self.dh['2']['a'])
        self.theta_21 = m.degrees(-m.acos(a_cos_arg) + m.atan2(self.nx_1, self.c_0[2][0] - self.dh['1']['d']))

    def theta_3(self):
        a_cos_arg = (self.s1_sq - (self.dh['2']['a']) ** 2 - self.k_sq) / (2 * self.dh['2']['a'] * m.sqrt(self.k_sq))
        self.theta_31 = m.degrees(m.acos(a_cos_arg) - m.atan2(-self.dh['3']['a'], self.dh['4']['d']) - (m.pi / 2))

    def theta_4_1(self):
        c_11 = m.cos(m.radians(self.theta_11))
        c_23_1 = m.cos(m.radians(self.theta_21) + m.radians(self.theta_31) + m.pi/2)
        s_11 = m.sin(m.radians(self.theta_11))
        s_23_1 = m.sin(m.radians(self.theta_21) + m.radians(self.theta_31) + m.pi/2)
        arg_1 = self.e_23 * c_11 - self.e_13 * s_11
        arg_2 = self.e_13 * c_23_1 * c_11 + self.e_23 * c_23_1 * s_11 - self.e_33 * s_23_1
        self.theta_41 = m.degrees(m.atan2(arg_1, arg_2))

    def theta_4_5(self):
        if self.theta_41 > 0:
            self.theta_45 = self.theta_41 - m.degrees(m.pi)
        else:
            self.theta_45 = self.theta_41 + m.degrees(m.pi)

    def theta_5_1(self):
        s_23_1 = m.sin(m.radians(self.theta_21) + m.radians(self.theta_31) + m.pi/2)
        c_11 = m.cos(m.radians(self.theta_11))
        s_11 = m.sin(m.radians(self.theta_11))
        c_23_1 = m.cos(m.radians(self.theta_21) + m.radians(self.theta_31) + m.pi/2)
        m1 = self.e_13 * s_23_1 * c_11 + self.e_23 * s_23_1 * s_11 + self.e_33 * c_23_1
        self.theta_51 = m.degrees(m.atan2(m.sqrt(1 - m1 ** 2), m1))

    def theta_5_5(self):
        self.theta_55 = -self.theta_51

    def theta_6_1(self):
        s_23_1 = m.sin(m.radians(self.theta_21) + m.radians(self.theta_31) + m.pi/2)
        c_11 = m.cos(m.radians(self.theta_11))
        s_11 = m.sin(m.radians(self.theta_11))
        c_23_1 = m.cos(m.radians(self.theta_21) + m.radians(self.theta_31) + m.pi / 2)
        arg_1 = self.e_12 * s_23_1 * c_11 + self.e_22 * s_23_1 * s_11 + self.e_32 * c_23_1
        arg_2 = -self.e_11 * s_23_1 * c_11 - self.e_21 * s_23_1 * s_11 - self.e_31 * c_23_1
        self.theta_61 = m.degrees(m.atan2(arg_1, arg_2))

    def theta_6_5(self):
        if self.theta_61 >= 0:
            self.theta_65 = self.theta_61 - m.degrees(m.pi)
        else:
            self.theta_65 = self.theta_61 + m.degrees(m.pi)

    def inverse_solution(self):
        inverse_solution = {
                            '1': [self.theta_11,
                                  -self.theta_21,
                                  -self.theta_31,
                                  -self.theta_41,
                                  self.theta_51,
                                  -self.theta_61],
                            '5': [self.theta_11,
                                  -self.theta_21,
                                  -self.theta_31,
                                  -self.theta_45,
                                  self.theta_55,
                                  -self.theta_65]
                            }

        return inverse_solution
