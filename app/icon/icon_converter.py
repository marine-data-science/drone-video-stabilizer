from PIL import Image
import os

# Basisverzeichnis dieses Skripts bestimmen
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    # Falls kein Input-Icon übergeben wurde, nutze das Standard-Icon in `app/icon/`
    input_icon = os.path.join(SCRIPT_DIR, "Icon.png")

    # Output Directory innerhalb `app/icon/`
    output_folder = os.path.join(SCRIPT_DIR, "output_icons")
    os.makedirs(output_folder, exist_ok=True)

    # Prüfe, ob das Icon existiert
    if not os.path.exists(input_icon):
        print(f"Error: Input icon '{input_icon}' not found.")
        return

    # Load png Icon
    img = Image.open(input_icon)

    # 1. Windows .ico File
    ico_path = os.path.join(output_folder, "icon.ico")
    img.save(ico_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])

    # 2. macOS .icns file
    icns_path = os.path.join(output_folder, "icon.icns")
    img.resize((1024, 1024)).save(icns_path, format="ICNS")

    # 3. Linux .png Icons
    linux_icon_256 = os.path.join(output_folder, "icon-256.png")
    linux_icon_512 = os.path.join(output_folder, "icon-512.png")

    img.resize((256, 256)).save(linux_icon_256, format="PNG")
    img.resize((512, 512)).save(linux_icon_512, format="PNG")

    print(f"Icons were successfully saved in '{output_folder}'!")

if __name__ == "__main__":
    main()
