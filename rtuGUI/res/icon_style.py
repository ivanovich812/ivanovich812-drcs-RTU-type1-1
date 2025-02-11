from PyQt5.QtCore import QSize, QObject
from PyQt5.QtGui import QIcon, QPixmap

from res import resources


class IconStyle:
    def __init__(self, window, trjsavewindow, trjuploadwindow):
        self.window = window
        self.trjsavewindow = trjsavewindow
        self.trjuploadwindow = trjuploadwindow

        self.apply_icons()

    def invert_icons(self, theme):
        if theme == "Светлая": theme = "Light"
        if theme == "Темная": theme = "Dark"
        if theme == "Dark": self.apply_icons()
        elif theme == "Light": self.apply_icons_inv()

    def apply_icons(self):
        self.window.setWindowIcon(QIcon(':/res/logo_header_64.png'))
        pixmap_logo = QPixmap(':/res/logo_header_64.png')
        self.window.lbl_logo.setPixmap(pixmap_logo)

        pixmap_main_logo = QPixmap(':/res/logo_main_last.png')
        self.window.lbl_main_logo.setPixmap(pixmap_main_logo)

        # pixmap_size_grip = QPixmap(':/res/resize.png')
        # self.window.lbl_size_grip.setPixmap(pixmap_size_grip)

        pixmap_caibration = QPixmap(':/res/ruler_22.png')
        self.window.lbl_calibration_cur_page_icon.setPixmap(pixmap_caibration)

        pixmap_jog = QPixmap(':/res/joystick_22.png')
        self.window.lbl_jog_cur_page_icon.setPixmap(pixmap_jog)

        pixmap_data = QPixmap(':/res/data_22.png')
        self.window.lbl_data_cur_page_icon.setPixmap(pixmap_data)

        pixmap_trajectory = QPixmap(':/res/trajectory_22.png')
        self.window.lbl_trajectory_cur_page_icon.setPixmap(pixmap_trajectory)

        pixmap_signals = QPixmap(':/res/signals_22.png')
        self.window.lbl_signals_cur_page_icon.setPixmap(pixmap_signals)

        pixmap_settings = QPixmap(':/res/settings_22.png')
        self.window.lbl_settings_cur_page_icon.setPixmap(pixmap_settings)

        pixmap_log = QPixmap(':/res/log_22.png')
        self.window.lbl_log_cur_page_icon.setPixmap(pixmap_log)

        pixmap_scope = QPixmap(':/res/oscil_22.png')
        self.window.lbl_scope_cur_page_icon.setPixmap(pixmap_scope)

        pixmap_scope = QPixmap(':/res/authorization_22.png')
        self.window.lbl_authorization_cur_page_icon.setPixmap(pixmap_scope)

        # pixmap_authorization = QPixmap(':/res/authorization.png')
        # pixmap_authorization = pixmap_authorization.scaledToWidth(20)
        # self.window.lbl_authorization_cur_page_icon.setPixmap(pixmap_authorization)

        self.window.btn_close_window.setIcon(QIcon(':/res/close.png'))
        self.trjsavewindow.btn_close_window.setIcon(QIcon(':/res/close.png'))
        self.trjuploadwindow.btn_close_window.setIcon(QIcon(':/res/close.png'))
        self.window.btn_restore_window.setIcon(QIcon(':/res/restore.png'))
        self.window.btn_minimize_window.setIcon(QIcon(':/res/minimize.png'))

        self.window.btn_menu.setIcon(QIcon(':/res/menu.png'))
        self.window.btn_calibration.setIcon(QIcon(':/res/ruler.png'))
        self.window.btn_jog.setIcon(QIcon(':/res/joystick.png'))
        self.window.btn_data.setIcon(QIcon(':/res/data.png'))
        self.window.btn_trajectory.setIcon(QIcon(':/res/trajectory.png'))
        self.window.btn_signals.setIcon(QIcon(':/res/signals.png'))
        self.window.btn_settings.setIcon(QIcon(':/res/settings.png'))
        self.window.btn_log.setIcon(QIcon(':/res/log.png'))
        self.window.btn_scope.setIcon(QIcon(':/res/oscil.png'))
        self.window.btn_authorization.setIcon(QIcon(':/res/authorization.png'))
        self.window.btn_jog_axes.setIcon(QIcon(':/res/axis.png'))
        self.window.btn_jog_linear.setIcon(QIcon(':/res/linear.png'))
        self.window.btn_jog_reorient.setIcon(QIcon(':/res/reorient.png'))
        self.window.btn_jog_go_to.setIcon(QIcon(':/res/goto.png'))
        self.window.btn_joints_action_empty.setIcon(QIcon(':/res/zero_target.png'))
        self.window.btn_joints_action_teach.setIcon(QIcon(':/res/teach_target.png'))
        self.window.btn_joints_action_change.setIcon(QIcon(':/res/edit_target.png'))
        self.window.btn_joints_action_delete.setIcon(QIcon(':/res/delete_target.png'))
        self.window.btn_joints_keyboard.setIcon(QIcon(':/res/keyboard.png'))
        self.window.btn_virtual_keyboard.setIcon(QIcon(':/res/keyboard.png'))
        self.window.btn_go_to_axis_zero_1.setIcon(QIcon(':/res/axis.png'))
        self.window.btn_go_to_axis_zero_2.setIcon(QIcon(':/res/axis.png'))
        self.window.btn_go_to_axis_zero_3.setIcon(QIcon(':/res/axis.png'))
        self.window.btn_go_to_axis_zero_4.setIcon(QIcon(':/res/axis.png'))
        self.window.btn_go_to_axis_zero_5.setIcon(QIcon(':/res/axis.png'))
        self.window.btn_go_to_axis_zero_6.setIcon(QIcon(':/res/axis.png'))

        self.window.btn_no_discrete.setIcon(QIcon(':/res/discrete_none.png'))
        self.window.btn_medium_discrete.setIcon(QIcon(':/res/discrete_medium.png'))
        self.window.btn_large_discrete.setIcon(QIcon(':/res/discrete_small.png'))
        self.window.btn_no_discrete_reorient.setIcon(QIcon(':/res/discrete_none.png'))
        self.window.btn_medium_discrete_reorient.setIcon(QIcon(':/res/discrete_medium.png'))
        self.window.btn_large_discrete_reorient.setIcon(QIcon(':/res/discrete_small.png'))
        self.window.btn_lang_eng.setIcon(QIcon(':/res/united_kingdom.png'))
        self.window.btn_lang_rus.setIcon(QIcon(':/res/russia.png'))

    def apply_icons_inv(self):

        self.window.setWindowIcon(QIcon(':/res/logo_header_64_inv.png'))

        pixmap_logo = QPixmap(':/res/logo_header_64_inv.png')
        self.window.lbl_logo.setPixmap(pixmap_logo)

        pixmap_main_logo = QPixmap(':/res/logo_main_last_inv.png')
        self.window.lbl_main_logo.setPixmap(pixmap_main_logo)

        pixmap_caibration = QPixmap(':/res/ruler-inv_22.png')
        self.window.lbl_calibration_cur_page_icon.setPixmap(pixmap_caibration)

        pixmap_jog = QPixmap(':/res/joystick-inv_22.png')
        self.window.lbl_jog_cur_page_icon.setPixmap(pixmap_jog)

        pixmap_data = QPixmap(':/res/data-inv_22.png')
        self.window.lbl_data_cur_page_icon.setPixmap(pixmap_data)

        pixmap_trajectory = QPixmap(':/res/trajectory-inv_22.png')
        self.window.lbl_trajectory_cur_page_icon.setPixmap(pixmap_trajectory)

        pixmap_signals = QPixmap(':/res/signals-inv_22.png')
        self.window.lbl_signals_cur_page_icon.setPixmap(pixmap_signals)

        pixmap_settings = QPixmap(':/res/settings-inv_22.png')
        self.window.lbl_settings_cur_page_icon.setPixmap(pixmap_settings)

        pixmap_log = QPixmap(':/res/log-inv_22.png')
        self.window.lbl_log_cur_page_icon.setPixmap(pixmap_log)

        pixmap_scope = QPixmap(':/res/oscil-inv_22.png')
        self.window.lbl_scope_cur_page_icon.setPixmap(pixmap_scope)

        pixmap_scope = QPixmap(':/res/authorization-inv_22.png')
        self.window.lbl_authorization_cur_page_icon.setPixmap(pixmap_scope)

        self.window.btn_menu.setIcon(QIcon(':/res/menu-inv.png'))
        self.window.btn_close_window.setIcon(QIcon(':/res/close-inv.png'))
        self.trjsavewindow.btn_close_window.setIcon(QIcon(':/res/close-inv.png'))
        self.trjuploadwindow.btn_close_window.setIcon(QIcon(':/res/close-inv.png'))
        self.window.btn_restore_window.setIcon(QIcon(':/res/restore-inv.png'))
        self.window.btn_minimize_window.setIcon(QIcon(':/res/minimize-inv.png'))
        self.window.btn_calibration.setIcon(QIcon(':/res/ruler-inv.png'))
        self.window.btn_jog.setIcon(QIcon(':/res/joystick-inv.png'))
        self.window.btn_data.setIcon(QIcon(':/res/data-inv.png'))
        self.window.btn_trajectory.setIcon(QIcon(':/res/trajectory-inv.png'))
        self.window.btn_signals.setIcon(QIcon(':/res/signals-inv.png'))
        self.window.btn_settings.setIcon(QIcon(':/res/settings-inv.png'))
        self.window.btn_log.setIcon(QIcon(':/res/log-inv.png'))
        self.window.btn_scope.setIcon(QIcon(':/res/oscil-inv.png'))
        self.window.btn_authorization.setIcon(QIcon(':/res/authorization-inv.png'))
        self.window.btn_jog_axes.setIcon(QIcon(':/res/axis-inv.png'))
        self.window.btn_jog_go_to.setIcon(QIcon(':/res/goto-inv.png'))
        self.window.btn_jog_reorient.setIcon(QIcon(':/res/reorient-inv.png'))
        self.window.btn_jog_linear.setIcon(QIcon(':/res/linear-inv.png'))
        self.window.btn_no_discrete.setIcon(QIcon(':/res/discrete_none-inv.png'))
        self.window.btn_medium_discrete.setIcon(QIcon(':/res/discrete_medium-inv.png'))
        self.window.btn_large_discrete.setIcon(QIcon(':/res/discrete_small-inv.png'))
        self.window.btn_no_discrete_reorient.setIcon(QIcon(':/res/discrete_none-inv.png'))
        self.window.btn_medium_discrete_reorient.setIcon(QIcon(':/res/discrete_medium-inv.png'))
        self.window.btn_large_discrete_reorient.setIcon(QIcon(':/res/discrete_small-inv.png'))
        self.window.btn_joints_action_empty.setIcon(QIcon(':/res/zero_target-inv.png'))
        self.window.btn_joints_action_teach.setIcon(QIcon(':/res/teach_target-inv.png'))
        self.window.btn_joints_action_change.setIcon(QIcon(':/res/edit_target-inv.png'))
        self.window.btn_joints_action_delete.setIcon(QIcon(':/res/delete_target-inv.png'))
        self.window.btn_joints_keyboard.setIcon(QIcon(':/res/keyboard-inv_50.png'))
        self.window.btn_virtual_keyboard.setIcon(QIcon(':/res/keyboard-inv_50.png'))
        self.window.btn_go_to_axis_zero_1.setIcon(QIcon(':/res/axis-inv.png'))
        self.window.btn_go_to_axis_zero_2.setIcon(QIcon(':/res/axis-inv.png'))
        self.window.btn_go_to_axis_zero_3.setIcon(QIcon(':/res/axis-inv.png'))
        self.window.btn_go_to_axis_zero_4.setIcon(QIcon(':/res/axis-inv.png'))
        self.window.btn_go_to_axis_zero_5.setIcon(QIcon(':/res/axis-inv.png'))
        self.window.btn_go_to_axis_zero_6.setIcon(QIcon(':/res/axis-inv.png'))



