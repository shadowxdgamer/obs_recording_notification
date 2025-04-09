# OBS Recording Notification

A modern, Shadowplay-style notification for OBS Studio that shows when recording starts and stops.

![Notification Preview](Instructions/recording.PNG)

## Features

- **Modern Design**
  - Sleek dark theme with subtle borders
  - Rounded corners effect
  - Professional typography
  - Vibrant indicator colors (red for recording, green checkmark when saved)

- **Smooth Animations**
  - Elegant fade in/out transitions
  - 3 second display duration

- **Reliable Operation**
  - Only shows for actual recording events
  - Lightweight and efficient
  - Always stays on top of other windows

## Installation

1. Download the python-3.6.8-embed-amd64.rar that includes a Python compatible package with the necessary libraries.
2. Open OBS and go to Tools > Scripts
3. Configure the Python installation path by selecting the extracted folder
4. Go to Scripts tab, click the "+" button and add "obs_recording_notification.py"
5. Restart OBS Studio

![Python Setup](Instructions/python%20select.PNG)

## Requirements

- OBS Studio 28.0 or newer
- Python 3.6.8 with Tkinter support
- Windows operating system

## Preview

![Recording Started](Instructions/recording.PNG)
![Recording Saved](Instructions/recording_saved.PNG)

## Notes

- If you encounter any issues, restart OBS and check the script console
- The notification appears in the top-right corner by default
- Tested on Windows 10
