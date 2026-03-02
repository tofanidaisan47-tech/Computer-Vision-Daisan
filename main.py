"""
SmartAttend - Sistem Pencatat Kehadiran Digital Berbasis Kartu Identitas
Main program yang mengintegrasikan semua modul
"""

import os
import sys
from datetime import datetime

# Import dari modul lokal
from capture_module import load_image, capture_from_webcam, list_input_images, capture_with_preview
from process_module import (
    resize_standard, convert_to_grayscale, adjust_brightness_contrast,
    auto_adjust_brightness, apply_border, histogram_equalization
)
from utils import (
    add_timestamp, add_watermark, save_with_organization,
    create_collage, preview_image
)
from config import OUTPUT_FOLDER, COLLAGE_FOLDER


def print_menu():
    """Tampilkan menu utama"""
    print("\n" + "="*60)
    print("  🎫 SMARTATTEND - Sistem Pencatat Kehadiran Digital 🎫")
    print("="*60)
    print("\n📋 MENU UTAMA:")
    print("  1. Load & Process gambar dari file")
    print("  2. Capture dari webcam (ADVANCED MODE)")
    print("  3. Batch process gambar (4+ gambar → collage)")
    print("  4. List gambar di folder input")
    print("  5. View hasil di folder output")
    print("  6. Settings & Configuration")
    print("  7. Keluar")
    print("\n" + "-"*60)


def menu_load_and_process():
    """Menu untuk load dan process gambar dari file"""
    print("\n📁 LOAD & PROCESS GAMBAR")
    print("-" * 40)
    
    # List gambar yang ada
    images = list_input_images()
    
    if not images:
        print("⚠️  Tidak ada gambar di folder 'input'")
        print("💡 Tip: Taruh gambar (.jpg/.png) di folder 'input' terlebih dahulu")
        return
    
    print("\n📸 Gambar yang tersedia:")
    for i, img_path in enumerate(images, 1):
        print(f"  {i}. {os.path.basename(img_path)}")
    
    try:
        choice = int(input("\n📝 Pilih nomor gambar (0 untuk cancel): "))
        
        if choice == 0:
            print("❌ Dibatalkan")
            return
        
        if 1 <= choice <= len(images):
            image_path = images[choice - 1]
        else:
            print("❌ Pilihan tidak valid")
            return
        
    except ValueError:
        print("❌ Input tidak valid")
        return
    
    # Load gambar
    img, success = load_image(image_path)
    if not success:
        return
    
    # Show processing options
    print("\n⚙️  OPSI PEMROSESAN:")
    print("  1. Resize ke standar (400x250)")
    print("  2. Resize dengan keep aspect ratio")
    print("  3. Tambah brightness/contrast")
    print("  4. Histogram equalization")
    print("  5. Konversi ke grayscale")
    print("  0. Proses standar (recommended)")
    
    try:
        proc_choice = int(input("\n📝 Pilih opsi (0-5): "))
    except ValueError:
        proc_choice = 0
    
    # Apply processing
    if proc_choice == 1:
        img = resize_standard(img)
    elif proc_choice == 2:
        img = resize_standard(img, keep_aspect=True)
    elif proc_choice == 3:
        br = int(input("Brightness (-100~100, default=0): ") or 0)
        ct = float(input("Contrast (0.5~3.0, default=1.0): ") or 1.0)
        img = adjust_brightness_contrast(img, br, ct)
    elif proc_choice == 4:
        img = histogram_equalization(img)
    elif proc_choice == 5:
        img = convert_to_grayscale(img)
    else:  # Default processing
        print("\n🔄 Applying standard processing...")
        img = resize_standard(img)
        img = auto_adjust_brightness(img)
    
    if img is None:
        print("❌ Processing gagal")
        return
    
    # Add annotations
    print("\n📝 ANNOTATIONS:")
    add_ts = input("Tambah timestamp? (y/n, default=y): ").lower() or 'y'
    if add_ts == 'y':
        img = add_timestamp(img)
    
    add_wm = input("Tambah watermark? (y/n, default=y): ").lower() or 'y'
    if add_wm == 'y':
        img = add_watermark(img)
    
    add_bd = input("Tambah border? (y/n, default=y): ").lower() or 'y'
    if add_bd == 'y':
        img = apply_border(img)
    
    # Preview
    show_preview = input("\nTampilkan preview? (y/n, default=y): ").lower() or 'y'
    if show_preview == 'y':
        preview_image(img)
    
    # Save
    save_choice = input("\nSimpan hasil? (y/n, default=y): ").lower() or 'y'
    if save_choice == 'y':
        filepath = save_with_organization(img)
        if filepath:
            print(f"\n✅ Berhasil! File disimpan di: {filepath}")
    
    print("\n✅ Menu selesai\n")


def menu_webcam_capture():
    """Menu untuk capture dari webcam dengan berbagai mode"""
    print("\n" + "="*60)
    print("📷 ADVANCED WEBCAM CAPTURE")
    print("="*60)
    print("\n🎬 PILIH MODE CAPTURE:")
    print("  1. Single Capture (ambil 1 gambar)")
    print("  2. Countdown Mode (countdown 5 detik sebelum capture)")
    print("  3. Burst Mode (ambil 5 gambar berturut-turut)")
    print("  4. Kembali ke menu")
    print("\n" + "-"*60)
    
    try:
        choice = input("Pilih mode (1-4): ").strip()
        
        if choice == '4':
            return
        
        if choice == '1':
            mode = 'single'
        elif choice == '2':
            mode = 'countdown'
        elif choice == '3':
            mode = 'burst'
        else:
            print("❌ Pilihan tidak valid")
            return
        
        print(f"\n⚙️  OPTIONS:")
        show_guides = input("Tampilkan frame guides? (y/n, default=y): ").lower() or 'y'
        show_brightness = input("Tampilkan light indicator? (y/n, default=y): ").lower() or 'y'
        
        show_guides = show_guides == 'y'
        show_brightness = show_brightness == 'y'
        
        # Capture dengan settings yang dipilih
        frames = capture_with_preview(
            window_title="SmartAttend - Advanced Capture",
            capture_mode=mode,
            show_guides=show_guides,
            show_brightness=show_brightness
        )
        
        if not frames or len(frames) == 0:
            return
        
        # Process each captured frame
        print(f"\n🔄 Processing {len(frames)} captured image(s)...")
        
        for idx, frame in enumerate(frames, 1):
            print(f"\n⏳ Processing image {idx}/{len(frames)}...")
            
            img = frame.copy()
            img = resize_standard(img)
            img = auto_adjust_brightness(img)
            img = add_timestamp(img)
            img = add_watermark(img)
            img = apply_border(img)
            
            # Preview
            show_preview = input(f"Tampilkan preview? (y/n, default=y): ").lower() or 'y'
            if show_preview == 'y':
                preview_image(img, f"Preview - Image {idx}/{len(frames)}")
            
            # Save
            save_choice = input(f"Simpan image {idx}? (y/n, default=y): ").lower() or 'y'
            if save_choice == 'y':
                filepath = save_with_organization(img)
                if filepath:
                    print(f"✅ Image {idx} disimpan: {filepath}")
        
        print(f"\n✅ Semua {len(frames)} gambar selesai diproses!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n✅ Menu selesai\n")


def menu_batch_process():
    """Menu untuk batch process dan buat collage"""
    print("\n📦 BATCH PROCESS & COLLAGE GENERATOR")
    print("-" * 40)
    
    images = list_input_images()
    
    if len(images) < 4:
        print(f"⚠️  Hanya {len(images)} gambar ditemukan, dibutuhkan 4 gambar minimum")
        return
    
    print(f"\n📸 Ditemukan {len(images)} gambar:")
    for i, img_path in enumerate(images, 1):
        print(f"  {i}. {os.path.basename(img_path)}")
    
    # Select images for collage (default: 4 pertama)
    print("\n💡 Default: Menggunakan 4 gambar pertama")
    use_default = input("Lanjutkan? (y/n): ").lower() or 'y'
    
    if use_default != 'y':
        return
    
    # Process dan load images
    processed_images = []
    for i, img_path in enumerate(images[:4]):
        print(f"\n⏳ Processing gambar {i+1}/4...")
        img, success = load_image(img_path)
        
        if success:
            img = resize_standard(img)
            img = auto_adjust_brightness(img)
            img = add_timestamp(img)
            img = add_watermark(img)
            processed_images.append(img)
            print(f"   ✅ {os.path.basename(img_path)} siap")
    
    if len(processed_images) < 4:
        print(f"\n❌ Hanya {len(processed_images)} gambar berhasil diproses")
        return
    
    # Create collage
    print("\n🎨 Membuat collage...")
    title = f"DAILY SUMMARY: {datetime.now().strftime('%Y-%m-%d')}"
    
    # Generate save path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(COLLAGE_FOLDER, f"collage_{timestamp}.jpg")
    
    collage = create_collage(processed_images, title=title, save_path=save_path)
    
    if collage is not None:
        # Preview
        show_preview = input("\nTampilkan preview? (y/n, default=y): ").lower() or 'y'
        if show_preview == 'y':
            preview_image(collage, "Collage Preview")
        
        print(f"\n✅ Collage berhasil dibuat!")
        print(f"   📁 {save_path}")
    else:
        print("❌ Gagal membuat collage")
    
    print("\n✅ Menu selesai\n")


def menu_list_images():
    """Tampilkan list gambar di input folder"""
    print("\n📋 DAFTAR GAMBAR DI FOLDER INPUT")
    print("-" * 40)
    
    images = list_input_images()
    
    if not images:
        print("⚠️  Tidak ada gambar di folder 'input'")
        return
    
    print(f"\n✅ Total {len(images)} gambar ditemukan:\n")
    for i, img_path in enumerate(images, 1):
        filename = os.path.basename(img_path)
        print(f"  {i:2}. {filename}")
    
    print("\n✅ Menu selesai\n")


def menu_view_output():
    """Buka folder output"""
    print("\n📂 FOLDER OUTPUT")
    print("-" * 40)
    
    if os.path.exists(OUTPUT_FOLDER):
        print(f"\n✅ Folder output: {os.path.abspath(OUTPUT_FOLDER)}")
        print("\n🔍 Struktur folder:")
        
        for root, dirs, files in os.walk(OUTPUT_FOLDER):
            level = root.replace(OUTPUT_FOLDER, '').count(os.sep)
            indent = ' ' * 2 * level
            folder_name = os.path.basename(root) or OUTPUT_FOLDER
            print(f'{indent}📁 {folder_name}/')
            
            sub_indent = ' ' * 2 * (level + 1)
            for file in files:
                print(f'{sub_indent}📄 {file}')
        
        # Try to open folder
        open_folder = input("\nBuka folder di explorer? (y/n): ").lower()
        if open_folder == 'y':
            if sys.platform == 'win32':
                os.startfile(os.path.abspath(OUTPUT_FOLDER))
            elif sys.platform == 'darwin':
                os.system(f'open \"{os.path.abspath(OUTPUT_FOLDER)}\"')
            else:
                os.system(f'xdg-open \"{os.path.abspath(OUTPUT_FOLDER)}\"')
            print("✅ Folder dibuka!")
    else:
        print(f"⚠️  Folder output belum ada: {OUTPUT_FOLDER}")
    
    print("\n✅ Menu selesai\n")


def menu_settings():
    """Menu settings dan configuration"""
    print("\n" + "="*60)
    print("⚙️  SETTINGS & CONFIGURATION")
    print("="*60)
    print("\n📝 AVAILABLE SETTINGS:")
    print("  1. View konfigurasi saat ini")
    print("  2. Informasi sistem")
    print("  3. Help & Documentation")
    print("  4. Kembali ke menu")
    print("\n" + "-"*60)
    
    try:
        choice = input("Pilih menu (1-4): ").strip()
        
        if choice == '1':
            menu_view_config()
        elif choice == '2':
            menu_system_info()
        elif choice == '3':
            menu_help()
        elif choice == '4':
            return
        else:
            print("❌ Pilihan tidak valid")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n✅ Menu selesai\n")


def menu_view_config():
    """View konfigurasi saat ini"""
    print("\n📋 KONFIGURASI SAAT INI")
    print("-" * 40)
    
    import config
    
    print("\n🎨 DIMENSI KARTU:")
    print(f"  Width: {config.CARD_WIDTH} px")
    print(f"  Height: {config.CARD_HEIGHT} px")
    
    print("\n📝 TEXT & WATERMARK:")
    print(f"  Watermark: {config.WATERMARK_TEXT}")
    print(f"  Timestamp Format: {config.TIMESTAMP_FORMAT}")
    
    print("\n🎯 BORDER & STYLING:")
    print(f"  Border Thickness: {config.BORDER_THICKNESS} px")
    print(f"  Border Color (BGR): {config.BORDER_COLOR}")
    
    print("\n💾 OUTPUT:")
    print(f"  Input Folder: {config.INPUT_FOLDER}")
    print(f"  Output Folder: {config.OUTPUT_FOLDER}")
    print(f"  JPEG Quality: {config.JPEG_COMPRESSION}%")
    
    print("\n💡 TIP: Edit config.py untuk customize parameter")
    
    open_config = input("\nBuka config.py di editor? (y/n): ").lower()
    if open_config == 'y':
        try:
            if sys.platform == 'win32':
                os.startfile("config.py")
            else:
                os.system("nano config.py")
        except Exception as e:
            print(f"⚠️  Tidak bisa membuka editor: {str(e)}")


def menu_system_info():
    """Tampilkan informasi sistem"""
    print("\n📊 INFORMASI SISTEM")
    print("-" * 40)
    
    import config
    
    print(f"\n💻 Platform: {sys.platform}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    print("\n📦 MODULE VERSIONS:")
    try:
        import cv2
        print(f"  OpenCV: {cv2.__version__}")
    except:
        print("  OpenCV: Not installed")
    
    try:
        import numpy
        print(f"  NumPy: {numpy.__version__}")
    except:
        print("  NumPy: Not installed")
    
    print("\n📝 PROJECT INFO:")
    print("  Name: SmartAttend - ID Card Capture System")
    print("  Version: 1.0")
    print("  Purpose: Digital attendance system with image processing")
    
    print("\n📂 FOLDER STATUS:")
    print(f"  Input Folder: {'✅ exists' if os.path.exists(config.INPUT_FOLDER) else '❌ missing'}")
    print(f"  Output Folder: {'✅ exists' if os.path.exists(config.OUTPUT_FOLDER) else '❌ missing'}")
    print(f"  Collage Folder: {'✅ exists' if os.path.exists(config.COLLAGE_FOLDER) else '❌ missing'}")


def menu_help():
    """Tampilkan help & documentation"""
    print("\n" + "="*60)
    print("📚 HELP & DOCUMENTATION")
    print("="*60)
    
    print("\n🎯 QUICK START:")
    print("""
1. Siapkan gambar di folder 'input/'
2. Pilih menu untuk capture atau load gambar
3. Gambar akan otomatis diproses (resize, brightness, timestamp)
4. Hasil disimpan di folder 'output/' dengan organisasi per tanggal
5. Buat collage dengan batch process
    """)
    
    print("\n📷 ADVANCED WEBCAM FEATURES:")
    print("""
Format: SPACE      → Capture/Start countdown
        F          → Cycle through filters
        G          → Toggle frame guides
        L          → Toggle light indicator
        P          → Toggle preview info
        ESC        → Exit/Cancel

Filters: None, Grayscale, Sepia, Blur, Edge Detection, Negative

Modes: 
  • Single: Capture 1 gambar
  • Countdown: 5 detik countdown sebelum auto-capture
  • Burst: Capture 5 gambar berturut-turut
    """)
    
    print("\n💾 FILE ORGANIZATION:")
    print("""
Output structure:
  output/
  ├── YYYY-MM-DD/
  │   ├── YYYYMMDD_HHMMSS_kartu.jpg
  │   └── ... (more files)
  └── collages/
      └── collage_YYYYMMDD_HHMMSS.jpg
    """)
    
    print("\n❓ FAQ:")
    print("""
Q: Bagaimana jika webcam tidak terdeteksi?
A: Check webcam connection atau try dengan index berbeda

Q: Gambar terlalu gelap?
A: Use histogram equalization atau adjust brightness manual

Q: Cara customize watermark text?
A: Edit WATERMARK_TEXT di config.py

Q: Bagaimana membaca dokumentasi lengkap?
A: Buka README.md atau lihat docstrings di source code
    """)
    
    print("\n📖 DOKUMENTASI LENGKAP:")
    print("  • README.md: Dokumentasi project lengkap")
    print("  • QUICKSTART.md: Panduan setup 5 menit")
    print("  • Docstrings: Ada di setiap function")
    print("  • config.py: Parameters documentation")
    
    view_readme = input("\nBuka README.md? (y/n): ").lower()
    if view_readme == 'y':
        try:
            if sys.platform == 'win32':
                os.startfile("README.md")
            else:
                os.system("cat README.md | less")
        except Exception as e:
            print(f"⚠️  Tidak bisa membuka file: {str(e)}")


def main():
    """Program utama"""
    print("\n🚀 Initializing SmartAttend System...")
    
    # Create necessary folders
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(COLLAGE_FOLDER, exist_ok=True)
    
    print("✅ System ready!\n")
    
    while True:
        print_menu()
        
        try:
            choice = input("Pilih menu (1-7): ").strip()
            
            if choice == '1':
                menu_load_and_process()
            elif choice == '2':
                menu_webcam_capture()
            elif choice == '3':
                menu_batch_process()
            elif choice == '4':
                menu_list_images()
            elif choice == '5':
                menu_view_output()
            elif choice == '6':
                menu_settings()
            elif choice == '7':
                print("\n👋 Terima kasih! Keluar dari SmartAttend System")
                print("Goodbye! 🚀\n")
                break
            else:
                print("❌ Pilihan tidak valid. Silakan pilih 1-7")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Program dihentikan oleh user")
            print("Goodbye! 🚀\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Silakan coba lagi\n")


if __name__ == "__main__":
    main()
