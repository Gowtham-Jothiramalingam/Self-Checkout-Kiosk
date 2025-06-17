# Self-Checkout-Kiosk
Engineered an intelligent self-checkout kiosk for Indian fruits and vegetables, automating item identification and pricing to reduce checkout queues and optimize store operations during peak hours

![image](https://github.com/user-attachments/assets/dc117ce3-9aff-4108-a8ac-d1440933199c)

# Self-Checkout Kiosk: YOLO-based Product Recognition

## Overview

This project implements an intelligent self-checkout kiosk for fruits and vegetables, leveraging YOLOv5 for real-time object detection and a Tkinter-based GUI for user interaction. The system automates checkout by identifying produce, weighing items, and calculating prices, streamlining the retail experience for both customers and store operators.

---


## Features

- Real-time object detection of fruits and vegetables using YOLOv5.
- Automated weight-based pricing via a calibrated load cell.
- User-friendly checkout interface built with Tkinter.
- Seamless integration of hardware and software for a complete kiosk experienc.
- Easy dataset expansion and retraining support.



## Project Structure

| Folder/File         | Description                                                      |
|---------------------|------------------------------------------------------------------|
| `src/Train_Yolo.ipynb`  | Jupyter notebook for training the YOLOv5 model on your dataset   |
| `dataset/`          | Contains images and annotations for fruits and vegetables        |
| `src/Esp/caliberation/`     | Load cell calibration code and scripts                           |
| `GUI/`              | Assets and resources for the Tkinter-based GUI                   |
| `src/Kiosk_main.py`     | Main Python script for running the kiosk application             |

---


### Prerequisites

- Python 3.7 or higher.
- pip (Python package manager)
- [PyTorch](https://pytorch.org/) (for YOLOv5)
- OpenCV (`cv2`)
- Tkinter (usually included with Python)
- PIL (Pillow)


---

## Usage

1. **Train the YOLO Model**
   - Open `Train_Yolo.ipynb` and follow the notebook steps to train or fine-tune the YOLOv5 model on your dataset.

2. **Calibrate the Load Cell**
   - Use the scripts in the `caliberation/` folder to calibrate your load cell hardware before running the kiosk application.

3. **Run transmit_reading.ino**
   - starts transmitting the loadcell value in a local host server. Note the url shown after the code and replace the url in Kiosk_main.py.
  
4. **Run the Kiosk Application**
   - Start the application with:
     ```bash
     python Kiosk_main.py
     ```
   - The GUI will guide the user through placing items, weighing, and payment steps.

---

## Dataset

- The `dataset/` folder contains images of Indian fruits and vegetables, annotated for YOLO training.
- To add new items, expand the dataset and update annotations, then retrain the YOLO model using the provided notebook.
- A total of 636 images of 14 different fruits and vegetables were captured under various lighting conditions to enhance the model's robustness and adaptability to different environments.

A total of 636 images of 14 different fruits and vegetables were captured under various lighting conditions to enhance the model's robustness and adaptability to different environments.

| CLASS | NAME           | NO OF IMAGES |
|-------|----------------|--------------|
| 0     | Apple          | 60           |
| 1     | Beetroot       | 41           |
| 2     | Brinjal        | 60           |
| 3     | Brinjal White  | 30           |
| 4     | Capsicum       | 15           |
| 5     | Chilly         | 17           |
| 6     | Coconut        | 90           |
| 7     | Guava          | 30           |
| 8     | Lemon          | 39           |
| 9     | Mosambi        | 60           |
| 10    | Onion          | 40           |
| 11    | Pomegranate    | 30           |
| 12    | Potato         | 60           |
| 13    | Tomato         | 64           |

## GUI

### Start Window:
![image](https://github.com/user-attachments/assets/7e843e09-4ce3-47c0-9db9-af5ba3b3f508)

### Main Window:
![image](https://github.com/user-attachments/assets/a84b4db0-d649-4148-9db8-7532409f7c36)

### Checkout Window:
![image](https://github.com/user-attachments/assets/53f9a658-9e0a-4782-92bd-bb1c22a1fe0a)

## Communication between ESP8266 and Python script

In our setup, the ESP8266 connects to our Wi- Fi network and creates a local host server, awaiting requests from the Python script running on our system. Upon receiving a request, the ESP8266 executes the desired code to measure the weight using the load cell and HX711 amplifier. Subsequently, it returns the weight measurement as an HTTP request, allowing the Python script to retrieve and process the data seamlessly. This integration streamlines the communication between the hardware and software components, facilitating efficient operation of the self-checkout system.

![image](https://github.com/user-attachments/assets/4a9a2f7e-0b87-4448-89be-598d25594dca)

