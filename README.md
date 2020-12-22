Raspberry Pi with HDMI-connected TV used to run a looping [Aquarium movie](https://www.uscenes.com/download/aquarium-video/), a optional button could be used to randomize movie to play.
The mp4-movies and the fishtank.py-script could be mounted on a USB-disk for easy upgrade of clips, and preventing SD-card wear.

Button is connected between +5v pin and GPIO #14-pin (see script if you want to change)

1. Edit "sudo nano /boot/config.txt" and make sure "gpu_mem=128"
2. "sudo apt update"
3. "sudo apt upgrade"
4. "sudo install omxplayer screen python3 python-rpi.gpio python3-rpi.gpio"
5. Run "sudo rpi-update" to make sure you have the latest firmware (fixes glitches with blinking green screen).
6. Edit "sudo nano /etc/fstab" and enter:
"PARTUUID=<id of USB-drive>  /media/FISHDISK vfat    defaults,noatime,ro  0       0"
7. "chmod 755 fishtank.py"
8. Run script "./fishtank.py"
