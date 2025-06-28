#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
import subprocess
import webbrowser
import threading
import os
import sys

# Custom exception for clearer error handling
class CommandError(Exception):
    def __init__(self, message, details=""):
        super().__init__(message)
        self.details = details

class DebianOptimizerApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_application_id("com.cyfare.debianoptimizer")
        self.connect('activate', self.on_activate)
        self.win = None

    def on_activate(self, app):
        if not self.win:
            self.win = MainWindow(application=app)
        self.win.present()

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_title("CYFARE Debian Optimizer")
        self.set_default_size(900, 700)

        self.optimizations_map = {
            # ID: (Label, Function, requires_reboot, description, icon_name)
            "reduce_ssd_writes": ("Reduce SSD Writes", self.apply_fstab_ssd, True, "Optimizes SSD longevity by reducing write operations using 'noatime' and 'nodiratime'.", "drive-harddisk-solidstate-symbolic"),
            "use_ram_for_temp": ("Use RAM for Temp &amp; Log Files", self.apply_fstab_ram, True, "Mounts /tmp and /var/log to RAM (tmpfs) to reduce disk I/O.", "memory-symbolic"),
            "sysctl_optimizations": ("Apply TCP/UDP &amp; System Optimizations", self.apply_sysctl, True, "Applies kernel parameters for improved network and system performance.", "network-server-symbolic"),
            "grub_deadline": ("Set GRUB Elevator to 'deadline'", self.apply_grub_deadline, True, "Changes the I/O scheduler for better disk performance on SSDs.", "media-cdrom-symbolic"),
            "grub_kernel_security_off": ("Turn Off Kernel Security Mitigations", self.apply_grub_security_off, True, "Disables certain kernel security features for a slight performance gain (advanced users).", "security-high-symbolic"),
            "grub_timeout": ("Reduce GRUB Timeout to 2 seconds", self.apply_grub_timeout, True, "Speeds up boot time by reducing the GRUB menu display duration.", "hourglass-symbolic"),
            "apt_no_languages": ("Remove Unnecessary Languages from Aptitude", self.apply_apt_lang, False, "Prevents APT from downloading unneeded translation files.", "language-symbolic"),
            "install_preload": ("Install and Enable Preload", self.install_preload, False, "Installs Preload, an adaptive readahead daemon.", "system-run-symbolic"),
            "install_compton": ("Install Compton Screen Tear Fix (XFCE)", self.install_compton, True, "Installs Compton, a standalone compositor for X, to fix screen tearing.", "display-symbolic"),
            "nvidia_powermizer": ("Set NVIDIA PowerMizer to Max Performance", self.apply_nvidia_powermizer, True, "Configures NVIDIA PowerMizer for maximum performance.", "video-display-symbolic"),
            "install_intel_microcode": ("Install Intel Microcode &amp; Non-Free Firmware", self.install_intel_microcode, True, "Installs essential microcode updates for Intel CPUs and non-free firmware.", "chip-symbolic"),
            "disable_nouveau": ("Disable Nouveau Drivers", self.disable_nouveau, True, "Blacklists the open-source Nouveau drivers.", "video-display-symbolic"),
            "remove_tlp": ("Remove TLP (Fix for freezes)", self.remove_tlp, False, "Removes TLP (Linux Advanced Power Management) which can cause system freezes.", "power-off-symbolic"),
            "fix_firefox_fonts": ("Fix Ugly Fonts in Firefox/Librewolf", self.fix_firefox_fonts, False, "Installs Microsoft core fonts to improve font rendering.", "font-x-generic-symbolic"),
            "install_xanmod": ("Install XanMod Kernel (Latest Mainline)", self.install_xanmod, True, "Installs the XanMod kernel for responsiveness and performance.", "drive-harddisk-system-symbolic"),
            "xanmod_udev_rules": ("Add XanMod BFQ Scheduler Udev Rule", self.apply_xanmod_udev, True, "Applies a udev rule to set the BFQ I/O scheduler for NVMe drives.", "drive-harddisk-solidstate-symbolic"),
            "xanmod_cake_queue": ("Set Cake Queuing Discipline (XanMod)", self.apply_xanmod_cake, True, "Configures the Cake queuing discipline to improve bufferbloat.", "network-transmit-receive-symbolic"),
        }

        self.toast_overlay = Adw.ToastOverlay.new()
        self.set_content(self.toast_overlay)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toast_overlay.set_child(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        title_widget = Adw.WindowTitle(title="CYFARE Debian Optimizer", subtitle="v1.0")
        header.set_title_widget(title_widget)

        social_box = Gtk.Box(spacing=6)
        header.pack_start(social_box)

        twitter_button = Gtk.Button.new_from_icon_name("twitter-symbolic")
        twitter_button.set_tooltip_text("Follow us on X")
        twitter_button.connect("clicked", self.open_link, "https://x.com/cyfarelabs")
        social_box.append(twitter_button)

        github_button = Gtk.Button.new_from_icon_name("github-symbolic")
        github_button.set_tooltip_text("Check us out on GitHub")
        github_button.connect("clicked", self.open_link, "https://github.com/CYFARE/")
        social_box.append(github_button)

        site_button = Gtk.Button.new_from_icon_name("emblem-web-symbolic")
        site_button.set_tooltip_text("Visit our Website")
        site_button.connect("clicked", self.open_link, "https://cyfare.net/")
        social_box.append(site_button)

        action_box_end = Gtk.Box(spacing=6)
        header.pack_end(action_box_end)

        app_menu_button = Gtk.MenuButton()
        app_menu_button.set_icon_name("open-menu-symbolic")
        app_menu_button.set_tooltip_text("Application Menu")

        app_menu = Gio.Menu.new()
        app_menu.append("About", "app.about")
        app_menu.append("Quit", "app.quit")

        action_about = Gio.SimpleAction.new("about", None)
        action_about.connect("activate", self.show_about_dialog)
        self.get_application().add_action(action_about)

        action_quit = Gio.SimpleAction.new("quit", None)
        action_quit.connect("activate", lambda a, p: self.get_application().quit())
        self.get_application().add_action(action_quit)

        app_menu_button.set_menu_model(app_menu)
        action_box_end.append(app_menu_button)

        self.view_stack = Adw.ViewStack()
        self.view_stack.set_vexpand(True)
        main_box.append(self.view_stack)

        optimizations_page_content = self.create_optimizations_page()
        self.view_stack.add_titled(optimizations_page_content, "optimizations", "Optimizations")

    def create_optimizations_page(self):
        optimizations_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        optimizations_box.set_margin_top(20)
        optimizations_box.set_margin_bottom(20)
        optimizations_box.set_margin_start(20)
        optimizations_box.set_margin_end(20)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_has_frame(False)
        scrolled_window.set_vexpand(True)
        optimizations_box.append(scrolled_window)

        preferences_group = Adw.PreferencesGroup()
        preferences_group.set_title("System Optimizations")
        preferences_group.set_description("Select the optimizations you want to apply to your Debian system.")
        scrolled_window.set_child(preferences_group)

        self.check_buttons = {}
        for key, (label, _, _, description, icon_name) in self.optimizations_map.items():
            row = Adw.ActionRow()
            row.set_title(label)
            row.set_subtitle(description)
            icon_image = Gtk.Image.new_from_icon_name(icon_name)
            row.add_prefix(icon_image)

            switch = Gtk.Switch()
            switch.set_valign(Gtk.Align.CENTER)
            switch.set_active(False)
            row.add_suffix(switch)
            row.set_activatable_widget(switch)

            self.check_buttons[key] = switch
            preferences_group.add(row)

        action_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        action_area.set_margin_start(20)
        action_area.set_margin_end(20)
        action_area.set_margin_bottom(20)
        optimizations_box.append(action_area)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_vexpand(False)
        action_area.append(self.progress_bar)

        self.status_label = Gtk.Label(label="Select optimizations and click 'Apply'.")
        self.status_label.set_halign(Gtk.Align.CENTER)
        action_area.append(self.status_label)

        self.apply_button = Gtk.Button(label="Apply Selected Optimizations")
        self.apply_button.add_css_class("suggested-action")
        self.apply_button.set_halign(Gtk.Align.CENTER)
        self.apply_button.connect("clicked", self.on_apply_clicked)
        action_area.append(self.apply_button)

        return optimizations_box

    def open_link(self, button, url):
        webbrowser.open_new(url)

    def show_about_dialog(self, action, param):
        about_dialog = Adw.AboutWindow()
        about_dialog.set_transient_for(self)
        about_dialog.set_application_name("CYFARE Debian Optimizer")
        about_dialog.set_version("v1.0")
        about_dialog.set_developer_name("CYFARE")
        about_dialog.set_copyright("© 2025 CYFARE.NET")
        about_dialog.set_comments("A simple tool to optimize Debian-based systems for performance and efficiency.")
        about_dialog.set_website("https://cyfare.net/")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_developers(["CYFARE"])
        about_dialog.present()

    def show_error_dialog(self, message, details):
        dialog = Adw.MessageDialog.new(self, message, details)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.connect("response", lambda d, r: d.close())
        dialog.present()

    def show_toast(self, message):
        toast = Adw.Toast.new(title=message)
        self.toast_overlay.add_toast(toast)

    def on_apply_clicked(self, button):
        self.apply_button.set_sensitive(False)
        self.progress_bar.set_fraction(0)
        self.status_label.set_label("Starting optimizations...")

        selected_opts = [key for key, switch in self.check_buttons.items() if switch.get_active()]

        if not selected_opts:
            self.status_label.set_label("No optimizations selected.")
            self.apply_button.set_sensitive(True)
            self.show_toast("No optimizations selected.")
            return

        self.show_toast("Applying optimizations...")
        thread = threading.Thread(target=self.run_optimizations, args=(selected_opts,))
        thread.daemon = True
        thread.start()

    def run_optimizations(self, selected_opts):
        total_steps = len(selected_opts)
        current_step = 0
        reboot_needed = False

        for key in selected_opts:
            current_step += 1
            label, func, requires_reboot, _, _ = self.optimizations_map[key]
            unformatted_label = label.replace('&amp;', '&')
            GLib.idle_add(self.status_label.set_label, f"Applying: {unformatted_label}...")

            try:
                func()
                if requires_reboot:
                    reboot_needed = True
            except CommandError as e:
                GLib.idle_add(self.status_label.set_label, f"Failed: {unformatted_label}")
                GLib.idle_add(self.show_error_dialog, str(e), e.details)
                GLib.idle_add(self.apply_button.set_sensitive, True)
                return

            fraction = current_step / total_steps
            GLib.idle_add(self.progress_bar.set_fraction, fraction)

        final_message = "All selected optimizations have been applied."
        if reboot_needed:
            final_message += " A reboot is required for changes to take effect."

        GLib.idle_add(self.status_label.set_label, final_message)
        GLib.idle_add(self.show_toast, final_message)
        GLib.idle_add(self.apply_button.set_sensitive, True)

    def run_command(self, command):
        """Executes a command with pkexec for root privileges and non-interactively."""
        # Prepend DEBIAN_FRONTEND to prevent interactive prompts from apt, etc.
        full_command = f"export DEBIAN_FRONTEND=noninteractive; {command}"
        pkexec_command = ["pkexec", "bash", "-c", full_command]

        try:
            result = subprocess.run(pkexec_command, capture_output=True, text=True, check=True, timeout=600)
            return result.stdout
        except FileNotFoundError:
            raise CommandError("Command 'pkexec' not found.",
                               "Please ensure PolicyKit is installed and configured on your system.")
        except subprocess.TimeoutExpired:
            raise CommandError("Operation Timed Out",
                               "The command took too long to complete (more than 10 minutes).")
        except subprocess.CalledProcessError as e:
            # Handle pkexec authentication failure specifically
            if e.returncode in [126, 127]:
                raise CommandError("Authentication Failed",
                                   "Could not get administrator privileges. Please try again.")
            else:
                raise CommandError(f"Command failed with exit code {e.returncode}", e.stderr.strip())

    # --- Optimization Functions ---
    def apply_fstab_ssd(self):
        self.run_command("sed -i '/\\s\\/\\s/s/defaults/defaults,noatime,nodiratime,discard/' /etc/fstab")

    def apply_fstab_ram(self):
        commands = """
        grep -q 'tmpfs /tmp' /etc/fstab || echo 'tmpfs /tmp tmpfs defaults,noatime,mode=1777 0 0' >> /etc/fstab
        grep -q 'tmpfs /var/log' /etc/fstab || echo 'tmpfs /var/log tmpfs defaults,noatime,mode=0755 0 0' >> /etc/fstab
        """
        self.run_command(commands)

    def apply_sysctl(self):
        sysctl_conf_path = "/etc/sysctl.d/99-custom-optimizations.conf"
        sysctl_conf = """
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem="4096 87380 16777216"
net.ipv4.tcp_wmem="4096 87380 16777216"
net.ipv4.tcp_window_scaling=1
vm.dirty_ratio=10
vm.dirty_background_ratio=5
vm.swappiness=10
vm.vfs_cache_pressure=50
        """
        self.run_command(f"echo '{sysctl_conf}' > {sysctl_conf_path} && sysctl --system")

    def apply_grub_deadline(self):
        self.run_command("sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT=\"\\(.*\\)\"/GRUB_CMDLINE_LINUX_DEFAULT=\"\\1 elevator=deadline\"/' /etc/default/grub && update-grub")

    def apply_grub_security_off(self):
        cmdline = "quiet mitigations=off"
        self.run_command(f"sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT=\"{cmdline}\"/' /etc/default/grub && update-grub")

    def apply_grub_timeout(self):
        self.run_command("sed -i 's/GRUB_TIMEOUT=.*/GRUB_TIMEOUT=2/' /etc/default/grub && update-grub")

    def apply_apt_lang(self):
        self.run_command("echo 'Acquire::Languages \"none\";' > /etc/apt/apt.conf.d/99-no-languages")

    def install_preload(self):
        self.run_command("apt-get update && apt-get install -y preload && systemctl enable --now preload")

    def install_compton(self):
        self.run_command("apt-get update && apt-get install -y compton")
        GLib.idle_add(self.status_label.set_label, "Compton installed. Add to startup applications.")

    def apply_nvidia_powermizer(self):
        GLib.idle_add(self.status_label.set_label, "Add 'nvidia-settings -a \"[gpu:0]/GpuPowerMizerMode=1\"' to startup.")

    def install_intel_microcode(self):
        self.run_command("apt-get update && apt-get install -y intel-microcode firmware-misc-nonfree")

    def disable_nouveau(self):
        conf_file = "/etc/modprobe.d/nvidia-blacklists-nouveau.conf"
        content = "blacklist nouveau\\noptions nouveau modeset=0"
        self.run_command(f"echo -e '{content}' > {conf_file} && update-initramfs -u")

    def remove_tlp(self):
        self.run_command("apt-get remove --purge -y tlp tlp-rdw")

    def fix_firefox_fonts(self):
        # Automatically accept the EULA for MS Core Fonts
        commands = """
        echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections
        apt-get update
        apt-get install -y ttf-mscorefonts-installer fonts-liberation
        """
        self.run_command(commands)
        GLib.idle_add(self.status_label.set_label, "Core fonts installed.")

    def install_xanmod(self):
        commands = """
        apt-get update && apt-get install -y wget gpg
        wget -qO - https://dl.xanmod.org/archive.key | gpg --dearmor -o /usr/share/keyrings/xanmod-archive-keyring.gpg
        echo 'deb [signed-by=/usr/share/keyrings/xanmod-archive-keyring.gpg] http://deb.xanmod.org releases main' > /etc/apt/sources.list.d/xanmod-release.list
        apt-get update && apt-get install -y linux-xanmod-x64v3
        """
        self.run_command(commands)

    def apply_xanmod_udev(self):
        rule = 'ACTION==\"add|change\", KERNEL==\"nvme*\", ATTR{queue/scheduler}==\"bfq\", ATTR{queue/iosched/low_latency}=\"1\"'
        self.run_command(f"echo '{rule}' > /etc/udev/rules.d/60-ioschedulers.rules && udevadm control --reload-rules && udevadm trigger")

    def apply_xanmod_cake(self):
        conf = "net.core.default_qdisc=cake\\nnet.ipv4.tcp_congestion_control=bbr"
        self.run_command(f"echo -e '{conf}' > /etc/sysctl.d/90-override.conf && sysctl --system")

if __name__ == "__main__":
    app = DebianOptimizerApp()
    sys.exit(app.run(sys.argv))
