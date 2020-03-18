#!/bin/bash

# This installation script uses 'sudo'.
# ./install_ctakes --help


usage()
{
cat << _USAGE_

Usage: $(basename $0) [--help] [--run] [--java JAVA_MODE] [--ctakes cTAKES_MODE]
          [--ducc DUCC_MODE] [--umls UMLS_MODE] [--owner USER]

Install script for the following packages in Ubuntu:
  Java SDK 8 and Java JRE 8 (OpenJDK 8)
  Apache cTAKES 4.0
  Apache UIMA DUCC 2.2.2 (requires Python 2 as /usr/bin/env python)
  National Library of Medicine's Unified Medical Language System (UMLS)

Commands are printed to screen for validation purpose, enable 'run' option
to execute the commands. The 'run' option needs to be enabled internally for
distributed installation.

'USER' is the username used for owner/group permissions of cTAKES/UMLS,
installation, default is 'cades'.

Default installation directory for packages is '/opt'.
Default temporary directory for downloaded files is '/tmp'.
Default installation directory for environment profiles is '/etc/profile.d'.

cTAKES/UMLS requires UMLS credentials, see internal configuration options for
specifying authentication credentials.

Some packages are available in a CADES data server, see internal configuration
options for specifying authentication credentials.

JAVA_MODE:
 *0 -> do not install
  1 -> install with package manager

cTAKES_MODE:
 *0 -> do not install
  1 -> download and install the user installation version (608MB)
  2 -> copy from CADES server and install the user installation version (608MB)

DUCC_MODE:
 *0 -> do not install
  1 -> download and install (104MB)
  2 -> copy from CADES server and install (104MB)

UMLS_MODE:
 *0 -> do not install
  1 -> download and install Original Dictionary Lookup (562MB)
  2 -> copy from CADES server and install Original Dictionary Lookup (562MB)
  3 -> download and install Fast Dictionary Lookup (12MB)
  4 -> copy from CADES server and install Fast Dictionary Lookup (12MB)

_USAGE_
}


#################
# CONFIGURATION #
#################

top_install_dir="/opt"  # path to install packages
tmp_install_dir="/tmp"  # path to download packages, for current directory use "."
profile_install_dir="/etc/profile.d"  # path for profiles, environment variables
run_mode=0
java_mode=0
ctakes_mode=0
ducc_mode=0
umls_mode=0
umls_user="eponcemo"
umls_pw="oslORNL18"
ctakes_owner="cades"  # also applies to UMLS resources
data_server_ftp="ftp://172.22.4.129/pub"


##########################
# COMMAND-LINE ARGUMENTS #
##########################

while [ "$1" ]; do
    case "$1" in
        -h | --help)
            usage
            exit 0 ;;
        -r | --run)
            run_mode=1
            shift ;;
        -j | --java)
            case ${2#[-+]} in
                "") echo "ERROR! incomplete command line option, $1"
                    exit 1 ;;
                *[!0-9]*)
                    echo "ERROR! invalid command line option-value, $1 $2"
                    exit 1 ;;
                *) java_mode=$2 ;;
            esac
            shift 2 ;;
        -c | --ctakes)
            case ${2#[-+]} in
                "") echo "ERROR! incomplete command line option, $1"
                    exit 1 ;;
                *[!0-9]*)
                    echo "ERROR! invalid command line option-value, $1 $2"
                    exit 1 ;;
                *) ctakes_mode=$2 ;;
            esac
            shift 2 ;;
        -d | --ducc)
            case ${2#[-+]} in
                "") echo "ERROR! incomplete command line option, $1"
                    exit 1 ;;
                *[!0-9]*)
                    echo "ERROR! invalid command line option-value, $1 $2"
                    exit 1 ;;
                *) ducc_mode=$2 ;;
            esac
            shift 2 ;;
        -u | --umls)
            case ${2#[-+]} in
                "") echo "ERROR! incomplete command line option, $1"
                    exit 1 ;;
                *[!0-9]*)
                    echo "ERROR! invalid command line option-value, $1 $2"
                    exit 1 ;;
                *) umls_mode=$2 ;;
            esac
            shift 2 ;;
        -o | --owner)
            case "$2" in
                "") echo "ERROR! incomplete command line option, $1"
                    exit 1 ;;
                *) ctakes_owner="$2" ;;
            esac
            shift 2 ;;
        *) usage
            echo "ERROR! invalid command line option, $1"
            exit 1 ;;
    esac
done


####################
# HELPER FUNCTIONS #
####################

# Print or run a command
# Requires: $run_mode
# Inputs: command
# Outputs:
run_cmd()
{
    [ $# -lt 1 ] && return
    echo "$@"
    [ $run_mode -eq 1 ] && $@
}


# Print or evaluate a command
# Requires: $run_mode
# Inputs: command
# Outputs:
eval_cmd()
{
    [ $# -lt 1 ] && return
    echo "$@"
    [ $run_mode -eq 1 ] && eval $@
}


# Check Linux distro (Ubuntu or CentOS)
# Requires: run_cmd(), lsb_release | uname
# Inputs:
# Outputs: distro
check_distro()
{
    local distro
    if [ "$(command -v lsb_release)" ]; then
        if [ "$(lsb_release -d | grep -i 'ubuntu')" ] || [ "$(lsb_release -i | grep -i 'ubuntu')" ]; then
            distro="ubuntu"
        elif [ "$(lsb_release -d | grep -i 'centos')" ] || [ "$(lsb_release -i | grep -i 'centos')" ]; then
            distro="centos"
        fi
    elif [ "$(command -v uname)" ]; then
        if [ "$(uname -v | grep -i 'ubuntu')" ]; then
            distro="ubuntu"
        elif [ "$(uname -v | grep -i 'centos')" ]; then
            distro="centos"
        fi
    fi
    echo "$distro"
}


# Install tool/library using a package service
# Requires: run_cmd(), apt | yum
# Inputs: package
# Outputs:
install_package()
{
    [ $# -lt 1 ] && return
    local distro="$(check_distro)"
    local pkg="$1"
    if [ "$distro" = "ubuntu" ]; then
        run_cmd "sudo apt -y install $pkg"
    elif [ "$distro" = "centos" ]; then
        run_cmd "sudo yum -y install $pkg"
    fi
}


# Check if tool/library is installed
# If no argument is given, then checks if internal listed tools are installed
# Requires: install_package()
# Inputs: [package]
# Outputs:
check_package()
{
    local distro="$(check_distro)"
    if [ $# -lt 1 ]; then
        if [ "$distro" = "ubuntu" ]; then
            for pkg in tar gawk bc wget unzip; do
                if [ ! "$(command -v "$pkg")" ]; then
                    echo "WARNING! package '$pkg' was not found. Installing..."
                    install_package "$pkg"
                fi
            done
        elif [ "$distro" = "centos" ]; then
            for pkg in tar gawk bc wget unzip; do
                if [ ! "$(command -v "$pkg")" ]; then
                    echo "WARNING! package '$pkg' was not found. Installing..."
                    install_package "$pkg"
                fi
            done
        fi
    else
        local pkg="$1"
        if [ ! "$(command -v "$pkg")" ]; then
            echo "WARNING! package '$pkg' was not found. Installing..."
            install_package "$pkg"
        fi
    fi
}


# Uncompress a file into a given path
# Requires: run_cmd(), tar | unzip
# Inputs: compressed_file [extract_path]
# Outputs:
uncompress_file()
{
    [ $# -lt 1 ] && return
    local compress_file="$1"
    local extract_path="."
    [ "$2" ] && extract_path="$2"

    # Check if composite file extensions (e.g., tar.gz, tar.bz2)
    local file_ext="${compress_file##*.}"
    if [ "$file_ext" = "gz" ] || [ "$file_ext" = "bz2" ]; then
        local file_plain="${compress_file%.*}"
        local tmp_ext="${file_plain##*.}"
        if [ "$tmp_ext" = "tar" ]; then
           file_ext="$tmp_ext.$file_ext"
        fi
    fi

    case "$file_ext" in
        tar) run_cmd "sudo tar -xf $compress_file -C $extract_path" ;;
        tgz | tar.gz) run_cmd "sudo tar -xzf $compress_file -C $extract_path" ;;
        tar.bz2) run_cmd "sudo tar -xjf $compress_file -C $extract_path" ;;
        zip) run_cmd "sudo unzip -o $compress_file -d $extract_path" ;;
        *) echo "WARNING! Do not know how to uncompress file, $compress_file";;
    esac
}


################
# MAIN PROGRAM #
################
distro="$(check_distro)"
if [ -z "$distro" ]; then
    echo "ERROR! Failed to identify Linux distro."
    exit 1
fi
echo "Linux distro is $distro"
check_package


# Oracle OpenJDK 8 and OpenJRE 8
# ------------------------------
if [ $java_mode -gt 0 ]; then
    # Check if already installed
    has_jdk=0
    if [ "$(command -v java)" ]; then
        jdk_ver=$(java -version 2>&1 | awk '/openjdk version/ { print $NF }' \
                    | awk -F'.' '{ gsub("\"",""); print $1 "." $2 }')
        has_jdk=$(echo "$jdk_ver >= 1.8" | bc -l)
    fi

    # If necessary, install
    if [ $has_jdk -eq 0 ]; then
        if [ "$distro" = "ubuntu" ]; then
            jdk_pkg="openjdk-8-jdk"
        elif [ "$distro" = "centos" ]; then
            jdk_pkg="java-1.8.0-openjdk-devel"
            #jdk_pkg="java-1.8.0-openjdk"
        fi
        install_package "$jdk_pkg"
    else
        echo "OpenJDK $jdk_ver is already installed."
    fi

    # Check installation path
    # /usr/lib/jvm/java-1.8.0-openjdk-amd64 -> /usr/lib/jvm/java-8-openjdk-amd64
    # /usr/lib/jvm/java-default -> /usr/lib/jvm/java-1.8.0-openjdk-amd64
    jdk_install_dir="/usr/lib/jvm"
    if [ "$distro" = "ubuntu" ]; then
        jdk8_install_dir="$jdk_install_dir/java-8-openjdk-amd64"
        jdk_install_link="$jdk_install_dir/java-1.8.0-openjdk-amd64"
    elif [ "$distro" = "centos" ]; then
        jdk8_install_dir="$jdk_install_dir/java-openjdk"
        jdk_install_link="$jdk_install_dir/java-1.8.0-openjdk"
    fi
    java_install_link="$jdk_install_dir/default-java"
    if [ ! -d "$jdk_install_dir" ]; then
        echo "ERROR! JVM path, $jdk_install_dir, does not exists."
        run_cmd "exit 1"
    fi
    if [ ! -d "$jdk8_install_dir" ]; then
        echo "ERROR! OpenJDK 8 path, $jdk8_install_dir, does not exists."
        run_cmd "exit 1"
    fi

    # Set environment variables
    java_profile="java_env.sh"
    if [ ! -f "$profile_install_dir/$java_profile" ]; then
        echo "Creating symbolic link to OpenJDK 8..."
        run_cmd "sudo ln -fs $jdk8_install_dir $jdk_install_link"
        echo "Creating symbolic link to OpenJDK 1.8.0..."
        run_cmd "sudo ln -fs $jdk_install_link $java_install_link"
        eval_cmd "sudo echo 'export JAVA_HOME=\"$java_install_link\"' > $java_profile"
        eval_cmd "sudo echo 'export JRE_HOME=\"\$JAVA_HOME/jre\"' >> $java_profile"
        run_cmd "sudo mv $java_profile $profile_install_dir"
        run_cmd "sudo chmod 0644 $profile_install_dir/$java_profile"
    fi
fi


# Apache cTAKES
# -------------
ctakes_ver="ctakes-4.0.0"
ctakes_dir="apache-$ctakes_ver"
ctakes_install_dir="$top_install_dir/$ctakes_dir"
ctakes_install_link="$top_install_dir/apache-ctakes"

if [ $ctakes_mode -gt 0 ]; then

    # Download user installation
    if [ $ctakes_mode -eq 1 ] || [ $ctakes_mode -eq 2 ]; then
        if [ ! -d "$ctakes_install_dir" ]; then
            ctakes_zip="${ctakes_dir}-bin.tar.gz"

            # Download from web
            if [ $ctakes_mode -eq 1 ]; then
                ctakes_url="http://apache.mirrors.ionfish.org/ctakes/$ctakes_ver/$ctakes_zip"

            # Download from CADES server
            elif [ $ctakes_mode -eq 2 ]; then
                ctakes_url="$data_server_ftp/$ctakes_zip"
            fi
            if [ ! -f "$tmp_install_dir/$ctakes_zip" ]; then
                run_cmd "wget -P $tmp_install_dir $ctakes_url"
            fi
            uncompress_file "$tmp_install_dir/$ctakes_zip" "$top_install_dir"
            run_cmd "sudo chown -R $ctakes_owner:$ctakes_owner $ctakes_install_dir"
            run_cmd "sudo rm $tmp_install_dir/$ctakes_zip"
        fi
    fi

    # Check installation path
    if [ ! -d "$ctakes_install_dir" ]; then
        echo "ERROR! cTAKES path, $ctakes_install_dir, does not exists."
        run_cmd "exit 1"
    fi

    # Set environment variables
    ctakes_profile="ctakes_env.sh"
    if [ ! -f "$profile_install_dir/$ctakes_profile" ]; then
        echo "Creating symbolic link to Apache cTAKES..."
        run_cmd "sudo ln -fs $ctakes_install_dir $ctakes_install_link"
        eval_cmd "sudo echo 'export CTAKES_HOME=\"$ctakes_install_link\"' > $ctakes_profile"
        eval_cmd "sudo echo 'export PATH=\"\$CTAKES_HOME/bin:\$PATH\"' >> $ctakes_profile"
        run_cmd "sudo mv $ctakes_profile $profile_install_dir"
        run_cmd "sudo chmod 0644 $profile_install_dir/$ctakes_profile"
    fi
fi


# Apache UIMA DUCC
# ----------------
ducc_owner="ducc"
ducc_ver="uima-ducc-2.2.2"
ducc_dir="apache-$ducc_ver"
ducc_install_dir="$top_install_dir/$ducc_dir"
ducc_install_link="$top_install_dir/ducc_runtime"

if [ $ducc_mode -gt 0 ]; then

    # Download user installation
    if [ $ducc_mode -eq 1 ] || [ $ducc_mode -eq 2 ]; then
        if [ ! -d "$ducc_install_dir" ]; then
            ducc_zip="${ducc_ver}-bin.tar.gz"

            # Download from web
            if [ $ducc_mode -eq 1 ]; then
                ducc_url="http://apache.spinellicreations.com/uima/$ducc_ver/$ducc_zip"

            # Download from CADES server
            elif [ $ducc_mode -eq 2 ]; then
                ducc_url="$data_server_ftp/$ducc_zip"
            fi
            if [ ! -f "$tmp_install_dir/$ducc_zip" ]; then
                run_cmd "wget -P $tmp_install_dir $ducc_url"
            fi
            umask 022 && uncompress_file "$tmp_install_dir/$ducc_zip" "$top_install_dir"
            run_cmd "sudo chown -R $ducc_owner:$ducc_owner $ducc_install_dir"
            run_cmd "sudo rm $tmp_install_dir/$ducc_zip"
        fi
    fi

    # Check installation path
    if [ ! -d "$ducc_install_dir" ]; then
        echo "ERROR! DUCC path, $ducc_install_dir, does not exists."
        run_cmd "exit 1"
    fi

    # Set environment variables
    ducc_profile="ducc_env.sh"
    if [ ! -f "$profile_install_dir/$ducc_profile" ]; then
        echo "Creating symbolic link to Apache UIMA DUCC..."
        run_cmd "sudo ln -fs $ducc_install_dir $ducc_install_link"
        eval_cmd "sudo echo 'export DUCC_HOME=\"$ducc_install_link\"' > $ducc_profile"
        eval_cmd "sudo echo 'export PATH=\"\$DUCC_HOME/admin:\$PATH\"' >> $ducc_profile"
        eval_cmd "sudo echo 'export PATH=\"\$DUCC_HOME/bin:\$PATH\"' >> $ducc_profile"
        run_cmd "sudo mv $ducc_profile $profile_install_dir"
        run_cmd "sudo chmod 0644 $profile_install_dir/$ducc_profile"
    fi

    # Post installation
    # run_cmd "cd $ducc_install_dir/admin"
    # run_cmd "echo '\r\r' | ducc_post_install"
    # run_cmd "keytool -importkeystore -srckeystore $ducc_install_dir/webserver/etc/keystore -destkeystore $ducc_install_dir/webserver/etc/keystore -deststoretype pkcs12"

    # Configure ducc_ling
    # run_cmd "sudo chown ducc:ducc amd64"
    # run_cmd "sudo chmod 700 amd64"
    # run_cmd "sudo chown root:$ducc_owner amd64/ducc_ling"
    # run_cmd "sudo chmod 4750 amd64/ducc_ling"
fi


# NLM UMLS
# --------
if [ $umls_mode -gt 0 ]; then

    # Download Original Dictionary Lookup
    # These are the resources from ctakes-resources-3.2.1.1-bin.zip with hsql databases
    # converted to hsqldb 2.3.4 and compacted. They were converted using the following command:
    #   java -cp hsqldb-2.3.4.jar org.hsqldb.util.DatabaseManager
    # And compacted using this command: SHUTDOWN COMPACT
    if [ $umls_mode -eq 1 ] || [ $umls_mode -eq 2 ]; then
        umls_zip="ctakes-resources-4.0-bin.zip"

        # Download from web
        if [ $umls_mode -eq 1 ]; then
            umls_url="https://sourceforge.net/projects/ctakesresources/files/$umls_zip"

        # Download from CADES server
        elif [ $umls_mode -eq 2 ]; then
            umls_url="$data_server_ftp/umls_dictionaries/$umls_zip"
        fi
        if [ ! -f "$tmp_install_dir/$umls_zip" ]; then
            run_cmd "wget -P $tmp_install_dir $umls_url"
        fi
        uncompress_file "$tmp_install_dir/$umls_zip" "$tmp_install_dir"
        run_cmd "sudo mv $tmp_install_dir/resources $ctakes_install_dir"
        run_cmd "sudo chown -R $ctakes_owner:$ctakes_owner $ctakes_install_dir/resources"
        run_cmd "sudo rm $tmp_install_dir/$umls_zip"

    # Download Fast Dictionary Lookup
    # This is the dictionary used by the Fast Dictionary Lookup
    # component for cTAKES 4.0. These were created using hsqldb 2.3.4.
    elif [ $umls_mode -eq 3 ] || [ $umls_mode -eq 4 ]; then
        umls_dir="sno_rx_16ab"
        umls_zip="$umls_dir.zip"

        # Download from web
        if [ $umls_mode -eq 3 ]; then
            umls_url="https://sourceforge.net/projects/ctakesresources/files/$umls_zip"

        # Download from CADES server
        elif [ $umls_mode -eq 4 ]; then
            umls_url="$data_server_ftp/umls_dictionaries/$umls_zip"
        fi
        if [ ! -f "$tmp_install_dir/$umls_zip" ]; then
            run_cmd "wget -P $tmp_install_dir $umls_url"
        fi
        uncompress_file "$tmp_install_dir/$umls_zip" "$tmp_install_dir"
        run_cmd "sudo cp $tmp_install_dir/${umls_dir}.xml $ctakes_install_dir/resources/org/apache/ctakes/dictionary/lookup/fast/"
        run_cmd "sudo cp -r $tmp_install_dir/$umls_dir $ctakes_install_dir/resources/org/apache/ctakes/dictionary/lookup/fast/"
        run_cmd "sudo chown -R $ctakes_owner:$ctakes_owner $ctakes_install_dir"
        run_cmd "sudo rm $tmp_install_dir/$umls_zip"
        run_cmd "sudo rm $tmp_install_dir/${umls_dir}.xml"
        run_cmd "sudo rm -rf $tmp_install_dir/$umls_dir"
    fi

    # NOTE: set UMLS access rights in CTAKES_HOME/bin/runctakesC[VD|PE].sh.
    # Probably setting environment variables for user and password suffice.
    # java -Dctakes.umlsuser=username -Dctakes.umlspw=password -cp ...
    # Also, set environment variables:
    #   ctakes_umlsuser=username
    #   ctakes_umlspw=password

    # Set environment variables
    umls_profile="umls_env.sh"
    if [ ! -f "$profile_install_dir/$umls_profile" ]; then
        eval_cmd "sudo echo 'export ctakes_umlsuser=\"$umls_user\"' > $umls_profile"
        eval_cmd "sudo echo 'export ctakes_umlspw=\"$umls_pw\"' >> $umls_profile"
        run_cmd "sudo mv $umls_profile $profile_install_dir"
        run_cmd "sudo chmod 0644 $profile_install_dir/$umls_profile"
    fi
fi


