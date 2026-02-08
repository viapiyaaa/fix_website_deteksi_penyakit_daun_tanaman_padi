from utils.validation import validate_leaf_rice_image

# Daftar path gambar
image_paths = [
    "images/sheathblight.jpg",
    "images/jagung.jpg",
    "images/blast.jpg",
    "images/bacterialblight.jpg"
]

# Proses semua gambar dan simpan hasil
results = [validate_leaf_rice_image(path) for path in image_paths]

print(results)