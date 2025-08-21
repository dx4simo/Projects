# -----------------------------------------------------
# -- Photo Editor (Improved) with Debugging (Recursive + HEIC optional)
# -- Pillow docs: https://pillow.readthedocs.io/en/stable/
# -----------------------------------------------------

from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError
import sys

# ====== (اختياري) دعم HEIC/HEIF لو متثبت pillow-heif ======
try:
    from pillow_heif import register_heif_opener  # pip install pillow-heif
    register_heif_opener()
    HEIF_ENABLED = True
except Exception:
    HEIF_ENABLED = False

# ====== إعدادات عامة ======
CONTRAST_FACTOR = 1.5
FORCE_OUTPUT_JPG = True       # True: حفظ دائمًا JPG. False: نفس امتداد الأصل إن أمكن.
RECURSIVE = True              # امشي جوّه كل الساب-فولدرز
SHARPEN_FIRST = True          # طبق فلتر SHARPEN قبل التحويل
TO_GRAYSCALE = True           # حول إلى تدرّج رمادي 'L'


# ====== مسارات ======
BASE_DIR = Path(__file__).resolve().parent
IN_DIR = BASE_DIR / "imgs"          
OUT_DIR = BASE_DIR / "editedImgs"       
OUT_DIR.mkdir(parents=True, exist_ok=True)

def process_one(src: Path) -> bool:
    """يرجّع True لو اتحفظت صورة بنجاح، وإلا False"""
    try:
        with Image.open(src) as img_in:
            img = img_in
            if SHARPEN_FIRST:
                img = img.filter(ImageFilter.SHARPEN)
            if TO_GRAYSCALE:
                img = img.convert("L")

            out_ext = ".jpg" if FORCE_OUTPUT_JPG else (src.suffix.lower() or ".jpg")
            out_name = f"{src.stem}_edited{out_ext}"
            out_path = OUT_DIR / out_name

            save_kwargs = {}
            if out_ext in (".jpg", ".jpeg"):
                # مفيش 'keep' هنا — استخدم 0 لأعلى جودة وثبات
                save_kwargs.update({
                    "quality": 95,
                    "optimize": True,
                    "subsampling": 0,   # << المهم: لا تستخدم "keep"
                })

            img.save(out_path, **save_kwargs)
            print(f"✅ Saved: {out_path}")
            return True

    except UnidentifiedImageError:
        print(f"⏭️ Skipped (not an identifiable image): {src}")
    except PermissionError:
        print(f"⚠️ Permission denied: {src}")
    except OSError as e:
        # بيظهر أحيانًا مع ملفات تالفة أو HEIC بدون دعم
        print(f"❌ OSError on {src}: {e}")
        if (src.suffix.lower() in {".heic", ".heif"}) and not HEIF_ENABLED:
            print("💡 Tip: install HEIC support → pip install pillow-heif")
    except Exception as e:
        print(f"❌ Error processing {src}: {e}")
    return False

def main():
    print(f"🔎 BASE_DIR : {BASE_DIR}")
    print(f"📂 IN_DIR   : {IN_DIR} (exists={IN_DIR.exists()})")
    print(f"📁 OUT_DIR  : {OUT_DIR} (exists={OUT_DIR.exists()})")
    print(f"📸 HEIF support: {'ON' if HEIF_ENABLED else 'OFF'}")
    print("-" * 60)

    if not IN_DIR.exists():
        print(f"❌ Input folder not found. Create it and put images inside: {IN_DIR}")
        sys.exit(1)

    # لف على الملفات
    entries = (IN_DIR.rglob("*") if RECURSIVE else IN_DIR.iterdir())

    total_seen = 0
    total_images_tried = 0
    total_saved = 0

    for p in entries:
        if p.is_dir():
            continue

        total_seen += 1
        # تجاهل ملفات الإخراج لو بالخطأ جوا imgs (احتياطًا)
        if OUT_DIR in p.parents:
            continue

        print(f"→ Checking: {p.relative_to(BASE_DIR)}")
        total_images_tried += 1
        if process_one(p):
            total_saved += 1

    print("-" * 60)
    print(f"📊 Summary")
    print(f"  • Files scanned : {total_seen}")
    print(f"  • Tried to edit : {total_images_tried}")
    print(f"  • Saved edited  : {total_saved}")
    print(f"  • Output dir    : {OUT_DIR}")


if __name__ == "__main__":
    main()
