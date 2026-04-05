try: #Jetson
    import Jetson.GPIO as GPIO
    import time

    GPIO.setmode(GPIO.BOARD)

    class Led:
        def __init__(self):
            self.r = 7
            self.g = 15
            self.b = 29
            self.channels = (self.r, self.g, self.b)  # channels R G B
            GPIO.setup(self.channels, GPIO.OUT)

        def change(self, c, waiting_time):
            if c == 'R':
                GPIO.output(self.r, 1)
                GPIO.output(self.g, 0)
                GPIO.output(self.b, 0)

            elif c == 'G':
                GPIO.output(self.r, 0)
                GPIO.output(self.g, 1)
                GPIO.output(self.b, 0)

            elif c == 'O':
                GPIO.output(self.r, 1)
                GPIO.output(self.g, 1)
                GPIO.output(self.b, 0)

            time.sleep(waiting_time)

            self.turn_off()

        def turn_off(self):
            GPIO.output(self.r, 0)
            GPIO.output(self.b, 0)
            GPIO.output(self.g, 0)

        def exit(self):
            GPIO.cleanup()

except: #autre
    class Led:
        def __init__(self):
            pass

        def change(self, c, waiting_time):
            pass

        def turn_off(self):
            pass

        def exit(self):
            pass
