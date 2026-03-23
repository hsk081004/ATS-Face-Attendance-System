import cv2
import face_recognition
import numpy as np
import os
from ats_app.models import Attendance, Student

# store known faces
known_faces = []
known_names = []

# folder containing student images
path = "faces"

valid_extensions = (".jpg", ".jpeg", ".png")

images = os.listdir(path)
print("Loaded images:", images)

# load images and create encodings
for img_name in images:

    if not img_name.lower().endswith(valid_extensions):
        continue

    img_path = os.path.join(path, img_name)

    img = face_recognition.load_image_file(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    encodings = face_recognition.face_encodings(img)

    if len(encodings) > 0:
        known_faces.append(encodings[0])

        name = os.path.splitext(img_name)[0]
        name = name.capitalize()

        known_names.append(name)

print("Encodings created for:", known_names)


def recognize():

    marked = []

    # 🔥 AUTO CAMERA DETECT (WORKS FOR IRIUN + NORMAL CAM)
    sources = [0, 1, 2, "http://192.168.1.5:8080/video"]

    video = None

    for src in sources:
        print(f"Trying camera source: {src}")
        cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)

        if cap.isOpened():
            print(f"✅ Camera connected: {src}")
            video = cap
            break

    if video is None:
        print("❌ No camera found")
        return

    while True:
        ret, frame = video.read()

        if not ret:
            print("❌ Frame not received")
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        faces = face_recognition.face_locations(rgb_small)
        encodings = face_recognition.face_encodings(rgb_small, faces)

        face_names = []  # ✅ FIX: store names per face

        for face_encoding in encodings:

            matches = face_recognition.compare_faces(known_faces, face_encoding)
            face_distances = face_recognition.face_distance(known_faces, face_encoding)

            name = "Unknown"

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index] and face_distances[best_match_index] < 0.5:
                    name = known_names[best_match_index]

                    # ✅ FIXED DB SAVE
                    if name not in marked:
                        try:
                            student_obj = Student.objects.get(name=name)
                            Attendance.objects.create(student=student_obj)
                            marked.append(name)
                            print("✅ Attendance Marked:", name)

                        except Student.DoesNotExist:
                            print("❌ Student not found in DB:", name)

                        except Exception as e:
                            print("❌ DB error:", e)

            face_names.append(name)

        # ✅ DRAW CORRECT NAMES
        for (top, right, bottom, left), name in zip(faces, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Face Attendance System", frame)

        if cv2.waitKey(1) == 27:
            break

    video.release()
    cv2.destroyAllWindows()