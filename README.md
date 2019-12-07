# micropython-sonoff-webswitch

Minimal MicroPython project to get a webserver on Sonoff WiFi Smart Socket.

Tested devices:

* Sonoff S20 (Easy to connect. Solder joints prepared.)
* Sonoff S26 (Harder to connect: Solder joints very small.)

## Features

* web interface
* schedule multiple timers
* OTA updates
* turn the switch on/off by the web page or the device button
* Reset the device by long pressing the button
* supports multiple WIFI credentials

The device will do this on every boot:

* boot
* connect to your WiFi
* get current time via ntp
* make OTA Update
* serve web page


## Screenshot

The Web Page looks like this:

![Screenshot_2019-12-02 Sonoff S20.png](https://raw.githubusercontent.com/jedie/micropython-sonoff-webswitch/master/Screenshot_2019-12-02%20Sonoff%20S20.png)


## prepare

* Open the device
* make a connection with a UART-USB converter with 3.3V option and to the `3.3V`, `GND`, `TX` and `RX` pins

Very good information to get started can you found here: https://github.com/tsaarni/mqtt-micropython-smartsocket

* Flash last MicroPython firmware to your device, see: http://docs.micropython.org/en/latest/esp8266/tutorial/intro.html


### config.json

To connect the device with your WIFI it needs the SSID/password.
Several WLAN network access data can be specified.

Copy and edit [config-example.json](https://github.com/jedie/micropython-sonoff-webswitch/blob/master/config-example.json) to `src/config.json`


## quickstart

Clone the sources, and setup virtualenv via `pipenv`:
```bash
~$ git clone https://github.com/jedie/micropython-sonoff-webswitch.git
~$ cd micropython-sonoff-webswitch
~/micropython-sonoff-webswitch$ pipenv sync
~/micropython-sonoff-webswitch$ pipenv run start_ota_server.py
```

* Create a `src/config.json` with your WiFi SSID/password ([See example file](https://github.com/jedie/micropython-sonoff-webswitch/blob/master/config.json))

### bootstrap

Bootstrap a new, fresh, empty device:

Connect device via TTL-USB-converter to your PC and run [upload_files.py](https://github.com/jedie/micropython-sonoff-webswitch/blob/master/upload_files.py)

This script will do this:

* compile `src` files with [mpy-cross](https://pypi.org/project/mpy-cross/) to `bdist`
* upload all files from `bdist` to the device via [mpycntrl](https://github.com/kr-g/mpycntrl)


### OTA updates

After the initial setup and when everything is working and the device is connected to your wlan, you can use OTA updates.

The device will run the [/src/ota_client.py](https://github.com/jedie/micropython-sonoff-webswitch/blob/master/src/ota_client.py) on every boot.

The script waits some time for the OTA server and after the timeout the normal web server will be started.

To start the `OTA Server`, do this:

```bash
~$ cd micropython-sonoff-webswitch
~/micropython-sonoff-webswitch$ pipenv run start_ota_server.py
```

If server runs: reboot device and look to the output of the OTA server.

## project structure

* `./bdist/` - Contains the compiled files that will be uploaded to the device.
* `./helpers/` - Some device tests/helper scripts for developing (normaly not needed)
* `./ota/` - source code of the OTA server
* `./src/` - device source files
* `./tests/` - some pytest files
* `./utils/` - utils for local run (compile, code lint, sync with mpycntrl)
* `./start_ota_server.py` - Starts the local OTA server (will compile, lint the `src` files and create `bdist`)
* `./upload_files.py` - Upload files via USB (will compile, lint the `src` files and create `bdist`)


## Links

### Forum links

* OTA updates: https://forum.micropython.org/viewtopic.php?f=2&t=7300
* free RAM: https://forum.micropython.org/viewtopic.php?f=2&t=7345

### misc

* S20 Wifi Smart Socket Schematic: https://www.itead.cc/wiki/S20_Smart_Socket
