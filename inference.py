import torch, os, json
from PIL import Image
import numpy as np, pytesseract, pandas as pd, cv2

def inference():
    model = None
    flag = 0
    if(not model):
        model = torch.hub.load('ultralytics/yolov5', 'custom', path="./best.pt")

    # inference on testing image
    results = {}

    for root, subdirectories, files in os.walk('./temp'):
        for subdirectory in subdirectories:
            print(os.path.join(root, subdirectory))
        for file in files:
            img = Image.open(os.path.join(root, file))
            result = model(img)
            results[file] = result.pandas().xyxy[0]
    
    file = open("./recognized.json", "w+")

    d = {}
    for root, dirs, files in os.walk('./temp'):
        for dir in dirs:
            print('dir: ', dir)
            d[dir] = {}
    for root, dirs, files in os.walk('./temp'):
        for dir in dirs:        
            for fileName in os.listdir(os.path.join(root, dir)):
                print("fileName: ", fileName)
                # Read image from which text needs to be extracted
                img = cv2.imread(os.path.join(root, dir, fileName))

                # Convert the image to gray scale
                # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                im2 = img.copy()
                
                df = pd.DataFrame(results[fileName])
                for index,row in df.iterrows():
                    cropped = im2[int(row['ymin']):int(row['ymax']), int(row['xmin']):int(row['xmax'])]
                    kernel = np.array([[0, -1, 0],
                                [-1, 5,-1],
                                [0, -1, 0]])
                    cropped = cv2.filter2D(src=cropped, ddepth=-1, kernel=kernel)
                    # cv2.imshow('cropped', cropped)
                    # Apply OCR on the cropped image
                    text = pytesseract.image_to_string(cropped).strip()
                    print('text: ', text)
                    k = ''
                    v = ''
                    for i in range(len(text)):
                        if(text[i] == '\n' or text[i] == ':'):
                            v = text[i+1:].strip()
                            break
                        else:
                            k += text[i]
                    # Appending the text into file
                    d[dir][k] = v
    print(d)
    file.write(json.dumps(d))
    flag = 1
    file.close()
    return flag

# inference()