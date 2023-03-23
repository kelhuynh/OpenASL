import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp
#from sklearn.model_selection import train_test_split
#from tensorflow.python.keras.utils import to_categorical
#from tensorflow.python.keras.models import Sequential
#from tensorflow.python.keras.layers import LSTM, Dense
#from tensorflow.python.keras.callbacks import TensorBoard


mp_holistic = mp.solutions.holistic # Holistic model
mp_drawing = mp.solutions.drawing_utils # Drawing utilities

def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
    return image, results
def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS) # Draw pose connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS) # Draw left hand connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS) # Draw right hand connections
def draw_styled_landmarks(image, results):
    # Draw pose connections
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                             ) 
    # Draw left hand connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                             mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                             ) 
    # Draw right hand connections  
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                             mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                             ) 
def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])

def sel_mode(key, mode):
    num = -1
    if key == 49:  # 1 - Normal operation
          mode = 0
    if key == 50:  # 2 - Train keypoint
         mode = 1
    return num, mode

def __ui(self, image, frames, mode, num):
    text = "FPS: {}  Resolution: {}x{}".format(frames, image.shape[1], image.shape[0])
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
    text_w, text_h = text_size
    cv2.rectangle(image, (636 - text_w, 0), (640, 4 + text_h), (0,0,0), -1)
    cv2.putText(image, text, (638 - text_w, 2 + text_h), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
        
    if mode == 0:
        text_size, _ = cv2.getTextSize('Press 2 to Training Mode, 3 to Point History, ESC to Exit Program', cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        text_w, text_h = text_size
        cv2.rectangle(image, (0,0), (0 + text_w, 2 + text_h), (0,0,0), -1)
        cv2.putText(image, 'Press 2 to Training Mode, 3 to Point History, ESC to Exit Program', (0, text_h), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        text_size, _ = cv2.getTextSize("The current string is: " + self.tts, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        text_w, text_h = text_size
        cv2.rectangle(image, (0, 475 - text_h), (text_w, 480), (0,0,0), -1)
        cv2.putText(image, "The current string is: " + self.tts, (0, 476), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

    elif mode == 1:
        text_size, _ = cv2.getTextSize('Press 1 for Translation, 3 to Point History, ESC to Exit Program', cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        text_w, text_h = text_size
        cv2.rectangle(image, (0,0), (0 + text_w, 2 + text_h), (0,0,0), -1)
        cv2.putText(image, 'Press 1 for Translation, 3 to Point History, ESC to Exit Program', (0, text_h), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

    elif mode == 2:
        text_size, _ = cv2.getTextSize('Press 1 for Translation, 2 to Training Mode, ESC to Exit Program', cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        text_w, text_h = text_size
        cv2.rectangle(image, (0,0), (0 + text_w, 2 + text_h), (0,0,0), -1)
        cv2.putText(image, 'Press 1 for Translation, 2 to Training Mode, ESC to Exit Program', (0, text_h), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    return

def __textBuilder(self, tts, text, frame):
        
    if (frame%40) == 0: #Modify this value for string record frequency
         tts = tts + text + " "

    return tts
    
def __textToSpeech(self, tts, text):

    if text == "Speak": #Read the current string and clear string
        engine = pyttsx3.init()
        engine.setProperty('rate', 125)
        voices = engine.getProperty('voices') 
        engine.setProperty('voice', voices[1].id)
        engine.say(tts)
        engine.runAndWait()
        engine.stop()
        tts = ""

    return tts


# Path for exported data, numpy arrays
cwd = os.getcwd()
DATA_PATH = os.path.join('MP_Data') 

# Actions that we try to detect
actions = np.array(['hello', 'thanks', 'iloveyou'])

# Thirty videos worth of data
no_sequences = 30

# Videos are going to be 30 frames in length
sequence_length = 30

# Folder start
start_folder = 0
for action in actions: 
    dirmax = np.max(np.array(os.listdir(os.path.join(DATA_PATH, action))).astype(int))
    for sequence in range(1,no_sequences+1):
        try: 
            os.makedirs(os.path.join(DATA_PATH, action, str(dirmax+sequence)))
        except:
            pass
""" for action in actions: 
    for sequence in range(no_sequences):
        try: 
            os.makedirs(os.path.join(DATA_PATH, action, str(sequence)))
        except:
            pass """

cap = cv2.VideoCapture(0)
# Set mediapipe model 
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        key = cv2.waitKey(10)
        if key == 27:
            break
        num, mode = sel_mode(key, mode)

    # NEW LOOP
    # Loop through actions
    for action in actions:
        # Loop through sequences aka videos
        for sequence in range(dirmax, dirmax+no_sequences+1):
            # Loop through video length aka sequence length
            for frame_num in range(sequence_length):

                # Read feed
                ret, frame = cap.read()

                # Make detections
                image, results = mediapipe_detection(frame, holistic)

                # Draw landmarks
                draw_styled_landmarks(image, results)
                
                # NEW Apply wait logic
                if frame_num == 0: 
                    cv2.putText(image, 'STARTING COLLECTION', (120,200), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 4, cv2.LINE_AA)
                    cv2.putText(image, 'Collecting frames for {} Video Number {}'.format(action, sequence), (15,12), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    # Show to screen
                    cv2.imshow('OpenCV Feed', image)
                    cv2.waitKey(500)
                else: 
                    cv2.putText(image, 'Collecting frames for {} Video Number {}'.format(action, sequence), (15,12), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    # Show to screen
                    cv2.imshow('OpenCV Feed', image)
                
                # NEW Export keypoints
                keypoints = extract_keypoints(results)
                npy_path = os.path.join(DATA_PATH, action, str(sequence), str(frame_num))
                np.save(npy_path, keypoints)

                # Break gracefully
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                    
    cap.release()
    cv2.destroyAllWindows()