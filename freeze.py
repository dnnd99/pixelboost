from flask_frozen import Freezer
from app import app

freezer = Freezer(app)

@freezer.register_generator
def static_pages():
    # Daftarin semua rute yang mau dijadikan HTML
    yield "/"
    # yield "/about/" # tambahin sesuai rute kamu

if __name__ == "__main__":
    freezer.freeze()
