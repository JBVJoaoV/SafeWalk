import cv2
import mediapipe as mp
import serial
import time
import math

# Inicializa conexão serial com o Arduino
arduino = serial.Serial('COM6', 9600)
time.sleep(2)

# Inicializa o MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

def postura_correta(landmarks, margem_erro=0.03):
    ombro_esq = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    ombro_dir = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

    diferenca_y = abs(ombro_esq.y - ombro_dir.y)

    # Se os ombros estão praticamente na mesma altura, postura está correta
    return diferenca_y < margem_erro

# Detecta possível queda com base em quadril e tornozelo
def detecta_queda(landmarks):
    quadril_esq = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    quadril_dir = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    tornozelo_esq = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    tornozelo_dir = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    nariz = landmarks[mp_pose.PoseLandmark.NOSE.value]

    # Média da posição dos quadris e tornozelos
    quadril_medio_y = (quadril_esq.y + quadril_dir.y) / 2
    tornozelo_medio_y = (tornozelo_esq.y + tornozelo_dir.y) / 2

    # Se o quadril estiver próximo do chão (ou abaixo do esperado)
    queda_por_quadril = quadril_medio_y > tornozelo_medio_y - 0.05

    # Adicional: cabeça (nariz) muito próxima do chão → queda provável
    queda_por_nariz = nariz.y > tornozelo_medio_y - 0.1

    return queda_por_quadril or queda_por_nariz

# Carrega o vídeo
#video_path = "MicrosoftTeams-video.mp4"  # Caminho do seu vídeo
cap = cv2.VideoCapture(0)

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
-/            arduino.write(b'N\n')  # Envia aviso de postura
        else:
            print("Postura correta")
            arduino.write(b'S\n')  # Envia status OK

    cv2.imshow('Monitoramento', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Pressione ESC para sair
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()
