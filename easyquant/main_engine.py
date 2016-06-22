# -*- coding:utf-8 -*-
import importlib
import os
import pathlib
import sys
from collections import OrderedDict
import dill

import easytrader
from logbook import Logger, StreamHandler

from .event_engine import EventEngine
from .log_handler.default_handler import DefaultLogHandler
from .push_engine.clock_engine import ClockEngine
from .push_engine.quotation_engine import DefaultQuotationEngine

log = Logger(os.path.basename(__file__))
StreamHandler(sys.stdout).push_application()

PY_MAJOR_VERSION, PY_MINOR_VERSION = sys.version_info[:2]
if (PY_MAJOR_VERSION, PY_MINOR_VERSION) < (3, 5):
    raise Exception('Python 鐗堟湰闇�瑕� 3.5 鎴栦互涓�, 褰撳墠鐗堟湰涓� %s.%s 璇峰崌绾� Python' % (PY_MAJOR_VERSION, PY_MINOR_VERSION))

ACCOUNT_OBJECT_FILE = 'account.session'

class MainEngine:
    """涓诲紩鎿庯紝璐熻矗琛屾儏 / 浜嬩欢椹卞姩寮曟搸 / 浜ゆ槗"""

    def __init__(self, broker=None, need_data=None, quotation_engines=None,
                 log_handler=DefaultLogHandler(), now=None, tzinfo=None):
        """鍒濆鍖栦簨浠� / 琛屾儏 寮曟搸骞跺惎鍔ㄤ簨浠跺紩鎿�
        """
        self.log = log_handler

        # 鐧诲綍璐︽埛
        if (broker is not None) and (need_data is not None):
            self.user = easytrader.use(broker)
            need_data_file = pathlib.Path(need_data)
            if need_data_file.exists():
                self.user.prepare(need_data)
                with open(ACCOUNT_OBJECT_FILE, 'wb') as f:
                    dill.dump(self.user, f)
                    f.close()
            else:
                log_handler.warn("鍒稿晢璐﹀彿淇℃伅鏂囦欢 %s 涓嶅瓨鍦�, easytrader 灏嗕笉鍙敤" % need_data)
        else:
            self.user = None
            self.log.info('閫夋嫨浜嗘棤浜ゆ槗妯″紡')

        self.event_engine = EventEngine()
        self.clock_engine = ClockEngine(self.event_engine, now, tzinfo)

        quotation_engines = quotation_engines or [DefaultQuotationEngine]

        if type(quotation_engines) != list:
            quotation_engines = [quotation_engines]
        self.quotation_engines = []
        for quotation_engine in quotation_engines:
            self.quotation_engines.append(quotation_engine(self.event_engine, self.clock_engine))

        # 淇濆瓨璇诲彇鐨勭瓥鐣ョ被
        self.strategies = OrderedDict()
        self.strategy_list = list()

        self.log.info('鍚姩涓诲紩鎿�')

    def start(self):
        """鍚姩涓诲紩鎿�"""
        self.event_engine.start()
        for quotation_engine in self.quotation_engines:
            quotation_engine.start()
        self.clock_engine.start()

    def load_strategy(self, names=None):
        """鍔ㄦ�佸姞杞界瓥鐣�
        :param names: 绛栫暐鍚嶅垪琛紝鍏冪礌涓虹瓥鐣ョ殑 name 灞炴��"""
        s_folder = 'strategies'
        strategies = os.listdir(s_folder)
        strategies = filter(lambda file: file.endswith('.py') and file != '__init__.py', strategies)
        importlib.import_module(s_folder)
        for strategy_file in strategies:
            strategy_module_name = os.path.basename(strategy_file)[:-3]
            strategy_module = importlib.import_module('.' + strategy_module_name, 'strategies')
            strategy_class = getattr(strategy_module, 'Strategy')

            if names is None or strategy_class.name in names:
                self.strategies[strategy_module_name] = strategy_class
                self.strategy_list.append(strategy_class(log_handler=self.log, main_engine=self))
                self.log.info('鍔犺浇绛栫暐: %s' % strategy_module_name)
        for strategy in self.strategy_list:
            self.event_engine.register(ClockEngine.EventType, strategy.clock)
            for quotation_engine in self.quotation_engines:
                self.event_engine.register(quotation_engine.EventType, strategy.run)
        self.log.info('load strategy')
