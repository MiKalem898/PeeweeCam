import cv2
import torch
import numpy as np
from vision import Vision
from led import Led
from interface import Interface
import threading

np.bool = bool

first_track_done = False
is_running = True

#verification CUDA
print(f'PyTorch: {"GPU" if torch.cuda.is_available() else "CPU"}')

app = Interface()
vision = Vision(app)
app.vision = vision
led = Led()
led.turn_off() # éteindre la led au départ

vision.warmup_model()

print('Chargement...')


def yolo_main():
    try:
        while is_running:
            vision.update()

            # if cv2.waitKey(1) == ord('a') or vision.recognizer == None:
            #    break

        led.exit()

    except Exception as e:
        print(e)

    #vider la mémoire
    finally:
        if vision.cam.isOpened:
            vision.cam.release()

        cv2.destroyAllWindows()

        del vision.model       # del YOLO
        del vision.recognizer  # del FaceNet
        torch.cuda.empty_cache() # vider cache VRAM PyTorch


if __name__ == "__main__":    
    def starter():
        main_thread = threading.Thread(target=yolo_main)
        main_thread.start()

    app.after(0, starter)
    app.mainloop()
    is_running = False

