# -*- coding:utf-8 -*-
from collections import defaultdict
from queue import Queue, Empty
from threading import Thread


class Event:
    """浜嬩欢瀵硅薄"""

    def __init__(self, event_type, data=None):
        self.event_type = event_type
        self.data = data


class EventEngine:
    """浜嬩欢椹卞姩寮曟搸"""

    def __init__(self):
        """鍒濆鍖栦簨浠跺紩鎿�"""
        # 浜嬩欢闃熷垪
        self.__queue = Queue()

        # 浜嬩欢寮曟搸寮�鍏�
        self.__active = False

        # 浜嬩欢寮曟搸澶勭悊绾跨▼
        self.__thread = Thread(target=self.__run)

        # 浜嬩欢瀛楀吀锛宬ey 涓烘椂闂达紝 value 涓哄搴旂洃鍚簨浠跺嚱鏁扮殑鍒楄〃
        self.__handlers = defaultdict(list)

    def __run(self):
        """鍚姩寮曟搸"""
        while self.__active:
            try:
                event = self.__queue.get(block=True, timeout=1)
                handle_thread = Thread(target=self.__process, args=(event,))
                handle_thread.start()
            except Empty:
                pass

    def __process(self, event):
        """浜嬩欢澶勭悊"""
        # 妫�鏌ヨ浜嬩欢鏄惁鏈夊搴旂殑澶勭悊鍑芥暟
        if event.event_type in self.__handlers:
            # 鑻ュ瓨鍦�,鍒欐寜椤哄簭灏嗘椂闂翠紶閫掔粰澶勭悊鍑芥暟鎵ц
            for handler in self.__handlers[event.event_type]:
                handler(event)

    def start(self):
        """寮曟搸鍚姩"""
        self.__active = True
        self.__thread.start()

    def stop(self):
        """鍋滄寮曟搸"""
        self.__active = False
        self.__thread.join()

    def register(self, event_type, handler):
        """娉ㄥ唽浜嬩欢澶勭悊鍑芥暟鐩戝惉"""
        if handler not in self.__handlers[event_type]:
            self.__handlers[event_type].append(handler)

    def unregister(self, event_type, handler):
        """娉ㄩ攢浜嬩欢澶勭悊鍑芥暟"""
        handler_list = self.__handlers.get(event_type)
        if handler_list is None:
            return
        if handler in handler_list:
            handler_list.remove(handler)
        if len(handler_list) == 0:
            self.__handlers.pop(event_type)

    def put(self, event):
        self.__queue.put(event)

    @property
    def queue_size(self):
        return self.__queue.qsize()
