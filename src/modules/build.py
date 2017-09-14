# -*- coding: utf-8 -*-

import threading, os, shutil, subprocess, re

from . import settings
from .log import Log


log = Log(level="info")


class MQL5CompBuildError(Exception):
    pass


class Build(threading.Thread):
    """docstring for Build"""
    def __init__(self, window, source_file):

        try:
            proc_name = "build-" + window.extract_variables()["project_base_name"]
        except KeyError:
            proc_name = "build_mql5comp"
        threading.Thread.__init__(self, group=None, target=None, name=proc_name)


        self.window = window
        """
        sublime.Window Class
        """


        self.mql_version = settings.mql_version(window)
        """
        Version of MQL project is writtten in
        """


        self.mql_type = settings.mql_type(window)
        """
        Type of MQL program being compiled (script/indicator/expert)
        """

        self.mql_type_subdir = self.get_type_sub_dir()
        """
        Subdir for type of program, derived from mql_type
        """


        self.mql_version_subdir = "MQL" + self.mql_version
        """
        Subdir for version off MQL that is being compiled
        """


        self.source_file = source_file
        """
        Full path to context source_file from where build is invoked
        """


        self.mql_source_dir_name = settings.mql_source_dir_name(window)
        """
        Name of the source directory
        """


        self.source_file_relative_dos_path = self.get_source_file_relative_dos_path()
        """
        Source file dos path relative to source directory
        """


        self.project_path = settings.project_path(window)
        """
        Full project path
        """


        self.mql_compiler = self.get_mql_compiler(window)
        """
        MQL compiler file name
        """


        self.wine_prefix = settings.wine_prefix(window)
        """
        Full path to wine prefix in use
        """
        

        self.wine_project_dos_path = settings.wine_project_dos_path(window)
        """
        Full dos path (including mapped drive in wine) to project
        """


        self.copy_mode = settings.copy_mode(window)
        """
        Copy binary using smb or local copy mode
        """


        self.smb_params = None
        """
        Holds validated smb paramaters
        """


        self.local_params = None
        """
        Holds validated local paramaters
        """


    def run(self):

        self.compile()

        if self.copy_mode == "smb":
            self.smb_params = self.get_smb_params()
            self.smb_copy()
        elif self.copy_mode == "local":
            self.local_params = self.get_local_params()
            self.local_copy()
        else:
            raise MQL5CompBuildError("Copy mode '{}' not valid.".format(self.copy_mode))


    def get_mql_compiler(self, window):
        mql_compiler = settings.mql_compiler(window)
        if mql_compiler is None:
            mql_compiler = "metaeditor.exe"

        compiler_full_path = self.project_path + "/" + self.mql_source_dir_name + "/" + mql_compiler

        if not os.path.exists(compiler_full_path):
            raise MQL5CompBuildError("Compiler not found: {}.".format(compiler_full_path))

        return compiler_full_path


    def get_source_file_relative_dos_path(self):
        """Returns source file path relative to src dir in dos path style"""
        if not self.source_file.endswith(".mq4") and not self.source_file.endswith(".mq5"):
            msg = "{} is not a valid mql file. Expected .mq4 or .mq5.".format(self.source_file)
            log.error(msg)
            raise MQL5CompBuildError(msg)

        if not os.path.exists(self.source_file):
            raise MQL5CompBuildError("Could not find file {}".format(self.source_file))

        sf_parts = self.source_file.split(self.mql_source_dir_name + "/")
        
        return sf_parts[len(sf_parts) - 1].replace('/','\\')


    def compile_log_result(self):
        """ 
        Get last line of log file.
        Why: Wine exits unnecessary with code 1 even though 
        process completes without error.
        """
        file = self.source_file[:-4] + ".log"
        log.info("[COMPILE LOG] log file is here: {}".format(file))
        try:
            with open(file, encoding="utf16", mode="r") as f:
                count = 0
                for line in f:
                    if count > 1 and len(line) > 1:
                        log.info("[COMPILE LOG] " + re.sub(r"\n|\r", "", line))
                    #if re.match(r"^Result: ", last_line.decode('utf-8')):
                    #   break;
                    count = count + 1
            return line
        except OSError:
            log.warning("Log file not found.")
            return "None"
        log.warning("Could not read compile result.")
        return "None"
            


    def compile(self):
        log.info("Compiling...")

        source_file_path = self.wine_project_dos_path + "\\" + self.mql_source_dir_name + "\\" + self.source_file_relative_dos_path

        # TODO: Include dir is hardcoded, should be user specifiable?
        include_dir_path = self.wine_project_dos_path + "\\" + self.mql_source_dir_name + "\\" + self.mql_version_subdir
        log.debug("include_dir_path: " + include_dir_path)

        build_cmd = self.mql_compiler + ' /compile:"{source_file_path}" /inc:"{include_dir_path}" /log'.format(
            source_file_path = source_file_path, 
            include_dir_path = include_dir_path)

        wine_debug = "-all"

        build_command_string = "WINEDEBUG={wine_debug} WINEPREFIX=\"{wine_prefix}\" wine {build_cmd}".format(
            wine_debug = wine_debug,
            wine_prefix = self.wine_prefix, 
            build_cmd = build_cmd)

        try:
            log.debug("Running command: `{}`".format(build_command_string))
            build_proc = subprocess.check_output(build_command_string, stderr=subprocess.STDOUT, shell=True)
            log.debug(build_proc.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                log.warning("Possible errors (wine) - double check results.")
            else:
                raise MQL5CompBuildError(str(e))

        self.compile_log_result()


    def get_type_sub_dir(self):
        try:
            if self.mql_type.lower() == "ea" or self.mql_type.lower() == "expert":
                return "Experts"
            elif self.mql_type.lower() == "indicator":
                return "Indicators"
            elif self.mql_type.lower() == "script":
                return "Scripts"
            else:
                raise MQL5CompBuildError("MQL type not recognised: {}.".format(self.mql_type))
        except AttributeError:
            raise MQL5CompBuildError("Error parsing MQL type: {}".format(type(self.mql_type)))


    def get_smb_params(self):
        try:
            return settings.smb_params(self.window)
        except KeyError:
            raise MQL5CompBuildError("MQL5Comp Error: No smb paramaters configured.")


    def get_local_params(self):
        try:
            return settings.local_params(self.window)
        except KeyError:
            raise MQL5CompBuildError("MQL5Comp Error: No local paramaters configured.")


    def smb_copy(self):
        build_path = self.project_path + "/" + self.mql_source_dir_name + "/" + self.mql_version_subdir + "/" + self.mql_type_subdir

        for filename in os.listdir(build_path):
            if filename.endswith(".ex4") or filename.endswith(".ex5"):
                build_file_path = build_path + "/" + filename
                smb_copy_cmd = "smbclient -U \"{smb_user}%{smb_password}\" //{smb_server}/{smb_share} " \
                    "--directory \"{smb_remote_dir}\" " \
                    "-c 'put \"{build_file_path}\" {filename}'".format(
                            smb_user = self.smb_params["user"],
                            smb_password = self.smb_params["password"],
                            smb_server = self.smb_params["server"],
                            smb_share = self.smb_params["share"],
                            smb_remote_dir = self.mql_version_subdir + "/" + self.mql_type_subdir,
                            build_file_path = build_file_path,
                            filename = filename
                        )
                try:
                    log.info("Copying {filename} to {remote}".format(
                        filename=filename, 
                        remote="//" + self.smb_params["server"] + "/" + self.smb_params["share"] + "/" + self.mql_version_subdir + "/" + self.mql_type_subdir))
                    log.debug("Running command: `{}`".format(smb_copy_cmd))
                    copy_proc = subprocess.check_output(smb_copy_cmd, stderr=subprocess.STDOUT, shell=True)
                    log.debug(copy_proc.decode('utf-8'))
                except subprocess.CalledProcessError as e:
                    raise MQL5CompBuildError(e.output)


    def local_copy(self):
        build_path = self.project_path + "/" + self.mql_source_dir_name + "/" + self.mql_version_subdir + "/" + self.mql_type_subdir
        target = os.path.expanduser(self.local_params["target_root_dir"]) + "/" + self.mql_version_subdir + "/" + self.mql_type_subdir

        if not os.path.exists(target):
            raise MQL5CompBuildError("Target directory not found: {}".format(target))

        for filename in os.listdir(build_path):
            if filename.endswith(".ex4") or filename.endswith(".ex5"):
                try:
                    file = build_path + "/" + filename
                    log.info("Copying {file} to {target}...".format(
                        file=file, 
                        target=target))
                    shutil.copy(file, target)
                except Exception as e:
                    raise MQL5CompBuildError(e)



def run(window, source_file):
    """
    Convenience function calling Build. 
    start() calls the subclass' run method.
    """
    Build(window, source_file).start()
