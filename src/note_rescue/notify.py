from __future__ import annotations

import subprocess
import sys


def show_toast(title: str, message: str, duration: str = "short") -> bool:
    """
    Show a Windows toast notification without extra dependencies.
    Returns True if the notification was attempted successfully.
    """
    if sys.platform != "win32":
        return False

    title_escaped = title.replace("'", "''")
    message_escaped = message.replace("'", "''")

    ps_script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$template = @"
<toast duration="{duration}">
  <visual>
    <binding template="ToastGeneric">
      <text>{title_escaped}</text>
      <text>{message_escaped}</text>
    </binding>
  </visual>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("note-rescue").Show($toast)
"""

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0
    except Exception:
        return False
