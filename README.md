# Razer Audio Mixer - Linux Daemon

A Python-based daemon to control the Razer Audio Mixer (RZ19-0386) on Linux (PulseAudio/PipeWire). 

This script:
- Maps the 4 faders to 4 virtual virtual sinks (System, Game, Chat, Music).
- Mixes all 4 virtual sinks into a single hardware output (Pro Audio 0/1).
- Unmutes and sets hardware volumes to 100% on startup.
- Handles both 0-100 and 0-255 HID volume scales.

## Requirements

- Python 3.8+
- `hidapi` (Python library: `pip install hidapi`)
- `pactl` (PulseAudio/PipeWire CLI)
- `amixer` (ALSA CLI)

## Installation

1. Install dependencies:
   ```bash
   pip install hidapi
   ```
2. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_GITHUB_USER/razer-audio-mixer-linux.git
   cd razer-audio-mixer-linux
   ```
3. Run the daemon:
   ```bash
   python main.py
   ```

## Auto-start with systemd

To run this automatically when your computer starts:

1. Copy `razer-mixer.service` to `~/.config/systemd/user/`:
   ```bash
   mkdir -p ~/.config/systemd/user/
   cp razer-mixer.service ~/.config/systemd/user/
   ```
2. Enable and start the service:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable razer-mixer.service
   systemctl --user start razer-mixer.service
   ```

## License

MIT
