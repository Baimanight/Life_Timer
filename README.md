# Life Timer [Linux]

A minimalist Python-based break reminder.

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
```

### Usage
```bash
Life 1s/2m/3h
```
On the first run of the day, it will print a summary

[]()

