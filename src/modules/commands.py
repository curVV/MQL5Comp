# -*- coding: utf-8 -*-

import sublime_plugin

from . import build 

        
class MqlfCompBaseCommand(sublime_plugin.TextCommand):
    def is_enabled(self, **kwargs):
        # return self.view.settings().get('git_gutter_is_enabled', False)
        return True


class MqlfCompTestCommand(MqlfCompBaseCommand):
    def run(self, edit):
        #self.view.insert(edit, 0, "Hello, {}".format("-------------------------------"))
        print("file_name: ", self.view.file_name())
        print("view_id:", self.view.id())


class MqlfCompBuildCommand(sublime_plugin.WindowCommand):
    def run(self):
        build.run(window=self.window, source_file=self.window.extract_variables().get("file"))


