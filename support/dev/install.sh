#!/bin/bash

########################################################################################
# Installs the sublimepackage - used for development of plugin.
#
# It's a simply convenience script that copies the package files to the SublimeText user 
# package directory, and does some checks.
#
# Sublimetext executes this script on build (ctrl+B), configured in project file as 
# build system:
#        {
#            "file_regex": "^[ ]*File \"(...*?)\", line ([0-9]*)",
#            "name": "mql5comp - Copy/Install",
#            "shell_cmd": "sh $project_path/install.sh copy"
#        },
########################################################################################


##### SET THE FOLLOWING VARS ####
package_name="MQL5Comp"

# Project source path
src_path="${HOME}/workspace/Sublime/plugins/mql5comp/src/" 

# Sublime config root path
base_path="${HOME}/.config/sublime-text-3/"

########################################################################################

echo "[Install Package ${package_name}]"

src_path="$(readlink -m ${src_path})"
build_path="$(readlink -m ${src_path}/../build)"

package_file_name="${package_name}.sublime-package"


log_ok(){
    printf "[ OK ]\t${1}\n"
}

log_fail(){
    printf "[FAIL]\t${1}\n"
}

log_info(){
    printf "[INFO]\t${1}\n"
}


if [ "$1" == "zip" ]; then
    log_ok "install mode: zipping package"
    action="zip"
else
    if [ "$1" == "copy" ]; then
        log_ok "install mode: copy dir"
        action="copy"
    else
        log_fail "CONFIG ERROR"
        log_info "USAGE: { \"shell_cmd\": \"sh \$project_path/install.sh <zip|copy>\" }"
        exit 0
    fi
fi

# Check source path
if [ ! -d "${src_path}" ]; then
    log_fail "ERROR: source path is invalid: ${src_path}"
    exit 0
fi

# Check/Create build path
if [ ! -d "${build_path}" ]; then
    if [ ! -d $(readlink -m "${build_path}/../") ]; then
        log_fail "ERROR: build path is invalid: ${build_path}"
        exit 0
    else
        log_ok "creating build dir..."
        mkdir -p "${build_path}"
        if [ ! "$?" -eq "0" ]; then
            log_fail "ERROR: could not create build dir ${build_path}"
            exit 0
        fi
    fi
fi

# Check base path
if [ ! -d "${base_path}" ]; then
    log_fail "ERROR: base path is invalid: ${base_path}"
    exit 0
fi

# clean build dir
log_ok "cleaning build dir..."
rm -rf "${build_path}/*"
if [ ! "$?" -eq "0" ]; then
    log_fail "ERROR: could not clean out build dir!"
    exit 0
fi


# build/zip
log_ok "building ${package_name}..."
cd "${src_path}" && zip -r "${build_path}/${package_file_name}" *
if [ ! "$?" -eq "0" ]; then
    log_fail "ERROR: could not zip the source."
    exit 0
fi

# Sync build
if [ "$action" == "zip" ]; then
    log_ok "installing ${package_file_name}..."
    cp  "${build_path}/${package_file_name}" "${base_path}/Installed Packages/${package_file_name}"
    if [ ! "$?" -eq "0" ]; then 
        log_fail "ERROR: could not copy package!"
        exit 0
    fi
fi

# Sync dir
if [ "$action" == "copy" ]; then
    # Create/Clean install dir
    if [ ! -d $(readlink -m "${base_path}/Packages") ]; then
        log_fail "ERROR: destination path is invalid: ${base_path}/Packages"
        exit 0
    else
        log_ok "cleaning/creating install dir..."
        mkdir -p "${base_path}/Packages/${package_name}"
        rm -rf "${base_path}/Packages/${package_name}/*"
        if [ ! "$?" -eq "0" ]; then
            log_fail "ERROR: could not create install dir ${base_path}/Packages/${package_name}"
            exit 0
        fi
    fi
    # Copy src to install
    log_ok "installing ${package_name}..."
    cp -r "${src_path}/"* "${base_path}/Packages/${package_name}/"
    if [ ! "$?" -eq "0" ]; then 
        log_fail "ERROR: could not copy package!"
        exit 0
    fi
fi

log_ok "done."
