CYFARE Debian Optimizer

Overview

The CYFARE Debian Optimizer is a user-friendly graphical tool designed to help you apply various performance, security, and usability tweaks to your Debian-based Linux distribution. With a simple and intuitive interface built with GTK4 and Adwaita, you can select and apply a range of optimizations to enhance your system's responsiveness and efficiency.

Features

This tool provides a collection of optimizations that can be applied to your system. Below is a list of the available tweaks and what they do:

System & Performance

    Reduce SSD Writes: Optimizes your /etc/fstab to use noatime and nodiratime, reducing wear on your SSD and potentially improving its lifespan.

    Use RAM for Temp & Log Files: Configures your system to store temporary files and logs in RAM (tmpfs), which can speed up I/O operations and reduce disk writes.

    Apply TCP/UDP & System Optimizations: Applies a set of sysctl configurations to improve network performance and overall system responsiveness.

    Set GRUB Elevator to 'deadline': Changes the I/O scheduler to 'deadline' for potentially better disk I/O performance, especially on SSDs.

    Reduce GRUB Timeout to 2 seconds: Shortens the GRUB bootloader timeout to speed up the boot process.

    Install and Enable Preload: Installs preload, a daemon that monitors your application usage and preloads libraries into memory to speed up application launch times.

    Remove TLP (Fix for freezes): Uninstalls the TLP power management tool, which can sometimes cause system freezes or instability on certain hardware.

Security

    Turn Off Kernel Security Mitigations: Disables certain kernel-level security mitigations (like those for Spectre and Meltdown) to gain a slight performance boost. This is intended for advanced users who understand the security implications.

    Disable Nouveau Drivers: Blacklists the open-source Nouveau drivers for NVIDIA GPUs, which is often a necessary step before installing proprietary NVIDIA drivers.

    Install Intel Microcode & Non-Free Firmware: Installs the latest microcode for Intel CPUs and other non-free firmware, which can be crucial for system stability and security.

Application & Desktop Experience

    Remove Unnecessary Languages from Aptitude: Configures apt to only download language files for your locale, saving disk space and speeding up package manager operations.

    Install Compton Screen Tear Fix (XFCE): Installs compton, a compositor that can help eliminate screen tearing on XFCE and other desktop environments that lack a compositor.

    Set NVIDIA PowerMizer to Max Performance: Provides instructions to configure NVIDIA's PowerMizer settings for maximum performance.

    Fix Ugly Fonts in Firefox/Librewolf: Installs Microsoft's Core Fonts to improve font rendering in web browsers like Firefox and its forks.

    Install XanMod Kernel (Latest Mainline): Installs the XanMod kernel, a custom kernel designed for enhanced performance, responsiveness, and lower latency.

    Add XanMod BFQ Scheduler Udev Rule: Adds a udev rule to set the BFQ I/O scheduler for NVMe drives when using the XanMod kernel.

    Set Cake Queuing Discipline (XanMod): Configures the "Cake" queuing discipline to combat bufferbloat and improve network quality, especially on slower or congested connections.

Requirements

    A Debian-based Linux distribution (e.g., Debian, Ubuntu, Linux Mint, Pop!_OS).

    Python 3.

    The following Python libraries: PyGObject, which provides bindings for GTK4 and Adwaita. You can typically install these with your system's package manager. For example, on Debian/Ubuntu:

sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

    pkexec (part of the PolicyKit package) for running commands with administrative privileges.

How to Use

    Save the Code: Save the Python code as a file, for example, debian_optimizer.py.

    Make it Executable: Open a terminal and run the following command to make the script executable:

chmod +x debian_optimizer.py

    Run the Application: Execute the script from your terminal:

./debian_optimizer.py

    Select and Apply: The application window will open. Check the boxes for the optimizations you wish to apply.

    Apply Optimizations: Click the "Apply Selected Optimizations" button. You will be prompted for your password to grant administrative privileges.

    Reboot if Necessary: Some optimizations require a system reboot to take effect. The application will notify you if a reboot is needed.

Disclaimer

Applying system-level optimizations can have unintended consequences. While these tweaks are generally considered safe, there is always a risk of instability or data loss. It is highly recommended to back up your important data before applying any changes. The creators of this tool are not responsible for any damage to your system. Use at your own risk.

Contributing

Contributions are welcome! If you have ideas for new optimizations, bug fixes, or improvements to the code, feel free to open an issue or submit a pull request on the project's GitHub repository.

License

This project is licensed under the GPLv3 License. See the LICENSE file for more details.
