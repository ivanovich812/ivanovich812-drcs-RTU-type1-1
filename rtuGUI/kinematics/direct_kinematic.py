"""
Module for calculation of direct kinematics problem for 6DoF manipulator.
Author: Skirchenko A. V.
Module based on homemade calculations that was made in July 2021 by Author: not diakont property!!!

Input data: angles (in degrees)
"""
import math as m
import numpy as np


def _update_dh_parameters(theta_config, dh_parameters):
    # function for update dh parameters by current angles
    dh = dh_parameters
    try:
        dh[str(1)]['theta'] = theta_config[0]
        dh[str(2)]['theta'] = theta_config[1] * (-1) - m.pi / 2
        dh[str(3)]['theta'] = theta_config[2] * (-1)
        dh[str(4)]['theta'] = theta_config[3] * (-1)
        dh[str(5)]['theta'] = theta_config[4] + m.pi
        dh[str(6)]['theta'] = theta_config[5] * (-1)
    except IndexError:
        pass

    return dh


def _hm(a, d, alpha, theta):
    # homogeneous matrix
    level_a = [m.cos(theta), -(m.sin(theta) * m.cos(alpha)), m.sin(theta) * m.sin(alpha), a * m.cos(theta)]
    level_b = [m.sin(theta), m.cos(theta) * m.cos(alpha), -(m.cos(theta) * m.sin(alpha)), a * m.sin(theta)]
    level_c = [0.0, m.sin(alpha), m.cos(alpha), d]
    level_d = [0.0, 0.0, 0.0, 1.0]

    array = np.array([level_a, level_b, level_c, level_d])
    homo_matrix = array.reshape(4, 4)

    return homo_matrix


def solve_direct_problem(raw_theta_config, dh_parameters):
    theta_config = np.deg2rad(raw_theta_config)
    current_dh = _update_dh_parameters(theta_config, dh_parameters)
    t1 = _hm(current_dh['1']['a'], current_dh['1']['d'], current_dh['1']['alpha'], current_dh['1']['theta'])
    t2 = _hm(current_dh['2']['a'], current_dh['2']['d'], current_dh['2']['alpha'], current_dh['2']['theta'])
    t3 = _hm(current_dh['3']['a'], current_dh['3']['d'], current_dh['3']['alpha'], current_dh['3']['theta'])
    t4 = _hm(current_dh['4']['a'], current_dh['4']['d'], current_dh['4']['alpha'], current_dh['4']['theta'])
    t5 = _hm(current_dh['5']['a'], current_dh['5']['d'], current_dh['5']['alpha'], current_dh['5']['theta'])
    t6 = _hm(current_dh['6']['a'], current_dh['6']['d'], current_dh['6']['alpha'], current_dh['6']['theta'])
    t7 = _hm(current_dh['7']['a'], current_dh['7']['d'], current_dh['7']['alpha'], current_dh['7']['theta'])
    t8 = _hm(current_dh['8']['a'], current_dh['8']['d'], current_dh['8']['alpha'], current_dh['8']['theta'])

    t_res = t1 @ t2 @ t3 @ t4 @ t5 @ t6 @ t7 @ t8


    return {'tcp_x': str(round(t_res[0][3], 2)),
            'tcp_y': str(round(t_res[1][3], 2)),
            'tcp_z': str(round(t_res[2][3], 2))}, t_res
