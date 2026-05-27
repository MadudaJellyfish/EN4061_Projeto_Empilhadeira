import cv2
import numpy as np
import math
from pupil_apriltags import Detector

def get_robot_yaw(R):
    yaw_rad = math.atan2(R[0, 2], R[2, 2])
    return math.degrees(yaw_rad)

try:
    with np.load("params_multilaser.npz") as data:
        mtx = data['mtx']
        dist = data['dist']
    cam_params = [mtx[0,0], mtx[1,1], mtx[0,2], mtx[1,2]]
    print("Calibração carregada com sucesso!")
except Exception as e:
    cam_params = None
    print(f"Aviso: Arquivo de calibração não carregado ({e}). Pose 3D desativada.")


at_detector = Detector(families='tag25h9')
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

TAG_SIZE = 0.05 # 5cm em metros

print("Iniciando detecção... Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Falha ao capturar frame da câmera.")
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 3. Detectar Tags
    if cam_params:
        results = at_detector.detect(gray, estimate_tag_pose=True, 
                                   camera_params=cam_params, 
                                   tag_size=TAG_SIZE)
    else:
        results = at_detector.detect(gray, estimate_tag_pose=False)

    for r in results:
        # Extrair cantos para desenho
        pts = np.array(r.corners, dtype=np.int32)
        cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
        
        # Canto superior esquerdo para texto
        origem_texto = (int(r.corners[0][0]), int(r.corners[0][1]) - 10)

        # 4. Cálculo de Localização (Se houver calibração)
        if r.pose_t is not None and r.pose_R is not None:
            tx = r.pose_t[0][0] # Desvio lateral
            tz = r.pose_t[2][0] # Profundidade (Z)
            
            # Bearing: Onde a tag está na visão do robô (esquerda/direita)
            bearing = math.degrees(math.atan2(tx, tz))
            
            # Tag Yaw: Para onde a tag está virada
            tag_yaw = get_robot_yaw(r.pose_R)

            info = f"ID:{r.tag_id} Z:{tz:.2f}m Pos:{bearing:.1f}deg Ori:{tag_yaw:.1f}deg"
        else:
            info = f"ID: {r.tag_id} (Sem Pose)"

        # Desenhar fundo para o texto (melhora leitura)
        cv2.putText(frame, info, origem_texto, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3) # Contorno
        cv2.putText(frame, info, origem_texto, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1) # Texto

    # 5. Exibir
    cv2.imshow('Localizacao Robotica - AprilTag', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
