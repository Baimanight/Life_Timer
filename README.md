# Life Timer [Linux]

A minimalist Python-based break reminder for Ubuntu/GNOME. It provides a terminal countdown and a graphical popup to help reclaim your rhythm from intensive work.

## Prerequisites
Install the required image processing libraries:
```bash
sudo apt update
sudo apt install python3-pil python3-pil.imagetk
```
### Setup & Customization
- Save Script: Save your script as Life.py in your home directory.
- Custom Paths: Open Life.py and set your preferred directories:
- IMAGE_DIR: Folder containing your background photos.
- HISTORY_FILE: Location for the .json statistics log.
- Add Alias: Add the following to your ~/.bashrc to ensure the timer persists after closing the terminal.
```bash
# Path defaults to ~/Life.py; adjust if you saved it elsewhere
echo "alias Life='nohup python3 ~/Life.py \"\$1\" >/dev/null 2>&1 & disown'" >> ~/.bashrc
source ~/.bashrc
```bash

### Usage
```bash
Life 25m    # 25 minutes for focused study or TOEFL practice
Life 1h     # 1 hour for deep geophysical data analysis
Life 10s    # Quick functionality test
```bash
