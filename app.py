from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
from PIL import Image
from models import db, Conversion
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversions.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

db.init_app(app)

# Ensure upload and converted directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        original_format = filename.rsplit('.', 1)[1].lower()
        new_format = request.form.get('format', 'jpg').lower()
        width = request.form.get('width')
        height = request.form.get('height')
        quality = int(request.form.get('quality', 85))

        # Save uploaded file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)

        # Open and process image
        img = Image.open(upload_path)
        if width and height:
            img = img.resize((int(width), int(height)))

        # Generate new filename
        new_filename = f"{uuid.uuid4().hex}.{new_format}"
        converted_path = os.path.join(app.config['CONVERTED_FOLDER'], new_filename)

        # Save converted image
        if new_format in ['jpg', 'jpeg']:
            img.save(converted_path, new_format.upper(), quality=quality)
        else:
            img.save(converted_path, new_format.upper())

        # Save to database
        conversion = Conversion(
            original_filename=filename,
            original_format=original_format,
            new_format=new_format,
            new_filename=new_filename,
            width=int(width) if width else None,
            height=int(height) if height else None
        )
        db.session.add(conversion)
        db.session.commit()

        return render_template('result.html', original=filename, converted=new_filename, format=new_format)
    else:
        flash('Invalid file type')
        return redirect(request.url)

@app.route('/history')
def history():
    conversions = Conversion.query.order_by(Conversion.timestamp.desc()).all()
    return render_template('history.html', conversions=conversions)

@app.route('/converted/<filename>')
def converted_file(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
