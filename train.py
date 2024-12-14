import cv2
import face_recognition
import numpy as np

def load_known_faces(known_face_images):
    known_face_encodings = []
    known_face_names = []

    for image_path, name in known_face_images:
        image = face_recognition.load_image_file("C:\\Users\\Kitti\\Downloads\\human1.jpg")
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(name)
    
    return known_face_encodings, known_face_names

def recognize_faces_in_video(known_face_encodings, known_face_names):
    video_capture = cv2.VideoCapture(0)  # Use 0 for webcam

    while True:
        ret, frame = video_capture.read()
        rgb_frame = frame[:, :, ::-1]  # Convert BGR to RGB for face_recognition

        # Detect all face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            name = "Unknown"
            if True in matches:
                best_match_index = np.argmin(face_distances)
                name = known_face_names[best_match_index]

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Load known faces (Provide image paths and corresponding names)
    known_face_images = [
        ("C:\\Users\\Kitti\\Downloads\\human2.jpg", "Person1"),
        ("C:\\Users\\Kitti\\Downloads\\human3.jpg", "Person2"),
    ]
    known_face_encodings, known_face_names = load_known_faces(known_face_images)

    # Recognize faces in live video feed
    recognize_faces_in_video(known_face_encodings, known_face_names)
