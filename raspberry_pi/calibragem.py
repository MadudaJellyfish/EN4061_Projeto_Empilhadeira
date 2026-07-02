import cv2
import numpy as np

# Configurações do tabuleiro
CHECKERBOARD = (8, 5) # Cantos internos do seu tabuleiro
SQUARE_SIZE = 0.025   # Tamanho do quadrado em METROS (ex: 2.5cm = 0.025)

#classe que organiza a calibração da camera
class Calibration:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.criterio = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        #modelo matemático do tabuleiro
        self.objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32) 
        self.objp[:, :2] = 
        np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2) * SQUARE_SIZE
        #arrays com os pontos do mundo real e do plano da imagem
        self.objpoints = [] # Pontos 3d no mundo real
        self.imgpoints = [] # Pontos 2d no plano da imagem

    #------------------------------------------#
    #captura a imagem do tabuleiro
    def capture_chess_image(self):
        print("Pressione 's' para salvar um frame ou 'q' para terminar a captura e iniciar a calibração.")
        print("Capture pelo menos 20 imagens!!!")
        while True:
            ret, self.img = self.capture.read()
            if not ret: break

            self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

            ret_c, corners = cv2.findChessboardCorners(
            gray, 
            CHECKERBOARD, 
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE
            )

            if ret_c:
                self.objpoints.append(self.objp)
                corners2 = corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                self.imgpoints.append(corners)
                cv2.drawChessboardCorners(display_frame, CHECKERBOARD, corners2, ret_c)
                cv2.putText(display_frame, "TABULEIRO ENCONTRADO! Aperte 'S'", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, "Buscando tabuleiro...", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow('Calibragem', display_frame)
            key = cv2.waitKey(1)
            
            if key == ord('s'):
                if ret_c:
                    self.objpoints.append(self.objp)
                    self.imgpoints.append(corners2)
                    print(f"Imagem {len(self.objpoints)} salva com sucesso!")
                else:
                    print("Tabuleiro não detectado. Ajuste a câmera.")
                    
            elif key == ord('q'):
                print("Encerrando captura...")
                break
        
        self.capture.release()
        cv2.destroyAllWindows()

    # ------------------------------------- #
    #pega os pontos do mundo 3d e compara com os pontos 2d distorcidos capturados pela câmera
    def calibrate(self):
        ret, self.mtx, self.distort, self.rvecs, self.tvecs = 
            cv2.calibrateCamera(self.objpoints, self.imgpoints, self.gray.shape[::-1], None, None)
        print ('ret: ', ret)
        print ('mtx:\n', self.mtx)
        print ('distort: ', self.distort)
        print ('rvecs: ', self.rvecs)
        print ('tvecs: ', self.tvecs)
        print("Calibração salva com sucesso no arquivo 'params_multilaser.npz'!")
        np.savez('calibration_savez', mtx=self.mtx, dist=self.distort,rvecs=self.rvecs,tvecs=self.tvecs)

    #--------------------------------------- #
    def undistort(self):
        h, w = self.img.shape[:2]
        self.newcameramtx, self.roi=cv2.getOptimalNewCameraMatrix(self.mtx, self.distort, (w,h), 1, (w,h))
        # undistort
        undst = cv2.undistort(self.img, self.mtx, self.distort, None, self.newcameramtx)
        # crop the image
        x, y, self.w, self.h = self.roi
        undst = undst[y:y+self.h, x:x+self.w]
        # cv2.imwrite('calibresult.png', dst)
        cv2.imshow('undistorted', undst)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()

    # ------------------------------------------------------------ #
    def remapping(self):
        # undistort
        mapx, mapy = cv2.initUndistortRectifyMap(self.mtx, self.distort, None, self.newcameramtx, (self.w,self.h), 5)
        dstort = cv2.remap(self.img, mapx, mapy, cv2.INTER_LINEAR)
        # crop the image
        x, y, w, h = self.roi
        dst = dstort[y:y+h, x:x+w]
        cv2.imshow('Remapping', dst)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ------------------------------------------------------------ #
    def projection_Error(self):
        mean_error = 0
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], self.rvecs[i], self.tvecs[i], self.mtx, self.distort)
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
            mean_error += error
        print( "total error: {}".format(mean_error/len(self.objpoints)) )


# ================ Camera Calibration =============


calib_obj = Calibration()
calib_obj.capture_chessboard()

if len(calib_obj.objpoints) > 0:
    print("Calibrando imagem...")
    calib_obj.calibrate()
    calib_obj.undistort()
    calib_obj.remapping()
    calib_obj.projection_Error()
    print("Calibragem finalizada :)")

else:
    print("Nenhuma imagem capt")
