from flask import Flask, render_template, request, send_file
from pdf2image import convert_from_path
import os, shutil
from inference import inference

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './temp'
app.config['WEIGHTS'] = "./best.pt"
# fields = ['pan of the employee', 'tan of the deductor', 'quarters', 'name and address of the employee', 'certificate no.', 'name and address of the employer', 'last updated on', 'i, ']

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/upload", methods = ["POST"])
def fileUpload():
    uploaded_files = request.files.getlist("file[]")
    print(uploaded_files)
    if(not os.path.isdir(app.config['UPLOAD_FOLDER'])):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    for file in uploaded_files:
        fileName = file.filename
        print("file: ", file)
        file_ext = os.path.splitext(fileName)[1]
        if(file_ext.lower() == ".pdf"):
            filePath = os.path.join(app.config['UPLOAD_FOLDER'], fileName)
            file.save(filePath)
            pages = convert_from_path(os.path.join(app.config['UPLOAD_FOLDER'], fileName))
            folderName = os.path.join(app.config['UPLOAD_FOLDER'], fileName[:-4])
            os.makedirs(folderName)
            counter = 1
            for page in pages:
                page.save(folderName +'/' + str(counter) + '.jpg', 'JPEG')
                counter += 1
            print('PDF converted')
            os.remove(filePath)
        else:
            if(not os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], "others"))):
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], "others"))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "others", fileName))
    result = inference()
    os.remove(app.config['UPLOAD_FOLDER'])
    return render_template('home.html', flag = result)


@app.route("/downloadFile")
def sendFile():
    return send_file('./recognized.json',
                     mimetype='text/json',
                     attachment_filename='recognized.json',
                     as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)