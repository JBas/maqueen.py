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

LINE_SENSOR_L2:int          = const(0)
LINE_SENSOR_L1:int          = const(1)
LINE_SENSOR_M:int           = const(2)
LINE_SENSOR_R1:int          = const(3)
LINE_SENSOR_R2:int          = const(4)

class Maqueen():
    # I just took this from the maqueen github repo
    I2C_ADDR                = const(0x10)
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
    LINE_STATE_REGISTER     = const(0x1D)

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

        self.setLED(0)
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

    def setLED(self, state:int, led:int|None=None) -> int:
        if not Maqueen.is_initialized:
            print("Not initialized!")
            return -1

        if led == LEFT_LED:
            self.left_led_state = state
            microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.LEFT_LED_REGISTER, self.left_led_state]))
        elif led == RIGHT_LED:
            self.right_led_state = state
            microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.RIGHT_LED_REGISTER, self.right_led_state]))
        else:
            self.left_led_state = state
            self.right_led_state = state
            microbit.i2c.write(Maqueen.I2C_ADDR, bytes([Maqueen.LEFT_LED_REGISTER, self.left_led_state, self.right_led_state]))

        return 0

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
        if not Maqueen.is_initialized:
            print("Not initialized!")
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
        if not Maqueen.is_initialized:
            print("Not initialized!")
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

    def readLineSensorState(self, sensor:int|None=None) -> list[int]|int:
        microbit.i2c.write(I2C_ADDR, bytes([LINE_STATE_REGISTER]))
        raw_data_buffer = microbit.i2c.read(I2C_ADDR, 2)

        # states_u = [
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x10),
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x08),
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x04),
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x02),
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x01)
        # ]

        # microbit.uart.write("Raw: " + str(states_u) + "   ")

        states = [
            int(int.from_bytes(raw_data_buffer, "little") & 0x10 == 0x10),
            int(int.from_bytes(raw_data_buffer, "little") & 0x08 == 0x08),
            int(int.from_bytes(raw_data_buffer, "little") & 0x04 == 0x04),
            int(int.from_bytes(raw_data_buffer, "little") & 0x02 == 0x02),
            int(int.from_bytes(raw_data_buffer, "little") & 0x01 == 0x01)
        ]

        # microbit.uart.write("Processed: " + str(states_c) + "   ")

        # states = [
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x10 >> 4),
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x08 >> 3),
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x04 >> 2),
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x02 >> 1),
        #     bin(int.from_bytes(raw_data_buffer, "little") & 0x01 >> 0)
        # ]

        if sensor:
            try:
                return states[sensor]
            except:
                print("Not a valid sensor!")
                return -1
        else:
            return states

    def readLineSensorData(self, sensor:int) -> int:
        if sensor == LINE_SENSOR_L2:
            microbit.i2c.write(I2C_ADDR, bytes([ADC0_REGISTER]))
            raw_data_buffer = microbit.i2c.read(I2C_ADDR, 2)
            adc_data = raw_data_buffer[1] << 8 | raw_data_buffer[0]
        elif sensor == LINE_SENSOR_L1:
            microbit.i2c.write(I2C_ADDR, bytes([ADC1_REGISTER]))
            raw_data_buffer = microbit.i2c.read(I2C_ADDR, 2)
            adc_data = raw_data_buffer[1] << 8 | raw_data_buffer[0]
        elif sensor == LINE_SENSOR_M:
            microbit.i2c.write(I2C_ADDR, bytes([ADC2_REGISTER]))
            raw_data_buffer = microbit.i2c.read(I2C_ADDR, 2)
            adc_data = raw_data_buffer[1] << 8 | raw_data_buffer[0]
        elif sensor == LINE_SENSOR_R1:
            microbit.i2c.write(I2C_ADDR, bytes([ADC3_REGISTER]))
            raw_data_buffer = microbit.i2c.read(I2C_ADDR, 2)
            adc_data = raw_data_buffer[1] << 8 | raw_data_buffer[0]
        elif sensor == LINE_SENSOR_R2:
            microbit.i2c.write(I2C_ADDR, bytes([ADC4_REGISTER]))
            raw_data_buffer = microbit.i2c.read(I2C_ADDR, 2)
            adc_data = raw_data_buffer[1] << 8 | raw_data_buffer[0]
        else:
            print("Not a valid sensor!")
            return -1
        
        return adc_data


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


if __name__=="__main__":
    robot = Maqueen()
    microbit.uart.init(115200)

    while True:
        data = robot.readLineSensorState(LINE_SENSOR_M)
        microbit.uart.write("Line sensor states: " + str(data) + "\r\n")
        microbit.sleep(1000)