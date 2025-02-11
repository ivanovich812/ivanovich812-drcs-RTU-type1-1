from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPropertyAnimation, QTranslator, QEvent
from PyQt5.QtGui import QColor, QFont, QBrush, QTextCursor
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from forms import mainwindow, trj_save_window, trj_upload_window
from res import colors
import datetime
import os
from file_hadlers.txt_handler import write_to_txt_file, read_from_txt_file, delete_txt_file
from file_hadlers.json_handler import add_to_json
from file_hadlers.log_handler import read_from_log_file
from event_logger import logger
from font_delegate import FontDelegate


class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):

    def __init__(self, database):
        super().__init__()
        self.setupUi(self)
        self.trans = QTranslator(self)
        self.db = database

        self.window().setEnabled(True)
        self.click_position = None
        self.side_menu_animation = None
        self.joint_edit_keyboard_animation = None
        self.virtual_keyboard_animation = None
        self._tab_item_font = None
        self._axes_positions = {}
        self._jog_progress_axes = {}
        self.curves = {}
        self._joint_points = []
        self._scope_signals = []
        self._selected_signals = []
        self.items_in_little_log = 5
        self.items_in_big_log = 300
        self.item_counter = 0
        self._axes_limits_alarm_offset = 0
        self._tab_item_bool_color = {'False': '#ff4040', 'True': 'green'}
        self._cartesian_colors = {'tcp_x': '#ff4040',
                                  'tcp_y': '#40ff66',
                                  'tcp_z': '#4090ff',
                                  'tcp_eu_x': '#ff4040',
                                  'tcp_eu_y': '#40ff66',
                                  'tcp_eu_z': '#4090ff'}
        self.colors = {
            'DEBUG': 'black',
            'INFO': 'green',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'purple',
        }
        self._mode_bool_text = {'False': 'Auto', 'True': 'Manual'}
        self._current_theme = "Dark"
        self._start_language = "English"
        self.old_selected_row = None
        self.old_selected_widget = None
        self.settings_filter = {
            "gui_update_time": "int",
            "scope_sampling_time_ms": "int",
            "save_trajectory_path": "string",
            "stop_conditions_directory": "string",
            "driver_server_ip": "ip",
            "driver_server_port": "int",
            "axis_1_min": "int",
            "axis_1_max": "int",
            "axis_2_min": "int",
            "axis_2_max": "int",
            "axis_3_min": "int",
            "axis_3_max": "int",
            "axis_4_min": "int",
            "axis_4_max": "int",
            "axis_5_min": "int",
            "axis_5_max": "int",
            "axis_6_min": "int",
            "axis_6_max": "int",
            "axes_limits_alarm_offset": "int"
        }
        self.lst_not_styled_accessibleDescription = ("not styled",
                                                     "define_axis",
                                                     "reset_fault",
                                                     "emergency_stop",
                                                     "calibrate_axis",
                                                     "go_to_axis_zero",
                                                     "all:stop",
                                                     "+",
                                                     "-",
                                                     "BASE",
                                                     "TOOL",
                                                     "1",
                                                     "10",
                                                     "50")
        self.dict_theme_styles = {
            'Light': {
                'MainWindow': "background: white",
                'Menu': "background-color: #e0e0eb",
                'QLabel': "color: #191929",
                'QListWidget': "background: #e0e0eb; color: black",
                'QTextEdit': "background: #e0e0eb; color: black",
                'QLineEdit': "background: #e0e0eb; color: black",
                'QPlainTextEdit': "background: #e0e0eb; color: black",
                'QPushButton': "color: #191929",
                'QComboBox': "color: #191929; background-color: white; border: 1px solid black; border-color: #191929; padding-left: 10px;",
                'QTableWidget': """
                     
                    QTableWidget {
                        background-color: transparent;
                        padding: 10px;
                        border-radius: 5px;
                        gridline-color: grey;
                        color:  #191929;
                        selection-color: #191929 
                    }
                    QTableWidget::item {
                        background-color: #e0e0eb;
                        padding-left: 5px;
                        padding-right: 5px;
                        border-right: 1px solid grey; 
                        border-bottom: 1px solid grey;                   
                        border-left: 1px solid grey;                  
                    }           
                    QHeaderView::section{
                        background-color: rgb(33, 37, 43);
                        max-width: 30px;
                        border: 1px solid rgb(44, 49, 58);
                        border-style: none;
                        border-bottom: 1px solid rgb(44, 49, 60);
                        border-right: 1px solid rgb(44, 49, 60);
                        color: white;
                    }
                    QTableWidget::horizontalHeader {
                        background-color: rgb(33, 37, 43);
                    }
                    QHeaderView::section:horizontal {
                        border: 1px solid rgb(33, 37, 43);
                        background-color: rgb(33, 37, 43);
                        padding: 3px;
                        border-top-left-radius: 7px;
                        border-top-right-radius: 7px;
                    }
                    QHeaderView::section:vertical {
                        border: 1px solid rgb(44, 49, 60);
                    }
                    QScrollBar::vertical { background-color: #e0e0eb; }
                    
                    """,
                'QTabWidget': """
                    QTabWidget::pane {
                        border: none;
                        border-top: 1px solid rgb(0, 0, 0);
                        background: transparent;
                    }
                    QTabBar::tab-bar {
                        border: none;
                    }
                    QTabBar::tab {
                        border: none;
                        border-top-left-radius: 10px;
                        border-top-rigth-radius: 10px;
                        color: rgb(255, 255, 255);
                        background: #191929;
                        height: 30px;
                        min-width: 200px;
                        margin-rigth: 5px;
                        padding-left: 10px;
                        padding-rigth: 10px;
                        color: #191929;
                    }
                    QTabBar::tab:hover {
                        background: rgb(58, 58, 112);
                    }
                    QTabBar::tab:selected {
                        color: white;
                        background:  rgb(109, 109, 209);
                    }
                                    """,
                'QProgressBar': """
                    QProgressBar {
                        border: 2px solid #41416b;
                        border-radius: 12px;
                        background-color:#41416b;
                    }                   
                    QProgressBar::chunk  {
                        background-color: #40ff66;
                        border-radius :10px;
                    }      """,
                'QSlider-speed': """
                    QSlider::groove:horizontal {
                        border-radius: 6px;
	                    border: 2px solid #41416b;
                        height: 10px;
	                    margin: 0px;
	                    background-color:#e0e0eb;
                    }

                    QSlider::handle:horizontal {
                        background-color: #41416b;
   	                    border: none;
                        height: 10px;
                        width: 10px;
                        margin: 0px;
	                    border-radius: 5px;
                    }

                    QSlider::handle:horizontal:hover {
	                    background-color:#4090ff;
                    }

                    QSlider::handle:horizontal:pressed {
	                     background-color: #40ff66;
                    }

                    QSlider::groove:vertical {
                        border-radius: 5px;
                        width: 10px;
                        margin: 0px;
                        background-color: rgb(52, 59, 72);
                    }

                    QSlider::groove:vertical:hover {
                        background-color: rgb(55, 62, 76);
                    }

                    QSlider::handle:vertical {
                        background-color: rgb(189, 147, 249);
                        border: none;
                        height: 10px;
                        width: 10px;
                        margin: 0px;
                        border-radius: 5px;
                    }
                    
                    QSlider::handle:vertical:hover {
                        background-color: rgb(195, 155, 255);
                    }
                    
                    QSlider::handle:vertical:pressed {
                        background-color: rgb(255, 121, 198);
                    }
                """,
                'QSlider-angle-norm': """
                    QSlider::groove:horizontal {
                        border-radius: 12px;
                        border: 2px solid #41416b;
                        height: 20px;
                        margin: 0px;
                        background-color:#e0e0eb;
                    }
                    
                    QSlider::handle:horizontal {
                        background-color: #40ff66;
                        border: none;
                        height: 20px;
                        width: 20px;
                        margin: 1px;
                        border-radius: 9px;
                    }
                """,
                'QSlider-angle-alarm': """
                    QSlider::groove:horizontal {
                        border-radius: 12px;
                        border: 2px solid #41416b;
                        height: 20px;
                        margin: 0px;
                        background-color:#e0e0eb;
                    }

                    QSlider::handle:horizontal {
                        background-color: red;
                        border: none;
                        height: 20px;
                        width: 20px;
                        margin: 1px;
                        border-radius: 9px;
                    }
                """

            },
            'Dark': {
                'MainWindow': "background: #191929",
                'Menu': "background-color: #41416b",
                'QLabel': "color: white",
                'QListWidget': "background: black; color: white",
                'QTextEdit': "background: black; color: white",
                'QLineEdit': "background: #41416b; color: white",
                'QPlainTextEdit': "background: black; color: white",
                'QPushButton': "color: white",
                'QComboBox': "color: White; background-color: #41416b; padding-left: 10px;",
                'QTableWidget': """
                     QTableWidget {
                        background-color: transparent;
                        padding: 10px;
                        border-radius: 5px;
                        gridline-color: rgb(44, 49, 58);
                        color: white;
                    }
                    QTableWidget::item {
                        border-color: rgb(44, 49, 60);
                        padding-left: 5px;
                        padding-right: 5px;
                        border-right: 1px solid rgb(44, 49, 60); 
                        border-bottom: 1px solid rgb(44, 49, 60);                   
                        border-left: 1px solid rgb(44, 49, 60);
                    }
                    QHeaderView::section{
                        background-color: rgb(33, 37, 43);
                        max-width: 30px;
                        border: 1px solid rgb(44, 49, 58);
                        border-style: none;
                        border-bottom: 1px solid rgb(44, 49, 60);
                        border-right: 1px solid rgb(44, 49, 60);
                        border-left: 1px solid rgb(44, 49, 60);
                        color: white;
                    }
                    QTableWidget::horizontalHeader {	
                        background-color: rgb(33, 37, 43);
                    }
                    QHeaderView::section:horizontal {
                        border: 1px solid rgb(33, 37, 43);
                        background-color: rgb(33, 37, 43);
                        padding: 3px;
                        border-top-left-radius: 7px;
                        border-top-right-radius: 7px;
                    }
                    QHeaderView::section:vertical {
                        border: 1px solid rgb(44, 49, 60);}
                    """,
                'QTabWidget': """
                    QTabWidget::pane {
                        border: none;
                        border-top: 1px solid rgb(0, 0, 0);
                        background: transparent;
                    }
                    QTabBar::tab-bar {
                        border: none;
                    }
                    QTabBar::tab {
                        border: none;
                        border-top-left-radius: 10px;
                        border-top-rigth-radius: 10px;
                        color: rgb(255, 255, 255);
                        background: #191929;
                        height: 30px;
                        min-width: 200px;
                        margin-rigth: 5px;
                        padding-left: 10px;
                        padding-rigth: 10px;
                        color: white;
                    }
                    QTabBar::tab:hover {
                        background: rgb(58, 58, 112);
                    }
                    QTabBar::tab:selected {
                        color: white;
                        background:  rgb(109, 109, 209);
                    }
                                    """,
                'QProgressBar': """
                    QProgressBar {
                        border: solid grey;
                        border-radius: 12px;
                        background-color: #41416b;
                    }   
                    QProgressBar::chunk  {
                        background-color:#40ff66;
                        border-radius: 10px;
                    }      
                """,
                'QSlider-speed': """
                    QSlider::groove:horizontal {
                        border-radius: 6px;
                        border: 2px solid #41416b;
                        height: 10px;
                        margin: 0px;
                        background-color:#19192;
                    }

                    QSlider::handle:horizontal {
                        background-color: #41416b;
                        border: none;
                        height: 10px;
                        width: 10px;
                        margin: 0px;
                        border-radius: 5px;
                    }

                    QSlider::handle:horizontal:hover {
                        background-color:#4090ff;
                    }

                    QSlider::handle:horizontal:pressed {
                         background-color: #40ff66;
                    }

                    QSlider::groove:vertical {
                        border-radius: 5px;
                        width: 10px;
                        margin: 0px;
                        background-color: rgb(52, 59, 72);
                    }

                    QSlider::groove:vertical:hover {
                        background-color: rgb(55, 62, 76);
                    }

                    QSlider::handle:vertical {
                        background-color: rgb(189, 147, 249);
                        border: none;
                        height: 10px;
                        width: 10px;
                        margin: 0px;
                        border-radius: 5px;
                    }

                    QSlider::handle:vertical:hover {
                        background-color: rgb(195, 155, 255);
                    }

                    QSlider::handle:vertical:pressed {
                        background-color: rgb(255, 121, 198);
                    }
                """,
                'QSlider-angle-norm': """
                    QSlider::groove:horizontal {
                        border-radius: 12px;
                        border: 2px solid #41416b;
                        height: 20px;
                        margin: 0px;
                        background-color:#41416b;
                    }
        
                    QSlider::handle:horizontal {
                        background-color: #40ff66;
                        border: none;
                        height: 20px;
                        width: 20px;
                        margin: 1px;
                        border-radius: 9px;
                    }
                """,
                'QSlider-angle-alarm': """
                    QSlider::groove:horizontal {
                        border-radius: 12px;
                        border: 2px solid #41416b;
                        height: 20px;
                        margin: 0px;
                        background-color:#41416b;
                    }

                    QSlider::handle:horizontal {
                        background-color: red;
                        border: none;
                        height: 20px;
                        width: 20px;
                        margin: 1px;
                        border-radius: 9px;
                    }
                """
            },
            'NotAuthorized': {
                'Menu-Light': "background-color: rgb(204, 204, 204)",
                'Menu-Dark': "background-color: rgb(77, 77, 77)",
                'QPushButton-Change':  """
                    QPushButton {
                        border-style: outset;
                        border-width: 2px;
                        border-radius:13px;
                        border-color: grey;
                        min-width: 2em;
                        padding: 6px;
                        color: grey;
                    }
                    QPushButton:pressed {
                        background-color:#40ff66;
                        border-width: 4px;
                        border-color:#1c1c1c;
                        color: white;
                    }
                    """
            },
            'Authorized': {
                'Menu-Light': "background-color: #e0e0eb",
                'Menu-Dark': "background-color: #41416b",
                'QPushButton-Change': """
                    QPushButton {
                        border-style: outset;
                        border-width: 2px;
                        border-radius:13px;
                        border-color: #41416b;
                        min-width: 2em;
                        padding: 6px;
                        color: #41416b;
                    }
                    QPushButton:pressed {
                        background-color:#40ff66;
                        border-width: 4px;
                        border-color:#1c1c1c;
                        color: white;
                    }
                    """
            }
        }

        self.variation_rus = ("Русский", "Russian", "RUS", "РУС")
        self.variation_eng = ("Английский", "English", "ENG", "АНГ")
        self.monitor_data = None

        self.set_start_page()
        self._default()
        self.not_authorized()
        self._init_mdb_rtu_signals()

    # TODO: remove 'PANIC' button and aline 'ACK' and 'enable' buttons (GUI fix)
    def _default(self):
        self.setWindowTitle('DRCS Pendant')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.lbl_speed_value.setText(str(self.slider_speed.value()))
        QSizeGrip(self.lbl_size_grip)

        self._tab_item_font = QFont()
        self._tab_item_font.setFamily("MS Shell Dlg 2")
        self._tab_item_font.setPixelSize(14)
        self._tab_item_font.setBold(True)

        self.btn_no_discrete.setChecked(True)
        self.btn_base_frame.setChecked(True)
        self.btn_enable.setCheckState(False)

        self.trajectory_btn_run.setDisabled(True)
        self.btn_panic.setShortcut('Space')

        self.jog_progress_axis_1.setDisabled(True)
        self.jog_progress_axis_2.setDisabled(True)
        self.jog_progress_axis_3.setDisabled(True)
        self.jog_progress_axis_4.setDisabled(True)
        self.jog_progress_axis_5.setDisabled(True)
        self.jog_progress_axis_6.setDisabled(True)

        self.cmb_settings_theme.setCurrentText(self._current_theme)
        self.cmb_settings_language.setCurrentText(self._start_language)

        # TODO: try to make it in QtCreator (about button groups)
        self.jog_joint_controls_group = QButtonGroup()
        for i, btn in enumerate((self.btn_jog_cw, self.btn_jog_ccw)):
            self.jog_joint_controls_group.addButton(btn, i)

        self.jog_linear_controls_group = QButtonGroup()
        for i, btn in enumerate((self.btn_move_forward, self.btn_move_backward)):
            self.jog_linear_controls_group.addButton(btn, i)

        self.jog_reorient_controls_group = QButtonGroup()
        for i, btn in enumerate((self.btn_move_forward_reorient, self.btn_move_backward_reorient)):
            self.jog_reorient_controls_group.addButton(btn, i)

        self.data_back_group = QButtonGroup()
        for i, btn in enumerate((self.btn_data_joint_back, self.btn_data_cartesian_back)):
            self.data_back_group.addButton(btn)

        self.go_group = QButtonGroup()
        self.go_group.addButton(self.btn_jog_go, 0)

        for child in self.jog_angles_info.findChildren(QLabel):
            if hasattr(child, 'accessibleName') and child.accessibleName():
                self._axes_positions[child.accessibleName()] = child

        for child in self.jog_angles_info.findChildren(QSlider):
            if hasattr(child, 'accessibleName') and child.accessibleName():
                self._jog_progress_axes[child.accessibleName()] = child

        self.grid = QGridLayout(self.widget_for_plot)
        self.view = pg.GraphicsLayoutWidget()
        self.view.setBackground(QColor(255, 255, 255, 0))
        self.grid.addWidget(self.view)
        self.plot = self.view.addPlot()
        self.plot.showGrid(True, True, 1.0)
        self.legend = pg.LegendItem((80, 60), offset=(70, 20))
        self.legend.setParentItem(self.plot.graphicsItem())

        self.settings_tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.settings_tab.setItemDelegate(FontDelegate(self.settings_tab))

        self.data_joint_points.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_joint_points.setItemDelegate(FontDelegate(self.data_joint_points))

        self.signals_tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.signals_tab.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.mdb_rtu_signals_tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mdb_rtu_signals_tab.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.jog_controls.setCurrentIndex(0)

    def authorized(self): # добавлять сюда действия с интерфейсом при блокировке авторизацией
        self.btn_change.setStyleSheet(self.dict_theme_styles['Authorized']['QPushButton-Change'])
        if self._current_theme == 'Light':
            self.body_frame_left_menu.setStyleSheet(self.dict_theme_styles['Authorized']['Menu-Light'])
        else:
            self.body_frame_left_menu.setStyleSheet(self.dict_theme_styles['Authorized']['Menu-Dark'])

        self.btn_change.setDisabled(False)
        self.btn_calibration.setDisabled(False)
        self.btn_data.setDisabled(False)
        self.btn_jog.setDisabled(False)
        self.btn_log.setDisabled(False)
        self.btn_scope.setDisabled(False)
        self.btn_settings.setDisabled(False)
        self.btn_signals.setDisabled(False)
        self.btn_trajectory.setDisabled(False)
        self.lbl_calibration.setDisabled(False)
        self.lbl_data.setDisabled(False)
        self.lbl_jog.setDisabled(False)
        self.lbl_log.setDisabled(False)
        self.lbl_scope.setDisabled(False)
        self.lbl_settings.setDisabled(False)
        self.lbl_signals.setDisabled(False)
        self.lbl_trajectory.setDisabled(False)
        self.btn_enable.setDisabled(False)

    def not_authorized(self): # добавлять сюда действия с интерфейсом при разблокировке авторизацией
        self.btn_change.setStyleSheet(self.dict_theme_styles['NotAuthorized']['QPushButton-Change'])
        if self._current_theme == 'Light':
            self.body_frame_left_menu.setStyleSheet(self.dict_theme_styles['NotAuthorized']['Menu-Light'])
        else:
            self.body_frame_left_menu.setStyleSheet(self.dict_theme_styles['NotAuthorized']['Menu-Dark'])

        self.btn_change.setDisabled(True)
        self.btn_calibration.setDisabled(True)
        self.btn_data.setDisabled(True)
        self.btn_jog.setDisabled(True)
        self.btn_log.setDisabled(True)
        self.btn_scope.setDisabled(True)
        self.btn_settings.setDisabled(True)
        self.btn_signals.setDisabled(True)
        self.btn_trajectory.setDisabled(True)
        self.lbl_calibration.setDisabled(True)
        self.lbl_data.setDisabled(True)
        self.lbl_jog.setDisabled(True)
        self.lbl_log.setDisabled(True)
        self.lbl_scope.setDisabled(True)
        self.lbl_settings.setDisabled(True)
        self.lbl_signals.setDisabled(True)
        self.lbl_trajectory.setDisabled(True)
        self.btn_enable.setDisabled(True)
        self.led_login.clear()
        self.led_password.clear()

    def keyPressEvent(self, event):

        index = self.jog_controls.currentIndex()
        if self.work_area.currentIndex() == 2: #num pad should to work only in jog mode menu (work_area == 2)
            # manage speed slider
            if event.key() == Qt.Key_Asterisk:
                self.slider_speed.setValue(self.slider_speed.value() + 1)
            if event.key() == Qt.Key_Slash:
                self.slider_speed.setValue(self.slider_speed.value() - 1)

            # manage mode
            if event.key() == Qt.Key_0:
                self.btn_jog_axes.animateClick()
            if event.key() == Qt.Key_Q:
                self.btn_jog_axes.animateClick()
            if event.key() == Qt.Key_W:
                self.btn_jog_linear.animateClick()
            if event.key() == Qt.Key_E:
                self.btn_jog_reorient.animateClick()
            if event.key() == Qt.Key_R:
                self.btn_jog_go_to.animateClick()

            # jog mode
            if index == 1:
                if event.key() == Qt.Key_1:
                    self.btn_jog_axis_1.animateClick()
                if event.key() == Qt.Key_2:
                    self.btn_jog_axis_2.animateClick()
                if event.key() == Qt.Key_3:
                    self.btn_jog_axis_3.animateClick()
                if event.key() == Qt.Key_4:
                    self.btn_jog_axis_4.animateClick()
                if event.key() == Qt.Key_5:
                    self.btn_jog_axis_5.animateClick()
                if event.key() == Qt.Key_6:
                    self.btn_jog_axis_6.animateClick()

                if event.key() == Qt.Key_Plus:
                    self.btn_jog_cw.animateClick(1000)
                if event.key() == Qt.Key_Minus:
                    self.btn_jog_ccw.animateClick(1000)

            # linear mode
            if index == 2:
                if event.key() == Qt.Key_7:
                    self.btn_axis_x.animateClick()
                if event.key() == Qt.Key_8:
                    self.btn_axis_y.animateClick()
                if event.key() == Qt.Key_9:
                    self.btn_axis_z.animateClick()
                if event.key() == Qt.Key_4:
                    self.btn_base_frame.animateClick()
                if event.key() == Qt.Key_5:
                    self.btn_tool_frame.animateClick()
                if event.key() == Qt.Key_1:
                    self.btn_no_discrete.animateClick()
                if event.key() == Qt.Key_2:
                    self.btn_medium_discrete.animateClick()
                if event.key() == Qt.Key_3:
                    self.btn_large_discrete.animateClick()

                if event.key() == Qt.Key_Plus:
                    self.btn_move_forward.animateClick(1000)
                if event.key() == Qt.Key_Minus:
                    self.btn_move_backward.animateClick(1000)

            # reorient mode
            if index == 3:
                if event.key() == Qt.Key_7:
                    self.btn_axis_x_reorient.animateClick()
                if event.key() == Qt.Key_8:
                    self.btn_axis_y_reorient.animateClick()
                if event.key() == Qt.Key_9:
                    self.btn_axis_z_reorient.animateClick()
                if event.key() == Qt.Key_4:
                    self.btn_base_frame_reorient.animateClick()
                if event.key() == Qt.Key_5:
                    self.btn_tool_frame_reorient.animateClick()
                if event.key() == Qt.Key_1:
                    self.btn_no_discrete_reorient.animateClick()
                if event.key() == Qt.Key_2:
                    self.btn_medium_discrete_reorient.animateClick()
                if event.key() == Qt.Key_3:
                    self.btn_large_discrete_reorient.animateClick()

                if event.key() == Qt.Key_Plus:
                    self.btn_move_forward_reorient.animateClick(1000)
                if event.key() == Qt.Key_Minus:
                    self.btn_move_backward_reorient.animateClick(1000)

        # if event.key() == Qt.Key_Z:
        #     self.btn_jog_gripper_open.animateClick()
        #
        # if event.key() == Qt.Key_X:
        #     self.btn_jog_gripper_close.animateClick()

        if event.key() == Qt.Key_Z:
            self.invert_signal_by_key('out_tool_2_open')

        if event.key() == Qt.Key_X:
            self.invert_signal_by_key('out_tool_1_open')

    def keyReleaseEvent(self, event):
        index = self.jog_controls.currentIndex()
        if self.work_area.currentIndex() == 2:
            if index == 1:
                if event.key() == Qt.Key_Plus:
                    self.btn_jog_cw.animateClick(0)
                if event.key() == Qt.Key_Minus:
                    self.btn_jog_ccw.animateClick(0)
            if index == 2:
                if event.key() == Qt.Key_Plus:
                    self.btn_move_forward.animateClick(0)
                if event.key() == Qt.Key_Minus:
                    self.btn_move_backward.animateClick(0)
            if index == 3:
                if event.key() == Qt.Key_Plus:
                    self.btn_move_forward_reorient.animateClick(0)
                if event.key() == Qt.Key_Minus:
                    self.btn_move_backward_reorient.animateClick(0)

    def ext_res_monitoring(self, data):  # for testing ext_resolvers

        # axe 1
        raw_position_1_ext = data['raw_position_1_ext']
        self.lbl_current_axe_1_ext.setText(str(raw_position_1_ext))
        try:
            zero_axe_1 = int(self.led_zero_axe_1_ext.text())
        except:
            zero_axe_1 = 0
        delta_axe_1_ext = raw_position_1_ext - zero_axe_1
        self.lbl_delta_axe_1_ext.setText(str(delta_axe_1_ext))

        # axe 2
        raw_position_2_ext = data['raw_position_2_ext']
        self.lbl_current_axe_2_ext.setText(str(raw_position_2_ext))
        try:
            zero_axe_2 = int(self.led_zero_axe_2_ext.text())
        except:
            zero_axe_2 = 0
        delta_axe_2_ext = raw_position_2_ext - zero_axe_2
        self.lbl_delta_axe_2_ext.setText(str(delta_axe_2_ext))

        #axe 3
        raw_position_3_ext = data['raw_position_3_ext']
        self.lbl_current_axe_3_ext.setText(str(raw_position_3_ext))
        try:
            zero_axe_3 = int(self.led_zero_axe_3_ext.text())
        except:
            zero_axe_3 = 0
        delta_axe_3_ext = raw_position_3_ext - zero_axe_3
        self.lbl_delta_axe_3_ext.setText(str(delta_axe_3_ext))

        #axe 4
        raw_position_4_ext = data['raw_position_4_ext']
        self.lbl_current_axe_4_ext.setText(str(raw_position_4_ext))
        try:
            zero_axe_4 = int(self.led_zero_axe_4_ext.text())
        except:
            zero_axe_4 = 0
        delta_axe_4_ext = raw_position_4_ext - zero_axe_4
        self.lbl_delta_axe_4_ext.setText(str(delta_axe_4_ext))

        # axe 5 (ext_resolver 5)
        raw_position_5_5_ext = data['raw_position_5_ext']
        self.lbl_current_axe_5_5_ext.setText(str(raw_position_5_5_ext))
        try:
            zero_axe_5_5 = int(self.led_zero_axe_5_5_ext.text())
        except:
            zero_axe_5_5 = 0
        delta_axe_5_5_ext = raw_position_5_5_ext - zero_axe_5_5
        self.lbl_delta_axe_5_5_ext.setText(str(delta_axe_5_5_ext))

        # axe 5 (ext_resolver 6)
        raw_position_5_6_ext = data['raw_position_6_ext']
        self.lbl_current_axe_5_6_ext.setText(str(raw_position_5_6_ext))
        try:
            zero_axe_5_6 = int(self.led_zero_axe_5_6_ext.text())
        except:
            zero_axe_5_6 = 0
        delta_axe_5_6_ext = raw_position_5_6_ext - zero_axe_5_6
        self.lbl_delta_axe_5_6_ext.setText(str(delta_axe_5_6_ext))

        # axe 6 (ext_resolver 7)
        raw_position_6_7_ext = data['raw_position_7_ext']
        self.lbl_current_axe_6_7_ext.setText(str(raw_position_6_7_ext))
        try:
            zero_axe_6_7 = int(self.led_zero_axe_6_7_ext.text())
        except:
            zero_axe_6_7 = 0
        delta_axe_6_7_ext = raw_position_6_7_ext - zero_axe_6_7
        self.lbl_delta_axe_6_7_ext.setText(str(delta_axe_6_7_ext))

        # axe 6 (ext_resolver 8)
        raw_position_6_8_ext = data['raw_position_8_ext']
        self.lbl_current_axe_6_8_ext.setText(str(raw_position_6_8_ext))
        try:
            zero_axe_6_8 = int(self.led_zero_axe_6_8_ext.text())
        except:
            zero_axe_6_8 = 0
        delta_axe_6_8_ext = raw_position_6_8_ext - zero_axe_6_8
        self.lbl_delta_axe_6_8_ext.setText(str(delta_axe_6_8_ext))

    def disable_main_window(self, data):
        gui_enable = data['in_manual_mode']
        self.window().setEnabled(gui_enable)

    def set_start_page(self):
        self.work_area.setCurrentIndex(0)
        self.jog_controls.setCurrentIndex(0)
        self.current_page.setCurrentIndex(0)
        self.lbl_logo.setVisible(False)

    def set_style(self, qclass, style):
        for child in self.findChildren(qclass):
            if child.accessibleDescription() not in self.lst_not_styled_accessibleDescription:
                child.setStyleSheet(style)

    def change_theme(self, theme):

        if theme == "Светлая": theme = "Light"
        if theme == "Темная": theme = "Dark"

        if theme == 'Light':
            self.btn_enable.bg_color = '#e0e0eb'
        else:
            self.btn_enable.bg_color = '#41416b'

        self.setStyleSheet(self.dict_theme_styles[theme]['MainWindow'])
        self.body_frame_left_menu.setStyleSheet(self.dict_theme_styles[theme]['Menu'])
        self.slider_speed.setStyleSheet(self.dict_theme_styles[theme]['QSlider-speed'])
        self.set_style(QLabel, style=self.dict_theme_styles[theme]['QLabel'])
        self.set_style(QListWidget, style=self.dict_theme_styles[theme]['QListWidget'])
        self.set_style(QTextEdit, style=self.dict_theme_styles[theme]['QTextEdit'])
        self.set_style(QLineEdit, style=self.dict_theme_styles[theme]['QLineEdit'])
        self.set_style(QPlainTextEdit, style=self.dict_theme_styles[theme]['QPlainTextEdit'])
        self.set_style(QPushButton, style=self.dict_theme_styles[theme]['QPushButton'])
        self.set_style(QComboBox, style=self.dict_theme_styles[theme]['QComboBox'])
        self.set_style(QTableWidget, style=self.dict_theme_styles[theme]['QTableWidget'])
        self.set_style(QTabWidget, style=self.dict_theme_styles[theme]['QTabWidget'])
        self.set_style(QProgressBar, style=self.dict_theme_styles[theme]['QProgressBar'])
        self._current_theme = theme

    def update_little_log(self, msg):
        counter = self.logo_text.count()
        self.logo_text.insertItem(counter, f'{msg}')
        self.logo_text.item(counter).setForeground(QColor(self.colors.get(msg.split(' ')[0], 'black')))
        if counter == self.items_in_little_log:
            self.logo_text.takeItem(0)

    def update_big_log(self, msg):
        for level, color in self.colors.items():
            if level in msg:
                s = '<pre><font color="%s">%s</font></pre>' % (color, msg)
                self.item_counter += 1
                self.log_plain.appendHtml(s)
                if self.item_counter == self.items_in_big_log:
                    self.log_plain.clear()
                    self.item_counter = 0

    def update_log_list(self, file_list):
        self.log_files_list.clear()
        for element in file_list:
            self.log_files_list.addItem(element)

    def update_old_log_plain(self, path):
        self.old_log_plain.clear()
        data = read_from_log_file(path)
        self.old_log_plain.setPlainText(data)

    def is_number(self, str):
        try:
            float(str)
            return True
        except ValueError:
            return False

    def restore_or_maximize_window(self):
        if not self.isMaximized():
            self.showMaximized()
            self.lbl_size_grip.hide()
        else:
            self.showNormal()
            self.lbl_size_grip.show()

    def define_first_click_position(self, event):
        # save first click position on the header frame
        self.click_position = event.globalPos()

    def move_window(self, event):
        if not self.isMaximized() and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.click_position)
            self.click_position = event.globalPos()
            event.accept()

    def slide_menu_animation(self, current_width, new_width):
        self.side_menu_animation = QPropertyAnimation(self.body_frame_left_menu, b'maximumWidth')
        self.side_menu_animation.setDuration(500)
        self.side_menu_animation.setStartValue(current_width)
        self.side_menu_animation.setEndValue(new_width)
        self.side_menu_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.side_menu_animation.start()

    def slide_menu(self):
        # TODO: make one method for slide animation.
        #  Input data: new_width(int), key for widget: 'main_menu', 'joint_keyboard', etc
        #  Make dict like: {'main_menu': [self.side_menu_animation, self.body_frame_left_menu]}
        current_width = self.body_frame_left_menu.width()

        if current_width == 0:
            new_width = 200
        else:
            new_width = 0

        self.slide_menu_animation(current_width, new_width)

    def slide_menu_short(self):
        current_width = self.body_frame_left_menu.width()
        new_width = 70
        self.slide_menu_animation(current_width, new_width)

    def slide_joint_edit_keyboard(self):
        current_width = self.data_joint_keyboard_frame.width()
        if current_width == 0:
            new_width = 800
        else:
            new_width = 0

        self.joint_edit_keyboard_animation = QPropertyAnimation(self.data_joint_keyboard_frame, b'maximumWidth')
        self.joint_edit_keyboard_animation.setDuration(500)
        self.joint_edit_keyboard_animation.setStartValue(current_width)
        self.joint_edit_keyboard_animation.setEndValue(new_width)
        self.joint_edit_keyboard_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.joint_edit_keyboard_animation.start()

    def slide_virtual_keyboard(self):
        current_width = self.virtual_keyboard_frame.width()
        if current_width == 0:
            new_width = 150
        else:
            new_width = 0

        self.virtual_keyboard_animation = QPropertyAnimation(self.virtual_keyboard_frame, b'maximumWidth')
        self.virtual_keyboard_animation.setDuration(500)
        self.virtual_keyboard_animation.setStartValue(current_width)
        self.virtual_keyboard_animation.setEndValue(new_width)
        self.virtual_keyboard_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.virtual_keyboard_animation.start()

    def open_work_widget(self, index):
        self.work_area.setCurrentIndex(index)
        self.current_page.setCurrentIndex(index)
        self.lbl_logo.setVisible(True)
        #self.data_joints_list.sortItems()

    def open_jog_widget(self, index):
        self.jog_controls.setCurrentIndex(index)
        if index == 1:
            self.btn_jog_axes.setChecked(True)
        elif index == 2:
            self.btn_jog_linear.setChecked(True)
        elif index == 3:
            self.btn_jog_reorient.setChecked(True)
        elif index == 4:
            self.btn_jog_go_to.setChecked(True)
        else:
            self.btn_jog_axes.setChecked(False)
            self.btn_jog_linear.setChecked(False)
            self.btn_jog_reorient.setChecked(False)
            self.btn_jog_go_to.setChecked(False)

    def update_speed_unit(self, index):
        jog_mode = index

        if jog_mode == 4:
            unit = 'sec'
        elif 1 <= jog_mode <= 3:
            unit = '%'
        else:
            unit = 'sec / %'

        self.lbl_speed_unit.setText(unit)

    def update_speed_value(self, value):
        self.lbl_speed_value.setText(value)

    def rtc_update_speed_slider(self, value):
        self.lbl_speed_value.setText(str(value))
        self.slider_speed.setValue(value)

    def rtc_update_btn_jog_axis(self, number):
        if number == 1: self.btn_jog_axis_1.setChecked(True)
        elif number == 2: self.btn_jog_axis_2.setChecked(True)
        elif number == 3: self.btn_jog_axis_3.setChecked(True)
        elif number == 4: self.btn_jog_axis_4.setChecked(True)
        elif number == 5: self.btn_jog_axis_5.setChecked(True)
        elif number == 6: self.btn_jog_axis_6.setChecked(True)

    def update_plc_signals(self, data):
        if data is not None:
            self.signals_tab.setRowCount(len(data.values()))

            for i, key in enumerate(data.keys()):
                self.signals_tab.setItem(i, 0, QTableWidgetItem(str(key)))
                self.signals_tab.item(i, 0).setFont(self._tab_item_font)
                self.signals_tab.setColumnWidth(i, int(self.width() / 3))

            for j, value in enumerate(data.values()):
                self.signals_tab.setItem(j, 1, QTableWidgetItem(str(value)))
                if self._current_theme == 'Dark':
                    self.signals_tab.item(j, 1).setForeground(QColor(self._tab_item_bool_color.get(str(value), 'white')))
                else:
                    self.signals_tab.item(j, 1).setForeground(
                        QColor(self._tab_item_bool_color.get(str(value), '#191929')))

                self.signals_tab.item(j, 1).setFont(self._tab_item_font)
                self.signals_tab.item(j, 1).setTextAlignment(45)

    def _init_mdb_rtu_signals(self):
        data = self.db.read_mdbrtu_io_monitor()
        if data is not None:
            self.mdb_rtu_signals_tab.setRowCount(len(data.values()))

            for i, key in enumerate(data.keys()):
                self.mdb_rtu_signals_tab.setItem(i, 0, QTableWidgetItem(str(key)))
                self.mdb_rtu_signals_tab.item(i, 0).setFont(self._tab_item_font)
                self.mdb_rtu_signals_tab.setColumnWidth(i, int(self.width() / 4))

            for j, value in enumerate(data.values()):
                self.mdb_rtu_signals_tab.setItem(j, 1, QTableWidgetItem(str(value)))
                self.mdb_rtu_signals_tab.setItem(j, 2, QTableWidgetItem(str(value)))
                self.mdb_rtu_signals_tab.item(j, 1).setFont(self._tab_item_font)
                self.mdb_rtu_signals_tab.item(j, 2).setFont(self._tab_item_font)
                self.mdb_rtu_signals_tab.item(j, 1).setTextAlignment(45)
                self.mdb_rtu_signals_tab.item(j, 2).setTextAlignment(45)

    def update_mdb_rtu_signals(self, data):
        if data is not None:
            self.mdb_rtu_signals_tab.setRowCount(len(data.values()))

            for i, key in enumerate(data.keys()):
                self.mdb_rtu_signals_tab.setItem(i, 0, QTableWidgetItem(str(key)))
                self.mdb_rtu_signals_tab.item(i, 0).setFont(self._tab_item_font)
                self.mdb_rtu_signals_tab.setColumnWidth(i, int(self.width() / 4))

            for j, value in enumerate(data.values()):
                self.mdb_rtu_signals_tab.setItem(j, 1, QTableWidgetItem(str(value)))
                if self._current_theme == 'Dark':
                    self.mdb_rtu_signals_tab.item(j, 1).setForeground(QColor(self._tab_item_bool_color.get(str(value), 'white')))
                else:
                    self.mdb_rtu_signals_tab.item(j, 1).setForeground(
                        QColor(self._tab_item_bool_color.get(str(value), '#191929')))

                self.mdb_rtu_signals_tab.item(j, 1).setFont(self._tab_item_font)
                self.mdb_rtu_signals_tab.item(j, 1).setTextAlignment(45)

    def write_mdb_rtu_tab_signals(self, data):
        for row, key in enumerate(data.keys()):
            # if key[3:6] == 'out':
            if key.split('_')[1] == 'out':
                value = int(self.mdb_rtu_signals_tab.item(row, 2).text())
                btn = QPushButton('Write')
                btn.setStyleSheet("""
                            QPushButton {
                                background-color: transparent;
                                border-style: outset;
                                border-width: 2px;
                                border-radius:13px;
                                border-color: #41416b;
                                min-width: 3em;
                                padding: 6px;
                                margin: 0px;
                                color: #41416b;
                                }

                            QPushButton:pressed {
                                background-color:#40ff66;
                                border-width: 4px;
                                border-color:#1c1c1c;
                                color: white;
                                }""")
                self.mdb_rtu_signals_tab.setCellWidget(row, 3, btn)
                self.mdb_rtu_signals_tab.item(row, 2).setForeground(QColor('orange'))
                btn.pressed.connect(
                    lambda key=key, val=value: self.db.add_to_mdbrtu_tasks(key, val))

    def invert_tab_signals(self, monitor_data):
        self.monitor_data = monitor_data
        for row, key in enumerate(monitor_data.keys()):
            if key.split('_')[0] == 'out':
                value = monitor_data[key]
                btn = QPushButton('Invert')
                btn.setStyleSheet("""
                            QPushButton {
                                background-color: transparent;
                                border-style: outset;
                                border-width: 2px;
                                border-radius:13px;
                                border-color: #41416b;
                                min-width: 3em;
                                padding: 6px;
                                margin: 0px;
                                color: #41416b;
                                }
    
                            QPushButton:pressed {
                                background-color:#40ff66;
                                border-width: 4px;
                                border-color:#1c1c1c;
                                color: white;
                                }""")
                self.signals_tab.setCellWidget(row, 2, btn)
                btn.pressed.connect(
                    lambda key=key, val=value: self.invert_signal(key, val))

    def invert_signal_by_key(self, key):
        value = self.monitor_data[key]
        self.invert_signal(key, value)

    def invert_signal(self, key, val):
        value = not val
        self.db.add_to_plc_tasks(key, value)

    def update_settings(self, data):
        if data is not None:
            self.settings_tab.setRowCount(len(self.settings_filter))
            i = 0
            for key in data.keys():
                if key in self.settings_filter:
                    self.settings_tab.setItem(i, 0, QTableWidgetItem(str(key)))
                    self.settings_tab.item(i, 0).setFont(self._tab_item_font)
                    self.settings_tab.setColumnWidth(i, int(self.width() / 3))
                    self.settings_tab.setItem(i, 1, QTableWidgetItem(str(data[key])))
                    # self.settings_tab.item(j, 1).setForeground(QColor(self._tab_item_bool_color.get(str(value), 'white')))
                    self.settings_tab.item(i, 1).setFont(self._tab_item_font)
                    self.settings_tab.item(i, 1).setTextAlignment(45)
                    i += 1

    def write_settings(self, path):
        item = QTableWidgetItem()
        for i in range(len(self.settings_filter)):
            key = self.settings_tab.item(i, 0).text()
            value = self.settings_tab.item(i, 1).text()

            if key in self.settings_filter:
                if self.settings_filter[key] == 'int':
                    if self.is_number(value):
                        value = int(value)
                        add_to_json(path, key, value)
                elif self.settings_filter[key] == 'ip':  # to do ip-verification
                    add_to_json(path, key, value)
                else:
                    add_to_json(path, key, value)

    def update_mode_status(self, data):
        self.lbl_mode_value.setStyleSheet(f'color:{self._tab_item_bool_color["True"]}')
        self.lbl_mode_value.setText(f'{self._mode_bool_text[str(data["in_manual_mode"])]}')

    def update_axes_poses(self, data):
        for key, value in data.items():
            if key in self._axes_positions.keys():
                self._axes_positions[key].setText(str(round(value, 2)))
                if self._current_theme == "Dark":
                    self._axes_positions[key].setStyleSheet('color: white')
                elif self._current_theme == "Light":
                    self._axes_positions[key].setStyleSheet('color: #191929')

    def update_axes_limits(self, limits, offset):
        axes_limits = limits
        self._axes_limits_alarm_offset = offset
        self.jog_progress_axis_1.setMinimum(axes_limits['axis_1_min'])
        self.jog_progress_axis_1.setMaximum(axes_limits['axis_1_max'])
        self.jog_progress_axis_2.setMinimum(axes_limits['axis_2_min'])
        self.jog_progress_axis_2.setMaximum(axes_limits['axis_2_max'])
        self.jog_progress_axis_3.setMinimum(axes_limits['axis_3_min'])
        self.jog_progress_axis_3.setMaximum(axes_limits['axis_3_max'])
        self.jog_progress_axis_4.setMinimum(axes_limits['axis_4_min'])
        self.jog_progress_axis_4.setMaximum(axes_limits['axis_4_max'])
        self.jog_progress_axis_5.setMinimum(axes_limits['axis_5_min'])
        self.jog_progress_axis_5.setMaximum(axes_limits['axis_5_max'])
        self.jog_progress_axis_6.setMinimum(axes_limits['axis_6_min'])
        self.jog_progress_axis_6.setMaximum(axes_limits['axis_6_max'])

    def update_axes_progress(self, data):
        theme = self._current_theme
        offset = self._axes_limits_alarm_offset
        for key, value in data.items():
            if key in self._jog_progress_axes.keys():
                self._jog_progress_axes[key].setValue(int(value))

                if (self._jog_progress_axes[key].minimum() + offset) <= value <= (
                        self._jog_progress_axes[key].maximum() - offset) and (theme == 'Dark' or theme == 'Light'):
                    self._jog_progress_axes[key].setStyleSheet(self.dict_theme_styles[theme]['QSlider-angle-norm'])
                else:
                    self._jog_progress_axes[key].setStyleSheet(self.dict_theme_styles[theme]['QSlider-angle-alarm'])

    def update_fault_codes(self, data):
        if sum(data.values()):
            text_status = ""
            for key, value in data.items():
                if value:
                    num_axes = (key.split("_"))[1]
                    text_status = text_status + f"#{num_axes}: code {value}     "
            self.lbl_status_value.setText(text_status)
            self.lbl_status_value.setStyleSheet(f'color: {self._tab_item_bool_color["False"]}')
        else:
            self.lbl_status_value.setText("Ok")
            self.lbl_status_value.setStyleSheet(f'color: {self._tab_item_bool_color["True"]}')

    def update_cartesian_poses(self, data):
        for key, value in data.items():
            if key in self._axes_positions.keys():
                self._axes_positions[key].setText(value)
                self._axes_positions[key].setStyleSheet(f'color: {self._cartesian_colors.get(key, "white")}')

    def show_data_types_widget(self, index):
        self.data_types.setCurrentIndex(index)

    def update_joint_points_list(self, data):
        if data:
            for point_name, joints in data.items():
                if point_name not in self._joint_points:
                    self._joint_points.append(point_name)
                    self.data_joints_list.addItem(f'{point_name}: {joints}')
                    self.jog_point_list.addItem(f'{point_name}')

        #self.jog_point_list.sortItems() (закомментил потому что не корректно работает список точек в GO TO... (в Ручном режиме))

    def remove_joint_item(self, name):
        index = self._joint_points.index(name)
        self._joint_points.remove(name)
        self.data_joints_list.takeItem(index)
        self.jog_point_list.takeItem(index)

    def edit_joint_point_data(self, char):
        selected_row = self.data_joint_points.currentIndex().row()
        selected_column = self.data_joint_points.currentIndex().column()

        if selected_column == 1:
            item = QTableWidgetItem()
            index = self.data_joint_points.currentIndex()
            print('index: ', index)
            old_char = self.data_joint_points.item(index.row(), index.column()).text()
            print('old_char: ', old_char)

            if char == 'bck':
                item.setText(old_char[:-1])
                self.data_joint_points.setItem(index.row(), index.column(), item)
                self.data_joint_points.item(index.row(), index.column()).setFont(self._tab_item_font)
            else:
                if selected_row != self.old_selected_row:
                    item.setText(char)
                else:
                    item.setText(old_char + char)

            if selected_row != 0:
                if self.is_number(item.text()):
                    self.data_joint_points.setItem(index.row(), index.column(), item)
                    self.data_joint_points.item(index.row(), index.column()).setFont(self._tab_item_font)
            else:
                self.data_joint_points.setItem(index.row(), index.column(), item)
                self.data_joint_points.item(index.row(), index.column()).setFont(self._tab_item_font)

            self.old_selected_row = selected_row

    def virtual_keyboard_edit_data(self, char):
        if self.focusWidget():
            widgetname = self.focusWidget().objectName()
            widget_type = self.focusWidget().metaObject().className()

            if widget_type == 'QTableWidget':

                selected_row = self.focusWidget().currentIndex().row()
                selected_column = self.focusWidget().currentIndex().column()

                if selected_column == 1:
                    item = QTableWidgetItem()
                    index = self.focusWidget().currentIndex()
                    old_char = self.focusWidget().item(index.row(), index.column()).text()

                    if char == 'Bck':
                        item.setText(old_char[:-1])
                        self.focusWidget().setItem(index.row(), index.column(), item)
                        self.focusWidget().item(index.row(), index.column()).setFont(self._tab_item_font)
                    elif char == 'Ent': pass
                    else:
                        if char == 'Shift': pass
                        else:
                            if self.btn_virtual_keyboard_symbol_shift.isChecked():
                                if selected_row != self.old_selected_row:
                                    item.setText(char.upper())
                                else:
                                    item.setText(old_char + char.upper())
                            else:
                                if selected_row != self.old_selected_row:
                                    item.setText(char)
                                else:
                                    item.setText(old_char + char)

                            if widgetname=='data_joint_points' and selected_row != 0:
                                if self.is_number(item.text()):
                                    self.focusWidget().setItem(index.row(), index.column(), item)
                                    self.focusWidget().item(index.row(), index.column()).setFont(self._tab_item_font)
                            else:
                                self.focusWidget().setItem(index.row(), index.column(), item)
                                self.focusWidget().item(index.row(), index.column()).setFont(self._tab_item_font)

                            self.old_selected_row = selected_row

                    if widgetname == 'settings_tab':
                        self.focusWidget().item(index.row(), index.column()).setTextAlignment(45)

            elif widget_type == 'QLineEdit':
                selected_widget = self.focusWidget().objectName()
                old_char = self.focusWidget().text()
                if char == 'Bck':
                    if selected_widget != self.old_selected_widget:
                        self.focusWidget().clear()
                    else:
                        self.focusWidget().setText(old_char[:-1])
                        self.focusWidget().setFont(self._tab_item_font)
                elif char == 'Ent': pass
                else:
                    if char != 'Shift':
                        if self.btn_virtual_keyboard_symbol_shift.isChecked():
                            if selected_widget != self.old_selected_widget:
                                self.focusWidget().setText(char.upper())
                            else:
                                self.focusWidget().setText(old_char + char.upper())
                        else:
                            if selected_widget != self.old_selected_widget:
                                self.focusWidget().setText(char)
                            else:
                                self.focusWidget().setText(old_char + char)

                        self.old_selected_widget = selected_widget

            elif widget_type == 'QTextEdit':
                cursor = self.focusWidget().textCursor()
                if char == 'Bck':
                    cursor.deletePreviousChar()
                elif char == 'Ent':
                    cursor.insertText('\n')
                else:
                    if char != 'Shift':
                        if self.btn_virtual_keyboard_symbol_shift.isChecked():
                            cursor.insertText(char.upper())
                        else:
                            cursor.insertText(char)

            else: pass

    def show_joint_data_for_edit(self, data):
        row_names = ('Name',
                     'angle_axis_1',
                     'angle_axis_2',
                     'angle_axis_3',
                     'angle_axis_4',
                     'angle_axis_5',
                     'angle_axis_6')

        if data is not None:
            self.data_joint_points.setRowCount(len(data))

            for i, name in enumerate(row_names):
                self.data_joint_points.setItem(i, 0, QTableWidgetItem(name))
                self.data_joint_points.item(i, 0).setFont(self._tab_item_font)

            for j, value in enumerate(data):
                self.data_joint_points.setItem(j, 1, QTableWidgetItem(str(value)))
                self.data_joint_points.item(j, 1).setFont(self._tab_item_font)

        self.data_joint_points.resizeColumnsToContents()

    def unlock_run_trajectory(self):
        self.trajectory_btn_run.setEnabled(True)

    def lock_run_trajectory(self):
        self.trajectory_btn_run.setDisabled(True)

    def update_scope_signals(self, signals):
        for signal in signals:
            if signal not in self._scope_signals:
                self._scope_signals.append(signal)
                self.lst_avaliable_signals.addItem(signal)

    def add_scope_signal(self, item):
        if item not in self._selected_signals:
            self._selected_signals.append(item)
            self.lst_selected_signals.addItem(item)

    def clear_selected_signals(self):
        self.lst_selected_signals.clear()
        self._selected_signals.clear()

    def update_plot_files(self, files):
        self.lst_plot_files.clear()

        for file in files:
            self.lst_plot_files.addItem(file)

    def show_plot(self, data):

        self.plot.clear()
        self.legend.clear()

        plot_widget = pg.PlotWidget()
        plot_widget.showGrid(x=True, y=True)

        if data:
            for parameter, value in data.items():
                index = list(data.values()).index(value)
                plot = plot_widget.plot(list(data.values())[0], value, pen=colors.COLORS.get(index, (128, 128, 128)))
                self.curves[plot] = colors.COLORS.get(index, (128, 128, 128))

                self.legend.addItem(plot, parameter)
                self.plot.addItem(plot)

    def clear_trajectory(self):
        self.trajectory_edit.clear()

    def update_motors_status(self, status, color):
        self.lbl_motors_value.setText(status)
        self.lbl_motors_value.setStyleSheet(f'color:{self._tab_item_bool_color[color]}')

    def enable_visualization(self):
        if not self.btn_enable.isChecked():
            self.btn_enable.animateClick()

    def disable_visualization(self):
        if self.btn_enable.isChecked():
            self.btn_enable.animateClick()

    def clicked_language(self, lang):
        if lang in self.variation_rus:
            self.trans.load('./translates/eng-rus')
            _app = QApplication.instance()
            _app.installTranslator(self.trans)
            logger.info(self.tr('Russian language is selected'))
            self.cmb_settings_language.setCurrentText("Russian")
        elif lang in self.variation_eng:
            _app = QApplication.instance()
            _app.removeTranslator(self.trans)
            logger.info(self.tr('English language is selected'))
            self.cmb_settings_language.setCurrentText("Английский")

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi(self)


# TODO: DONE! this two classes looks like the same. Try to inherit
class TrjSaveWindow(QWidget, trj_save_window.Ui_TrjSaveWindow):
    def __init__(self, path):
        super().__init__()
        self.setupUi(self)
        self.trans = QTranslator(self)
        self.old_selected_widget = None
        self.lst_not_styled_accessibleDescription = ("not styled",
                                                     "save",
                                                     "cancel",
                                                     "upload",
                                                     "delete")
        self.dict_theme_styles = {
            'Light': {
                'MainWindow': "background: white",
                'Window_frame': "border-style: solid; border-width: 1px; border-color: grey",
                'QFrame': "border-width: 0px",
                'QLabel': "color: #191929",
                'QListWidget': "background: #e0e0eb; color: black;",
                'QTextEdit': "background: #e0e0eb; color: black;",
                'QPushButton': "color: #191929",
                'QComboBox': "color: #191929; background-color: white; border: 1px solid black; border-color: #191929",
                'QLineEdit': "background: #e0e0eb; color: black;"
            },
            'Dark': {
                'MainWindow': "background: #191929",
                'Window_frame': "border-style: solid; border-width: 1px; border-color: white",
                'QFrame': "border-width: 0px",
                'QLabel': "color: white",
                'QListWidget': "background: black; color: white; border-style: solid; border-width: 2px; border-color: white;",
                'QTextEdit': "background: black; color: white; border-style: solid; border-width: 2px; border-color: white;",
                'QPushButton': "color: white",
                'QComboBox': "color: White; background-color: #41416b",
                'QLineEdit': "background: black; color: white; border-style: solid; border-width: 2px; border-color: white;"
            }
        }
        self.file_path = path
        self._default()

    def _default(self):
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

    def set_style(self, qclass, style):
        for child in self.findChildren(qclass):
            if child.accessibleDescription() not in self.lst_not_styled_accessibleDescription:
                child.setStyleSheet(style)

    def change_theme(self, theme):
        if theme == "Светлая": theme = "Light"
        if theme == "Темная": theme = "Dark"

        self.setStyleSheet(self.dict_theme_styles[theme]['MainWindow'])
        self.set_style(QFrame, style=self.dict_theme_styles[theme]['QFrame'])
        self.set_style(QLabel, style=self.dict_theme_styles[theme]['QLabel'])
        self.set_style(QListWidget, style=self.dict_theme_styles[theme]['QListWidget'])
        self.set_style(QTextEdit, style=self.dict_theme_styles[theme]['QTextEdit'])
        self.set_style(QPushButton, style=self.dict_theme_styles[theme]['QPushButton'])
        self.set_style(QComboBox, style=self.dict_theme_styles[theme]['QComboBox'])
        self.set_style(QLineEdit, style=self.dict_theme_styles[theme]['QLineEdit'])

        self.window_frame.setStyleSheet(self.dict_theme_styles[theme]['Window_frame'])

    def set_current_time(self):
        # TODO: DONE!  self.led_path_save.setText(f"{datetime.datetime.now():%Y_%m_%d_%H_%M_%S}.txt")
        self.led_path_save.setText(f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}")

    def write_to_file(self, data):
        filename = self.led_path_save.text()
        trajectory_text = data
        path = self.file_path
        if trajectory_text:
            write_to_txt_file(data, self.file_path, filename)

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi(self)

    def virtual_keyboard_edit_data(self, char):
        if self.focusWidget():
            widget_type = self.focusWidget().metaObject().className()
            selected_widget = self.focusWidget().objectName()

            print(widget_type)
            print(selected_widget)


            if widget_type == 'QLineEdit':
                old_char = self.focusWidget().text()

                if char == 'Bck':
                    if selected_widget != self.old_selected_widget:
                        self.focusWidget().clear()
                    else:
                        self.focusWidget().setText(old_char[:-1])
                    # self.focusWidget().setFont(self._tab_item_font)
                elif char in ['Shift', 'Ent', ':', ' ', '=', '<', '#', '>', '+']:
                    pass
                else:
                    self.focusWidget().setText(old_char + char)
                self.old_selected_widget = selected_widget
            else: self.old_selected_widget = None

            print(self.old_selected_widget)


class TrjUploadWindow(trj_upload_window.Ui_TrjUploadWindow, TrjSaveWindow):

    def walk_dir(self):
        self.lst_select.clear()
        self.lst_select.addItems(os.listdir(self.file_path))
        self.lst_select.sortItems()

    def read_from_file(self):
        data = read_from_txt_file(self.file_path, self.lst_select.currentItem().text())
        return data

    def delete_file(self):
        path = self.file_path
        filename = self.lst_select.currentItem().text()
        delete_txt_file(path, filename)
        self.walk_dir()

