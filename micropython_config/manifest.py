"""
    Based on:
    micropython/ports/esp8266/boards/manifest_release.py
"""

# Include only needed files from ".../micropython/ports/esp8266/modules/":
#freeze('$(PORT_DIR)/modules', '_boot.py') # use own case of: https://github.com/micropython/micropython/pull/5509
freeze('$(PORT_DIR)/modules', 'flashbdev.py')
freeze('$(PORT_DIR)/modules', 'ntptime.py')


freeze('$(PORT_DIR)/sdist')  # project sources, mounted via docker


#freeze('$(MPY_DIR)/tools', ('upip.py', 'upip_utarfile.py'))
#freeze('$(MPY_DIR)/drivers/dht', 'dht.py')
#freeze('$(MPY_DIR)/drivers/onewire')
#include('$(MPY_DIR)/extmod/webrepl/manifest.py')

# drivers
# freeze('$(MPY_DIR)/drivers/display', 'ssd1306.py')

# file utilities
# freeze('$(MPY_LIB_DIR)/upysh', 'upysh.py')

# uasyncio
freeze('$(MPY_LIB_DIR)/uasyncio', 'uasyncio/__init__.py')
freeze('$(MPY_LIB_DIR)/uasyncio.core', 'uasyncio/core.py')

# requests
# freeze('$(MPY_LIB_DIR)/urequests', 'urequests.py')
# freeze('$(MPY_LIB_DIR)/urllib.urequest', 'urllib/urequest.py')

# umqtt with examples
# freeze('$(MPY_LIB_DIR)/umqtt.simple', 'umqtt/simple.py')
# freeze('$(MPY_LIB_DIR)/umqtt.robust', 'umqtt/robust.py')
# freeze('$(MPY_LIB_DIR)/umqtt.simple', 'example_pub_button.py')
# freeze('$(MPY_LIB_DIR)/umqtt.simple', 'example_sub_led.py')

# HTTP examples
# freeze('$(MPY_DIR)/examples/network', 'http_client.py')
# freeze('$(MPY_DIR)/examples/network', 'http_client_ssl.py')
# freeze('$(MPY_DIR)/examples/network', 'http_server.py')
# freeze('$(MPY_DIR)/examples/network', 'http_server_ssl.py')
