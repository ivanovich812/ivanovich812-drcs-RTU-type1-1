'''
Это общий класс для всех nodes, импортируем класс, создаем экземпляр и используем методы для записи, чтения в БД
'''
from time import sleep

from sqlalchemy import create_engine, String, Column, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

class SQLClient:
    engine = create_engine("postgresql+psycopg2://postgres:1@localhost/rtu")
    Base = declarative_base()


    # Здесь создавать таблицы
    class J_Points(Base):
        __tablename__ = 'joint_points'
        name = Column(String(100), primary_key=True, nullable=False, unique=True)
        axis_1 = Column(Float())
        axis_2 = Column(Float())
        axis_3 = Column(Float())
        axis_4 = Column(Float())
        axis_5 = Column(Float())
        axis_6 = Column(Float())

    class FC_Axes_Monitor(Base):
        __tablename__ = 'fc_axes_monitor'
        var = Column(String(100), primary_key=True, nullable=False)
        axis_1_var = Column(String(100), nullable=False, unique=True)
        axis_1_value = Column(Float())
        axis_2_var = Column(String(100), nullable=False, unique=True)
        axis_2_value = Column(Float())
        axis_3_var = Column(String(100), nullable=False, unique=True)
        axis_3_value = Column(Float())
        axis_4_var = Column(String(100), nullable=False, unique=True)
        axis_4_value = Column(Float())
        axis_5_var = Column(String(100), nullable=False, unique=True)
        axis_5_value = Column(Float())
        axis_6_var = Column(String(100), nullable=False, unique=True)
        axis_6_value = Column(Float())

    class PLC_IO_Monitor_Bool(Base):
        __tablename__ = 'plc_io_monitor_bool'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Boolean())

    class PLC_IO_Monitor_Int(Base):
        __tablename__ = 'plc_io_monitor_int'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Integer())

    class PLC_Tasks_Bool(Base):
        __tablename__ = 'plc_tasks_bool'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Boolean())

    class PLC_Tasks_Int(Base):
        __tablename__ = 'plc_tasks_int'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Integer())

    class Raw_Positions(Base):
        __tablename__ = 'raw_positions'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Integer())

    class RTC_Control_Bool(Base):
        __tablename__ = 'rtc_control_bool'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Boolean())

    class RTC_Control_Int(Base):
        __tablename__ = 'rtc_control_int'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Integer())

    class Scope_Signals_Bool(Base):
        __tablename__ = 'scope_signals_bool'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Boolean())

    class Scope_Signals_Int(Base):
        __tablename__ = 'scope_signals_int'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Integer())

    class Scope_Signals_Float(Base):
        __tablename__ = 'scope_signals_float'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Float())

    class MdbRTU_IO_Monitor_Int(Base):
        __tablename__ = 'mdbrtu_io_monitor_int'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Integer())

    class MdbRTU_IO_Monitor_Bool(Base):
        __tablename__ = 'mdbrtu_io_monitor_bool'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Boolean())

    class MdbRTU_Tasks_Bool(Base):
        __tablename__ = 'mdbrtu_tasks_bool'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Boolean())

    class MdbRTU_Tasks_Int(Base):
        __tablename__ = 'mdbrtu_tasks_int'
        var = Column(String(100), primary_key=True, nullable=False)
        value = Column(Integer())



    # Base.metadata.create_all(engine)

    def __init__(self, logger, name):
        # self.session = Session(bind=SQLClient.engine)
        self.r_session = Session(bind=SQLClient.engine)
        self.w_session = Session(bind=SQLClient.engine)
        self._logger = logger

        try:
            SQLClient.Base.metadata.create_all(SQLClient.engine)
            self._logger.event(f'debug', f'SQL Alchemy.{name}: Connection is succesful!')
        except Exception as e:
            self._logger.event(f'error', f'SQL ALchemy.{name}: Connection error: {e}.')


    def add_to_j_points(self, key, value):
        new_J_Points = self.J_Points(
            name=key,
            axis_1=value[0],
            axis_2=value[1],
            axis_3=value[2],
            axis_4=value[3],
            axis_5=value[4],
            axis_6=value[5]
        )

        query = self.w_session.query(self.J_Points).where(self.J_Points.name == new_J_Points.name)

        if query.first() is None:
            self.w_session.add(new_J_Points)
        else:
            query.update(
                {
                    self.J_Points.axis_1: value[0],
                    self.J_Points.axis_2: value[1],
                    self.J_Points.axis_3: value[2],
                    self.J_Points.axis_4: value[3],
                    self.J_Points.axis_5: value[4],
                    self.J_Points.axis_6: value[5]
                },
                synchronize_session = False)
        self.w_session.commit()

    def read_j_points(self):
        q = self.r_session.query(self.J_Points)
        self.r_session.commit()
        data = {}
        for c in q:
            data[c.name] = [c.axis_1, c.axis_2, c.axis_3, c.axis_4, c.axis_5, c.axis_6]
        return data

    def delete_from_j_points(self, key):
        try:
            query = self.w_session.query(self.J_Points).filter(self.J_Points.name == key).one()
            self.w_session.delete(query)
            self.w_session.commit()
        except:
            print(f"There isn't key: '{key}' in the 'joint_points' table")

    def read_fc_axes_monitor(self):
        try:
            q = self.r_session.query(self.FC_Axes_Monitor)
            self.r_session.commit()
            data = {}
            for c in q:
                data[c.var] = {
                    c.axis_1_var: c.axis_1_value,
                    c.axis_2_var: c.axis_2_value,
                    c.axis_3_var: c.axis_3_value,
                    c.axis_4_var: c.axis_4_value,
                    c.axis_5_var: c.axis_5_value,
                    c.axis_6_var: c.axis_6_value,
                }

            # print(data)
            return data

        except:
            self.r_session.rollback()
            print("Ошибка чтения таблицы SQL 'fc_axes_monitor'")

    # def write_fc_axes_monitor(self, data):
    #
    #     # print(data)
    #
    #     try:
    #         self.session.query(self.FC_Axes_Monitor).delete()
    #         self.session.commit()
    #
    #         data_list = []
    #         for key, val in data.items():
    #             # if val is None:
    #             #     break
    #             temp = {}
    #             temp['var'] = key
    #             temp['axis_1_var'] = 'axis_1_' + key
    #             temp['axis_1_value'] = val['axis_1_' + key]
    #             temp['axis_2_var'] = 'axis_2_' + key
    #             temp['axis_2_value'] = val['axis_2_' + key]
    #             temp['axis_3_var'] = 'axis_3_' + key
    #             temp['axis_3_value'] = val['axis_3_' + key]
    #             temp['axis_4_var'] = 'axis_4_' + key
    #             temp['axis_4_value'] = val['axis_4_' + key]
    #             temp['axis_5_var'] = 'axis_5_' + key
    #             temp['axis_5_value'] = val['axis_5_' + key]
    #             temp['axis_6_var'] = 'axis_6_' + key
    #             temp['axis_6_value'] = val['axis_6_' + key]
    #             data_list.append(temp)
    #
    #         # print('RECORD ACCEMBLED!!!')
    #         # for i in data_list:
    #         #     for g in i:
    #         #         print (g)
    #
    #         obj_list = []
    #         # Loop through each object in the list
    #         for record in data_list:
    #
    #             # print (record)
    #
    #             # for key,value in record.items():
    #             #     print (key, ':', value)
    #
    #             data_obj = self.FC_Axes_Monitor(**record)
    #             obj_list.append(data_obj)
    #
    #         # print(obj_list)
    #
    #         self.session.add_all(obj_list)
    #         self.session.commit()
    #
    #     except:
    #         self.session.rollback()
    #         print("Ошибка записи таблицы SQL 'fc_axes_monitor'")
    #
    # # def write_plc_io_monitor(self, data):
    # #     try:
    # #         self.session.query(self.PLC_IO_Monitor_Bool).delete()
    # #         self.session.query(self.PLC_IO_Monitor_Int).delete()
    # #         self.session.commit()
    # #
    # #         for key, val in data.items():
    # #             if isinstance(val, bool):
    # #                 np = self.PLC_IO_Monitor_Bool(var=key, value=val)
    # #                 self.session.add(np)
    # #             elif isinstance(val, int):
    # #                 np = self.PLC_IO_Monitor_Int(var=key, value=val)
    # #                 self.session.add(np)
    # #
    # #         self.session.commit()
    # #     except:
    # #         self.session.rollback()
    # #         print("Ошибка записи таблицы SQL 'plc_io_monitor'")

    def write_fc_axes_monitor(self, data):
        # print(data)
        try:
            for key, val in data.items():
                temp = {}
                temp['var'] = key
                temp['axis_1_var'] = 'axis_1_' + key
                temp['axis_1_value'] = val['axis_1_' + key]
                temp['axis_2_var'] = 'axis_2_' + key
                temp['axis_2_value'] = val['axis_2_' + key]
                temp['axis_3_var'] = 'axis_3_' + key
                temp['axis_3_value'] = val['axis_3_' + key]
                temp['axis_4_var'] = 'axis_4_' + key
                temp['axis_4_value'] = val['axis_4_' + key]
                temp['axis_5_var'] = 'axis_5_' + key
                temp['axis_5_value'] = val['axis_5_' + key]
                temp['axis_6_var'] = 'axis_6_' + key
                temp['axis_6_value'] = val['axis_6_' + key]

                query = self.w_session.query(self.FC_Axes_Monitor).filter(self.FC_Axes_Monitor.var == key)
                row = query.first()
                if row:
                    row.axis_1_value = temp['axis_1_value']
                    row.axis_2_value = temp['axis_2_value']
                    row.axis_3_value = temp['axis_3_value']
                    row.axis_4_value = temp['axis_4_value']
                    row.axis_5_value = temp['axis_5_value']
                    row.axis_6_value = temp['axis_6_value']

                else:
                    np = self.FC_Axes_Monitor(
                        var = key,
                        axis_1_var = temp['axis_1_var'],
                        axis_1_value = temp['axis_1_value'],
                        axis_2_var=temp['axis_2_var'],
                        axis_2_value=temp['axis_2_value'],
                        axis_3_var=temp['axis_3_var'],
                        axis_3_value=temp['axis_3_value'],
                        axis_4_var=temp['axis_4_var'],
                        axis_4_value=temp['axis_4_value'],
                        axis_5_var=temp['axis_5_var'],
                        axis_5_value=temp['axis_5_value'],
                        axis_6_var=temp['axis_6_var'],
                        axis_6_value=temp['axis_6_value']
                        )
                    self.w_session.add(np)

            self.w_session.commit()

        except:
            self.w_session.rollback()
            print("Ошибка записи таблицы SQL 'fc_axes_monitor'")

    # def write_plc_io_monitor(self, data):
    #     try:
    #         self.session.query(self.PLC_IO_Monitor_Bool).delete()
    #         self.session.query(self.PLC_IO_Monitor_Int).delete()
    #         self.session.commit()
    #
    #         for key, val in data.items():
    #             if isinstance(val, bool):
    #                 np = self.PLC_IO_Monitor_Bool(var=key, value=val)
    #                 self.session.add(np)
    #             elif isinstance(val, int):
    #                 np = self.PLC_IO_Monitor_Int(var=key, value=val)
    #                 self.session.add(np)
    #
    #         self.session.commit()
    #     except:
    #         self.session.rollback()
    #         print("Ошибка записи таблицы SQL 'plc_io_monitor'")

    def write_plc_io_monitor(self, data):
        # print('')
        # print('WRITE: ', data)
        try:
            for key, val in data.items():
                if isinstance(val, bool):

                    bool_query = self.w_session.query(self.PLC_IO_Monitor_Bool).filter(self.PLC_IO_Monitor_Bool.var == key)
                    bool_row = bool_query.first()
                    if bool_row:
                        bool_row.value = val
                    else:
                        np = self.PLC_IO_Monitor_Bool(var=key, value=val)
                        self.w_session.add(np)
                elif isinstance(val, int):

                    int_query = self.w_session.query(self.PLC_IO_Monitor_Int).filter(self.PLC_IO_Monitor_Int.var == key)
                    int_row = int_query.first()
                    if int_row:
                        int_row.value = val
                    else:
                        np = self.PLC_IO_Monitor_Int(var=key, value=val)
                        self.w_session.add(np)

            self.w_session.commit()
        except:
            self.w_session.rollback()
            print("Ошибка записи таблицы SQL 'plc_io_monitor'")

    def read_plc_io_monitor(self):
        try:
            q_bool = self.r_session.query(self.PLC_IO_Monitor_Bool).order_by(self.PLC_IO_Monitor_Bool.var.desc())
            q_int = self.r_session.query(self.PLC_IO_Monitor_Int).order_by(self.PLC_IO_Monitor_Int.var.desc())

            data_bool = {}
            for c in q_bool:
                data_bool[c.var] = c.value


            data_int = {}
            for c in q_int:
                data_int[c.var] = c.value

            # print('data_bool: ', data_bool)
            # print('data_int: ', data_int)
            data = {**data_bool, **data_int}
            # print('data: ', data)

            self.r_session.commit()

            # print('READ: ', data)
            return data


        except:
            self.r_session.rollback()
            print("Ошибка чтения таблицы SQL 'plc_io_monitor'")

    # def write_plc_tasks(self, data):
    #
    #     self.w_session.query(self.PLC_Tasks_Bool).delete()
    #     self.w_session.query(self.PLC_Tasks_Int).delete()
    #     self.w_session.commit()
    #
    #     for key, val in data.items():
    #         if isinstance(val, bool):
    #             np = self.PLC_Tasks_Bool(var=key, value=val)
    #             self.w_session.add(np)
    #         elif isinstance(val, int):
    #             np = self.PLC_Tasks_Int(var=key, value=val)
    #             self.w_session.add(np)
    #
    #     self.w_session.commit()

    def write_plc_tasks(self, data):

        for key, val in data.items():
            if isinstance(val, bool):
                # np = self.PLC_Tasks_Bool(var=key, value=val)
                # self.w_session.add(np)

                bool_query = self.w_session.query(self.PLC_Tasks_Bool).filter(self.PLC_Tasks_Bool.var == key)
                bool_row = bool_query.first()
                if bool_row:
                    bool_row.value = val
                else:
                    np = self.PLC_Tasks_Bool(var=key, value=val)
                    self.w_session.add(np)

            elif isinstance(val, int):
                # np = self.PLC_Tasks_Int(var=key, value=val)
                # self.w_session.add(np)

                int_query = self.w_session.query(self.PLC_Tasks_Int).filter(self.PLC_Tasks_Int.var == key)
                int_row = int_query.first()
                if int_row:
                    int_row.value = val
                else:
                    np = self.PLC_IO_Monitor_Int(var=key, value=val)
                    self.w_session.add(np)

        self.w_session.commit()

    def read_plc_tasks(self):
        q_bool = self.r_session.query(self.PLC_Tasks_Bool)
        q_int = self.r_session.query(self.PLC_Tasks_Int)

        data_bool = {}
        for c in q_bool:
            data_bool[c.var] = c.value

        data_int = {}
        for c in q_int:
            data_int[c.var] = c.value

        data = {**data_bool, **data_int}

        self.r_session.commit()

        return data

    def add_to_plc_tasks(self, key, value):

        if isinstance(value, bool):
            new_PLC_Tasks_Bool = self.PLC_Tasks_Bool(
                var=key,
                value=value
            )

            query = self.w_session.query(self.PLC_Tasks_Bool).where(self.PLC_Tasks_Bool.var == new_PLC_Tasks_Bool.var)

            if query.first() is None:
                self.w_session.add(new_PLC_Tasks_Bool)
            else:
                query.update(
                    {
                        self.PLC_Tasks_Bool.value: value
                    },
                    synchronize_session = False)

        elif isinstance(value, int):
            new_PLC_Tasks_Int = self.PLC_Tasks_Int(
                var=key,
                value=value
            )

            query = self.w_session.query(self.PLC_Tasks_Int).where(self.PLC_Tasks_Int.var == new_PLC_Tasks_Int.var)

            if query.first() is None:
                self.w_session.add(new_PLC_Tasks_Int)
            else:
                query.update(
                    {
                        self.PLC_Tasks_Int.value: value
                    },
                    synchronize_session=False)

        else:
            print ("There isn't such type of variable")
            self.w_session.rollback()

        self.w_session.commit()

    def add_to_raw_positions(self, key, value):

        new_Raw_Positions = self.Raw_Positions(
            var=key,
            value=value
        )

        query = self.w_session.query(self.Raw_Positions).where(self.Raw_Positions.var == new_Raw_Positions.var)

        if query.first() is None:
            self.w_session.add(new_Raw_Positions)
        else:
            query.update(
                {
                    self.Raw_Positions.value: value
                },
                synchronize_session=False)

        self.w_session.commit()

    def add_to_rtc_control(self, key, value):

        if isinstance(value, bool):
            new_RTC_Control_Bool = self.RTC_Control_Bool(
                var=key,
                value=value
            )

            query = self.w_session.query(self.RTC_Control_Bool).where(self.RTC_Control_Bool.var == new_RTC_Control_Bool.var)

            if query.first() is None:
                self.w_session.add(new_RTC_Control_Bool)
            else:
                query.update(
                    {
                        self.RTC_Control_Bool.value: value
                    },
                    synchronize_session = False)

        elif isinstance(value, int):
            new_RTC_Control_Int = self.RTC_Control_Int(
                var=key,
                value=value
            )

            query = self.w_session.query(self.RTC_Control_Int).where(self.RTC_Control_Int.var == new_RTC_Control_Int.var)

            if query.first() is None:
                self.w_session.add(new_RTC_Control_Int)
            else:
                query.update(
                    {
                        self.RTC_Control_Int.value: value
                    },
                    synchronize_session=False)

        else:
            print ("There isn't such type of variable")
            self.w_session.rollback()

        self.w_session.commit()

    def read_rtc_control(self):
        q_bool = self.r_session.query(self.RTC_Control_Bool)
        q_int = self.r_session.query(self.RTC_Control_Int)

        data_bool = {}
        for c in q_bool:
            data_bool[c.var] = c.value

        data_int = {}
        for c in q_int:
            data_int[c.var] = c.value

        data = {**data_bool, **data_int}

        self.r_session.commit()

        return data

    def write_scope_signals(self, data):
        try:
            for key, val in data.items():
                if isinstance(val, bool):

                    bool_query = self.w_session.query(self.Scope_Signals_Bool).filter(self.Scope_Signals_Bool.var == key)
                    bool_row = bool_query.first()
                    if bool_row:
                        bool_row.value = val
                    else:
                        np = self.Scope_Signals_Bool(var=key, value=val)
                        self.w_session.add(np)
                elif isinstance(val, int):

                    int_query = self.w_session.query(self.Scope_Signals_Int).filter(self.Scope_Signals_Int.var == key)
                    int_row = int_query.first()
                    if int_row:
                        int_row.value = val
                    else:
                        np = self.Scope_Signals_Int(var=key, value=val)
                        self.w_session.add(np)
                elif isinstance(val, float):

                    float_query = self.w_session.query(self.Scope_Signals_Float).filter(self.Scope_Signals_Float.var == key)
                    float_row = float_query.first()
                    if float_row:
                        float_row.value = val
                    else:
                        np = self.Scope_Signals_Float(var=key, value=val)
                        self.w_session.add(np)

            self.w_session.commit()
            self.w_session.commit()

        except:
            self.w_session.rollback()
            print("Ошибка записи таблицы SQL 'scope_signals'")

    def read_scope_signals(self):
        try:
            q_bool = self.r_session.query(self.Scope_Signals_Bool)
            q_int = self.r_session.query(self.Scope_Signals_Int)
            q_float = self.r_session.query(self.Scope_Signals_Float)

            data_bool = {}
            for c in q_bool:
                data_bool[c.var] = c.value

            data_int = {}
            for c in q_int:
                data_int[c.var] = c.value

            data_float = {}
            for c in q_float:
                data_float[c.var] = c.value

            data = {**data_bool, **data_int, **data_float}

            self.r_session.commit()
            return data

        except:
            self.r_session.rollback()
            print("Ошибка чтения таблицы SQL 'scope_signals'")

    def read_mdbrtu_io_monitor(self):
        try:
            q_bool = self.r_session.query(self.MdbRTU_IO_Monitor_Bool).order_by(self.MdbRTU_IO_Monitor_Bool.var.desc())
            q_int = self.r_session.query(self.MdbRTU_IO_Monitor_Int).order_by(self.MdbRTU_IO_Monitor_Int.var.desc())

            data_bool = {}
            for c in q_bool:
                data_bool[c.var] = c.value


            data_int = {}
            for c in q_int:
                data_int[c.var] = c.value

            # print('data_bool: ', data_bool)
            # print('data_int: ', data_int)
            data = {**data_bool, **data_int}
            # print('data: ', data)

            self.r_session.commit()

            # print('READ: ', data)
            return data


        except:
            self.r_session.rollback()
            print("Ошибка чтения таблицы SQL 'plc_io_monitor'")

    def write_mdbrtu_io_monitor(self, data):
        # print('')
        # print('WRITE: ', data)
        try:
            for key, val in data.items():
                if isinstance(val, bool):

                    bool_query = self.w_session.query(self.MdbRTU_IO_Monitor_Bool).filter(self.MdbRTU_IO_Monitor_Bool.var == key)
                    bool_row = bool_query.first()
                    if bool_row:
                        bool_row.value = val
                    else:
                        np = self.MdbRTU_IO_Monitor_Bool(var=key, value=val)
                        self.w_session.add(np)
                elif isinstance(val, int):

                    int_query = self.w_session.query(self.MdbRTU_IO_Monitor_Int).filter(self.MdbRTU_IO_Monitor_Int.var == key)
                    int_row = int_query.first()
                    if int_row:
                        int_row.value = val
                    else:
                        np = self.MdbRTU_IO_Monitor_Int(var=key, value=val)
                        self.w_session.add(np)

            self.w_session.commit()
        except:
            self.w_session.rollback()
            print("Ошибка записи таблицы SQL 'mdbrtu_io_monitor'")

    def read_mdbrtu_tasks(self):
        q_bool = self.r_session.query(self.MdbRTU_Tasks_Bool)
        q_int = self.r_session.query(self.MdbRTU_Tasks_Int)

        data_bool = {}
        for c in q_bool:
            data_bool[c.var] = c.value

        data_int = {}
        for c in q_int:
            data_int[c.var] = c.value

        data = {**data_bool, **data_int}

        self.r_session.commit()

        return data

    def write_mdbrtu_tasks(self, data):

        for key, val in data.items():
            if isinstance(val, bool):
                # np = self.PLC_Tasks_Bool(var=key, value=val)
                # self.w_session.add(np)

                bool_query = self.w_session.query(self.MdbRTU_Tasks_Bool).filter(self.MdbRTU_Tasks_Bool.var == key)
                bool_row = bool_query.first()
                if bool_row:
                    bool_row.value = val
                else:
                    np = self.MdbRTU_Tasks_Bool(var=key, value=val)
                    self.w_session.add(np)

            elif isinstance(val, int):
                # np = self.PLC_Tasks_Int(var=key, value=val)
                # self.w_session.add(np)

                int_query = self.w_session.query(self.MdbRTU_Tasks_Int).filter(self.MdbRTU_Tasks_Int.var == key)
                int_row = int_query.first()
                if int_row:
                    int_row.value = val
                else:
                    np = self.MdbRTU_Tasks_Int(var=key, value=val)
                    self.w_session.add(np)

        self.w_session.commit()

    def add_to_mdbrtu_tasks(self, key, value):

        if isinstance(value, bool):
            new_MdbRTU_Tasks_Bool = self.MdbRTU_Tasks_Bool(
                var=key,
                value=value
            )

            query = self.w_session.query(self.MdbRTU_Tasks_Bool).where(self.MdbRTU_Tasks_Bool.var == new_MdbRTU_Tasks_Bool.var)

            if query.first() is None:
                self.w_session.add(new_MdbRTU_Tasks_Bool)
            else:
                query.update(
                    {
                        self.MdbRTU_Tasks_Bool.value: value
                    },
                    synchronize_session = False)

        elif isinstance(value, int):
            new_MdbRTU_Tasks_Int = self.MdbRTU_Tasks_Int(
                var=key,
                value=value
            )

            query = self.w_session.query(self.MdbRTU_Tasks_Int).where(self.MdbRTU_Tasks_Int.var == new_MdbRTU_Tasks_Int.var)

            if query.first() is None:
                self.w_session.add(new_MdbRTU_Tasks_Int)
            else:
                query.update(
                    {
                        self.MdbRTU_Tasks_Int.value: value
                    },
                    synchronize_session=False)

        else:
            print ("There isn't such type of variable")
            self.w_session.rollback()

        self.w_session.commit()




    # def add_to_FC_Axes_Monitor(self, var, axis_var, value):
    #
    #     query = self.session.query(self.FC_Axes_Monitor).filter_by(var=var, axis_var=axis_var).first()
    #
    #     if query:
    #         query.axis_var =
    #     else:
    #         query = self.FC_Axes_Monitor(user_id=user_id, name=name, timer=timer, percent=percent)
    #         db.session.add(user_setting)
    #     db.session.commit()

    #     new_FC_Axes_Monitor = self.FC_Axes_Monitor(
    #         var=var,
    #         axis_1_var=value[0],
    #         axis_1_value=value[1],
    #         axis_2_var=value[0],
    #         axis_2_value=value[1],
    #         axis_3_var=value[0],
    #         axis_3_value=value[1],
    #         axis_4_var=value[0],
    #         axis_4_value=value[1],
    #         axis_5_var=value[0],
    #         axis_5_value=value[1],
    #         axis_6_var=value[0],
    #         axis_6_value=value[1],
    #
    #     )
    #
    #     query = self.session.query(self.J_Points).where(self.J_Points.name == new_J_Points.name)
    #
    #     if query.first() is None:
    #         self.session.add(new_J_Points)
    #     else:
    #         query.update(
    #             {
    #                 self.J_Points.axis_1: value[0],
    #                 self.J_Points.axis_2: value[1],
    #                 self.J_Points.axis_3: value[2],
    #                 self.J_Points.axis_4: value[3],
    #                 self.J_Points.axis_5: value[4],
    #                 self.J_Points.axis_6: value[5]
    #             },
    #             synchronize_session = False)
    #     self.session.commit()




