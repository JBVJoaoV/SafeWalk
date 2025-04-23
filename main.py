import cv2
import mediapipe as mp
import serial
import time

# Inicializa conexão serial com o Arduino
arduino = serial.Serial('COM6', 9600)
time.sleep(2)

# Inicializa o MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Detecta postura correta com base em ombro e quadril (vista de costas)
def postura_correta(landmarks):
    ombro = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    quadril = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    
    inclinacao = abs(ombro.y - quadril.y)

    # Quanto menor a diferença, mais "reta" está a postura
    return inclinacao < 0.10

# Detecta possível queda com base em quadril e tornozelo
def detecta_queda(landmarks):
    quadril = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    tornozelo = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

    # Se o quadril estiver muito próximo ao chão, pode ser queda
    return quadril.y > tornozelo.y - 0.05

# Carrega o vídeo
video_path = "MicrosoftTeams-video.mp4"  # Caminho do seu vídeo
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark

        if detecta_queda(landmarks):
            print(" Queda detectada")
            arduino.write(b'N\n')  # Envia alerta para o Arduino
        elif not postura_correta(landmarks):
            print("Postura incorreta detectada")
            arduino.write(b'N\n')  # Envia aviso de postura
        else:
            print("Postura correta")
            arduino.write(b'S\n')  # Envia status OK

    cv2.imshow('Monitoramento', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Pressione ESC para sair
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()
