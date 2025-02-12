import sys
sys.path.append('../')
import os
from PyQt5 import QtWidgets
from config import Configurator
from socket_client import SocketClient
from gui import MainWindow, TrjSaveWindow, TrjUploadWindow
from res import icon_style
from controller import ControllerGui, ControllerLogic
from SQL.sql_client import SQLClient
from logger import Logger

def main():
    app = QtWidgets.QApplication(sys.argv)

    config_path = os.path.join('../CFG', 'config.json')
    configurator = Configurator(config_path)
    save_path = configurator.get_value('save_trajectory_path')
    logger = Logger()

    sql_client = SQLClient(logger, name='rtuGUI-main')
    sql_client_thread = SQLClient(logger, name='rtuGUI-thread')
    sql_client_thread_2 = SQLClient(logger, name='rtuGUI-thread-2')
    sql_client_thread_3 = SQLClient(logger, name='rtuGUI-thread-3')

    client_socket = SocketClient(configurator)
    window = MainWindow(sql_client)
    trj_save_window = TrjSaveWindow(save_path)
    trj_upload_window = TrjUploadWindow(save_path)
    icons = icon_style.IconStyle(window, trj_save_window, trj_upload_window)
    controller_gui = ControllerGui(window, trj_save_window, trj_upload_window, configurator, sql_client)
    controller_logic = ControllerLogic(window, configurator, sql_client, sql_client_thread, sql_client_thread_2, sql_client_thread_3)

    controller_gui.restore_or_maximize.connect(window.restore_or_maximize_window)
    controller_gui.open_trj_save_window.connect(lambda: (trj_save_window.show(), trj_save_window.set_current_time()))
    controller_gui.open_trj_upload_window.connect(lambda: (trj_upload_window.show(), trj_upload_window.walk_dir()))
    controller_gui.lang_rus.connect(window.clicked_language)
    controller_gui.lang_eng.connect(window.clicked_language)
    controller_gui.lang_settings.connect(window.clicked_language)
    controller_gui.theme_style.connect(window.change_theme)
    controller_gui.theme_style.connect(icons.invert_icons)
    controller_gui.theme_style.connect(trj_save_window.change_theme)
    controller_gui.theme_style.connect(trj_upload_window.change_theme)
    controller_gui.trj_save.connect(trj_save_window.write_to_file)
    controller_gui.trj_upload.connect(window.trajectory_edit.setPlainText)
    controller_gui.header_clicked.connect(window.define_first_click_position)
    controller_gui.move_window.connect(window.move_window)
    controller_gui.slide_menu.connect(window.slide_menu)
    controller_gui.work_widget_index.connect(window.open_work_widget)
    controller_gui.work_widget_index.connect(window.slide_menu_short)
    controller_gui.start_page.connect(window.set_start_page)
    controller_gui.joint_keyboard_char.connect(window.edit_joint_point_data)
    controller_gui.virtual_keyboard_char.connect(window.virtual_keyboard_edit_data)
    controller_gui.virtual_keyboard_char.connect(trj_save_window.virtual_keyboard_edit_data)
    controller_gui.sub_work_widget_index.connect(window.open_jog_widget)
    controller_gui.sub_work_widget_index.connect(window.update_speed_unit)
    controller_gui.slider_speed_value.connect(window.update_speed_value)
    controller_gui.rtc_speed_value.connect(window.rtc_update_speed_slider)
    controller_gui.plc_data.connect(window.update_plc_signals)
    controller_gui.plc_data.connect(window.update_mode_status)
    controller_gui.plc_data_invert.connect(window.invert_tab_signals)
    controller_gui.mdb_rtu_data.connect(window.update_mdb_rtu_signals)
    controller_gui.mdb_rtu_data.connect(window.write_mdb_rtu_tab_signals)
    controller_gui.axes_position_data.connect(window.update_axes_poses)
    controller_gui.axes_position_data.connect(window.update_axes_progress)
    controller_gui.axes_limits.connect(window.update_axes_limits)
    controller_gui.fault_code_data.connect(window.update_fault_codes)
    controller_gui.sub_data_types_widget.connect(window.show_data_types_widget)
    controller_gui.joint_points.connect(window.update_joint_points_list)
    controller_gui.slide_joint_edit_keyboard.connect(window.slide_joint_edit_keyboard)
    controller_gui.slide_virtual_keyboard.connect(window.slide_virtual_keyboard)
    controller_gui.remove_joint_item.connect(window.remove_joint_item)
    controller_gui.edit_joint_item.connect(window.show_joint_data_for_edit)
    controller_gui.hide_joint_edit_keyboard.connect(window.slide_joint_edit_keyboard)
    controller_gui.cartesian_position_data.connect(window.update_cartesian_poses)
    controller_gui.scope_signals.connect(window.update_scope_signals)
    controller_gui.scope_signal.connect(window.add_scope_signal)
    controller_gui.clear_scope_signals.connect(window.clear_selected_signals)
    controller_gui.plot_files_list.connect(window.update_plot_files)
    controller_gui.motors_status.connect(window.update_motors_status)
    controller_gui.update_settings_data.connect(window.update_settings)
    controller_gui.apply_settings_data.connect(window.write_settings)
    controller_gui.log_path_signal.connect(window.update_old_log_plain)
    controller_gui.log_list_signal.connect(window.update_log_list)
    controller_gui.rtc_sub_work_widget_index.connect(window.open_jog_widget)
    controller_gui.plc_data.connect(window.disable_main_window)
    controller_gui.switched_mode.connect(controller_logic.up_stop_mode_flag)
    controller_gui.dimensional_stop.connect(client_socket.send_data)
    controller_gui.rtc_speed_value.connect(controller_logic.rtc_save_speed)
    controller_gui.rtc_trajectory_btn_run_pressed.connect(lambda: controller_logic._remote_begin_trajectory
        (window.trajectory_edit.toPlainText()))
    controller_gui.rtc_trajectory_btn_run_released.connect(controller_logic._begin_trajectory)
    controller_gui.rtc_joint_number.connect(controller_logic.rtc_save_joint_number)
    controller_gui.rtc_joint_number.connect(window.rtc_update_btn_jog_axis)
    controller_gui.rtc_btn_jog_pressed.connect(controller_logic.rtc_start_jog_joint_movement)
    controller_gui.rtc_btn_jog_released.connect(controller_logic.rtc_stop_jog_joint_movement)
    # for testing ext_resolvers:
    controller_gui.plc_data.connect(window.ext_res_monitoring)

    # TODO: DONE! TODO added to controller.py
    controller_logic.start_joint_jog.connect(client_socket.send_data)
    controller_logic.stop_joint_jog.connect(client_socket.send_data)
    controller_logic.calibrate_or_define.connect(client_socket.send_data)
    controller_logic.fault_action.connect(client_socket.send_data)
    controller_logic.go_to.connect(client_socket.send_data)
    controller_logic.start_go_to.connect(client_socket.send_data)
    controller_logic.stop_go_to.connect(client_socket.send_data)
    controller_logic.linear_jog.connect(client_socket.send_data)
    controller_logic.reorient_jog.connect(client_socket.send_data)
    controller_logic.jog_acceleration.connect(client_socket.send_data)
    controller_logic.unlock_run_trajectory.connect(window.unlock_run_trajectory)
    controller_logic.trajectory_stop.connect(client_socket.send_data)
    controller_logic.block_run_trajectory.connect(window.lock_run_trajectory)
    controller_logic.plot_data.connect(window.show_plot)
    controller_logic.start_joint_jog.connect(controller_gui.reset_no_dimensional_stop_flag)
    controller_logic.stop_joint_jog.connect(controller_gui.reset_no_dimensional_stop_flag)
    controller_logic.linear_jog.connect(controller_gui.reset_no_dimensional_stop_flag)
    controller_logic.reorient_jog.connect(controller_gui.reset_no_dimensional_stop_flag)

    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
