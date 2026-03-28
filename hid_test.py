import hid
import sys

def main():
    vendor_id = 0x1532
    product_id = 0x053e

    print(f"Söker efter Razer Audio Mixer (VID: 0x{vendor_id:04x}, PID: 0x{product_id:04x})...")
    
    devices = hid.enumerate(vendor_id, product_id)
    if not devices:
        print("Kunde inte hitta enheten. Är den ansluten?")
        sys.exit(1)

    print(f"Hittade {len(devices)} gränssnitt. Öppnar det första...")
    
    try:
        # Vi provar att öppna den första tillgängliga HID-interfacet
        # Razer Audio Mixer brukar ha flera interface, vi behöver det som skickar fader-data
        h = hid.device()
        h.open(vendor_id, product_id)
        print("Enheten är öppnad! Dra i ett reglage på din mixer nu (du har 15 sekunder)...")
        
        h.set_nonblocking(True)

        import time
        start_time = time.time()
        while time.time() - start_time < 15:
            d = h.read(64)
            if d:
                print(f"Data mottaget: {d}")
            time.sleep(0.01)

        print("Testet avslutades.")
        h.close()
    except Exception as e:
        print(f"Fel: {e}")

if __name__ == "__main__":
    main()
