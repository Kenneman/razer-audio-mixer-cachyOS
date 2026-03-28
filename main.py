import hid
import subprocess
import time
import sys
import os

# Konfiguration
VENDOR_ID = 0x1532
PRODUCT_ID = 0x053e

# De virtuella namnen
SINKS = ["razer_system", "razer_game", "razer_chat", "razer_music"]

def run_cmd(cmd):
    try:
        return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode().strip()
    except:
        return ""

def setup_hardware():
    print("--- Återställer ljudrouting (v6) ---")
    
    # 1. Sätt Pro Audio profil
    run_cmd("pactl set-card-profile alsa_card.usb-Razer_Razer_Audio_Mixer-00 pro-audio")
    time.sleep(1)
    
    # 2. Hårdvaru-sinks (vi testar båda för säkerhets skull)
    HW_SINK_0 = "alsa_output.usb-Razer_Razer_Audio_Mixer-00.pro-output-0"
    HW_SINK_1 = "alsa_output.usb-Razer_Razer_Audio_Mixer-00.pro-output-1"
    
    # 3. Rensa allt gammalt
    modules = run_cmd("pactl list short modules")
    for line in modules.split("\n"):
        if "razer" in line.lower() and ("module-null-sink" in line or "module-loopback" in line):
            mod_id = line.split("\t")[0]
            run_cmd(f"pactl unload-module {mod_id}")
    
    # 4. Skapa virtuella kanaler
    for sink in SINKS:
        name_pretty = sink.split('_')[1].title()
        print(f"Skapar: {name_pretty}")
        
        # Vi använder enkla beskrivningar utan mellanslag för att vara säkra
        desc = f"Razer_{name_pretty}"
        run_cmd(f'pactl load-module module-null-sink sink_name={sink} sink_properties="device.description={desc}"')
        
        # Unmute och sätt volym till 100%
        run_cmd(f"pactl set-sink-mute {sink} 0")
        run_cmd(f"pactl set-sink-volume {sink} 100%")
        
        # Routa till BÅDA pro-outputs (ifall hörlurarna lyssnar på fel enhet)
        # Vi använder högre latency för stabilitet
        run_cmd(f"pactl load-module module-loopback source={sink}.monitor sink={HW_SINK_0} latency_msec=20")
        run_cmd(f"pactl load-module module-loopback source={sink}.monitor sink={HW_SINK_1} latency_msec=20")

    # 5. Se till att hårdvaran är vaken och på 100% i ALSA
    run_cmd("amixer -c 0 cset numid=6 on")
    run_cmd("amixer -c 0 cset numid=10 on")
    run_cmd("amixer -c 0 cset numid=7 45")
    run_cmd("amixer -c 0 cset numid=11 45")
    
    # 6. Se till att hårdvaran är på 100% i Pulse/PipeWire
    run_cmd(f"pactl set-sink-volume {HW_SINK_0} 100%")
    run_cmd(f"pactl set-sink-volume {HW_SINK_1} 100%")
    run_cmd(f"pactl set-sink-mute {HW_SINK_0} 0")
    run_cmd(f"pactl set-sink-mute {HW_SINK_1} 0")
    run_cmd(f"pactl set-default-sink {HW_SINK_0}")
    print("--- Klart! ---")

def initialize_hid():
    try:
        h = hid.device()
        h.open(VENDOR_ID, PRODUCT_ID)
        h.write([0x00] * 16)
        return h
    except Exception as e:
        print(f"USB Fel: {e}")
        return None

def main():
    setup_hardware()
    h = initialize_hid()
    
    if not h:
        print("Kunde inte hitta mixern.")
        return

    print("Daemon aktiv. Bevakar faders...")
    
    last_values = [None, None, None, None]
    
    # En enkel test-ton för att verifiera ljud
    subprocess.Popen("paplay --device=razer_system /usr/share/sounds/alsa/Front_Left.wav", shell=True)
    
    try:
        while True:
            d = h.read(64)
            if d and len(d) >= 7:
                current_values = [d[3], d[4], d[5], d[6]]
                
                for i in range(4):
                    if current_values[i] != last_values[i]:
                        # Dynamisk skala (vissa firmwares kör 0-100, andra 0-255)
                        max_val = 100
                        if current_values[i] > 100:
                            max_val = 255
                        
                        vol_percent = int((current_values[i] / max_val) * 100)
                        if vol_percent > 100: vol_percent = 100
                        
                        # Vi sätter volymen direkt
                        subprocess.Popen(f"pactl set-sink-volume {SINKS[i]} {vol_percent}%", shell=True)
                        last_values[i] = current_values[i]
            
            time.sleep(0.01)
            
    except Exception as e:
        print(f"Loop error: {e}")
        time.sleep(2)
        main()

if __name__ == "__main__":
    main()
