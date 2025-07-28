import board
import displayio
import terminalio
import adafruit_displayio_sh1107
from adafruit_display_text import label
import time
import wifi
from secrets import secrets
import adafruit_requests
import ssl
import socketpool

# Display Initialisation
displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

WIDTH = 128
HEIGHT = 64
display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=WIDTH, height=HEIGHT, rotation=90
)

# WLAN Connection
print("Connecting to WLAN...")
try:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print("Connected")
except Exception as e:
    print("Failed to connect:", e)

# HTTP Session
pool = socketpool.SocketPool(wifi.radio)
httpsession = adafruit_requests.Session(pool, ssl.create_default_context())

# API URL
url = "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"

# Getting Data
try:
    response = httpsession.get(url)
    data = response.json()
    standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
except Exception as e:
    print("Failed to retrieve data:", e)
    standings = []

# Preparing Display Group
splash = displayio.Group()
display.root_group = splash

# Header
title = label.Label(terminalio.FONT, text="F1 Driver Standings", x=0, y=5)
splash.append(title)
empty_line = label.Label(terminalio.FONT, text =" ", x=0, y=5)
splash.append(empty_line)

# Show Top3 or error
if standings:
    max_drivers = min(3, len(standings))
    y_start = 30
    line_height = 14

    for i in range(max_drivers):
        pos = standings[i]["position"]
        driver = standings[i]["Driver"]
        name = f"{driver['familyName']}"
        points = standings[i]["points"]

        text = f"{pos}. {name[:12]} {points}P"
        text_area = label.Label(terminalio.FONT, text=text, x=0, y=y_start + i * line_height)
        splash.append(text_area)
else:
    err_label = label.Label(terminalio.FONT, text="Keine Daten", x=0, y=30)
    splash.append(err_label)


while True:
    pass