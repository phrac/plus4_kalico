# Qidi Plus 4 Mainline (vanilla) Klipper/Kalico Guide

# ![image](images/warning.gif) !!! DANGER - WARNING !!! ![image](images/warning.gif)
This is a work in progress. Do not use any of these configs or instructions unless you know what you're doing!
These modifications are for experienced users. If you are not comfortable with a command line, linux, and electronics, please stop here!

**ALSO NOTE: YOUR SCREEN WILL NOT WORK AFTER FOLLOWING THESE STEPS**

You could move to a Klipper screen setup to get a functioning screen. You could also check out [FreeDI](https://github.com/Phil1988/FreeDi) but it is not yet available for the Plus4.

---

# Introduction
Flashing mainline klipper/kalico on the Qidi Plus4 is relatively easy but does require some effort to flash the toolhead board. You will need an ST-Link programmer or clone to flash the toolhead.

# Backup
Before proceeding, backup any and all data in your printer configs, particularly your `printer.cfg`, `gcode_macros.cfg` and any other files
you may want to save. This can be done via the fluidd interface.

---

# Flashing the host with an updated Armbian image
## Tools required:
* USB EMMC reader such as [this one](https://www.amazon.com/Vacatga-Adapter-EMMC-Adapter-52-6x16x10mm-2-07x0-63x0-39in/dp/B0D1MY7943?gQT=1)
* A spare eMMC card (optional but recommended) if you want to preserve the original stock card

## Flashing Steps
1. Power down your printer and remove the eMMC card from the printer motherboard. It is held down with 2 screws.
2. Download one of the following images:
   - An older Q1 Pro image with KIAUH and Klipper preinstalled (https://github.com/frap129/armbian_qidi-q1-pro/releases).
   - A newer image with nothing preinstalled (https://github.com/redrathnure/armbian-mkspi/releases/download/mkspi%2F1.0.2-25.2.1/Armbian-unofficial_25.2.1_Mkspi_bookworm_current_6.12.12.img.xz)

   **Please Note: Many people have had problems getting the newer version to boot. This issues is being investigated. If your version doesn't boot, please try the Q1 Pro image.**
3. Write the image to your eMMC card via your preferred method (Balena Etcher, dd, etc)

    ### If you need wireless networking
    1. After writing the image to your eMMC card, open your file manager and open the `armbi_boot` drive.
    2. Rename the file `armbian_first_run.txt.template` to `armbian_first_run.txt`
    3. Open the file in a text editor, and add the SSID and Password for your wifi network. Find the line for enabling wifi and change 0 to 1.
        * `FR_net_change_defaults=1`
        * `FR_net_wifi_enabled=1`
        * `FR_net_wifi_ssid='MySSID'`
        * `FR_net_wifi_key='MyWiFiKEY'`
4. Unmount the eMMC card and re-install it into your printer and power on. If everything worked, you should now be able to access your printer via SSH.
5. SSH into your printer.
* If you're using the Q1 Image, the default username/password is `mks`. You will be asked to change your password on first login.
* If you're using the clean image, the default username is `root` and the password is `1234`
6. Install updates
    Lets make sure our system is up-to-date with the latest software. Note that this should NOT change your kernel.
    ```
    sudo apt update && sudo apt upgrade
    sudo apt install git -y
    ```

### Disable debug console
By default, the Plus4 uses `/dev/ttyS2` to communicate with the toolhead. The fresh armbian image you just flashed uses `/dev/ttyS2` as a
kernel debug console, so we need to disable that:
```
echo 'console=none' > sudo tee -a /boot/armbianEnv.txt

# Grant user permissions and prevent getty from taking over the port
echo 'KERNEL=="ttyS2",MODE="0660"' > /etc/udev/rules.d/99-ttyS2.rules
systemctl mask serial-getty@ttyS2.service
```
For more information on these changes, see here: https://github.com/frap129/armbian_qidi-q1-pro#disable-debug-console-uart2--or-freeup-uart1-interface

---

## Installing klipper/kalico, moonraker, fluidd/mainsail and friends
**NOTE THAT IF YOU INSTALLED THE Q1PRO IMAGE FROM ABOVE, YOU CAN SKIP THESE STEPS AS KLIPPER AND FRIENDS ARE ALREADY INSTALLED. CONTINUE ON TO MAINBOARD FLASHING**

Now that we have a clean, fresh system, we can start installing the software needed to run the printer. If you want to do this manually, you certainly can.
For everyone else, I recommend installing KIAUH.
## Installing KIAUH
KIAUH is a helper script to install klipper/kalico, mainsail, fluidd, crowsnest, moonraker, and many other things you may need or want.
The following steps will get KIAUH installed:
```
  cd ~
  git clone https://github.com/dw-0/kiauh.git
  ./kiauh/kiauh.sh
```
You will now be entered into the KIAUH main menu where you can install the software needed. At a minium install
* Klipper (or Kalico)
* moonraker
* fluidd (or mainsail)

KIAUH should automatically install all the required modules and start the services for you.

After everything is installed, we can move our backed up configurations over to the new setup:
Copy your `printer.cfg` and `gcode_macros` to `~/printer_data/config`

---

# Flashing the main MCU

## Flashing Katapult Deployer
These steps will build the Katapult deployer application. Make sure that you already have your ST-LINK programmer (or clone) on hand. If something goes wrong,
you will have to recover with the programmer. [Further details of Katapult deployer can be found here.](https://github.com/Arksine/katapult?tab=readme-ov-file#katapult-deployer)

1. SSH into your printer
2. Download Katapult and configure for the main board:
    ```
    cd ~/
    git clone https://github.com/Arksine/katapult
    cd katapult
    make menuconfig
    ```
    Once you are in `make menuconfig`, you want to build katapult with the following options:
    ![image](images/katapult_mainmcu.png)

    After you are sure your menuconfig matches the above settings, you can quit menuconfig (press q then y to save)
3. run `make -j4` to build katapult
4. Copy `~/katapult/out/deployer.bin` to your computer via your favorite method (scp, sftp, or using the fluidd interface)
5. On your computer, format the microSD card as FAT32
6. Copy the `deployer.bin` file to the microSD card and rename it `qd_mcu.bin`
7. Eject the microSD card and plug it into the microSD card slot on the printer.
8. Once the card is inserted, find the button labeled "RESET" on the main board and press it
9. Wait 30-60 seconds
    - You can verify that the flash worked by checking the file on the microSD card - it should be renamed to `qd_mcu.CUR`
10. Eject the microSD card. Katapult should now be flashed to the main MCU.

## Flashing Klipper on the main MCU

1. SSH into your printer
2. Install the `pyserial` Python package. This package is needed to run the katapult flashtool script.
   ```
   python -m pip install pyserial
   ```
4. Execute the following to build Klipper
    ```
    cd ~/klipper
    make menuconfig
    ```
    Configure the make arguments in `menuconfig` to match these settings:
    ![image](images/klipper_mainmcu.png)

5. Save and quit by pressing `q` then `y` to save
6. Build klipper by running `make clean; make -j4`
7. Prepare to flash. Double-click the "RESET" button on the board to load katapult. The button must be pressed twice within 500ms.
8. Flash via katapult by doing the following:
    ```
    cd ~/katapult/scripts
    python3 flashtool.py -b 500000 -d /dev/ttyS0 -f ~/klipper/out/klipper.bin
    ```
    You should see output similar to the following if the flash worked:
    ![image](images/flash_success-mainmcu.png)

9. Klipper is now flashed to the main MCU. We can now move on to the toolhead.

---

# Flashing the toolhead
The toolhead takes quite a bit more work to flash. You will need to solder some pins on the board and you will also need an ST-Link programmer (or clone).
The official ST-LINK programmer is what I used. You can purchase one from Digikey (or any other source). [This is the one I used](https://www.digikey.com/en/products/detail/stmicroelectronics/ST-LINK-V2/2214535)

## Preparing the toolhead
Begin by unsliding the back cover of the toolhead, disconnecting all connectors, and unscrewing the board from the toolhead.

Next, you need to solder a 6 pin header on the board like the below image:
![image](images/toolhead_with_pins.jpeg)

Once the header is soldered, we need to wire it to the ST-LINK:
![image](images/stlink-wiring.jpeg)

Use the following wiring diagram
![image](images/wiring-diagram.png)

```
This ASCII diagram is courtesy @transmutated
+-------- J1 6-Pin Connector --------+            +----- STLink V2 20-Pin Connector ------+
|                                    |            |                                       |
| Pin 1: DIO   ----------------------|------------| Pin 7: SWDIO / TMS7                   |
| Pin 3: CLK   ----------------------|------------| Pin 9: SWCLK / TCK9                   |
| Pin 5: RST   ----------------------|------------| Pin 15: MCU RST                       |
| Pin 6: GND   ----------------------|------------| Pin 12: GND                           |
| Pin 4: GND                         |            |                                       |
| Pin 2: 3V3   ----------------------|---+--------| Pin 1: VDD                            |
|                                    |   |        |                                       |
|                                    |   |--------| Pin 19: VDD                           |
+------------------------------------+            +---------------------------------------+
```

## Flashing Katapult on the toolhead
I used the printer itself to flash the toolhead but you can use any other computer available to build and flash.

1. Plug your ST-Link into the top usb port of the printer
2. Install the ST-Link tools: `sudo apt install stlink-tools`
3. Check that your ST-Link is recognized (and recognizing the toolhead): `st-info --probe`. You should see output similar to this:

  ![image](images/st-info.png)

  Note that your output might not match exactly. What you are looking for is that it found an stlink programmer, and it detects a chip (above we see `chipid: 0x0423` and `descr: F4xx`).
  If you don't see these things, double check your wiring.

4. Next, we need to build katapult for the toolhead:
    ```
    cd ~/katapult
    make menuconfig
    ```

    Make sure your menuconfig matches this:

    ![image](images/katapult-toolhead.png)

    ```
    make clean
    make -j4
    ```

5. Now we can flash katapult via the ST-Link:

    ```
    st-flash write ~/katapult/out/katapult.bin 0x8000000
    ```

    You should see a message like this:

    ![image](images/st-flash.png)

6. Unhook your ST-Link, and put the toolhead board back into the printer. Reconnect all wires and reboot the printer.

## Flashing Klipper on the toolhead
This is the same basic process that we used to flash klipper on the main MCU
1. Build klipper
    ```
    cd ~/klipper
    make menuconfig
    ```
    Your menuconfig should match this for the toolhead:

    ![image](images/klipper-toolhead.png)

    ```
    make clean
    make -j4
    ```
2. Double click the reset button on the toolhead within 500ms to enter Katapult
3. Flash klipper:
    ```
    cd ~/katapult/scripts
    python3 flashtool.py -b 500000 -d /dev/ttyS2 -f ~/klipper/out/klipper.bin
    ```
    You should see a successful flash like this:

    ![image](images/flash_success-toolhead.png)
4. Reboot the printer and you're done - you can now start configuring!

# Configuring the newly flashed printer

---
# Other References and Resources
- references from @transmutated - most likely the first person to flash the toolhead successfully: https://github.com/cgarwood82/plus4MainlineKlipperConfig/tree/main
- Open Q1 repo - the Q1 Pro uses the same main board as the plus4: https://github.com/frap129/OpenQ1/tree/main
