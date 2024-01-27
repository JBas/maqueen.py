from micropython import const
import microbit
import machine, utime
import neopixel

BLACK:tuple[int] = (0, 0, 0)
WHITE:tuple[int] = (255, 255, 255)
RED:tuple[int] = (255, 0, 0)
GREEN:tuple[int] = (0, 255, 0)
BLUE:tuple[int] = (0, 0, 255)
YELLOW:tuple[int] = (255,255,0)
CYAN:tuple[int] = (0, 255, 255)
MAGENTA:tuple[int] = (255, 0, 255)

LEFT_LED:int                = const(0)
RIGHT_LED:int               = const(1)

LEFT_MOTOR:int              = const(0)
RIGHT_MOTOR:int             = const(1)

class Maqueen():

    I2C_ADDR                = const(0x10) # I just took this from the maqueen github repo
    VERSION_CNT_REGISTER    = const(0x32)
    VERSION_DATA_REGISTER   = const(0x33)
    LEFT_LED_REGISTER       = const(0x0B)
    RIGHT_LED_REGISTER      = const(0x0C)
    LEFT_MOTOR_REGISTER     = const(0x00)
    RIGHT_MOTOR_REGISTER    = const(0x02)
    NEOPIXELS_N             = const(4)
    ADC0_REGISTER           = const(0x1E)
    ADC1_REGISTER           = const(0x20)
    ADC2_REGISTER           = const(0x22)
    ADC3_REGISTER           = const(0x24)
    ADC4_REGISTER           = const(0x26)

    is_initialized:bool = False

    def __init__(self):

        self.left_led_state:int = 0
        self.right_led_state:int = 0
        self.neopixel:neopixel.NeoPixel = None

        if not Maqueen.is_initialized:
            microbit.display.scroll("JB")
            microbit.i2c.init()

            self.neopixel = neopixel.NeoPixel(microbit.pin15, Maqueen.NEOPIXELS_N, bpp=3)
            self.neopixel.clear()

        Maqueen.is_initialized = True

        microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.LEFT_LED_REGISTER, 0, 0]))
        self.stopMotor()
        pass

    def setMotor(self, speed:int, dir:int, motor:int|None=None) -> int:
        if not Maqueen.is_initialized:
            print("Not initialized!")
            return -1
        # speed is a percentage (0 - 100)
        # when dir == 1, cw; ccw when dir is 0
        speed_scaled = int(microbit.scale(speed, from_=(0, 100), to=(0, 255)))

        if motor == LEFT_MOTOR:
            microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.LEFT_MOTOR_REGISTER, dir, speed_scaled]))
        elif motor == RIGHT_MOTOR:
            microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.RIGHT_MOTOR_REGISTER, dir, speed_scaled]))
        else:
            microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.LEFT_MOTOR_REGISTER, dir, speed_scaled, dir, speed_scaled]))

        return 0

    def stopMotor(self, motor:int|None=None) -> int:
        return self.setMotor(0, 0, motor)

    def toggleLED(self, led:int|None=None) -> int:
        if not Maqueen.is_initialized:
            print("Not initialized!")
            return -1

        if led == LEFT_LED:
            self.left_led_state = not self.left_led_state
            microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.LEFT_LED_REGISTER, self.left_led_state]))
        elif led == RIGHT_LED:
            self.right_led_state = not self.right_led_state
            microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.RIGHT_LED_REGISTER, self.right_led_state]))
        else:
            self.left_led_state = not self.left_led_state
            self.right_led_state = not self.right_led_state
            microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.LEFT_LED_REGISTER, self.left_led_state, self.right_led_state]))

        return 0

    def setNeoPixel(self, rgb:tuple[int]|list[int], i:int|None=None) -> int:
        r, g, b = rgb
        if not self.neopixel:
            print("NeoPixels not initialized!")
            return -1
        
        if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
            print("Invalid rgb values!")
            return -1

        if i and (i < 0 or i > Maqueen.NEOPIXELS_N):
            print("Invalid NeoPixel index!")
            return -1

        if i:
            self.neopixel[i] = (r, g, b)
        else:
            for j in range(Maqueen.NEOPIXELS_N):
                self.neopixel[j] = (r, g, b)

        self.neopixel.show()
        return 0

    def clearNeoPixel(self) -> int:
        if not self.neopixel:
            print("NeoPixels not initialized!")
            return -1

        self.neopixel.clear()
        return 0

    def readUltrasonicSensor(self) -> int|float:
        if not Maqueen.is_initialized:
            print("Not initialized!")
            return -1
        microbit.pin13.write_digital(0)
        utime.sleep_us(5)

        microbit.pin13.write_digital(1)
        utime.sleep_us(10)
        microbit.pin13.write_digital(0)

        t_us = machine.time_pulse_us(microbit.pin14, 1)
        d_cm = (0.034*t_us)/2 # sound in air: 340m/s
        return d_cm

    def readLineSensor(self):
        pass


    def _findI2CDevices(self):
        print(microbit.i2c.scan())

    def _testNeoPixels(self):
        for i in range(Maqueen.NEOPIXELS_N):
            for r in range(255):
                for g in range(255):
                    for b in range(255):
                        self.neopixel[i] = (r, g, b)
                        self.neopixel.show()
                        microbit.sleep(500)
            self.neopixel[i] = (0, 0, 0)
            self.neopixel.show()
        self.neopixel.clear()
