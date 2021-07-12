###  General Information
  WDE Software (_WhatsDumpExtractor_) is a set of software modules written in Python, linked to each other to extract the encrypted database WhatsApp from Google Drive, decrypt and provide it to the user. 
  WDE uses android emulator to authorize a user on the WhatsApp server and obtain a key file to decrypt the database. To install android emulator, you must download Android SDK from the official site of Android Studio. 
At the end of the program, the document generated from the decrypted database will be displayed.
To write a UI application with a set of bindings of the graphical framework PyQt5.

### Preparation setting
  Before starting with WDE Software, you must have python 3 installed. * (version 3.8.8 was used at the time of release).
It is necessary to download and install Intel Hardware Accelerated Execution Manager (HAXM). HAXM installation packages for Windows can be found on the page of releases GitHub devoted to <a href= https://github.com/intel/haxm/releases>Intel Hardware Accelerated Execution Manager</a>. Running android emulator uses x86-based system image. If uses an image of a system on the basis of ARM,it will work incorrectly. 
  Also must be install jdk-1.8. * .The version above or below,WDE will work incorrectly. At the time of release used "jdk 1.8.0_281".JDK is located <a href="https://gist.github.com/wavezhang/ba8425f24a968ec9b2a8619d7c2d86a6">on the page GitHub Gist</a>
  Make sure that the env variables(ANDROID_HOME,ANDROID_SDK_HOME,ANDROID_AVD_HOME) specified correctly.The android-sdk folder should appear after installation in the folder with the project. After creation AVD should appear in the .android folder inside the android-sdk folder.
  Before dump of WhatsApp,necessary get access of Google account from third-party devices. To do this, needs to login through any browser available Google account and click this link: https://accounts.google.com/b/0/DisplayUnlockCaptcha.

### Getting Started
Menu bar: 
  The SDK menu is required to check for Android SDKs installed and for installation SDK/AVD. Click "Install SDK" to start the installation. After that,wait dialog information window about success install of SDK/AVD. 
  The file menu includes: 
	

1. open .html document
2. encryption of .crypt12.Decryption requires an encrypted database, key and path to save the decrypted .db file.
3. converts the .db file to .html for reading of the database WhatsApp

  Action "New Dump" starts the key extraction process from the emulator android.First necessary make a presetting. To start the process,enter the phone number (the key of which will be extracted), the Google (Gmail) account on the disk of which the encrypted database and password from this account are stored. After launch, the databases from Google Drive will be downloaded and the android emulator will be launched. Then enter the verifycation code WhatsApp which will be sent via SMS to the specified number. At the end, the decrypted database is displayed for reading.

### WDE modules
WDE Software includes 5 main modules:

- <a href="https://github.com/MarcoG3/WhatsDump">whatsdump.py</a>
- <a href="https://github.com/YuriCosta/WhatsApp-GD-Extractor-Multithread">WhatsAppGDExtract.py</a>
- <a href="https://github.com/EliteAndroidApps/WhatsApp-Crypt12-Decrypter">decrypt12.py</a>
- <a href="https://github.com/fingersonfire/Whatsapp-Xtract">whatsapp_xtract.py</a>
- <a href="https://github.com/Vetalb60/WhatsDumpExtractor">whatsdumpextractor.py</a>


### Get Help
  Send questions to gmail: al9xgr99n@gmail.com

Author:Alex Green
