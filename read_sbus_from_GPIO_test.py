import read_sbus_from_GPIO
import time
from statistics import mean
from periphery import GPIO


def connection_test(m):
    print('Waiting for connection...')
    times = []
    try:
        while( not m.is_connected()):
            time.sleep(.2)
    except KeyboardInterrupt:
        m.end_listen()
        raise

    print('Connection Established.')


def ping_test(m):
    print('Waiting for connection...')
    times = []
    try:
        while( not m.is_connected()):
            time.sleep(.2)
    except KeyboardInterrupt:
        m.end_listen()
        raise

    print('Timing 3 seconds of packets....')
    time_start = time.time()
    while time.time() - time_start <=3:
        time.sleep(.01) # retrieve every 10ms
        times.append(m.get_latest_packet_age())
    
    print(f'Average Delay (ms): {mean(times)}, Max Delay (ms): {max(times)}')

def map_value(min_input,max_input,min_output,max_output,invert_mapping,input):
    #for a given input in a range, output to a normalized value in the output range

    input_delta = max_input-min_input
    output_delta = max_output-min_output
    input_percent = (input-min_input)/input_delta
    new_val = min_output+output_delta*input_percent
    if invert_mapping:
        new_val = max_output+min_output-new_val
    return new_val
     

def device_test(m):
    #demonstrates functionality of library on a servo and two leds connected to PI
    #on GPIOs specified below.

    #servo used here is a Tower Pro Digital MG995R - different servos will require 
    #different pwm settings

    from periphery import PWM
    
    #frequency and period
    f = 50
    T = 1/f
    
    TRANSMITTER_MIN_VAL = 352
    TRANSMITTER_MAX_VAL = 2047+(2047-352)
    SERVO_MIN_VAL = 500
    SERVO_MAX_VAL = 2500

    YAW_CHANNEL = 1
    PITCH_CHANNEL = 2
  
    yaw = PWM(0, 0)
    pitch = PWM(0, 1)
   
    yaw.frequency = f
    pitch.frequency = f
    
    print('ctrl-c to leave device_test....')
    
    while(True):
        if m.is_connected():
            
            yaw.enable()
            pitch.enable()
            
            latest_channel_data = m.translate_latest_packet()

            cur_servo_val = latest_channel_data[YAW_CHANNEL-1]
            pwm = map_value(TRANSMITTER_MIN_VAL,TRANSMITTER_MAX_VAL,SERVO_MIN_VAL,SERVO_MAX_VAL, True,cur_servo_val)
            yaw.duty_cycle = (pwm*(10**(-6)))/T

            cur_servo_val = latest_channel_data[PITCH_CHANNEL-1]
            pwm = map_value(TRANSMITTER_MIN_VAL,TRANSMITTER_MAX_VAL,SERVO_MIN_VAL,SERVO_MAX_VAL, True,cur_servo_val)
            pitch.duty_cycle = (pwm*10(**(-6)))/T

            
            
#SBUS connected to pin 13
DATA_PIN = 22
path = "/dev/gpiochip0"
timeout = 0.01 #non-blocking poll

if __name__=="__main__":

    m = read_sbus_from_GPIO.MonThread()
    m.start()
    
    print('Begin Tests...')
    #reader.display_latest_packet()
    
    connection_test(m)
    print('*******')
    
    m.display_latest_packet()
    ping_test(m)
    print('*******')

    m.display_latest_packet()
    print('*******')

    device_test(m)
    
    print('End Tests...')
    m.end_listen()
