# -*- coding: utf-8 -*-

'''

=========whatsdump.py=========

Updated by Tkd-Alex

Github:https://github.com/Tkd-Alex/WhatsDump

Updated by Alex Green

'''

import argparse
import sys
import phonenumbers
import os
import re
import code
import time

from PyQt5 import QtWidgets,QtCore
from src.android_sdk import AndroidSDK
from src.whatsapp import WhatsApp, WaException,WaCommunicate
from adb.client import Client as AdbClient
from phonenumbers.phonenumberutil import NumberParseException
from variables import Variables

class DumpThread(QtCore.QThread):
    def __init__(self, target):
        QtCore.QThread.__init__(self)
        self.__target = target
    def run(self):
        try:
            self.__target()
        except BaseException as e:
            raise DumpException(str(e))

class Communicate(QtCore.QObject,
                  Variables):
    setStatusBar = QtCore.pyqtSignal()
    setCode      = QtCore.pyqtSignal()

class DumpException(Exception):
    def __init__(self, text):
        self.txt = text

def wa_code_callback(variables):
    code = variables.getVerifyCode()
    code = re.sub(r'-\s*', '', code)
    return code

def check_sdk(sdk):
    # SDK Checks
    return sdk.is_avd_installed()

def Whatsdump(argv,variables,communicate):
    phone         = None
    source_device = None
    sdk           = AndroidSDK()

    def setStatus_inMainWindow(status):
        variables.setStatusBar(status)
        communicate.setStatusBar.emit()

    parser = argparse.ArgumentParser(prog = "WhatsDump")

    parser.add_argument("--check-sdk", action = "store_true")
    parser.add_argument("--install-sdk", action = "store_true")
    parser.add_argument("--msgstore")
    parser.add_argument("--wa-phone")
    parser.add_argument("--wa-verify", choices = ["sms", "call"])
    parser.add_argument("--verbose", action = "store_true")
    parser.add_argument("--show-emulator", action = "store_true")
    parser.add_argument("--no-accel", action = "store_true")

    args = parser.parse_args(argv)

    #Check if jdk is installed

    if args.check_sdk:
        if check_sdk(sdk):
            raise DumpException("WhatsDump SDK already installed!")
        else:
            raise DumpException("WhatsDump SDK is not installed!Install Android SDK.")

    if args.install_sdk:
        if check_sdk(sdk):
            raise DumpException("WhatsDump AVD already installed!\nRemove android-sdk/directory to reinstall Android SDK")

        # Download and install SDK
        if not sdk.install():
            raise DumpException("Failed to install Android SDK")

        raise DumpException("\nAndroid AVD successfully installed")
    else:
        if not check_sdk(sdk):
            raise DumpException("Cannot find WhatsDump AVD.\nInstall Android SDK.")

    # Connect / Start ADB server
    adb_client = AdbClient()

    try:
        setStatus_inMainWindow("[WhatsDump]:Connected to ADB @ 127.0.0.1:5037")
        adb_client.version()
    except:
        setStatus_inMainWindow("[WhatsDump]:Attempting to start ADB server...")

        if sdk.start_adb():
            setStatus_inMainWindow("[WhatsDump]:ADB server started successfully")
            adb_client = AdbClient()

            setStatus_inMainWindow("[WhatsDump]:Connected to ADB @ 127.0.0.1:5037" )
        else:
            raise DumpException("Could not connect/start ADB server")

    # Start emulator and connect to it
    setStatus_inMainWindow("[WhatsDump]:Starting emulator...")

    if args.no_accel:
        raise DumpException("Hardware acceleration disabled! Device might be very slow")

    emulator_device = sdk.start_emulator(adb_client, args.show_emulator, args.no_accel)

    if not emulator_device:
        raise DumpException("Could not start emulator!")

    if args.show_emulator:
        setStatus_inMainWindow("[WhatsDump]:Do not interact with the emulator!")

    # Require msgstore or connected device
    if args.msgstore:
        # Check if file exists
        if not os.path.isfile(args.msgstore):
            raise DumpException("Msgstore location is not valid (file does not exist)")
    else:
        setStatus_inMainWindow("[WhatsDump]:Msgstore location not provided, attempting to find connected devices with ADB...\n")

        devices = adb_client.devices()
        i = 0

        # If no devices and no msgstore, quit
        if len(devices) == 0:
            raise DumpException("Cannot find any connected devices")

        # Show all devices
        for device in devices:
            if 'emulator' in str(device.serial):
                dev_index = i

                if dev_index < 0 or dev_index + 1 > len(devices):
                    continue

                source_device = devices [dev_index]

            # Index of devices
            i += 1

    # Validate required phone
    if not args.wa_phone:
        raise DumpException("Please provide the phone number associated with msgstore")
    else:
        # Add "+" if not given
        if args.wa_phone [0] != "+":
            args.wa_phone = "+" + args.wa_phone

        try:
            phone = phonenumbers.parse(args.wa_phone)
        except NumberParseException:
            pass

        if not phone:
            raise DumpException("Provided phone number is NOT valid")

    if not args.wa_verify:
        raise DumpException("Please provide a WhatsApp verification method")

    if source_device:
        setStatus_inMainWindow(str("[WhatsDump]:Extract WhatsApp database from device >>" + source_device.serial))
    else:
        setStatus_inMainWindow(str("[WhatsDump]:Using msgstore database from path:" + args.msgstore))

    setStatus_inMainWindow(str("[WhatsDump]:Using WhatsApp phone number:" +
                            str(phone.country_code) + str(phone.national_number)))
    setStatus_inMainWindow(str("[WhatsDump]:Using WhatsApp verification method:" + args.wa_verify.upper()))

    # create phone directory tree where to store results
    dst_path = os.path.join(os.path.abspath("output"), str(phone.country_code) + str(phone.national_number))
    if not os.path.exists(dst_path):
        try:
            os.makedirs(dst_path)
        except OSError:
            raise DumpException("Cannot create output directory tree")

    # Extract msgstore.db from source device, if any
    msgstore_path = ''.join((dst_path, '\\files\\Databases\\msgstore.db.crypt12'))

    setStatus_inMainWindow("[WhatsDump]:Trying to register phone on emulator... (may take few minutes)")

    # Attempt to register phone using provided msgstore
    wa_emu = WhatsApp(emulator_device,communicate = communicate,variables = variables)
    sdk.adb_root()  # Allowing adb as root

    time.sleep(10)

    try:
        wa_emu.register_phone(msgstore_path, phone.country_code, phone.national_number)
        communicate.setCode.emit()
        # Verify by call or SMS
        if args.wa_verify == "sms":
            setStatus_inMainWindow("[WhatsDump]:You should receive a SMS by WhatsApp soon")

            wa_emu._verify_by_sms(code_callback = wa_code_callback,variables = variables)
        else:
            setStatus_inMainWindow("[WhatsDump]:You should receive a call by WhatsApp soon")
            wa_emu._verify_by_call(code_callback = wa_code_callback,variables = variables)

        wa_emu.complete_registration(phone.country_code, phone.national_number)

    except WaException as e:
        raise DumpException(("Exception in verification: %s", e.reason))

    setStatus_inMainWindow("[WhatsDump]:Phone registered successfully!")
    setStatus_inMainWindow("[WhatsDump]:Extracting key...")

    # Extract private key
    if not wa_emu.extract_priv_key(dst_path):
        raise DumpException("Could not extract private key!")

    setStatus_inMainWindow(str(''.join(("[WhatsDump]:Private key extracted in ",os.path.join(dst_path),"\\key"))).replace('\\', '/'))
