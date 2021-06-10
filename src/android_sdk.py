import subprocess
import os
import stat
import platform
import time
import logging
import re
import requests
import zipfile

from clint.textui import progress

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - [%(funcName)s]: %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    level=logging.INFO,
)

class CommandType:
    PLATFORM_TOOLS = 1
    TOOLS = 2
    TOOLS_BIN = 3
    EMULATOR = 4


class AndroidSDK:
    AVD_NAME = "WhatsDump"

    def __init__(self, avd_name = None, communicate = None,variables = None):
        self._sdk_path = os.path.abspath("android-sdk")
        self._env = self._get_env_vars()
        self._communicate = communicate
        self._variables = variables

        if avd_name is not None:
            self.AVD_NAME = avd_name
        self.logger = logging.getLogger("{} - AndroidSDK".format(self.AVD_NAME))

        # Update original environment var
        os.environ["ANDROID_HOME"] = self._env["ANDROID_HOME"]

    def setStatus_inMainWindow(self,status):
        self._variables.setStatusBar(status)
        self._communicate.setStatusBar.emit()

    def install(self):
        # Create android-sdk/ directory and download latest SDK
        if not os.path.exists("android-sdk"):
            try:
                os.makedirs("android-sdk")
            except OSError:
                self.setStatus_inMainWindow("Could not create android-sdk/ directory")
                return False

        if not self._download("android-sdk"):
            return False

        # Update SDK from sdkmanager
        self.setStatus_inMainWindow("Updating SDK from manager...")

        s0 = self._run_cmd_sdkmanager("--update", show=True)

        if s0.returncode != 0:
            self.setStatus_inMainWindow("Could not update SDK Manager")
            return False

        # Accept licenses
        self.setStatus_inMainWindow("Accepting SDK licenses..")
        s1 = self._run_cmd_sdkmanager("--licenses", input = 'yes', show=True)

        if s1.returncode != 0:
            self.setStatus_inMainWindow("Could not accept SDK Manager licenses")
            return False

        # List all packages to check HAXM is supported
        s2 = self._run_cmd_sdkmanager("--list", wait=False)
        s2_out, s2_err = s2.communicate()

        if s2.returncode != 0:
            self.setStatus_inMainWindow("Could not list SDK Manager packages")
            return False

        # Install required packages
        install_args = "--install emulator platform-tools platforms;android-23 system-images;android-23;google_apis;x86"

        if s2_out and s2_out.find("extras;intel;Hardware_Accelerated_Execution_Manager".encode()) != -1:
            install_args += " extras;intel;Hardware_Accelerated_Execution_Manager"

        self.setStatus_inMainWindow("Installing packages from SDK Manager...")
        s3 = self._run_cmd_sdkmanager(install_args, input='yes', show=True)

        if s3.returncode != 0:
            self.setStatus_inMainWindow("Could not install packages from SDK Manager")
            return False

        return self.create_avd()

    def create_avd(self):
        # Create AVD
        self.setStatus_inMainWindow("Creating AVD image...")
        self._avd_path = ''.join((os.path.normpath(os.getcwd()) + '\\android-sdk\\.android\\avd').split()).replace('\\','/')
        s4 = self._run_cmd_avdmanager("create avd --name %s -k system-images;android-23;google_apis;x86 -g google_apis" % (self.AVD_NAME), input="no\n", show=True)

        if s4.returncode != 0:
            self.setStatus_inMainWindow(("Could not create %s AVD from AVD Manager" + self.AVD_NAME))
            return False
        return True

    def start_adb(self, port=5037):
        return self._run_cmd_adb("-P %d start-server" % port).returncode == 0

    def stop_adb(self):
        return self._run_cmd_adb("kill-server").returncode == 0

    def adb_root(self, serialn = None):
        return self._run_cmd_adb("-s {} root".format(serialn)).returncode == 0

    def start_emulator(self, adb_client, show_screen=True, no_accel=True, snapshot=False, proxy=None):
        emulator_device = None
        params = [
            "avd {}".format(self.AVD_NAME),
            "writable-system",
            "selinux permissive",
            "no-boot-anim",
            "noaudio",
            "partition-size 1024"
        ]

        if snapshot is False:
            params.append("no-snapshot")

        # Stop any running instance of WhatsDump AVD
        # self.stop_emulator(adb_client)

        # Snapshot of currently running devices
        devices_snap = adb_client.devices()

        # Disable hardware acceleration if asked to
        if no_accel:
            params.append("no-accel")
            params.append("gpu on")

        if show_screen is False:
            params.append("no-window")

        if proxy is not None:
            params.append("http-proxy http://{}".format(proxy))

        # Start emulator
        params = "-" + " -".join(params)
        proc = self._run_cmd_emulator(params, wait=False, show=True)

        # Check if any emulator connects to ADB
        while not emulator_device:
            if proc.returncode is not None:
                if proc.returncode != 0:
                    self.setStatus_inMainWindow("Emulator process returned an error")
                    return False#

                break

            new_devices = list(set(adb_client.devices()) - set(devices_snap))

            for device in new_devices:
                if device.serial.find("emulator") != -1:
                    emulator_device = device
                    break

            time.sleep(1)

        # Wait boot to complete
        while True:
            try:
                if emulator_device.shell("getprop dev.bootcomplete").rstrip() == "1":
                    self.setStatus_inMainWindow("Emulator boot process completed")
                    break
            except RuntimeError:
                pass

            time.sleep(1)

        return emulator_device

    def stop_emulator(self, adb_client):
        devices = adb_client.devices()

        for device in devices:
            if device.serial.find("emulator") != -1:
                return self._run_cmd_adb("-s %s emu kill" % device.serial).returncode == 0

        return False

    def is_avd_installed(self):
        try:
            process = self._run_cmd_avdmanager("list avd")
        except Exception:
            return False

        if process.returncode != 0:
            self.logger.debug(("avdmanager list avd command return code: %d", process.returncode))
            return False

        for line in process.stdout:
            if line.find(self.AVD_NAME.encode()) != -1:
                return True

        return False

    def delete_avd(self):
        try:
            process = self._run_cmd_avdmanager("delete avd -n {}".format(self.AVD_NAME))
        except Exception:
            return False

        if process.returncode != 0:
            self.logger.debug("avdmanager delete avd -n {} command return code: {}".format(self.AVD_NAME, process.returncode))
            return False

        """
         ./avdmanager delete avd -n WhatsDump3
        Deleting file /home/alessandro/.android/avd/WhatsDump3.ini
        Deleting folder /home/alessandro/.android/avd/WhatsDump3.avd

        AVD 'WhatsDump3' deleted.
        """

        for line in process.stdout:
            if line.find("deleted".encode()) != -1:
                return True

        return False


    def _download(self, extract_dir):
        output_zip = os.path.join(extract_dir, "tools.zip")
        tools_dir = os.path.join(extract_dir, "tools")

        if os.path.exists(tools_dir):
            self.setStatus_inMainWindow("SDK tools directory already exists, skipping download & extraction...")
            return True

        if not os.path.isfile(output_zip):
            self.setStatus_inMainWindow("Downloading and installing Android SDK...")

            # Download
            result = requests.get("https://web.archive.org/web/20190403122148/https://developer.android.com/studio/",stream = True)


            if result.status_code != 200:
                self.setStatus_inMainWindow("Failed GET request to developer.android.com")
                return False

            sdk_re = re.search(r"https://dl.google.com/android/repository/sdk-tools-" + platform.system().lower() + "-(\d+).zip", result.text)

            if not sdk_re:
                self.setStatus_inMainWindow(("Failed regex matching to find latest Android SDK platform:" + str(platform.system())))
                return False

            result = requests.get(sdk_re.group(), stream=True)

            self.setStatus_inMainWindow(("Android SDK url found:" + str(sdk_re.group())))

            with open(output_zip, "wb") as f:
                total_length = int(result.headers.get("Content-Length"))
                dl = 0
                for chunk in progress.bar(result.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                    if chunk:
                        dl += len(chunk)
                        f.write(chunk)
                        done = int(50 * dl / total_length)
                        self.setStatus_inMainWindow("Downloading,wait:" + str(done)+'% ' + "\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                        f.flush()

            self.setStatus_inMainWindow("Extracting...")
        else:
            self.setStatus_inMainWindow("Android Tools already downloaded, extracting...")

        # Extraction
        z = zipfile.ZipFile(output_zip)
        z.extractall(extract_dir)

        self.setStatus_inMainWindow("Android SDK successfully extracted in android-sdk/")

        return True

    def _run_cmd_sdkmanager(self, args, wait=True, input=None, show=False):
        return self._run_cmd(CommandType.TOOLS_BIN, "sdkmanager", args, wait, input, show)

    def _run_cmd_avdmanager(self, args, wait=True, input=None, show=False):
        return self._run_cmd(CommandType.TOOLS_BIN, "avdmanager", args, wait, input, show)

    # https://stackoverflow.com/questions/51606128/windows-emulator-exe-panic-missing-emulator-engine-program-for-x86-cpu/51627009
    """
    If you want to run emulator from command line,

    <your-full-path>/emulator -avd 5.1_WVGA_API_28
    For newer version of Android SDK, the emulator path should be something as below:

    /<xxx>/Android/sdk/emulator/emulator
    For older version of Android SDK, the emulator path is as below:

    /<xxx>/Android/sdk/tools/emulator
    Try either one of above to see which is your case.

    Here is the official document for Android emulator command line usage: https://developer.android.com/studio/run/emulator-commandline
    """

    def _run_cmd_emulator(self, args, wait=True, input=None, show=False):
        # return self._run_cmd(CommandType.TOOLS, 'emulator', args, wait, input, show)
        return self._run_cmd(CommandType.EMULATOR, "emulator", args, wait, input, show)

    def _run_cmd_adb(self, args, wait=True, input=None, show=False):
        return self._run_cmd(CommandType.PLATFORM_TOOLS, "adb", args, wait, input, show)

    def _run_cmd(self, type, binary, args, wait, input, show):
        path = None
        is_windows = platform.system() == "Windows"

        if type == CommandType.PLATFORM_TOOLS:
            path = os.path.join(self._sdk_path, "platform-tools")
        elif type == CommandType.TOOLS:
            path = os.path.join(self._sdk_path, "tools")
        elif type == CommandType.EMULATOR:
            path = os.path.join(self._sdk_path, "emulator")
        elif type == CommandType.TOOLS_BIN:
            path = os.path.join(self._sdk_path, "tools","bin")

            if is_windows:
                binary = "%s.bat" % binary

        return self._run_raw_cmd("%s %s" % (os.path.join(path, binary), args), wait, input, show)

    # TODO: log SDK installation output / errors to android-sdk/log.txt
    def _run_raw_cmd(self, cmd, wait=True, input=None, show=False):
        args = cmd.split()

        # Set executable permission on linux if not set (zipfile not preserving permissions)
        if platform.system() != "Windows":
            self._set_executable(args[0])

        # Run process
        proc = subprocess.Popen(
            args,
            env      = self._env,
            cwd      = self._sdk_path,
            stdin    = subprocess.PIPE,
            stdout   = subprocess.PIPE,
            stderr   = subprocess.STDOUT,
            encoding = None if args[1] == '--licenses' else 'utf-8'
        )

        # Program cannot decode a line from STDOUT.
        # The status bar not show progress accepting licenses.
        if input:
            if args[1] == '--licenses':
                proc.stdin.write(input.encode())
            else:
                proc.stdin.write(input)
            proc.stdin.close()

        for line in proc.stdout:
            if line[0] == '[':
                self.setStatus_inMainWindow(line)

        if wait:
            proc.wait()

        return proc

    def _set_executable(self, bin_path):
        bin_path = os.path.join(self._sdk_path, bin_path)
        st = os.stat(bin_path)

        if not st.st_mode & stat.S_IEXEC:
            os.chmod(bin_path, st.st_mode | stat.S_IEXEC)

    def _get_env_vars(self):
        new_env = os.environ.copy()
        new_env["ANDROID_HOME"] = self._sdk_path
        new_env["ANDROID_SDK_HOME"] = self._sdk_path
        new_env["ANDROID_SDK_ROOT"] = self._sdk_path
        new_env["ANDROID_AVD_HOME"] = os.path.join(self._sdk_path, ".android/avd/")
        return new_env



if __name__ == "__main__":
    sdk = AndroidSDK()
    sdk.install()