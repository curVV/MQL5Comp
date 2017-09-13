# -*- coding: utf-8 -*-

import os

import sublime



class MQL5CompSettingsError(Exception):
    pass


class Settings(object):
    
    def __init__(self, window, scope):
        self.window = window
        self.scope = scope

    def get(self, var):
        func = getattr(self, 'settings_' + self.scope, None)
        if not func:
            raise MQL5CompSettingsError("Invalid settins scope: {}.".format(self.scope)) 
        return func(var)

    def settings_global(self, var):
        try:
            if var == "all":
                return self.window.extract_variables()
            else:
                return self.window.extract_variables().get(var)
        except KeyError:
            raise MQL5CompSettingsError("Project config missing.")

    def settings_project(self, var):
        try:
            if var == "all":
                return self.window.project_data()["MQL5Comp_Project"]
            else:
                return self.window.project_data()["MQL5Comp_Project"].get(var)
        except KeyError:
            raise MQL5CompSettingsError("Project config missing.")

    def settings_mql5comp(window, var):
        # TODO: get settings
        return None


def get(window, scope, var):
    return Settings(window, scope).get(var)


def copy_mode(window):
    return get(window, "project", "copy_mode")


def mql_version(window):
    return get(window, "project", "mql_version")


def mql_type(window):
    return get(window, "project", "mql_type")


def mql_compiler(window):
    return get(window, "project", "mql_compiler")


def mql_source_dir_name(window):
    return get(window, "project", "mql_source_dir_name")


def smb_params(window):
    return get(window, "project", "smb_params")


def project_path(window):
    project_path = get(window, "global", "project_path")
    if project_path == None or not os.path.exists(project_path):
        raise MQL5CompSettingsError("Could not determine project path.")
    return project_path 


def wine_prefix(window):
    wine_prefix = get(window, "project", "wine_prefix")
    if not wine_prefix:
        wine_prefix = os.path.expanduser('~/.wine')
    else:
        wine_prefix = os.path.expanduser(wine_prefix) 
    if not os.path.exists(wine_prefix):
        raise MQL5CompSettingsError("Could not locate wine prefix at {}.".format(wine_prefix))
    return wine_prefix


def find_wine_project_drive(wine_prefix, project_path):
    """Look for mapped wine dos drive to current project path"""
    dosdevices_dir = wine_prefix + "/dosdevices"
    if not os.path.exists(dosdevices_dir):
        raise MQL5CompSettingsError("Could not find wine dosdevices mapper directory at {}.".format(dosdevices_dir))

    for drive in os.listdir(dosdevices_dir):
        if drive.endswith("::"):
            continue
        if drive.endswith(":"):
            try:
                if os.readlink(dosdevices_dir + "/" + drive) == project_path:
                    return drive
            except OSError:
                continue
    return None


def create_wine_project_drive(wine_prefix, project_path):
    drives = ['q:','r:','s:','t:','u:','v:','w:','y:']
    for drive in drives:
        if not os.path.exists(wine_prefix + "/dosdevices/" + drive):
            os.symlink(project_path, wine_prefix + "/dosdevices/" + drive)
            return drive
    return None


def wine_project_dos_path(window):
    """Checks if wine works and if windows projet path map exists.
    Attempts to create map if not exists.
    """ 
    wine_project_dos_path = get(window, "project", "wine_project_dos_path")
    if not wine_project_dos_path:
        wine_project_dos_path = find_wine_project_drive(wine_prefix(window), project_path(window))
        if not wine_project_dos_path and sublime.ok_cancel_dialog(
                "A wine project drive map was not found. " \
                "Would you like to have one created automatically for you?", "Yes, map the wine drive!"):
            wine_project_dos_path = create_wine_project_drive(wine_prefix(window), project_path(window))
            if not wine_project_dos_path:
                raise MQL5CompSettingsError("Could not find or map a wine drive for the project.")
    return wine_project_dos_path