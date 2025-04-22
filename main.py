import cv2
import mediapipe as mp
import serial
import time

# Inicializa conexão serial com o Arduino
arduino = serial.Serial('COM6', 9600)
time.sleep(2)  # Aguarda a conexão estabilizar

# MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Função para detectar postura correta
def postura_correta(landmarks):
    ombro_esquerdo = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    quadril_esquerdo = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    cabeca = landmarks[mp_pose.PoseLandmark.NOSE.value]

    inclinacao = abs(ombro_esquerdo.y - quadril_esquerdo.y)
    
    if inclinacao < 0.15:  # valor empírico, pode ajustar conforme testes
        return True
    return False

# Função para detectar possível queda
def detecta_queda(landmarks):
    cabeca = landmarks[mp_pose.PoseLandmark.NOSE.value]
    tornozelo = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

    if cabeca.y > tornozelo.y - 0.1:  # Se a cabeça estiver quase no nível do chão
        return True
    return False

# Captura de vídeo
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
            arduino.write(b'ALERTA\n')  # Envia alerta de queda
        elif not postura_correta(landmarks):
            arduino.write(b'POSTURA_ERRADA\n')  # Feedback postural
        else:
            arduino.write(b'TUDO_OK\n')

    cv2.imshow('Monitoramento', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()
