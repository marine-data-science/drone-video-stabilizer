from PIL import Image
import os

# Eingabedatei (dein PNG-Icon)
input_icon = "Icon.png"

# Ausgabeordner erstellen
output_folder = "output_icons"
os.makedirs(output_folder, exist_ok=True)

# Laden des PNG-Icons
img = Image.open(input_icon)

# 1. Windows .ico Datei (mit mehreren Größen für Skalierung)
ico_path = os.path.join(output_folder, "icon.ico")
img.save(ico_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])

# 2. macOS .icns Datei (Icon in verschiedene Größen konvertieren)
icns_path = os.path.join(output_folder, "icon.icns")
img.resize((1024, 1024)).save(icns_path, format="ICNS")

# 3. Linux .png Icons (256x256 und 512x512)
linux_icon_256 = os.path.join(output_folder, "icon-256.png")
linux_icon_512 = os.path.join(output_folder, "icon-512.png")

img.resize((256, 256)).save(linux_icon_256, format="PNG")
img.resize((512, 512)).save(linux_icon_512, format="PNG")

print(f"Icons wurden erfolgreich in '{output_folder}' gespeichert!")
