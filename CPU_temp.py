import wmi
from time import sleep
from relais import Relais
from threading import Thread

MAX_TEMP = 65
MIN_TEMP = 60


def get_cpu_temp():

    w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
    temperature_infos = w.Sensor()
    cpu_temp = 0
    for sensor in temperature_infos:
        # print(sensor.SensorType, sensor.Value)
        if sensor.SensorType == u'Temperature':
            cpu_temp = max(cpu_temp, sensor.Value)
    # print(cpu_temp)
    return cpu_temp


def upper_fan_controller(relais):

    while relais.running:
        cpu_temp = get_cpu_temp()

        if cpu_temp > MAX_TEMP:
            # print("CPU Temp = " + str(cpu_temp) + ">" + str(MAX_TEMP) + " - Fan ON")
            relais.on('fanCam')

        if cpu_temp < MIN_TEMP:
            # print("CPU Temp = " + str(cpu_temp) + "<" + str(MIN_TEMP) + " - Fan OFF")
            relais.off('fanCam')

        sleep(5)


if __name__ == '__main__':
    new_relais = Relais(('light', 'fanPrinter', 'fanCam', ''))
    # upper_fan_controller(new_relais)

    upper_fan_thread = Thread(target=upper_fan_controller, args=[new_relais])
    upper_fan_thread.start()

    # get_cpu_temp()
