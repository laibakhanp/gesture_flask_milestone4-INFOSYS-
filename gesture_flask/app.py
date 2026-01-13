from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import math
import time

app = Flask(__name__)

# ======== MediaPipe Setup ==========
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# ======== Camera ==========
cap = cv2.VideoCapture(0)

# ======== Shared State (used by UI) ==========
state = {
    "volume": 50,
    "gesture": "No Gesture",
    "quality": 1
}

prev_vol = 50
last_time = time.time()


def generate():
    global prev_vol, last_time, state

    while True:
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        vol_percent = 50
        gesture_name = "No Gesture"
        quality = 1

        if result.multi_hand_landmarks:
            quality = 4
            for handLms in result.multi_hand_landmarks:
                lm_list = []
                h, w, _ = img.shape

                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((id, cx, cy))

                if len(lm_list) >= 9:
                    x1, y1 = lm_list[4][1], lm_list[4][2]
                    x2, y2 = lm_list[8][1], lm_list[8][2]

                    cv2.circle(img, (x1, y1), 10, (0,255,0), -1)
                    cv2.circle(img, (x2, y2), 10, (0,255,0), -1)
                    cv2.line(img,(x1,y1),(x2,y2),(0,255,0),3)

                    length = math.hypot(x2-x1, y2-y1)
                    vol_percent = int(np.interp(length,[30,200],[0,100]))

                    if length < 40:
                        gesture_name = "Volume Down"
                    elif length > 180:
                        gesture_name = "Volume Up"
                    else:
                        gesture_name = "Volume Control"

                    vol_bar = np.interp(length,[30,200],[400,150])
                    cv2.rectangle(img,(50,150),(85,400),(255,255,255),3)
                    cv2.rectangle(img,(50,int(vol_bar)),(85,400),(0,255,0),-1)
                    cv2.putText(img,f"{vol_percent}%",(35,430),
                                cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2)

                    mp_draw.draw_landmarks(img,handLms,mp_hands.HAND_CONNECTIONS)

        state["volume"] = vol_percent
        state["gesture"] = gesture_name
        state["quality"] = quality

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/status")
def status():
    return jsonify(state)


if __name__ == "__main__":
    app.run(debug=True)
 
