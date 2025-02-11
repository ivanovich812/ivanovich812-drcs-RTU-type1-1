import threading
import os
import hashlib
import time
from asyncio import sleep
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QPushButton

from file_hadlers import read_json, read_csv, pack_data, read_from_txt_file
from kinematics import solve_direct_problem, angles_euler
from recorder import Recorder
import logging
from event_logger import handler, logger

from clickable_label import ClickableLabel

from Axes_new.Axe_1 import ang_calc_raw as ang_calc_1_axis
from Axes_new.Axe_5 import ang_calc_raw as ang_calc_5_axis
from Axes_new.Axe_6 import ang_calc_raw as ang_calc_6_axis

from Axes_new.record import record_values


class ControllerGui(QObject):
    restore_or_maximize = pyqtSignal()
    open_trj_save_window = pyqtSignal()
    open_trj_upload_window = pyqtSignal()
    slide_menu = pyqtSignal()
    slide_joint_edit_keyboard = pyqtSignal()
    slide_virtual_keyboard = pyqtSignal()
    move_window = pyqtSignal(QMouseEvent)
    header_clicked = pyqtSignal(QMouseEvent)
    work_widget_index = pyqtSignal(int)
    joint_keyboard_char = pyqtSignal(str)
    virtual_keyboard_char = pyqtSignal(str)
    sub_work_widget_index = pyqtSignal(int)
    slider_speed_value = pyqtSignal(str)
    plc_data = pyqtSignal(object)
    mdb_rtu_data = pyqtSignal(object)
    # plc_data_invert = pyqtSignal(object, str, object, str)
    plc_data_invert = pyqtSignal(object)
    axes_position_data = pyqtSignal(dict)
    fault_code_data = pyqtSignal(dict)
    log_path_signal = pyqtSignal(str)
    log_list_signal = pyqtSignal(list)
    cartesian_position_data = pyqtSignal(dict)
    sub_data_types_widget = pyqtSignal(int)
    joint_points = pyqtSignal(dict)
    remove_joint_item = pyqtSignal(str)
    edit_joint_item = pyqtSignal(list)
    hide_joint_edit_keyboard = pyqtSignal()
    scope_signals = pyqtSignal(list)
    scope_signal = pyqtSignal(object)
    clear_scope_signals = pyqtSignal()
    plot_files_list = pyqtSignal(list)
    motors_status = pyqtSignal(str, str)
    trj_save = pyqtSignal(str)
    trj_upload = pyqtSignal(str)
    lang_rus = pyqtSignal(str)
    lang_eng = pyqtSignal(str)
    update_settings_data = pyqtSignal(dict)
    apply_settings_data = pyqtSignal(str)
    lang_settings = pyqtSignal(str)
    theme_style = pyqtSignal(str)
    start_page = pyqtSignal()
    axes_limits = pyqtSignal(dict, int)
    switched_mode = pyqtSignal()
    enable = pyqtSignal()
    disable = pyqtSignal()
    autorized = pyqtSignal()
    not_autorized = pyqtSignal()
    dimensional_stop = pyqtSignal(str)

    rtc_sub_work_widget_index = pyqtSignal(int)
    rtc_speed_value = pyqtSignal(int)
    rtc_joint_number = pyqtSignal(int)
    rtc_btn_enable = pyqtSignal(bool)
    rtc_trajectory_btn_check = pyqtSignal()
    rtc_trajectory_btn_run_pressed = pyqtSignal()
    rtc_trajectory_btn_run_released = pyqtSignal()
    rtc_btn_jog_pressed = pyqtSignal(str)
    rtc_btn_jog_released = pyqtSignal()

    _gui_update_timer = QTimer()
    _rtc_gui_update_timer = QTimer()


    def __init__(self, window, trj_save_window, trj_upload_window, config, database):
        super().__init__()

        self.window = window
        self.trj_save_window = trj_save_window
        self.trj_upload_window = trj_upload_window
        self.config = config
        self.db = database

        self._joint_target_info = None
        self._angles = None
        self._stop_conditions = None
        self._users_path = None
        self.level_dict = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self._default_user = {'login': '', 'password': ''}

        self._reset_rtc_vars()
        self._setup_logger()
        self._connect_signals()
        self._start_timers()
        self._start_rtc_gui_update_timer()

        self.old_in_manual_mode = None
        self.old_enable = None
        self.no_dimensional_stop_flag = True

        # Флаги для RS-триггеров
        self.s = 0
        self.n = 0
        self.b = 0
        self.c = 0

        self._update_dim_points()
        self._update_dimensional_stop_conditions()
        self._init_users_file()
        self._add_default_user()

    def func_emit(self, signal, *args):
        signal.emit(*args)

    def _connect_signals(self):
        for lbl in self.window.header_frame_middle.findChildren(ClickableLabel):
            lbl.clicked.connect(lambda: self.func_emit(self.start_page))

        for btn in self.window.body_frame_left_menu.findChildren((QPushButton, ClickableLabel)):
            btn.clicked.connect(self._menu_button_event)

        for btn in self.window.data_joint_keyboard_frame.findChildren(QPushButton):
            if btn.text() != 'OK':
                btn.clicked.connect(self._joint_keyboard_button_event)

        for btn in self.window.virtual_keyboard_frame.findChildren(QPushButton):
            if btn.text() != 'OK':
                btn.clicked.connect(self._virtual_keyboard_button_event)

        for btn in self.trj_save_window.window_frame.findChildren(QPushButton):
            btn.clicked.connect(lambda: self.trj_save_window.close())

        self.window.btn_close_window.clicked.connect(lambda: self.window.close())
        self.trj_upload_window.btn_upload.clicked.connect(lambda: self.trj_upload_window.close())
        self.trj_upload_window.btn_cancel.clicked.connect(lambda: self.trj_upload_window.close())
        self.trj_upload_window.btn_close_window.clicked.connect(lambda: self.trj_upload_window.close())
        self.window.btn_minimize_window.clicked.connect(lambda: self.window.showMinimized())
        self.window.btn_restore_window.clicked.connect(lambda: self.func_emit(self.restore_or_maximize))
        self.window.btn_lang_rus.clicked.connect(
            lambda: self.func_emit(self.lang_rus, self.window.btn_lang_rus.accessibleName()))
        self.window.btn_lang_eng.clicked.connect(
            lambda: self.func_emit(self.lang_eng, self.window.btn_lang_eng.accessibleName()))
        self.window.cmb_settings_language.currentIndexChanged.connect(
            lambda: self.func_emit(self.lang_settings, str(self.window.cmb_settings_language.currentText())))
        self.window.cmb_settings_theme.currentIndexChanged.connect(
            lambda: self.func_emit(self.theme_style, str(self.window.cmb_settings_theme.currentText())))
        self.window.trajectory_btn_save.clicked.connect(lambda: self.func_emit(self.open_trj_save_window))
        self.window.trajectory_btn_upload.clicked.connect(lambda: self.func_emit(self.open_trj_upload_window))
        self.window.btn_menu.clicked.connect(lambda: self.func_emit(self.slide_menu))
        self.window.btn_menu.clicked.connect(
            lambda: self.func_emit(self.update_settings_data, self.config.read_config()))
        self.window.btn_menu.clicked.connect(self._update_axes_limits)
        self.window.btn_settings_apply.clicked.connect(
            lambda: self.func_emit(self.apply_settings_data, self.config.config_path))
        self.window.header_frame.mousePressEvent = self._header_clicked_event
        self.window.header_frame.mouseMoveEvent = self._move_cursor_event
        self.window.jog_mode_group.buttonClicked.connect(self._jog_mode_group_event)
        self.window.slider_speed.valueChanged.connect(
            lambda: self.func_emit(self.slider_speed_value, str(self.window.slider_speed.value())))
        self.window.btn_enable.clicked.connect(self._update_motors_status)
        self.window.data_types_group.buttonClicked.connect(self._data_types_group_event)
        self.window.data_back_group.buttonClicked.connect(self._data_types_group_event)
        self.window.btn_joints_keyboard.clicked.connect(lambda: self.func_emit(self.slide_joint_edit_keyboard))
        self.window.btn_virtual_keyboard.clicked.connect(lambda: self.func_emit(self.slide_virtual_keyboard))
        self.window.btn_joints_action_change.clicked.connect(self._prepare_joint_target_for_change)
        self.window.data_joints_list.itemDoubleClicked.connect(self._save_joint_target_info)
        self.window.btn_joints_action_delete.clicked.connect(self._delete_selected_joint_target)
        self.window.btn_j_edit_ok.clicked.connect(self._delete_selected_joint_target)
        self.window.btn_data_joint_ok.clicked.connect(self._delete_selected_joint_target)
        self.window.btn_j_edit_ok.clicked.connect(lambda: self.hide_joint_edit_keyboard.emit())
        self.window.lst_avaliable_signals.itemDoubleClicked.connect(self._scope_item_selected)
        self.window.btn_clear_signals.clicked.connect(lambda: self.clear_scope_signals.emit())
        self.window.tab_scope.tabBarClicked.connect(self._update_plot_files_event)
        self.window.trajectory_btn_clear.clicked.connect(self.window.clear_trajectory)
        self.window.log_files_list.itemDoubleClicked.connect(self._old_log_upload)
        self.window.log_tab.tabBarClicked.connect(self._update_log_list)
        handler.new_record.connect(self._update_log_list)
        self.window.btn_change.clicked.connect(lambda: self.change_password())
        self.window.btn_log_in.clicked.connect(lambda: self.user_log_in())
        self.window.btn_log_out.clicked.connect(lambda: self.user_log_out())
        self.window.btn_panic.clicked.connect(lambda: self.window.trajectory_btn_run.setChecked(False))
        self.autorized.connect(self.window.authorized)
        self.not_autorized.connect(self.window.not_authorized)

        self.trj_save_window.btn_save.clicked.connect(
            lambda: self.func_emit(self.trj_save, str(self.window.trajectory_edit.toPlainText())))
        self.trj_upload_window.btn_cancel.clicked.connect(lambda: self.window.clear_trajectory())
        self.trj_upload_window.btn_upload.clicked.connect(
            lambda: self.func_emit(self.trj_upload, str(self.trj_upload_window.read_from_file())))
        self.trj_upload_window.lst_select.itemDoubleClicked.connect(
            lambda: self.func_emit(self.trj_upload, str(self.trj_upload_window.read_from_file())))
        self.rtc_btn_enable.connect(self._rtc_update_motors_status)
        self.trj_upload_window.btn_delete.clicked.connect(lambda: self.trj_upload_window.delete_file())

        for func in (self._show_plc_signals,
                     self._show_mdb_rtu_signals,
                     self._invert_plc_signals,
                     self._show_axes_poses,
                     self._show_status_word,
                     self._show_fault_code,
                     self._show_joint_points,
                     self._show_cartesian_poses,
                     self._check_dimensional_stop,
                     self._get_scope_signals
                     ):
            self._gui_update_timer.timeout.connect(func)

        self._rtc_gui_update_timer.timeout.connect(self._update_rtc_gui_data)

    def _init_users_file(self):  # Инициализация файла, если этого не сделать програма вылетит c ошибкой, что файла нет
        path = self.config.get_value('users_path')
        filename = 'users.txt'
        self._users_path = os.path.join(path, filename)

        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        if not os.path.exists(self._users_path):
            with open(self._users_path, 'w'):
                logger.info(self.tr(f"Created directory: '{self._users_path}'"))
                pass

    def _add_default_user(self):
            login = self._default_user['login']
            password = self._default_user['password']

            with open(self._users_path, 'r') as f:
                user = f.read().splitlines()  # Считываем всех пользователей из файла

            if user and user!=['']:
                pass
            else:
                with open(self._users_path, 'a') as f:
                    f.write(f'{login}:{hashlib.sha256(password.encode()).hexdigest()}\n')  # Добавляем нового пользователя

    def change_password(self):
        new_login = self.window.led_new_login.text()
        new_password = self.window.led_new_password.text()
        new_password_repeat = self.window.led_repeat_password.text()

        if new_password == new_password_repeat:
            result = self._change_user_password(new_login, hashlib.sha256(new_password.encode()).hexdigest())  # Вызываем функцию добавления пользователя. И хешируем пароль(безопасность)
        else:
            result = 101

        if result == 101:
            logger.error(self.tr('Новые пароли не совпадают!.'))
        else:
            logger.info(self.tr('Изменение логина и пароля прошло успешно!'))

    def user_log_in(self):
        login = self.window.led_login.text()
        password = self.window.led_password.text()
        result = self._get_user(login, hashlib.sha256(password.encode()).hexdigest())

        if result:
            self.autorized.emit()
            logger.info(self.tr('Вы вошли в систему.'))
        else:
            logger.error(self.tr('Неверный логин или пароль!'))

    def user_log_out(self):
        self.not_autorized.emit()
        logger.info(self.tr('Вы вышли из системы.'))

    def _change_user_password(self, login: str, password: str) -> int:
        with open(self._users_path, 'w') as f:
            f.write(f'{login}:{password}\n')  # Перезаписывает нового пользователя

        return 100

    def _get_user(self, login: str, password: str) -> bool:
        with open(self._users_path, 'r') as f:
            users = f.read().splitlines()  # Считываем всех пользователей из файла

        for user in users:
            args = user.split(':')
            if login == args[0] and password == args[1]:  # Если пользователь с таким логином и паролем существует
                return True
        return False

    def _reset_rtc_vars(self):

        self.db.add_to_rtc_control('subprocess_num', 0)
        self.db.add_to_rtc_control('rtc_sub_work_widget_index', 0)
        self.db.add_to_rtc_control('rtc_cmd_status', 0)
        self.db.add_to_rtc_control('rtc_joint_number', 0)

        self.db.add_to_rtc_control('rtc_btn_enable', False)
        self.db.add_to_rtc_control('rtc_trajectory_btn_check', False)
        self.db.add_to_rtc_control('rtc_trajectory_btn_run', False)

    def reset_no_dimensional_stop_flag(self):
        self.no_dimensional_stop_flag = True

    def json_data(self, json_key):
        path = self.config.get_value(json_key)
        if path is not None:
            data = read_json(path)
            return (data)
        else:
            print(f'Path {json_key} not found!')

    def _update_motors_status(self):
        if self.window.btn_enable.isChecked():
            self.motors_status.emit('On', str(self.window.btn_enable.isChecked()))
            self.db.add_to_rtc_control('rtc_btn_enable', True)
            logger.info(self.tr('Motors: On.'))
        else:
            self.motors_status.emit('Off', str(self.window.btn_enable.isChecked()))
            logger.info(self.tr('Motors: Off'))
            self.db.add_to_rtc_control('rtc_btn_enable', False)

    def _rtc_update_motors_status(self, enable):
        if enable:
            self.window.btn_enable.setChecked(True)
            self.motors_status.emit('On', str(self.window.btn_enable.isChecked()))
            # logger.info(self.tr('Motors: On.'))
        else:
            self.window.btn_enable.setChecked(False)
            self.motors_status.emit('Off', str(self.window.btn_enable.isChecked()))
            # logger.info(self.tr('Motors: Off'))

    def _update_plot_files_event(self):
        if self.window.tab_scope.currentIndex() == 0:
            files = os.listdir(self.config.get_value('plots_directory'))
            self.plot_files_list.emit(files)

    def _save_joint_target_info(self, item):
        self._joint_target_info = item.text()

    def _prepare_joint_target_for_change(self):
        if self._joint_target_info:
            raw_data = self._joint_target_info.split(':')
            raw_position_data = raw_data[1].strip().strip('[]').split(',')
            data = list(map(float, raw_position_data))
            data.insert(0, raw_data[0])
            self.edit_joint_item.emit(data)

    def _delete_selected_joint_target(self):
        if self._joint_target_info:
            target_name = self._joint_target_info.split(':')[0]
            self.remove_joint_item.emit(target_name)
            self._joint_target_info = None

    def _start_timers(self):
        timeout = self.config.get_value('gui_update_time')
        if timeout is not None:
            self._gui_update_timer.start(timeout)
        else:
            print('timer-updater not configured')

    def _header_clicked_event(self, event):
        # TODO: watch (***)
        self.header_clicked.emit(event)

    def _move_cursor_event(self, event):
        # TODO: watch (***)
        self.move_window.emit(event)

    def _menu_button_event(self):
        sender = self.sender()
        index = int(sender.accessibleName())
        self.work_widget_index.emit(index)

    def _joint_keyboard_button_event(self):
        sender = self.sender()
        char = str(sender.text())
        self.joint_keyboard_char.emit(char)

    def _virtual_keyboard_button_event(self):
        sender = self.sender()
        char = str(sender.text())
        self.virtual_keyboard_char.emit(char)

    def _jog_mode_group_event(self, btn):
        self.sub_work_widget_index.emit(int(btn.accessibleName()))
        self.db.add_to_rtc_control('rtc_sub_work_widget_index', int(btn.accessibleName()))

    def _switch_mode_stop_trajectory(self, data):
        in_manual_mode = data['in_manual_mode']
        if in_manual_mode != self.old_in_manual_mode:
            self.switched_mode.emit()
        self.old_in_manual_mode = in_manual_mode

    def _show_plc_signals(self):
        data = self.db.read_plc_io_monitor()
        if data is not None:
            self.plc_data.emit(data)
        self._switch_mode_stop_trajectory(data)


    def _show_mdb_rtu_signals(self):
        data = self.db.read_mdbrtu_io_monitor()
        if data is not None:
            self.mdb_rtu_data.emit(data)

    def _invert_plc_signals(self):
        monitor_data = self.db.read_plc_io_monitor()
        if monitor_data is not None:
            self.plc_data_invert.emit(monitor_data)

    def _show_axes_poses(self):
        data = self.db.read_fc_axes_monitor()
        if data is not None:
            self._angles = data.get('actual_position', None)
            self.axes_position_data.emit(self._angles)

    def _show_status_word(self):
        data = self.db.read_fc_axes_monitor()
        if data is not None:
            self._status_word = data.get('status_word', None)
            self._enable_bits = []
            for item in self._status_word.values():
                item = int(item)
                item = format(item, 'b')
                item = int(item[0]) # читаем 0-бит
                self._enable_bits.append(item)

            # если все оси enable
            # if all([x == 1 for x in self._enable_bits]):
            #     if all([x == 1 for x in self._enable_bits]) != self.old_enable:
            #         self.enable.emit()
            #         self.old_enable = True
            # if all([x == 0 for x in self._enable_bits]):
            #     if all([x == 0 for x in self._enable_bits]) == self.old_enable:
            #         self.disable.emit()
            #         self.old_enable = False

            # если хотя бы одна ось enable
            if any(self._enable_bits):
                if any(self._enable_bits) != self.old_enable:
                    self.enable.emit()
                    self.old_enable = True
            if all([x == 0 for x in self._enable_bits]):
                if all([x == 0 for x in self._enable_bits]) == self.old_enable:
                    self.disable.emit()
                    self.old_enable = False

    def _start_rtc_gui_update_timer(self):
        timeout = self.config.get_value('rtc_update_time')
        if timeout is not None:
            self._rtc_gui_update_timer.start(timeout)
        else:
            print('rtc_update_timer not configured')

    def _update_rtc_gui_data(self):
        data = self.db.read_rtc_control()
        if data is not None:
            index = data['rtc_sub_work_widget_index']
            self.rtc_sub_work_widget_index.emit(index)

            value = data['rtc_speed_value']
            self.rtc_speed_value.emit(value)

            number = data['rtc_joint_number']
            self.rtc_joint_number.emit(number)

            var = data['rtc_btn_enable']
            self.rtc_btn_enable.emit(var)

            var = data['rtc_trajectory_btn_check']
            if var and self.s == 0 :
                self.rtc_trajectory_btn_check.emit()
                self.s = 1
            if var == 0:
                self.s = 0

            var = data['rtc_trajectory_btn_run']
            if var and self.n == 0 :
                self.window.trajectory_btn_run.setChecked(True)
                self.rtc_trajectory_btn_run_pressed.emit()
                self.n = 1
            if var == 0 and self.n == 1:
                self.window.trajectory_btn_run.setChecked(False)
                self.rtc_trajectory_btn_run_released.emit()
                self.n = 0

            click = data['rtc_btn_jog_cw']
            if click == 1 and self.b == 0:
                sign = '+'
                self.rtc_btn_jog_pressed.emit(sign)
                self.b = 1
            if click == 0 and self.b == 1:
                self.rtc_btn_jog_released.emit()
                self.b = 0

            click = data['rtc_btn_jog_ccw']
            if click == 1 and self.c == 0:
                sign = '-'
                self.rtc_btn_jog_pressed.emit(sign)
                self.c = 1
            if click == 0 and self.c == 1:
                self.rtc_btn_jog_released.emit()
                self.c = 0

    def _update_axes_limits(self):
        self._axes_limits = {}
        self._axes_limits_alarm_offset = self.config.get_value('axes_limits_alarm_offset')
        self._axes_limits['axis_1_min'] = self.config.get_value('axis_1_min')
        self._axes_limits['axis_1_max'] = self.config.get_value('axis_1_max')
        self._axes_limits['axis_2_min'] = self.config.get_value('axis_2_min')
        self._axes_limits['axis_2_max'] = self.config.get_value('axis_2_max')
        self._axes_limits['axis_3_min'] = self.config.get_value('axis_3_min')
        self._axes_limits['axis_3_max'] = self.config.get_value('axis_3_max')
        self._axes_limits['axis_4_min'] = self.config.get_value('axis_4_min')
        self._axes_limits['axis_4_max'] = self.config.get_value('axis_4_max')
        self._axes_limits['axis_5_min'] = self.config.get_value('axis_5_min')
        self._axes_limits['axis_5_max'] = self.config.get_value('axis_5_max')
        self._axes_limits['axis_6_min'] = self.config.get_value('axis_6_min')
        self._axes_limits['axis_6_max'] = self.config.get_value('axis_6_max')
        self.axes_limits.emit(self._axes_limits, self._axes_limits_alarm_offset)

    def _show_fault_code(self):
        data = self.db.read_fc_axes_monitor()
        if data is not None:
            self._fault_codes = data.get('fault_code', None)
            self.fault_code_data.emit(self._fault_codes)

    def _update_dim_points(self):
        data = self.json_data('robot_parameters')
        for key in data:
            if key[:3] == 'dh_':
                self.window.cmb_settings_dim_point.addItem(key)

    def _update_dimensional_stop_conditions(self):
        path = self.config.get_value('stop_conditions_directory')
        with open(path, "r") as file:
            self._stop_conditions = file.read().replace('\n', ' ')

    def _check_dimensional_stop(self):
        if self.window.cmb_settings_dim_mode.currentText() == 'Enable':
            data = self.json_data('robot_parameters')
            for key in data:
                if key[:3] == 'dh_':
                    dh_point = key
                    dh = data.get(dh_point, None)
                    if data is not None and dh is not None:
                        try:
                            xyz_position, matrix = solve_direct_problem(list(self._angles.values()), dh)
                            x = float(xyz_position['tcp_x'])
                            y = float(xyz_position['tcp_y'])
                            z = float(xyz_position['tcp_z'])
                            if self.no_dimensional_stop_flag and eval(self._stop_conditions):
                                self.no_dimensional_stop_flag = False
                                self.dimensional_stop.emit('all:emergency_stop')
                                logger.warning(self.tr('Dimensional stop is active!'))

                        except Exception as e:
                            pass
        else:
            pass

    def _show_cartesian_poses(self):
        dh_point = 'dh'

        if self.window.cmb_settings_dim_point.currentText() != 'None':
            dh_point = self.window.cmb_settings_dim_point.currentText()

        data = self.json_data('robot_parameters')
        dh = data.get(dh_point, None)
        if data is not None and dh is not None:
            try:
                xyz_position, matrix = solve_direct_problem(list(self._angles.values()), dh)
                euler_angles = angles_euler(matrix)
                self.cartesian_position_data.emit({**xyz_position, **euler_angles})
            except Exception as e:
                pass

    def _data_types_group_event(self, btn):
        self.sub_data_types_widget.emit(int(int(btn.accessibleName())))

    def _show_joint_points(self):
        data = self.db.read_j_points()
        if data is not None:
            self.joint_points.emit(data)
        else:
            print('System file "joint_points.json" is broken. Fix this problem and restart application.')
            self._gui_update_timer.timeout.disconnect(self._show_joint_points)

    def _get_scope_signals(self):
        data = self.db.read_scope_signals()
        try:
            signals = list(data.keys())
            self.scope_signals.emit(signals)
        except Exception as e:
            pass

    def _scope_item_selected(self, item):
        self.scope_signal.emit(item.text())

    def _setup_logger(self):
        logger.setLevel(self.level_dict['INFO'])
        handler.new_record.connect(self.window.update_big_log)
        handler.new_record.connect(self.window.update_little_log)
        logger.info(self.tr('Application started.'))

    def _old_log_upload(self, item):
        path = self.config.get_value('gui_log_path')
        log_name = item.text()
        log_path = os.path.join(path, f'{log_name}')
        self.log_path_signal.emit(log_path)

    def _update_log_list(self):
        path = self.config.get_value('gui_log_path')
        file_list = os.listdir(path)
        self.log_list_signal.emit(file_list)


def generate_point_name(data, variant_name, index, name_space):
    # function for generate target name
    name = None
    for i in name_space:
        if i != index and variant_name + str(i) not in data.keys() and i > index:
            name = variant_name + str(i)
            break
    return name


def find_actual_position(data):
    # function for search actual position data
    key = 'actual_position'
    if key in data.keys():
        return data[key]
    else:
        return None


def prepare_point_data(position_data):
    # check length of position data and create point data
    if len(position_data) == 6:
        return list(position_data.values())
    else:
        return None


def create_edited_point(dataset):
    if dataset and len(dataset) == 7:
        return dataset[0], list(map(float, dataset[1:]))
    else:
        return None


def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def isint(str):
    try:
        int(str)
        return  True
    except ValueError:
        return False

def format_trajectory_text(data):
    raw_data = data.split('\n')
    # Добавлен фильтр однострочных комментариев (использовать # первым символом строки!)
    formatted_data = list(filter((lambda x: x and x.lstrip()[0] != '#'), raw_data))
    return formatted_data


def separate_trajectory_text(data):
    return list(map(lambda x: x.split(':'), data))

def add_def_data_to_trajectory(config, data):
    full_data = []
    for raw in data:
        if raw[0] == 'DEF':
            def_file_name = raw[1] + '.txt'
            def_path = config.get_value('save_trajectory_path')
            full_path = def_path + def_file_name
            if os.path.exists(full_path):
                def_data = read_from_txt_file(def_path, def_file_name)
                def_raw_data = format_trajectory_text(def_data)
                formatted_def_data = separate_trajectory_text(def_raw_data)
                for def_raw in formatted_def_data:
                    full_data.append(def_raw)
            else:
                print('Not such trajectory function file!')
                full_data = []
                break
        else:
            full_data.append(raw)
    return full_data

def test_point_syntax(accessible_points, test_points, plc_registers, plc_io_registers, rtu_registers):
    def check_custom_cmd(cmd, plc_registers_, plc_io_registers_, rtu_registers_):
        if cmd[0] == 'cmdWait':
            if len(cmd) < 2:
                return False
            if is_number(cmd[1]):
                return True
            # if cmd[1].lstrip().isdigit():
            #     return True

        if cmd[0] == 'cmdStatus':
            if len(cmd) < 2:
                return False
            if cmd[1].lstrip().isdigit():
                return True

        if cmd[0] == 'cmdStop':
            return True if len(cmd) < 2 else False

        if cmd[0] == 'cmdSetDO':
            if len(cmd) < 3:
                return False
            else:
                try:
                    if cmd[1] in plc_registers_.keys() and 0 <= int(cmd[2].lstrip()) <= 1:
                        return True
                except TypeError:
                    return False

        if cmd[0] == 'cmdSetReg':
            if len(cmd) < 3:
                return False
            else:
                try:
                    if cmd[1] in rtu_registers_.keys() and isint(cmd[2].lstrip()):
                        return True
                except TypeError:
                    return False

        if cmd[0] == 'cmdPrint':
            return True

        if cmd[0] == 'cmdRec':
            return True

        if cmd[0] == 'cmdBrake':
            return True

        if cmd[0] == 'cmdWhileDiff':
            if len(cmd) < 4:
                return False
            else:
                try:
                    print(cmd[1] in rtu_registers_.keys())
                    print(cmd[2] in rtu_registers_.keys())
                    print(cmd[3].lstrip().isdigit())
                    if (cmd[1] in rtu_registers_.keys()) and (cmd[2] in rtu_registers_.keys()) and (cmd[3].lstrip().isdigit()):
                        return True
                except TypeError:
                    return False

        if cmd[0] == 'cmdWhileGripper':
            if len(cmd) < 6:
                return False
            else:
                try:
                    print(cmd[1] in rtu_registers_.keys())
                    print(cmd[2] in rtu_registers_.keys())
                    print(cmd[3].lstrip().isdigit())
                    print(cmd[4] in plc_io_registers_.keys())
                    print(isint(cmd[5].lstrip()))
                    if cmd[1] in rtu_registers_.keys() and \
                            cmd[2] in rtu_registers_.keys() and \
                            cmd[3].lstrip().isdigit() and \
                            cmd[4] in plc_io_registers_.keys() and \
                            isint(cmd[5].lstrip()):
                        return True
                except TypeError:
                    return False

        if cmd[0] == 'cmdIf':
            if len(cmd) < 3:
                return False
            else:
                try:
                    if cmd[1] in plc_io_registers_.keys() and 0 <= int(cmd[2].lstrip()) <= 1:
                        return True
                except TypeError:
                    return False

        return False

    counter_test_point = len(test_points)
    counter_exist_point = -1
    counter_num_params = -1
    counter_accuracy = -1

    # test is data empty
    if test_points:
        counter_exist_point = 0
        counter_num_params = 0
        counter_accuracy = 0

    for point in test_points:
        # test is point exists
        if point[0] in accessible_points.keys() or point[0] in ('cmdWait', 'cmdStop', 'cmdSetDO', 'cmdWhileDiff', 'cmdWhileGripper', 'cmdIf', 'cmdSetReg', 'cmdStatus', 'cmdPrint', 'cmdRec', 'cmdBrake'):
            counter_exist_point += 1

        # test accuracy parameter
        if point[0] in accessible_points.keys():
            if len(point) > 2:
                try:
                    if len(eval(point[2])) == 6:
                        counter_accuracy += 1
                except:
                    pass
            else:
                counter_accuracy += 1
        else:
            counter_accuracy += 1

        # test num parameters (time value)
        try:
            if point[1].lstrip().isdigit() or check_custom_cmd(point, plc_registers, plc_io_registers, rtu_registers):
                counter_num_params += 1
        except IndexError:
            if check_custom_cmd(point, plc_registers, plc_io_registers, rtu_registers):
                counter_num_params += 1

    return counter_test_point == counter_exist_point, counter_test_point == counter_num_params, counter_test_point == counter_accuracy


def add_coordinates_for_trajectory(accessible_points, formatted_trajectory):
    print('accessible_points', accessible_points)
    print('formatted_trajectory', formatted_trajectory)
    trajectory = formatted_trajectory.copy()
    for point in trajectory:
        point_name = point[0]
        if point_name not in ('cmdWait', 'cmdStop', 'cmdSetDO', 'cmdWhileDiff', 'cmdWhileGripper', 'cmdIf', 'cmdSetReg', 'cmdStatus', 'cmdPrint', 'cmdRec', 'cmdBrake'):
            if len(point) < 3:
                point[0] = accessible_points[point_name]
                point[1] = int(point[1])
            else:
                point[0] = accessible_points[point_name]
                point[1] = int(point[1])
                point[2] = eval(point[2])

        else:
            point[0] = point_name
            if len(point) > 1 and point_name != 'cmdSetDO' and point_name != 'cmdWait' and point_name != 'cmdSetReg' and point_name != 'cmdWhileDiff' and point_name != 'cmdWhileGripper' and point_name != 'cmdIf':
                point[1] = int(point[1])
            if len(point) == 3 and point_name == 'cmdSetDO':
                point[1] = str(point[1])
                point[2] = bool(int(point[2]))
            if len(point) == 3 and point_name == 'cmdSetReg':
                point[1] = str(point[1])
                point[2] = int(point[2])
            if len(point) == 4 and point_name == 'cmdWhileDiff':
                point[1] = str(point[1])
                point[2] = str(point[2])
                point[3] = int(point[3])
            if len(point) == 6 and point_name == 'cmdWhileGripper':
                point[1] = str(point[1])
                point[2] = str(point[2])
                point[3] = int(point[3])
                point[4] = str(point[4])
                point[5] = int(point[5])
            if len(point) == 5 and point_name == 'cmdIf':
                point[1] = str(point[1])
                point[2] = bool(int(point[2]))
            if len(point) > 1 and point_name == 'cmdWait':
                point[1] = float(point[1])
    return trajectory


def save_raw_positions(data, tmp=None):
    if tmp is None:
        tmp = {}
    positions = tmp
    for key, value in data.items():
        if not isinstance(value, dict):
            if 'raw_position' in key:
                positions[key] = value
        else:
            save_raw_positions(value, positions)
    return positions


def _get_selected_scope_signals(list_widget):
    for i in range(list_widget.count()):
        yield list_widget.item(i).text()


class ControllerLogic(QObject):
    # TODO: remove all stop signals and make ONE SIGNAL!!!

    # TODO: create two separate methods for speed control mode and position control mode.
    #  connect this methods with mode buttons in GUI!!!
    calibrate_or_define = pyqtSignal(str)
    start_joint_jog = pyqtSignal(str)
    stop_joint_jog = pyqtSignal(str)
    fault_action = pyqtSignal(str)
    go_to = pyqtSignal(str)
    start_go_to = pyqtSignal(str)
    stop_go_to = pyqtSignal(str)
    linear_jog = pyqtSignal(str)
    reorient_jog = pyqtSignal(str)
    jog_acceleration = pyqtSignal(str)
    unlock_run_trajectory = pyqtSignal()
    block_run_trajectory = pyqtSignal()
    trajectory_stop = pyqtSignal(str)
    plot_data = pyqtSignal(dict)

    linear_send_timer = QTimer()
    reorient_send_timer = QTimer()
    actual_position_update_timer = QTimer()
    scope_timer = QTimer()
    gripper_timer = QTimer()
    # _rtc_logic_update_timer = QTimer()

    ZERO_POINT = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def __init__(self, window, config, database, database_thread, database_thread_2, database_thread_3):
        super().__init__()
        self.window = window
        self.config = config
        self.db = database
        self.db_thread = database_thread
        self.db_thread_2 = database_thread_2
        self.db_thread_3 = database_thread_3

        self.recorder = None
        self._default_axis_accuracy = {'1': 0.05,'2': 0.05,'3':0.05,'4': 0.08,'5': 0.08,'6': 0.08}
        self._point_name_space = tuple(range(1, 201, 1))
        self._joint_number = None
        self._available_joint_points = {}
        self._speed_value_percent = 0
        self._joint_target_info = ''
        self._linear_direction = None
        self._linear_axis = None
        self._discrete_levels = {'low_discrete': 1, 'medium_discrete': 500, 'high_discrete': 500}
        self._linear_discrete_distance = '50'
        self._linear_send_time = 0.001
        self._linear_working_frame = 'BASE'

        self._reorient_direction = None
        self._reorient_axis = None
        self._reorient_discrete_distance = '10'
        self._reorient_send_time = 0.001
        self._reorient_working_frame = 'TOOL'

        self._trajectory = None
        self._actual_position = None
        self._actual_mdb_rtu_data = None
        self._mdb_rtu_connection_flag = None # true - когда все устройства на связи, добавить по надобности в def go_to
        self._actual_plc_data = None
        self._scope_signals = []
        self._stop_record_flag = False
        self._stop_mode_flag = False

        # for modbus rtu gripper
        # self.tool_managment_commands = {
        #     'open_gripper': [['cmdSetReg', '10_out_operation_mode', 2],
        #            ['cmdSetReg', '10_out_starting_type', 10],
        #            ['cmdSetReg', '10_out_motor_speed_set_value', 300],
        #            ['cmdSetReg', '10_out_motor_current_set_value', 9],
        #            ['cmdWhileGripper', '10_in_motor_actual_current_value', '10_out_motor_current_set_value', 300, 'in_multitool_1_on', 310],
        #            ['cmdSetReg', '10_out_motor_current_set_value', 4],
        #            ['cmdWhileGripper', '10_in_motor_actual_current_value', '10_out_motor_current_set_value', 300, 'in_multitool_1_on', 2000],
        #            ['cmdSetReg', '10_out_motor_current_set_value', -6],
        #            ['cmdWhileGripper', '10_in_motor_actual_current_value', '10_out_motor_current_set_value', 200, 'in_reset', 200],
        #            ['cmdSetReg', '10_out_starting_type', 0],
        #            ['cmdSetReg', '10_out_motor_current_set_value', 0],
        #            ['cmdSetReg', '10_out_motor_speed_set_value', 0],
        #            ['cmdIf', 'in_multitool_1_on', '1'],
        #             ['cmdStop']],
        #     'close_gripper':[
        #         ['cmdPrint',111111],
        #         ['cmdWait',1]
        #                      ]
        # }

        # for usual gripper
        self.tool_managment_commands = {
            'open_gripper': [
                             ['cmdSetDO', 'out_gripper_1_1', True],
                             ['cmdStop']
            ],
            'close_gripper':[
                ['cmdSetDO','out_gripper_1_1',False],
                ['cmdStop']
             ]
        }


        self._connect_signals()
        self._read_available_points()
        self._start_timers()

        self.subprocess_num = 0
        self.old_status = False
        self.rtc_cmd_status = None

        self._trajectory_thread = threading.Thread(target=self._go_to_trajectory, args=(), daemon=True)
        self.reset_rtc_speed_value()


    def _connect_signals(self):
        for btn in self.window.calibration_tab.findChildren(QPushButton):
            btn.clicked.connect(self._calibrate_or_define_event)

        for btn in (self.window.btn_fault_reset, self.window.btn_panic):
            btn.clicked.connect(self._handle_fault_event)

        self.window.btn_close_window.clicked.connect(self._remove_enable)
        self.window.slider_speed.valueChanged.connect(lambda: self._save_speed(self.window.slider_speed.value()))
        self.window.axes_group.buttonClicked.connect(self._save_joint_number)
        self.window.jog_joint_controls_group.buttonPressed.connect(self._start_jog_joint_movement)
        self.window.jog_joint_controls_group.buttonReleased.connect(self._stop_jog_joint_movement)
        self.window.btn_enable.clicked.connect(self._enable_axes)
        self.window.btn_joints_action_empty.clicked.connect(lambda: self._add_joint_target(self.ZERO_POINT))
        self.window.jog_point_list.itemClicked.connect(self._go_to_point_selected_event)
        self.window.go_group.buttonPressed.connect(self._start_go_to)
        self.window.go_group.buttonReleased.connect(self._stop_go_to)
        self.window.btn_joints_action_teach.clicked.connect(self._teach_joint_position)
        self.window.data_joints_list.itemDoubleClicked.connect(self._save_joint_target_info)
        self.window.btn_joints_action_delete.clicked.connect(self._delete_selected_joint_target)
        self.window.btn_j_edit_ok.clicked.connect(self._edit_joint_data_event)
        self.window.btn_data_joint_ok.clicked.connect(self._edit_joint_data_event)
        self.window.btn_j_edit_ok.clicked.connect(lambda: self._read_available_points())
        self.window.btn_data_joint_ok.clicked.connect(lambda: self._read_available_points())
        self.linear_send_timer.timeout.connect(self._linear_jog_event)
        self.reorient_send_timer.timeout.connect(self._reorient_jog_event)
        self.window.jog_linear_controls_group.buttonPressed.connect(self._start_linear_jog_timer)
        self.window.jog_linear_controls_group.buttonReleased.connect(self._stop_linear_jog_timer)
        self.window.jog_reorient_controls_group.buttonPressed.connect(self._start_reorient_jog_timer)
        self.window.jog_reorient_controls_group.buttonReleased.connect(self._stop_reorient_jog_timer)
        self.window.linear_group.buttonClicked.connect(self._save_linear_axis)
        self.window.reorient_axes_group.buttonClicked.connect(self._save_reorient_axis)
        self.window.linear_discrete_group.buttonPressed.connect(self._define_linear_discrete_level)
        self.window.reorient_discrete_group.buttonPressed.connect(self._define_reorient_discrete_level)
        self.window.btn_jog_axes.clicked.connect(self._set_jog_acceleration)
        self.window.frame_group.buttonClicked.connect(self._define_jog_frame)
        self.window.reorient_frame_group.buttonClicked.connect(self._define_reorient_frame)
        self.window.trajectory_btn_check.clicked.connect(lambda: self._check_trajectory
        (self.window.trajectory_edit.toPlainText()))
        # TODO: add current text changed event in trajectory editor for blocking run button
        self.actual_position_update_timer.timeout.connect(self._read_current_position)
        self.actual_position_update_timer.timeout.connect(self._read_current_mdb_rtu_data)
        self.actual_position_update_timer.timeout.connect(self._read_current_plc_data)
        self.window.trajectory_btn_run.clicked.connect(self._begin_trajectory)
        self.window.btn_jog_gripper_open.clicked.connect(self._man_begin_trajectory)
        self.window.btn_jog_gripper_close.clicked.connect(self._man_begin_trajectory)
        self.window.trajectory_edit.textChanged.connect(lambda: self.block_run_trajectory.emit())
        self.window.btn_record.clicked.connect(self.start_scope)
        self.scope_timer.timeout.connect(self._record_scope_data)
        self.window.lst_plot_files.itemDoubleClicked.connect(self._get_plot_file)


    def json_data(self, json_key):
        path = self.config.get_value(json_key)
        if path is not None:
            data = read_json(path)
            return (data)
        else:
            print(f'Path {json_key} not found!')

    def _get_plot_file(self, item):
        path = os.path.join(self.config.get_value('plots_directory'), item.text())
        raw_data = read_csv(path)
        packed_data = pack_data(raw_data)
        self.plot_data.emit(packed_data)

    def start_scope(self, btn):
        sender = self.sender()
        if sender.isChecked():
            self._stop_record_flag = False
            self._scope_signals = list(_get_selected_scope_signals(self.window.lst_selected_signals))
            self.scope_timer.start(self.config.get_value('scope_sampling_time_ms'))
            self.recorder = Recorder(self.config.get_value('plots_directory'), self._scope_signals)
        else:
            self._stop_record_flag = True
            self._scope_signals.clear()
            self.recorder.save_data()

    def up_stop_mode_flag(self):
        self._stop_mode_flag = True
        self.window.trajectory_btn_run.setChecked(False)
        self.trajectory_stop.emit('all:stop')

    def _record_scope_data(self):
        flag = False

        data = self.recorder.read_scope_signals(self.db)

        if data is not None:
            for key, value in data.items():
                if key in self._scope_signals:
                    flag = True
                    self.recorder.record_data(key, value)

            if flag:
                self.recorder.add_timestamp()
        self._check_record_stop_flag()

    def _check_record_stop_flag(self):
        if self._stop_record_flag:
            self.scope_timer.stop()

    def _set_jog_acceleration(self, btn):
        self.linear_jog.emit('all:stop')
        self.jog_acceleration.emit('all:set_acceleration')

    def _send_stop_before_manual_mode(self):
        self.linear_jog.emit('all:stop')

    def _linear_jog_event(self):
        if self._linear_axis and self._linear_direction:  # (X, Y or Z) and ('+' or '-')
            cmd_1 = 'all:linear_jog:' + \
                    self._linear_axis + ':' + \
                    self._linear_direction + self._linear_discrete_distance + \
                    ':' + str(self._speed_value_percent) + ':' + self._linear_working_frame
            cmd_2 = 'all:position_mode'

            for cmd in (cmd_1, cmd_2):
                self.linear_jog.emit(cmd)

    def _start_linear_jog_timer(self, btn):
        self._linear_direction = btn.text()
        self.linear_send_timer.start(int(self._linear_send_time))

    def _stop_linear_jog_timer(self, btn):
        # send stop cmd for all
        self.linear_send_timer.stop()
        self.linear_jog.emit('all:hold')

    def _reorient_jog_event(self):
        if self._reorient_axis and self._reorient_direction:  # (X, Y or Z) and ('+' or '-')
            cmd_1 = 'all:reorient_jog:' + \
                    self._reorient_axis + ':' + \
                    self._reorient_direction + self._reorient_discrete_distance + \
                    ':' + str(self._speed_value_percent) + ':' + self._reorient_working_frame
            cmd_2 = 'all:position_mode'

            for cmd in (cmd_1, cmd_2):
                self.reorient_jog.emit(cmd)

    def _start_reorient_jog_timer(self, btn):
        self._reorient_direction = btn.text()
        self.reorient_send_timer.start(int(self._reorient_send_time))

    def _stop_reorient_jog_timer(self, btn):
        # send stop cmd for all
        self.reorient_send_timer.stop()
        self.reorient_jog.emit('all:hold')

    def _save_linear_axis(self, btn):
        self._linear_axis = btn.text()

    def _define_linear_discrete_level(self, btn):
        self._linear_discrete_distance = btn.accessibleDescription()
        discrete_level = btn.accessibleName()
        self._linear_send_time = self._discrete_levels.get(discrete_level, 0.0000000001)

    def _define_jog_frame(self, btn):
        self._linear_working_frame = btn.accessibleDescription()

    def _save_reorient_axis(self, btn):
        self._reorient_axis = btn.text()

    def _define_reorient_discrete_level(self, btn):
        self._reorient_discrete_distance = btn.accessibleDescription()
        discrete_level = btn.accessibleName()
        self._reorient_send_time = self._discrete_levels.get(discrete_level, 0.0000000001)

    def _define_reorient_frame(self, btn):
        self._reorient_working_frame = btn.accessibleDescription()

    def _read_available_points(self):
        # TODO: add reading og the cartesian points
        self._available_joint_points = self.db.read_j_points()

    def _start_timers(self):
        self.actual_position_update_timer.start(1)

    def _remove_enable(self):
        self.db.add_to_plc_tasks('out_enable_work', False)
        self.db.add_to_plc_tasks('out_ready', False)

    def _enable_axes(self):
        sender = self.sender()
        self.db.add_to_plc_tasks(sender.accessibleDescription(), sender.isChecked())
        self.db.add_to_plc_tasks(sender.accessibleName(), sender.isChecked())
        if sender.isChecked():
            self.linear_jog.emit('all:enable')
        if not sender.isChecked():
            self.linear_jog.emit('all:stop')

    def _handle_fault_event(self):
        sender = self.sender()
        if sender.isCheckable() and sender.isChecked():
            self.fault_action.emit(sender.accessibleName() + ':' + sender.accessibleDescription())
        elif not sender.isCheckable():
            self.fault_action.emit(sender.accessibleName() + ':' + sender.accessibleDescription())

    def _calibrate_or_define_event(self):
        sender = self.sender()
        if 'calibrate' in sender.accessibleDescription():
            self.calibrate_or_define.emit(sender.accessibleName() + ':' + sender.accessibleDescription())

        if 'axis_zero' in sender.accessibleDescription():
            self.calibrate_or_define.emit(sender.accessibleName() + ':' + sender.accessibleDescription())

        if 'define' in sender.accessibleDescription(): # Переделал эту неиспользуемую вкладку для ручного теста калибровки осей
            # углами, расчитанными на основе RAW значенией резольверов. Так как пока не понятно как реализовать эту функцию при
            # инициализации робота (plc процессы запускаются уже после ethercat инициализации).

            data_plc = self.db.read_plc_io_monitor()
            data_axes = self.db.read_fc_axes_monitor()

            # Сделать файлы Axe_1_zaytsev.py, Axe_2.py, Axe_3.py, Axe_4.py с расчетными форумалами методом пропорции
            # для этого составить соотношение raw значения резольвера и считанного по ethercat угла.
            # Составить условия по аналогии с 5, 6 осью, как ниже.

            if sender.accessibleName() == '1':
                # for 1-axis: a - внешний резольвер, b - мотор
                a = data_plc["raw_position_1_ext"]
                b = data_axes["raw_position_resolver_motor"]["axis_1_raw_position_resolver_motor"]

                angle = ang_calc_1_axis(a, b)
                print(a, b, angle)

            if sender.accessibleName() == '2':
                angle = 0

            if sender.accessibleName() == '3':
                angle = 0

            if sender.accessibleName() == '4':
                angle = 0

            if sender.accessibleName() == '5':
                # for 5-axis: a - левый резольвер, b - мотор, с - правый резольвер
                a = data_plc["raw_position_6_ext"]
                b = data_axes["raw_position_resolver_motor"]["axis_5_raw_position_resolver_motor"]
                c = data_plc["raw_position_5_ext"]

                angle = ang_calc_5_axis(a, b, c)
                print(a, b, c, angle)

            if sender.accessibleName() == '6':
                # for 6-axis: # a - левый, b - мотор, с - правый
                a = data_plc["raw_position_7_ext"]
                b = data_axes["raw_position_resolver_motor"]["axis_6_raw_position_resolver_motor"]
                c = data_plc["raw_position_8_ext"]

                angle = ang_calc_6_axis(a, b, c)
                print(a, b, c, angle)

            self.calibrate_or_define.emit(sender.accessibleName() + ':' + sender.accessibleDescription() + ':' + str(angle))

    def _save_joint_number(self, btn):
        # save joint number in independent axis moving mode
        self._joint_number = int(btn.text())
        self.db.add_to_rtc_control('rtc_joint_number', self._joint_number)

    def rtc_save_joint_number(self, number):
        if number > 6: number = 6
        if number < 1: number = 1
        self._joint_number = number

    def reset_rtc_speed_value(self):
        self.db.add_to_rtc_control('rtc_speed_value', self._speed_value_percent)

    def _save_speed(self, value):
        # save speed value in jog mode in %
        self._speed_value_percent = value
        self.db.add_to_rtc_control('rtc_speed_value', self._speed_value_percent)

    def rtc_save_speed(self, value):
        if value > 100: value = 100
        if value < 0: value = 0
        self._speed_value_percent = value

    def _start_jog_joint_movement(self, btn):
        axis_number = str(self._joint_number)
        print('axis_number: ', axis_number)
        cmd = btn.accessibleName().split('|')[0]
        speed_percent = btn.accessibleDescription() + str(self._speed_value_percent)
        message = axis_number + ':' + cmd + ':' + speed_percent
        self.start_joint_jog.emit(message)

    def rtc_start_jog_joint_movement(self, sign):
        axis_number = str(self._joint_number)
        cmd = 'speed_mode'
        speed_percent = sign + str(self._speed_value_percent)
        message = axis_number + ':' + cmd + ':' + speed_percent
        self.start_joint_jog.emit(message)

    def rtc_stop_jog_joint_movement(self):
        axis_number = str(self._joint_number)
        cmd = 'stop'
        message = axis_number + ':' + cmd
        self.stop_joint_jog.emit(message)

    def _stop_jog_joint_movement(self, btn):
        axis_number = str(self._joint_number)
        cmd = btn.accessibleName().split('|')[1]
        message = axis_number + ':' + cmd
        self.start_joint_jog.emit(message)

    def _add_joint_target(self, position, name='j_point_'):
        data = self.db.read_j_points()

        if data is not None:
            point_key = generate_point_name(data, name, len(data), self._point_name_space)
            self.db.add_to_j_points(point_key, position)
            self._available_joint_points = self.db.read_j_points()
        else:
            print('Could not add target point. Check system file "joint_points.json".')

    def _teach_joint_position(self):
        data = self.db.read_fc_axes_monitor()
        if data is not None:
            position_data = find_actual_position(data)
            point_position = prepare_point_data(position_data)
            if point_position is not None:
                self._add_joint_target(point_position)
            else:
                print('error during teaching target')

    def _go_to_point_selected_event(self, item):
        key = item.text()
        values = self._available_joint_points.get(key, None)
        if values is not None:
            message = 'all:go_to:' + str(values) + ':' + str(self._speed_value_percent)
            self.go_to.emit(message)

    def _start_go_to(self, btn):
        self.start_go_to.emit(btn.accessibleName())

    def _stop_go_to(self, btn):
        self.stop_go_to.emit(btn.accessibleDescription())

    def _save_joint_target_info(self, item):
        self._joint_target_info = item.text()

    def _clear_joint_info(self):
        self._joint_target_info = None

    def _delete_selected_joint_target(self):
        if self._joint_target_info:
            target_name = self._joint_target_info.split(':')[0]
            self.db.delete_from_j_points(target_name)
            self._joint_target_info = None
        else:
            print('Point list is empty or target not selected.')

    def _edit_joint_data_event(self):
        lst = []
        rows = self.window.data_joint_points.rowCount()
        for i in range(0, rows):
            parameter = self.window.data_joint_points.item(i, 1).text()
            lst.append(parameter)
        name, point_data = create_edited_point(lst)
        self._delete_selected_joint_target()
        self.db.add_to_j_points(name, point_data)
        self.window.data_joint_points.setRowCount(0)

    def update_sub_process_num(self):
        data_rtc_control = self.db.read_rtc_control()
        data_plc_monitor = self.db.read_plc_io_monitor()

        if data_plc_monitor['in_manual_mode']:
            self.subprocess_num = 0
        else:
            self.subprocess_num = data_rtc_control["subprocess_num"]

    def _remote_begin_trajectory(self, data):
        self._check_trajectory(data)
        # sleep(1)
        if self._trajectory:
            self._begin_trajectory()

    def _check_trajectory(self, data):
        # Выбор программы траектории с помощью записи int переменной протоколом ModbusTCP
        # По умолчанию программа инициализирует self.subprocess_num = 0 , соответственно ничего не происходит.
        self.db.add_to_rtc_control('rtc_cmd_status', 0)
        sleep(0.2)
        self.update_sub_process_num()
        print('self.update_sub_process_num(): ', self.update_sub_process_num())
        s = None
        if self.subprocess_num != 0:
            try:
                sub_file_name = str(self.subprocess_num) + '.txt'
                print('!!!!!!!!!!!!!!!!!!!!!!!!sub_file_name: ', sub_file_name)
                sub_path = self.config.get_value('save_trajectory_path')
                sub_data = read_from_txt_file(sub_path, sub_file_name)
                data = sub_data
            except:
                self.db.add_to_rtc_control('rtc_cmd_status', 102)
                s = 102
                print(f"There isn't such subprocess: {sub_file_name} in the path: {sub_path}.")

        print('data: ', data)

        raw_data = format_trajectory_text(data)
        formatted_data = separate_trajectory_text(raw_data)
        print('formatted_data', formatted_data)

        formatted_data =  add_def_data_to_trajectory(self.config, formatted_data)
        print('full_formatted_data', formatted_data)

        plc_data = self.db.read_plc_tasks()
        plc_io_data = self.db.read_plc_io_monitor()
        rtu_io_data = self.db.read_mdbrtu_io_monitor()
        tests_result = test_point_syntax(self._available_joint_points, formatted_data, plc_data, plc_io_data, rtu_io_data)
        print('tests_result', tests_result)
        if all(tests_result):
            self.unlock_run_trajectory.emit()
            self._trajectory = add_coordinates_for_trajectory(self._available_joint_points, formatted_data)
            print('self._trajectory: ', self._trajectory)
            self.db.add_to_rtc_control('rtc_cmd_status', 100)
        else:
            # TODO: add signal for blocking run button
            self._trajectory = None
            if s == 102:
                self.db.add_to_rtc_control('rtc_cmd_status', 102)
            else:
                self.db.add_to_rtc_control('rtc_cmd_status', 101)
            print('Errors in syntax!')

    def _read_current_position(self):
        data = self.db.read_fc_axes_monitor()
        if data is not None:
            angles = data.get('actual_position', None)
            self._actual_position = list(map(float, angles.values()))

    def _read_current_mdb_rtu_data(self):
        self._actual_mdb_rtu_data = self.db_thread_2.read_mdbrtu_io_monitor()

        actual_connections = []
        for key, val in self._actual_mdb_rtu_data.items():
            if key[2:] == 'connection_flag':
                actual_connections.append(val)
        self._mdb_rtu_connection_flag = all(actual_connections)

    def _read_current_plc_data(self):
        self._actual_plc_data = self.db_thread_3.read_plc_io_monitor()

    def _mdb_rtu_all_stop(self):
        self.db_thread.add_to_mdbrtu_tasks('1_out_starting_type', 0)
        # self.db_thread.add_to_mdbrtu_tasks('1_out_motor_current_set_value', 5)
        self.db_thread.add_to_mdbrtu_tasks('1_out_motor_speed_set_value', 0)

    def _begin_trajectory(self):
        print('')
        print('=== def _begin_trajectory ===============================================')
        print('if self.window.trajectory_btn_run.isChecked(): ', self.window.trajectory_btn_run.isChecked())
        if self.window.trajectory_btn_run.isChecked():
            if not self._trajectory_thread.is_alive():
                self._trajectory_thread = threading.Thread(target=self._go_to_trajectory, args=(), daemon=True)
                self._trajectory_thread.start()
                self._stop_mode_flag = False
                print('Start new thread!')
        else:
            self._trajectory_thread.join()
            self.linear_jog.emit('all:stop')

    def _man_begin_trajectory(self):
        sender = self.sender()
        trajectory = self.tool_managment_commands[sender.accessibleDescription()]
        print('')
        print('=== def _man_begin_trajectory ===============================================')
        if sender.isChecked():
            if not self._trajectory_thread.is_alive():
                self._trajectory_thread = threading.Thread(target=self._manual_go_to_trajectory, args=(sender, trajectory), daemon=True)
                self._trajectory_thread.start()
                print('Start new tool managment thread!')
        else:
            self._trajectory_thread.join()

    def _go_to_trajectory(self):
        print('')
        print('===def _go_to_trajectory=================================================')
        while self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
            print('self._trajectory:', self._trajectory)
            for target in self._trajectory:
                # TODO: make global variable with commands ['cmdWait', ..., ..., ...]
                if target[0] not in ('cmdWait', 'cmdStop', 'cmdSetDO', 'cmdSetReg', 'cmdWhileDiff','cmdWhileGripper', 'cmdIf', 'cmdStatus', 'cmdPrint', 'cmdRec', 'cmdBrake'):
                    if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
                        self.go_to.emit(f'all:go_to:{target[0]}:{target[1]}')  # place for emit signal for go_to command
                        self.start_go_to.emit('all:position_mode')  # place for emit signal for position mode command
                    else:
                        self.trajectory_stop.emit('all:stop')
                        break

                    self._axis_accuracy = self._default_axis_accuracy.copy()
                    if len(target) > 2:
                        self._axis_accuracy['1'] = target[2][0]
                        self._axis_accuracy['2'] = target[2][1]
                        self._axis_accuracy['3'] = target[2][2]
                        self._axis_accuracy['4'] = target[2][3]
                        self._axis_accuracy['5'] = target[2][4]
                        self._axis_accuracy['6'] = target[2][5]

                    # axis 1 position control
                    # TODO: one function for position control
                    while abs(target[0][0] - self._actual_position[0]) > self._axis_accuracy['1']:
                        if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                            self.trajectory_stop.emit('all:stop')
                            break
                        time.sleep(0.001)
                        pass

                    # axis 2 position control
                    while abs(target[0][1] - self._actual_position[1]) > self._axis_accuracy['2']:
                        if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                            self.trajectory_stop.emit('all:stop')
                            break
                        time.sleep(0.001)
                        pass

                    # axis 3 position control
                    while abs(target[0][2] - self._actual_position[2]) > self._axis_accuracy['3']:
                        if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                            self.trajectory_stop.emit('all:stop')
                            break
                        time.sleep(0.001)
                        pass

                    # axis 4 position control
                    while abs(target[0][3] - self._actual_position[3]) > self._axis_accuracy['4']:
                        if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                            self.trajectory_stop.emit('all:stop')
                            break
                        time.sleep(0.001)
                        pass

                    # axis 5 position control
                    while abs(target[0][4] - self._actual_position[4]) > self._axis_accuracy['5']:
                        if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                            self.trajectory_stop.emit('all:stop')
                            break
                        time.sleep(0.001)
                        pass

                    # axis 6 position control
                    while abs(target[0][5] - self._actual_position[5]) > self._axis_accuracy['6']:
                        if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                            self.trajectory_stop.emit('all:stop')
                            break
                        time.sleep(0.001)
                        pass
                else:

                    if target[0] == 'cmdWait':
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
                            time.sleep(float(target[1]))
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdStop':
                        self.window.trajectory_btn_run.setChecked(False)
                        self.trajectory_stop.emit('all:stop')
                        break

                    if target[0] == 'cmdSetDO':
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
                            self.db_thread.add_to_plc_tasks(target[1], target[2])
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdSetReg':
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
                            self.db_thread.add_to_mdbrtu_tasks(target[1], target[2])
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdStatus':
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
                            try:
                                print(f'tryCmdStatus:', target[1])
                                self.db_thread.add_to_rtc_control('rtc_cmd_status', target[1])
                            except:
                                print('passCmdStatus')
                                pass
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdPrint':
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
                            print(target[1])
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdRec':
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
                            print('REC!!!')
                            record_values(self)

                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdBrake':
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
                            self.trajectory_stop.emit('all:stop')
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdWhileDiff':
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):

                            while abs(self._actual_mdb_rtu_data[target[1]] - self._actual_mdb_rtu_data[target[2]]) > target[3]:
                                if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                                    self.trajectory_stop.emit('all:stop')
                                    self.db_thread.add_to_mdbrtu_tasks('1_out_starting_type', 7)
                                    self.db_thread.add_to_mdbrtu_tasks('1_out_motor_current_set_value', 7)
                                    self.db_thread.add_to_mdbrtu_tasks('1_out_motor_speed_set_value', 7)
                                    break
                                time.sleep(0.001)
                                pass
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    # first variant
                    # if target[0] == 'cmdWhileGripper':
                    #     sleep(3)
                    #     if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag) and (not self._actual_plc_data[target[4]]):
                    #         diff = abs(self._actual_mdb_rtu_data[target[1]] - self._actual_mdb_rtu_data[target[2]])
                    #         sensor = bool(self._actual_plc_data[target[4]])
                    #         while diff > target[3] and not sensor:
                    #             if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                    #                 self.trajectory_stop.emit('all:stop')
                    #                 self._mdb_rtu_all_stop()
                    #                 break
                    #             time.sleep(0.001)
                    #             diff = abs(self._actual_mdb_rtu_data[target[1]] - self._actual_mdb_rtu_data[target[2]])
                    #             print('actual:', self._actual_mdb_rtu_data[target[1]])
                    #             print('set:',self._actual_mdb_rtu_data[target[2]])
                    #             sensor = bool(self._actual_plc_data[target[4]])
                    #             # pass
                    #         else:
                    #             if not (diff > target[3]):
                    #                 print(f'Остановка захвата по сигналу тока: {target[1]}!')
                    #                 self.trajectory_stop.emit('all:stop')
                    #                 self._mdb_rtu_all_stop()
                    #                 self.window.trajectory_btn_run.setChecked(False)
                    #             elif sensor:
                    #                 print(f'Остановка захвата по сигналу концевика: {target[4]}!')
                    #             else:
                    #                 pass
                    #     else:
                    #         self.trajectory_stop.emit('all:stop')
                    #         self._mdb_rtu_all_stop()
                    #         self.window.trajectory_btn_run.setChecked(False)

                    if target[0] == 'cmdIf':
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag):
                            plc_value = int(self._actual_plc_data[target[1]])
                            if plc_value == int(target[2]):
                                pass
                            else:
                                self.trajectory_stop.emit('all:stop')
                                self._mdb_rtu_all_stop()
                                self.window.trajectory_btn_run.setChecked(False)
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    # # qtimer
                    # if target[0] == 'cmdWhileGripper':
                    #     if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag) and (not self._actual_plc_data[target[4]]):
                    #         # diff = abs(self._actual_mdb_rtu_data[target[1]]) - abs(self._actual_mdb_rtu_data[target[2]])
                    #         sensor = bool(self._actual_plc_data[target[4]])
                    #         while self.gripper_timer.remainingTime()!=0 and not sensor:
                    #             if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                    #                 self.trajectory_stop.emit('all:stop')
                    #                 self._mdb_rtu_all_stop()
                    #                 break
                    #             time.sleep(0.001)
                    #             diff = abs(self._actual_mdb_rtu_data[target[1]]) - abs(self._actual_mdb_rtu_data[target[2]])
                    #             print('actual:', self._actual_mdb_rtu_data[target[1]])
                    #             print('set:',self._actual_mdb_rtu_data[target[2]])
                    #             sensor = bool(self._actual_plc_data[target[4]])
                    #             if not (diff > 0):
                    #                 if self.gripper_timer.isActive():
                    #                     continue
                    #                 else:
                    #                     self.gripper_timer.start(target[3])
                    #             else:
                    #                 self.gripper_timer.stop()
                    #             # pass
                    #         else:
                    #             if self.gripper_timer.remainingTime()==0:
                    #                 print(f'Остановка захвата по сигналу тока: {target[1]}!')
                    #                 self.trajectory_stop.emit('all:stop')
                    #                 self._mdb_rtu_all_stop()
                    #                 self.window.trajectory_btn_run.setChecked(False)
                    #             elif sensor:
                    #                 print(f'Остановка захвата по сигналу концевика: {target[4]}!')
                    #             else:
                    #                 pass
                    #     else:
                    #         self.trajectory_stop.emit('all:stop')
                    #         self._mdb_rtu_all_stop()
                    #         self.window.trajectory_btn_run.setChecked(False)


                    # by counter
                    if target[0] == 'cmdWhileGripper': # by counter
                        if self.window.trajectory_btn_run.isChecked() and (not self._stop_mode_flag) and (not self._actual_plc_data[target[4]]):
                            # diff = abs(self._actual_mdb_rtu_data[target[1]]) - abs(self._actual_mdb_rtu_data[target[2]])
                            sensor = bool(self._actual_plc_data[target[4]])
                            n = 0
                            k = 0
                            while n < target[3] and k < target[5] and not sensor:
                                # t1 = datetime.now()
                                if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                                    self.trajectory_stop.emit('all:stop')
                                    self._mdb_rtu_all_stop()
                                    break
                                time.sleep(0.001)
                                diff = abs(self._actual_mdb_rtu_data[target[1]]) - (abs(self._actual_mdb_rtu_data[target[2]]-1))
                                print('actual:', self._actual_mdb_rtu_data[target[1]])
                                print('set:',self._actual_mdb_rtu_data[target[2]], datetime.now())
                                sensor = bool(self._actual_plc_data[target[4]])
                                if diff >= 0:
                                    n = n + 1
                                    if n < 0: n = 0
                                else:
                                    if n > 0: n = n - 1
                                print('n=', n)
                                k = k + 1
                                print('k=', k)
                                # pass
                                # t2 = datetime.now()
                                # print('cmdWhileGripper', t2-t1)
                            else:
                                if not(n < target[3]):
                                    print(f'Остановка захвата по сигналу тока: {target[1]}!')
                                    self.trajectory_stop.emit('all:stop')
                                    self._mdb_rtu_all_stop()
                                    self.window.trajectory_btn_run.setChecked(False)
                                elif sensor:
                                    print(f'Остановка захвата по сигналу концевика: {target[4]}!')
                                else:
                                    pass
                        else:
                            self.trajectory_stop.emit('all:stop')
                            self._mdb_rtu_all_stop()
                            self.window.trajectory_btn_run.setChecked(False)

    def _manual_go_to_trajectory(self, sender, trajectory):
        print('')
        print('===def _man_go_to_trajectory=================================================')
        while sender.isChecked():
            print('trajectory:', trajectory)
            for target in trajectory:
                # TODO: make global variable with commands ['cmdWait', ..., ..., ...]
                if target[0] not in ('cmdWait', 'cmdStop', 'cmdSetDO', 'cmdSetReg', 'cmdWhileDiff','cmdWhileGripper', 'cmdIf', 'cmdStatus', 'cmdPrint', 'cmdRec', 'cmdBrake'):
                    pass
                    # if (not self._stop_mode_flag):
                    #     self.go_to.emit(f'all:go_to:{target[0]}:{target[1]}')  # place for emit signal for go_to command
                    #     self.start_go_to.emit('all:position_mode')  # place for emit signal for position mode command
                    # else:
                    #     self.trajectory_stop.emit('all:stop')
                    #     break
                    #
                    # self._axis_accuracy = self._default_axis_accuracy.copy()
                    # if len(target) > 2:
                    #     self._axis_accuracy['1'] = target[2][0]
                    #     self._axis_accuracy['2'] = target[2][1]
                    #     self._axis_accuracy['3'] = target[2][2]
                    #     self._axis_accuracy['4'] = target[2][3]
                    #     self._axis_accuracy['5'] = target[2][4]
                    #     self._axis_accuracy['6'] = target[2][5]
                    #
                    # # axis 1 position control
                    # # TODO: one function for position control
                    # while abs(target[0][0] - self._actual_position[0]) > self._axis_accuracy['1']:
                    #     if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                    #         self.trajectory_stop.emit('all:stop')
                    #         break
                    #     time.sleep(0.001)
                    #     pass
                    #
                    # # axis 2 position control
                    # while abs(target[0][1] - self._actual_position[1]) > self._axis_accuracy['2']:
                    #     if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                    #         self.trajectory_stop.emit('all:stop')
                    #         break
                    #     time.sleep(0.001)
                    #     pass
                    #
                    # # axis 3 position control
                    # while abs(target[0][2] - self._actual_position[2]) > self._axis_accuracy['3']:
                    #     if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                    #         self.trajectory_stop.emit('all:stop')
                    #         break
                    #     time.sleep(0.001)
                    #     pass
                    #
                    # # axis 4 position control
                    # while abs(target[0][3] - self._actual_position[3]) > self._axis_accuracy['4']:
                    #     if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                    #         self.trajectory_stop.emit('all:stop')
                    #         break
                    #     time.sleep(0.001)
                    #     pass
                    #
                    # # axis 5 position control
                    # while abs(target[0][4] - self._actual_position[4]) > self._axis_accuracy['5']:
                    #     if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                    #         self.trajectory_stop.emit('all:stop')
                    #         break
                    #     time.sleep(0.001)
                    #     pass
                    #
                    # # axis 6 position control
                    # while abs(target[0][5] - self._actual_position[5]) > self._axis_accuracy['6']:
                    #     if not self.window.trajectory_btn_run.isChecked() or self._stop_mode_flag:
                    #         self.trajectory_stop.emit('all:stop')
                    #         break
                    #     time.sleep(0.001)
                    #     pass
                else:
                    if target[0] == 'cmdWait':
                        time.sleep(float(target[1]))

                    if target[0] == 'cmdStop':
                        sender.setChecked(False)
                        self.trajectory_stop.emit('all:stop')
                        break

                    if target[0] == 'cmdSetDO':
                        if sender.isChecked():
                            self.db_thread.add_to_plc_tasks(target[1], target[2])
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdSetReg':
                        if sender.isChecked():
                            self.db_thread.add_to_mdbrtu_tasks(target[1], target[2])
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdStatus':
                        if sender.isChecked():
                            try:
                                print(f'tryCmdStatus:', target[1])
                                self.db_thread.add_to_rtc_control('rtc_cmd_status', target[1])
                            except:
                                print('passCmdStatus')
                                pass
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdPrint':
                        if sender.isChecked():
                            print(target[1])
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdRec':
                        if sender.isChecked():
                            print('REC!!!')
                            record_values(self)

                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdBrake':
                        if sender.isChecked():
                            self.trajectory_stop.emit('all:stop')
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdWhileDiff':
                        if sender.isChecked():

                            while abs(self._actual_mdb_rtu_data[target[1]] - self._actual_mdb_rtu_data[target[2]]) > target[3]:
                                if not sender.isChecked():
                                    self.trajectory_stop.emit('all:stop')
                                    self.db_thread.add_to_mdbrtu_tasks('1_out_starting_type', 7)
                                    self.db_thread.add_to_mdbrtu_tasks('1_out_motor_current_set_value', 7)
                                    self.db_thread.add_to_mdbrtu_tasks('1_out_motor_speed_set_value', 7)
                                    break
                                time.sleep(0.001)
                                pass
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    if target[0] == 'cmdIf':
                        if sender.isChecked():
                            plc_value = int(self._actual_plc_data[target[1]])
                            if plc_value == int(target[2]):
                                pass
                            else:
                                self.trajectory_stop.emit('all:stop')
                                self._mdb_rtu_all_stop()
                                sender.setChecked(False)
                        else:
                            self.trajectory_stop.emit('all:stop')
                            break

                    # by counter
                    if target[0] == 'cmdWhileGripper': # by counter
                        if sender.isChecked() and (not self._actual_plc_data[target[4]]):
                            sensor = bool(self._actual_plc_data[target[4]])
                            n = 0
                            k = 0
                            while n < target[3] and k < target[5] and not sensor:
                                # t1 = datetime.now()
                                if not sender.isChecked():
                                    self.trajectory_stop.emit('all:stop')
                                    self._mdb_rtu_all_stop()
                                    break
                                time.sleep(0.001)
                                diff = abs(self._actual_mdb_rtu_data[target[1]]) - (abs(self._actual_mdb_rtu_data[target[2]]-1))
                                print('actual:', self._actual_mdb_rtu_data[target[1]])
                                print('set:',self._actual_mdb_rtu_data[target[2]], datetime.now())
                                sensor = bool(self._actual_plc_data[target[4]])
                                if diff >= 0:
                                    n = n + 1
                                    if n < 0: n = 0
                                else:
                                    if n > 0: n = n - 1
                                print('n=', n)
                                k = k + 1
                                print('k=', k)
                            else:
                                if not(n < target[3]):
                                    print(f'Остановка захвата по сигналу тока: {target[1]}!')
                                    self.trajectory_stop.emit('all:stop')
                                    self._mdb_rtu_all_stop()
                                    sender.setChecked(False)
                                elif sensor:
                                    print(f'Остановка захвата по сигналу концевика: {target[4]}!')
                                else:
                                    pass
                        else:
                            self.trajectory_stop.emit('all:stop')
                            self._mdb_rtu_all_stop()
                            sender.setChecked(False)



