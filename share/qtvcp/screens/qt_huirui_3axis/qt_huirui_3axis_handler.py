import os
import linuxcnc
import hal

from PyQt5 import QtCore, QtWidgets
from qtvcp.widgets.mdi_line import MDILine as MDI_WIDGET
from qtvcp.widgets.gcode_editor import GcodeEditor as GCODE
from qtvcp.widgets.origin_offsetview import OriginOffsetView as OFFSET_VIEW
from qtvcp.lib.keybindings import Keylookup
from qtvcp.core import Status, Action, Info
from qtvcp import logger
from qtvcp.widgets.stylesheeteditor import  StyleSheetEditor as SSE
#from qtvcp.lib.notify import Notify

LOG = logger.getLogger(__name__)
KEYBIND = Keylookup()
STAT = Status()
INFO = Info()
ACTION = Action()
#NOTIFY = Notify()

class HandlerClass:
    def __init__(self, halcomp, widgets, paths):
        self.w = widgets
        self.PATHS = paths
        self.hal = halcomp
        INIPATH = os.environ.get('INI_FILE_NAME', '/dev/null')
        self.inifile = linuxcnc.ini(INIPATH)
        self.STYLEEDITOR = SSE(widgets,paths)
        KEYBIND.add_call('Key_F12','on_keycall_F12')
        
        STAT.connect('state-on', self.machine_on)
        STAT.connect('state-off', self.machine_off)
        STAT.connect('hard-limits-tripped', self.hard_limit_tripped)
        STAT.connect("interp-idle", self.interp_idle_changed)
        STAT.connect("user-system-changed", self.user_system_changed)
        STAT.connect("file-loaded", self.file_loaded)
        STAT.connect("all-homed", self.all_homed)
        STAT.connect("not-all-homed", self.not_homed)

        # some global variables
        self.axis_list = INFO.AVAILABLE_AXES
        self.joint_list = INFO.AVAILABLE_JOINTS
        self.max_velocity = INFO.MAX_LINEAR_VELOCITY
        self.system_list = ["G53","G54","G55","G56","G57","G58","G59","G59.1","G59.2","G59.3"]
        self.home_location_x = self.inifile.find('JOINT_0', 'HOME')
        self.home_location_y = self.inifile.find('JOINT_1', 'HOME')
        self.home_location_z = self.inifile.find('JOINT_2', 'HOME')
        self.homed = False
        self.start_line = 0
        self.program_length = 0
        self.slow_jog_factor = 10
        self.reload_tool = 0
        self.last_loaded_program = ""
        self.onoff_list = ["widget_controls", "Program_frame", "DRO_frame"]

    def initialized__(self):
        #self.init_pins()
        self.init_preferences()
        self.init_widgets()
        self.init_locations()

    # initialize DRO style
        for i in map(str.lower, self.axis_list):
            self.w["dro_axis_{}".format(i)].setStyle(self.w["dro_axis_{}".format(i)].style())

    #############################
    # SPECIAL FUNCTIONS SECTION #
    #############################
    #def init_pins(self):
        # these pins are needed so that the touchoff subroutine can read the variables
        #self.hal.newpin("touch_height", hal.HAL_FLOAT, hal.HAL_OUT)
        
    def init_preferences(self):
        if self.w.PREFS_:
            self.last_loaded_program = self.w.PREFS_.getpref('last_file_path', None, str,'BOOK_KEEPING')
            temp1 = self.w.PREFS_.getpref('Reload program', False, bool,'CUSTOM_FORM_ENTRIES')
        else:
            temp1 = False
            self.add_alarm("No preference file found")
        self.w.checkBox_reload_program.setChecked(temp1)

    def init_widgets(self):
        #laser power set
        MAX_POWER = int(self.inifile.find('LASER', 'POWER')) or 500
        FIX_VEL_1 = int(self.inifile.find('LASER', 'FIX_VEL_1')) or 100
        FIX_VEL_2 = int(self.inifile.find('LASER', 'FIX_VEL_2')) or 200
        FIX_VEL_3 = int(self.inifile.find('LASER', 'FIX_VEL_3')) or 400
        self.w.label_max_power.setText(str(MAX_POWER))
        self.w.slider_power.setMaximum(MAX_POWER)
        self.w.slider_power.setValue(MAX_POWER/2)
        compare = lambda v,min,max : (v>min) and (v<max)
        if compare(FIX_VEL_1,0,MAX_POWER) and compare(FIX_VEL_2,0,MAX_POWER) and compare(FIX_VEL_3,0,MAX_POWER):
            self.w.btn_power_1.setText(str(FIX_VEL_1))
            self.w.btn_power_2.setText(str(FIX_VEL_2))
            self.w.btn_power_3.setText(str(FIX_VEL_3))
        else:
            self.w.btn_power_1.setText(str(0))
            self.w.btn_power_2.setText(str(MAX_POWER/2))
            self.w.btn_power_3.setText(str(MAX_POWER))
        #powder vel set
        MAX_POWER = int(self.inifile.find('POWDER', 'MAX_VEL')) or 29
        FIX_VEL_1 = float(self.inifile.find('POWDER', 'FIX_VEL_1')) or 1
        FIX_VEL_2 = float(self.inifile.find('POWDER', 'FIX_VEL_2')) or 5
        FIX_VEL_3 = float(self.inifile.find('POWDER', 'FIX_VEL_3')) or 10
        POWDER_NUM = int(self.inifile.find('POWDER', 'NUM')) or 1
        if POWDER_NUM > 26:
            POWDER_NUM = 26
        self.w.label_max_powder_vel.setText(str(MAX_POWER))
        self.w.slider_powder_vel.setMaximum(MAX_POWER*10)
        self.w.slider_powder_vel.setValue(MAX_POWER / 2)
        if compare(FIX_VEL_1, 0, MAX_POWER) and compare(FIX_VEL_2, 0, MAX_POWER) and compare(FIX_VEL_3, 0,MAX_POWER):
            self.w.btn_powder_vel_1.setText(str(FIX_VEL_1))
            self.w.btn_powder_vel_2.setText(str(FIX_VEL_2))
            self.w.btn_powder_vel_3.setText(str(FIX_VEL_3))
        else:
            self.w.btn_powder_vel_1.setText(str(0))
            self.w.btn_powder_vel_2.setText(str(MAX_POWER / 2))
            self.w.btn_powder_vel_3.setText(str(MAX_POWER))
        for index in range(POWDER_NUM):
            self.w.comboBox_powder_num.addItem("PDR " + str(index + 1))
        #other set
        self.w.main_tab_widget.setCurrentIndex(0)
        self.w.slider_jog.setMaximum(self.max_velocity * 60)
        self.w.slider_jog.setValue(INFO.DEFAULT_LINEAR_JOG_VEL)
        self.w.slider_maxv.setMaximum(self.max_velocity * 60)
        self.w.slider_maxv.setValue(self.max_velocity * 60)
        self.w.slider_feed.setMaximum(INFO.MAX_FEED_OVERRIDE)
        self.w.slider_feed.setValue(100)
        self.w.slider_rapid.setMaximum(100)
        self.w.slider_rapid.setValue(100)
        self.w.checkBox_override_limits.setChecked(False)
        self.w.checkBox_override_limits.setEnabled(False)
        self.w.filemanager.show()
        self.w.gcode_editor.hide()
        self.w.btn_from_line.setEnabled(False)
       
    def init_locations(self):
        self.w.lbl_maxv.setText(str(self.max_velocity * 60))
        # home location
        if not self.home_location_x or not self.home_location_y or not self.home_location_z:
            self.w.btn_go_home.setEnabled(False)
            self.w.groupBox_home.hide()
            self.w.lbl_no_home.show()
            self.add_alarm("No valid home location found")
        else:
            self.w.lbl_home_x.setText(self.home_location_x)
            self.w.lbl_home_y.setText(self.home_location_y)
            self.w.lbl_no_home.hide()

    def processed_key_event__(self,receiver,event,is_pressed,key,code,shift,cntrl):
        # when typing in MDI, we don't want keybinding to call functions
        # so we catch and process the events directly.
        # We do want ESC, F1 and F2 to call keybinding functions though
        if code not in(QtCore.Qt.Key_Escape,QtCore.Qt.Key_F1 ,QtCore.Qt.Key_F2):
#                    QtCore.Qt.Key_F3,QtCore.Qt.Key_F4,QtCore.Qt.Key_F5):

            # search for the top widget of whatever widget received the event
            # then check if it's one we want the keypress events to go to
            flag = False
            receiver2 = receiver
            while receiver2 is not None and not flag:
                if isinstance(receiver2, QtWidgets.QDialog):
                    flag = True
                    break
                if isinstance(receiver2, QtWidgets.QLineEdit):
                    flag = True
                    break
                if isinstance(receiver2, MDI_WIDGET):
                    flag = True
                    break
                if isinstance(receiver2, GCODE):
                    flag = True
                    break
                if isinstance(receiver2, TOOL_TABLE):
                    flag = True
                    break
                if isinstance(receiver2, OFFSET_VIEW):
                    flag = True
                    break
                receiver2 = receiver2.parent()

            if flag:
                if isinstance(receiver2, GCODE):
                    # if in manual do our keybindings - otherwise
                    # send events to gcode widget
                    if STAT.is_man_mode() == False:
                        if is_pressed:
                            receiver.keyPressEvent(event)
                            event.accept()
                        return True
                elif is_pressed:
                    receiver.keyPressEvent(event)
                    event.accept()
                    return True
                else:
                    event.accept()
                    return True

        # ok if we got here then try keybindings
        try:
            return KEYBIND.call(self,event,is_pressed,shift,cntrl)
        except NameError as e:
            self.add_alarm('Exception in KEYBINDING: {}'.format (e))
        except Exception as e:
            LOG.error('Exception in KEYBINDING:', exc_info=e)
            print 'Error in, or no function for: %s in handler file for-%s'%(KEYBIND.convert(event),key)
            return False

    #########################
    # CALLBACKS FROM STATUS #
    #########################
    def machine_on(self, obj):
        for widget in self.onoff_list:
            self.w[widget].setEnabled(True)

    def machine_off(self, obj):
        for widget in self.onoff_list:
            self.w[widget].setEnabled(False)

    def gcode_line_selected(self, obj, data):
        if self.w.btn_from_line.isChecked():
            self.start_line = data
            self.w.btn_start.setText("START FROM {}".format(data))

    def interp_idle_changed(self, obj):
        self.start_line = 0
        self.w.btn_start.setText("START FROM 0")
        
    def user_system_changed(self, obj, data):
        sys = self.system_list[int(data)]
        self.w.actionbutton_rel.setText(sys)

    def file_loaded(self, obj, filename):
        if filename is not None:
            self.w.progressBar.setValue(0)
            self.last_loaded_program = filename
            fileobject = file(filename, 'r')
            lines = fileobject.readlines()
            fileobject.close()
            self.program_length = len(lines)
            self.start_line = 0
            self.w.btn_from_line.setEnabled(True)
            self.w.btn_start.setText("START FROM 0")
        else:
            self.w.btn_from_line.setEnabled(False)
            self.add_alarm("Filename not valid")

    def all_homed(self, obj):
        self.homed = True
        self.w.actionbutton_view_p.click()
        for i in map(str.lower, self.axis_list):
            self.w["dro_axis_{}".format(i)].setProperty('homed', True)
            self.w["dro_axis_{}".format(i)].setStyle(self.w["dro_axis_{}".format(i)].style())
        if self.last_loaded_program and self.w.checkBox_reload_program.checkState():
            ACTION.OPEN_PROGRAM(self.last_loaded_program)
            self.w.filemanager.updateDirectoryView(self.last_loaded_program)

    def not_homed(self, obj, data):
        self.homed = False
        for i in map(str.lower, self.axis_list):
            self.w["dro_axis_{}".format(i)].setProperty('homed', False)
            self.w["dro_axis_{}".format(i)].setStyle(self.w["dro_axis_{}".format(i)].style())

    def hard_limit_tripped(self, obj, tripped, list_of_tripped):
        self.w.checkBox_override_limits.setEnabled(tripped)
        if not tripped:
            self.w.checkBox_override_limits.setChecked(False)
    
    #######################
    # CALLBACKS FROM FORM #
    #######################
    def tool_widgets_enable(self,state):
        self.w.btn_laser_on.setEnabled(state)
        self.w.btn_gas_on.setEnabled(state)
        self.w.btn_laser_en.setEnabled(state)
        self.w.btn_light_on.setEnabled(state)
        self.w.btn_powder_on.setEnabled(state)
        self.w.comboBox_powder_num.setEnabled(state)

    # program frame
    def btn_start_clicked(self):
        if not STAT.is_auto_mode():
            return
        self.w.btn_from_line.setChecked(False)
        self.tool_widgets_enable(False)
        self.add_alarm("Started program from line {}".format(self.start_line))
        ACTION.RUN(self.start_line)

    def btn_abort_clicked(self):
        self.tool_widgets_enable(True)

    def btn_reload_file_clicked(self):
        if self.last_loaded_program:
            self.w.progressBar.setValue(0)
            ACTION.OPEN_PROGRAM(self.last_loaded_program)

    def btn_from_line_clicked(self, state):
        if state is False:
            self.start_line = 0
            self.w.btn_start.setText("START FROM 0")

    # tool slot
    def btn_laser_on_clicked(self,state):
        if not STAT.is_mdi_mode():
            return
        if state is False:
            ACTION.CALL_MDI_WAIT("M115")
        else:
            ACTION.CALL_MDI_WAIT("M105 P{}".format(self.w.slider_power.value()))

    def btn_laser_enable_clicked(self,state):
        if state is False:
            ACTION.CALL_MDI_WAIT("M114")
        else:
            ACTION.CALL_MDI_WAIT("M104")

    def btn_gas_on_clicked(self,state):
        if state is False:
            ACTION.CALL_MDI_WAIT("M116")
        else:
            ACTION.CALL_MDI_WAIT("M106")

    def btn_light_on_clicked(self,state):
        if state is False:
            ACTION.CALL_MDI_WAIT("M117")
        else:
            ACTION.CALL_MDI_WAIT("M107")

    def btn_powder_on_clicked(self,state):
        if state is False:
            ACTION.CALL_MDI_WAIT("M118 P{}".format(self.w.comboBox_powder_num.currentIndex()+1))
        else:
            ACTION.CALL_MDI_WAIT("M108 P{} Q{}".format(self.w.comboBox_powder_num.currentIndex()+1, float(self.w.slider_powder_vel.value())/10))

    # override frame
    def btn_slow_clicked(self, state):
        if state:
            current = self.w.slider_jog.value()
            self.w.btn_slow.setText("SLOW")
            self.w.slider_jog.setMaximum(self.max_velocity * 60 / self.slow_jog_factor)
            self.w.slider_jog.setValue(current / self.slow_jog_factor)
        else:
            current = self.w.slider_jog.value()
            self.w.btn_slow.setText("FAST")
            self.w.slider_jog.setMaximum(self.max_velocity * 60)
            self.w.slider_jog.setValue(current * self.slow_jog_factor)

    def btn_maxv_max_clicked(self):
        self.w.slider_maxv.setValue(self.max_velocity * 60)

    def btn_power_fix_1(self):
        self.w.slider_power.setValue(int(self.w.btn_power_1.text()))

    def btn_power_fix_2(self):
        self.w.slider_power.setValue(int(self.w.btn_power_2.text()))

    def btn_power_fix_3(self):
        self.w.slider_power.setValue(int(self.w.btn_power_3.text()))

    def btn_powder_vel_fix_1(self):
        self.w.slider_powder_vel.setValue(float(self.w.btn_powder_vel_1.text())*10)

    def btn_powder_vel_fix_2(self):
        self.w.slider_powder_vel.setValue(float(self.w.btn_powder_vel_2.text())*10)

    def btn_powder_vel_fix_3(self):
        self.w.slider_powder_vel.setValue(float(self.w.btn_powder_vel_3.text())*10)

    def sld_powder_vel_changed(self,vel):
        self.w.label_powder_vel.setText(str(float(vel)/10))

    # file tab
    def btn_gcode_edit_clicked(self, state):
        if not STAT.is_on_and_idle():
            return
        for x in ["load", "next", "prev"]:
            self.w["btn_file_{}".format(x)].setEnabled(not state)
        if state:
            self.w.filemanager.hide()
            self.w.gcode_editor.show()
            self.w.gcode_editor.editMode()
        else:
            self.w.filemanager.show()
            self.w.gcode_editor.hide()
            self.w.gcode_editor.readOnlyMode()

    # alarm tab
    def btn_clear_alarms_clicked(self):
        STAT.emit('update-machine-log', None, 'DELETE')

    def btn_save_alarms_clicked(self):
        text = self.w.machinelog.toPlainText()
        filename = self.w.lbl_clock.text().encode('utf-8')
        filename = 'alarms_' + filename.replace(' ','_') + '.txt'
        with open(filename, 'w') as f:
            f.write(text)

    def chk_override_limits(self, state):
        if state:
            print("Override limits set")
            ACTION.SET_LIMITS_OVERRIDE()
        else:
            print("Override limits not set")

        
    #####################
    # GENERAL FUNCTIONS #
    #####################

    def kb_jog(self, state, joint, direction, fast = False, linear = True):
        if not STAT.is_man_mode() or not STAT.machine_is_on():
            return
        if linear:
            distance = STAT.get_jog_increment()
            rate = STAT.get_jograte()/60
        else:
            distance = STAT.get_jog_increment_angular()
            rate = STAT.get_jograte_angular()/60
        if state:
            if fast:
                rate = rate * 2
            ACTION.JOG(joint, direction, rate, distance)
        else:
            ACTION.JOG(joint, 0, 0, 0)

    def add_alarm(self, message):
        STAT.emit('update-machine-log', message, 'TIME')

    def alarm_added(self):
        self.w.led_alarm.setState(True)

    def tab_changed(self, index):
        self.w.btn_gcode_edit.setChecked(False)
        self.btn_gcode_edit_clicked(False)
        if index == 4:
            self.w.led_alarm.setState(False)

    #####################
    # KEY BINDING CALLS #
    #####################

    def on_keycall_ESTOP(self,event,state,shift,cntrl):
        if state:
            ACTION.SET_ESTOP_STATE(True)

    def on_keycall_POWER(self,event,state,shift,cntrl):
        if state:
            ACTION.SET_MACHINE_STATE(False)

    def on_keycall_ABORT(self,event,state,shift,cntrl):
        if state:
            ACTION.ABORT()

    def on_keycall_HOME(self,event,state,shift,cntrl):
        if state and self.homed is False:
            ACTION.SET_MACHINE_HOMING(-1)

    def on_keycall_XPOS(self,event,state,shift,cntrl):
        self.kb_jog(state, 0, 1, shift)

    def on_keycall_XNEG(self,event,state,shift,cntrl):
        self.kb_jog(state, 0, -1, shift)

    def on_keycall_YPOS(self,event,state,shift,cntrl):
        self.kb_jog(state, 1, 1, shift)

    def on_keycall_YNEG(self,event,state,shift,cntrl):
        self.kb_jog(state, 1, -1, shift)

    def on_keycall_ZPOS(self,event,state,shift,cntrl):
        self.kb_jog(state, 2, 1, shift)

    def on_keycall_ZNEG(self,event,state,shift,cntrl):
        self.kb_jog(state, 2, -1, shift)
    
    def on_keycall_F12(self,event,state,shift,cntrl):
        if state:
            self.STYLEEDITOR.load_dialog()

    ###########################
    # **** closing event **** #
    ###########################
# items to save in preference file
    def closing_cleanup__(self):
        if self.w.PREFS_:
            self.w.PREFS_.putpref('Reload program', self.w.checkBox_reload_program.checkState(), bool, 'CUSTOM_FORM_ENTRIES')

    ##############################
    # required class boiler code #
    ##############################
    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, value):
        return setattr(self, item, value)

################################
# required handler boiler code #
################################

def get_handlers(halcomp, widgets, paths):
    return [HandlerClass(halcomp, widgets, paths)]
