# Enabling Wake-on-LAN (WoL) on Windows

To make sure your PC wakes up when the SynoWoL app sends a signal, you need to configure three things:
1.  **BIOS/UEFI Settings**
2.  **Windows Network Adapter Settings**
3.  **Windows Power Settings**

---

## 1. Configure BIOS/UEFI

1.  Restart your PC.
2.  Enter BIOS/UEFI by pressing the specific key (usually `Del`, `F2`, `F12`, or `Esc`) before Windows starts.
3.  Look for "Power Management", "Advanced", or "PCIe Configuration" menus.
4.  Find a setting named **"Wake on LAN"**, **"Wake on Magic Packet"**, or **"Power On By PCI-E"**.
5.  Set it to **Enabled**.
6.  Look for "Deep Sleep" or "ErP" and **Disable** it (these features save power but kill the network card when off).
7.  **Save & Exit** (usually `F10`).

## 2. Configure Windows Network Adapter

1.  In Windows, right-click the **Start** button and select **Device Manager**.
2.  Expand **Network adapters**.
3.  Right-click your Ethernet adapter (e.g., "Realtek PCIe GbE Family Controller") and select **Properties**.
4.  Go to the **Advanced** tab:
    *   Find **"Wake on Magic Packet"** (or similar) and ensure it is **Enabled**.
    *   Find **"Shutdown Wake-On-Lan"** and ensure it is **Enabled**.
5.  Go to the **Power Management** tab:
    *   Check **"Allow the computer to turn off this device to save power"**.
    *   Check **"Allow this device to wake the computer"**.
    *   Check **"Only allow a magic packet to wake the computer"**.
6.  Click **OK**.

## 3. Disable Fast Startup (Important!)

Windows "Fast Startup" puts the PC into a semi-hibernation state that often ignores Wake-on-LAN packets.

1.  Open **Control Panel** (search for it in Start).
2.  Go to **Hardware and Sound** > **Power Options**.
3.  Click **"Choose what the power buttons do"** on the left.
4.  Click **"Change settings that are currently unavailable"** (requires admin rights).
5.  Under "Shutdown settings", **uncheck "Turn on fast startup (recommended)"**.
6.  Click **Save changes**.

---

## Testing

Once configured, shutdown your PC completely. Use the **SynoWoL** app to try and wake it up!
