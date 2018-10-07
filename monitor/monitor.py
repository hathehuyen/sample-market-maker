import os
import threading
from time import sleep
from market_maker.utils import read_json_from_shm


class Monitor(object):
    def __init__(self):
        self.update_thread = threading.Thread(target=lambda: self._run_loop())
        self.ticker = None
        self.position = None
        self.margin = None
        self.bot_running = False

    def _read_data(self):
        self.ticker = read_json_from_shm('ticker.json')
        self.position = read_json_from_shm('ticker.json')
        self.margin = read_json_from_shm('ticker.json')

    def _check_bot_process(self):
        cmd = 'ps ax | grep marketmaker | grep -v grep'
        result = os.popen(cmd).read()
        if result:
            self.bot_running = True
        else:
            self.bot_running = False

    def _run_loop(self):
        interval = 1
        while True:
            try:
                self._read_data()
                self._check_bot_process()
                sleep(interval)
            except Exception as ex:
                print(ex)
                sleep(interval)

    def start(self):
        self.update_thread.daemon = True
        self.update_thread.start()
        print('Monitor thread started')
