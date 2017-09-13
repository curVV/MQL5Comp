# -*- coding: utf-8 -*-


class Log(object):
    """Log stuff"""

    levels = {"debug": 5, "info": 4, "warning": 3, "error": 2}

    def __init__(self, level):
        self.level = level
        self.current_level = None

    def echo(self, msg):
        try:
            if self.levels.get(self.level) >= self.levels.get(self.current_level):
                print(msg)
        except Exception as e:
            print("[ERROR] Unable to log.")
            print("Logger Error: {}".format(str(e)))

    def info(self, msg):
        self.current_level = "info"
        self.echo("[INFO] " + msg)

    def warning(self, msg):
        self.current_level = "warning"
        self.echo("[WARNING] " + msg)

    def error(self, msg):
        self.current_level = "error"
        self.echo("[ERROR] " + msg)

    def debug(self, msg):
        self.current_level = "debug"
        self.echo("[DEBUG] " + msg)
