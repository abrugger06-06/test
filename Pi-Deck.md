# Pi Deck

A laptop-style, 3D-printed, solar-charged offline library built on a Raspberry Pi 4. It serves offline Wikipedia, maps, medical and repair guides, and courses to its own touchscreen and to any phone over its own Wi-Fi hotspot, with no internet needed.

- **Status:** rev 13 (Nov 15, 2026). Includes the fixes from the Fable design review, plus rev 13 doc fixes: the fan behaviour is described correctly, runtime figures agree, and there's a full-load undervoltage test, a serial-port note and a wake-button note. **Not printed or bench-tested yet.**
- **3D viewer:** https://claude.ai/artifact/TXjbNp5akn7R144BXXhnQ1
- **Model files:** `C:\Users\abrug\jarvis\pi-deck-case\` (the parametric script `pi_deck_case.py`, STLs, the Blender assembly and a GLB)

---

## 1. At a glance

| | |
|---|---|
| Size closed | 300 x 223 x 70 mm (11.8 x 8.8 x 2.8 in), plus a 40 mm handle on the left |
| Computer | Raspberry Pi 4B running Raspberry Pi OS and Internet-in-a-Box |
| Screen | Raspberry Pi Touch Display 2, 7 inch, 1280 x 720, in the lid |
| Keyboard | Logitech Pebble Keys 2 K380s (Bluetooth), on a lift-out tray |
| Storage | SanDisk 1 TB portable SSD (operating system and all content) |
| Power | Anker Zolo 20,000 mAh (about 74 Wh, about 60 Wh usable); runs about 5 to 6 hours in normal use, longer when idle with the screen off |
| Solar | 12 W USB-C panel. It stores in the lid and sets out in the sun on a 2 m cable. |
| Outside ports (right side) | Phone charging (USB-A), USB 3, USB, Ethernet, USB-C charge input |
| Controls | Power button top-right of the keyboard (shutdown and wake); inline on/off switch inside (hard power cut) |
| Lid | 2 M4 hinges, magnetic lock with 4 latch points (16 magnets) and 2 alignment pins |
| Cooling | Floor intake on 8 mm feet, rear exhaust fan (slow below 60 C, full speed above), Pi heatsink fan |
| Material | PETG for the case, TPU for the port covers and feet |

**Why Internet-in-a-Box and not Project NOMAD:** NOMAD only installs on Intel/AMD PCs. Internet-in-a-Box runs on the Pi and gives the same core content (Kiwix Wikipedia, Kolibri courses, OpenStreetMap maps, reference guides) without NOMAD's AI.

---

## 2. Shopping list (28 items, about $568 before tax)

Prices are what Amazon showed on Nov 14 to 15, 2026. **Nothing has been bought.** You already have the Pi 4B, the 6 x 3 mm magnets, PETG and TPU.

### Electronics
| Part | Link | Price |
|---|---|---|
| Raspberry Pi Touch Display 2, 7 inch | https://www.amazon.com/dp/B0DM24QFCF | $105.02 |
| Logitech Pebble Keys 2 K380s | https://www.amazon.com/dp/B0BT4DP7SC | $33.99 |
| SanDisk 1TB Portable SSD | https://www.amazon.com/dp/B0H3XD9351 | $129.99 |
| Anker Zolo 20,000 mAh 30W power bank | https://www.amazon.com/dp/B0CZ9LH53B | $42.99 |
| 12W 5V USB-C solar panel, 9.4 x 6.9 in | https://www.amazon.com/dp/B0GCHZPNQ4 | $29.99 |
| GeeekPi Armor Lite heatsink with PWM fan (Pi 4) | https://www.amazon.com/dp/B091L1XKL6 | $11.99 |
| GeeekPi 40 mm 5V PWM fans, 2-pack (1 used, 1 spare) | https://www.amazon.com/dp/B092YXQMX5 | $10.99 |
| Pi 5 display ribbon, 22 to 15 pin, **300 mm**, 2-pack | https://www.amazon.com/dp/B0D6B5LJ93 | $12.99 |
| SanDisk 32GB microSD (bootloader update, backup boot) | https://www.amazon.com/dp/B08L5HMJVW | $21.91 |
| 12 mm momentary push buttons, pre-wired, 5-pack | https://www.amazon.com/dp/B08L49F7DV | $7.99 |

### Cables and sockets
| Part | Link | Price |
|---|---|---|
| USB 3.0 panel-mount extension, 1 ft, 2-pack | https://www.amazon.com/dp/B0H2HFTG17 | $9.99 |
| USB 3.0 panel-mount extension, 30 cm, single | https://www.amazon.com/dp/B07LBFPG16 | $8.99 |
| RJ45 panel-mount extension, 1 ft, 2-pack | https://www.amazon.com/dp/B06Y4J9MZ4 | $8.99 |
| USB-C panel-mount extension, 1 ft (charge socket) | https://www.amazon.com/dp/B08HS6X44P | $9.69 |
| USB-C extension, 2 m (solar panel lead) | https://www.amazon.com/dp/B09VKY632R | $7.99 |
| USB-C inline on/off switch cable, 1 ft | https://www.amazon.com/dp/B0H23FC8TN | $13.99 |
| USB-A to USB-C adapter cable, 9 in, 2-pack (SSD) | https://www.amazon.com/dp/B07M999Y6T | $9.99 |
| Right-angle USB-C to USB-C, 1 ft, 2-pack (spares) | https://www.amazon.com/dp/B0FR4TWCFB | $11.99 |

### Hardware
| Part | Link | Price |
|---|---|---|
| Dupont jumper wires, 120 pieces | https://www.amazon.com/dp/B01EV70C78 | $6.98 |
| M2.5 brass standoff kit | https://www.amazon.com/dp/B0F6MNBQVL | $9.99 |
| M2.5 screw kit (4 to 20 mm, nuts, washers) | https://www.amazon.com/dp/B0B88RFGY9 | $9.98 |
| M4 x 70 mm socket bolts (hinge pins) | https://www.amazon.com/dp/B0DFYP9HNN | $6.89 |
| M4 nylon lock nuts | https://www.amazon.com/dp/B075ZZD3NN | $4.99 |
| M4 socket screw kit (handle bolts) | https://www.amazon.com/dp/B0FG2D92BV | $9.99 |
| M4 flat washers | https://www.amazon.com/dp/B0BGH6YLB7 | $4.99 |
| M3 x 10 mm self-tapping screws | https://www.amazon.com/dp/B0HGQKGLS3 | $6.99 |
| 3M double-sided foam tape | https://www.amazon.com/dp/B0DJLR75H9 | $9.99 |
| Small 4 in zip ties | https://www.amazon.com/dp/B0C2KGK2HR | $7.99 |

---

## 3. Printed parts

These need the **Bambu H2C** (305 x 320 mm bed). The base, lids and tray are too big for the A1 and P2S.

| File | Qty | Size (mm) | Material | Orientation and notes |
|---|---|---|---|---|
| `base.stl` | 1 | 300 x 223 x 53 | PETG | Floor down. Use corner brim ears in Y; there's only about 2 mm of room in X. |
| `lid_front.stl` | 1 | 300 x 223 x 18 | PETG | Screen face down. Supports on the build plate only, under the hinge knuckles. |
| `lid_back.stl` | 1 | 300 x 213 x 13 | PETG | Flat side down |
| `keyboard_tray.stl` | 1 | 280 x 125 x 2.5 | PETG | Flat |
| `bay_cover.stl` | 1 | 293 x 77 x 2 | PETG | Flat |
| `handle.stl` | 1 | 40 x 126 x 31 | PETG | As exported |
| `panel_clip_x4.stl` | 4 | 22 x 22 x 2.5 | PETG | Flat |
| `display_spacer_x4.stl` | 4 | 12 x 9 x 4 | PETG | Flat |
| `port_cover_usb_x3_TPU.stl` | 3 | 9 x 27 x 6 | TPU 95A | Flat, plug up, 20 to 30 mm/s |
| `port_cover_rj45_x1_TPU.stl` | 1 | 18 x 28 x 6 | TPU 95A | Flat, plug up |
| `foot_x4_TPU.stl` | 4 | 13 x 13 x 9 | TPU 95A | Upright |

- **Settings:** PETG at 0.2 mm layers, 4 walls, 15 to 20% gyroid infill. That's about 600 g of PETG and a little TPU.
- **Test first:** print just a hinge section and one port cutout before the big parts.

---

## 4. Layout

```
                 REAR (hinge)
 +-----------------------------------------------------+
 | [Power bank  ->]  [rear exhaust fan]   [ Pi 4 -> ] || <- right side I/O:
 |  % window in cover       hinge barrel   GPIO       ||    phone USB-A, USB 3,
 |                        + ribbon slot   heatsink    ||    USB, Ethernet
 |------------------------ divider -------------------||
 |                                     (button, top) ||
 |   [ K380s keyboard on lift-out tray ]              || <- USB-C charge socket
 |   SSD cradle + cables underneath                   ||    (below the tray)
 +-----------------------------------------------------+
 handle on the left side                FRONT (thumb scoop)
```

- **Lid:** the screen sits behind a bezel and is screwed to the lid back through its 4 mounting tabs, which are 140 x 70.7 mm apart. The solar panel stores in a flush pocket on the back of the lid, held by 4 turn clips.
- **Base:**
  - The keyboard sits 2 mm below the rim, with the SSD in a cradle underneath.
  - The power bank runs along the left wall, held by stop ribs, with a window in the cover over its charge display.
  - The Pi sits on printed standoffs.
  - Panel-mount sockets bring the ports out the right side.

---

## 5. Wiring

| From | To | Cable |
|---|---|---|
| Power bank built-in USB-C | Inline on/off switch, then Pi 4 USB-C | Built-in cable plus the 1 ft switch cable |
| Outside USB-C socket (right side) | Power bank USB-C port | 1 ft USB-C panel-mount extension, under the tray |
| Solar panel (outside, in the sun) | Outside USB-C socket | Panel cable plus the 2 m extension |
| Power bank USB-A | Side socket 1 (phone charging) | 30 cm USB 3.0 panel-mount extension |
| Pi blue USB 3 port (upper) | Side socket 2 (USB 3) | 1 ft USB 3.0 panel-mount extension |
| Pi black USB 2 port | Side socket 3 (USB) | 1 ft USB 3.0 panel-mount extension |
| Pi Ethernet | Side socket 4 (Ethernet) | 1 ft RJ45 panel-mount extension |
| SanDisk SSD | Pi blue USB 3 port (lower) | 9 in USB-A to USB-C adapter cable, through the divider notch |
| Pi DSI port | Touch Display 2 | **300 mm** ribbon. It goes flat through its own slot by the hinge and bends around the hinge axis; leave about a 25 mm loop. |
| Pi GPIO 5V and GND | Screen power socket | 2 jumpers, through the hinge barrel |
| Power button | Pi GPIO3 and GND | Button leads, under the bay cover |
| Rear exhaust fan | Pi 5V, GND and GPIO14 (PWM wire: low or full) | Fan lead |
| Heatsink fan | Pi 5V and GND | Short lead |

**GPIO pins used**

| Pin | Use |
|---|---|
| 2 (5V) | Rear fan and heatsink fan |
| 4 (5V) | Screen power |
| 5 (GPIO3) | Power button (shutdown and wake) |
| 6 (GND) | Screen ground |
| 8 (GPIO14) | Rear fan PWM wire, switched on/off by `gpio-fan` (keep the serial port off; see section 7) |
| 9 (GND) | Power button ground |
| 14 (GND) | Rear fan ground |
| 20 (GND) | Heatsink fan ground |

Fasten the runs to the 4 zip-tie anchors on the floor. Put plugs on the fan and button wires so the bay cover comes off cleanly.

---

## 6. Assembly order

1. **Measure first:** the screen tabs, keyboard, solar panel, power bank and sockets. Edit the PART SIZES block in `pi_deck_case.py` and rebuild if anything differs. The rebuild takes about a minute in Blender.
2. **Print** the test hinge section and an I/O cutout, then all the parts.
3. **Magnets:** 16 in total, 2 stacked in each pocket. Stack each base pair onto its lid pair so they attract, mark the faces that touch, then glue them in with CA glue or epoxy, facing that way.
4. **Base hardware:**
   - Fit the TPU feet into the floor sockets.
   - Bolt the handle on with 4 M4 x 20 bolts, heads inside the loop and nuts inside the base under the tray.
   - Screw the 4 I/O sockets and the USB-C charge socket on with M3 self-tapping screws.
   - Fit the rear fan so it blows outward.
5. **Electronics:**
   - Mount the Pi on its standoffs with the heatsink fitted.
   - Put the power bank against the left wall.
   - Put the SSD in its cradle.
   - Wire everything per section 5, with the inline switch on the Pi power cable.
6. **Lid:**
   - Seat the screen in the bezel frame.
   - Put a 4 mm spacer on each tab, then screw the lid back on with 6 M3 screws plus 4 M2.5 screws with washers into the screen tabs.
   - Set the panel in its pocket with the 4 clips.
7. **Hinge:**
   - Feed the screen power pair through the barrel.
   - Lay the ribbon flat through its slot and leave a loop.
   - Fit the M4 x 70 bolts with a washer in every knuckle gap, then tighten the nylocs until the lid holds its angle.
8. **Finish:** fit the bay cover and the power button, hang the TPU port covers from the top screw of each socket, and drop the keyboard onto the tray.

---

## 7. Software setup

1. **Write the system:** use Raspberry Pi Imager to write **Raspberry Pi OS (64-bit)** to the SSD. Boot with no microSD card in. If the Pi won't boot from USB, write Imager's "Bootloader > USB Boot" image to the microSD, boot from it once, then remove it.
2. **Settings:** add these lines to `/boot/firmware/config.txt`:
   ```
   dtoverlay=vc4-kms-dsi-ili9881-7inch       # Touch Display 2 on a Pi 4
   dtoverlay=gpio-shutdown                   # power button on GPIO3: press to shut down, press to wake
   dtoverlay=gpio-fan,gpiopin=14,temp=60000  # rear fan full speed above 60 C
   ```
   - `gpio-fan` is on/off only: it drives the fan's PWM wire fully high or fully low. Most PWM fans keep turning slowly when that wire is low, so expect a quiet idle spin below 60 C, not silence. If you want the fan fully off, switch its 5V line with a logic-level MOSFET driven by GPIO14 instead.
   - GPIO14 is also the serial port's transmit pin. Keep the serial port off (it is by default): `sudo raspi-config` > Interface Options > Serial Port > No login shell, No hardware port. Otherwise the fan pulses during boot.
3. **Install Internet-in-a-Box:** run `curl d.iiab.io/install.txt | sudo bash` and choose the MEDIUM install.
4. **Load content** at `http://box.lan/admin`:
   - Wikipedia (maxi, about 100 GB)
   - WikiMed, iFixit, Wikivoyage and Gutenberg
   - OpenStreetMap for Texas or the US
   - Kolibri channels
5. **Pair the K380s** in Bluetooth settings. Phones join the `Internet in a Box` Wi-Fi and open `http://box.lan`.

---

## 8. Bench tests before printing the big parts

1. **Pass-through power:** with the Pi running from the power bank, plug and unplug a charger (or the panel) and a phone 20 times. Then run `vcgencmd get_throttled`; it should read `0x0`. If the Pi reboots or shows undervoltage, that power bank isn't suitable.
2. **Full-load voltage:** the power bank puts out 5.0 V and the Pi 4 wants 5.1 V, and the screen, both fans and the SSD all draw through the Pi. Run the screen at full brightness, keep the SSD busy (for example `sudo dd if=/dev/sda of=/dev/null bs=1M count=20000`), load the CPU with `stress-ng --cpu 4 --timeout 10m` (install it first with `sudo apt install stress-ng`), then check `vcgencmd get_throttled`. It should read `0x0`. If it shows undervoltage (bit 0 or bit 16 set), remove the inline switch cable first and run the Pi straight from the bank's built-in cable.
3. **Power draw:** with everything running, it should draw about 9 to 12 W. With about 60 Wh usable, that gives about 5 to 6.5 hours on battery alone.
4. **Heat:** run it closed in a warm room and watch `vcgencmd measure_temp`. It should stay under about 75 C.

---

## 9. Known limits

- **Sizes aren't measured:** every size comes from listings or the official Touch Display 2 drawing.
- **Solar placement:** the panel charges best set out in the sun on its cable, with the case in the shade. A hot case in direct sun can stop the power bank from charging.
- **Hinge stop:** there's no separate lid stop. The hinge blocks stop the lid at about 150 degrees, so don't force it past that.
- **Charging from the wall:** use the right-side USB-C socket.
- **Power button vs. switch:** the button only wakes the Pi while it still has power. If the inline switch is off, the button does nothing. Shut down with the button, then turn the switch off for storage, and back on to start.
- **Spare parts:** the second 40 mm fan and the right-angle USB-C cables are spares.
- **History:** the full revision notes (rev 1 to 12) are in `README.md` next to this file.
