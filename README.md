# Ball and Beam

**The project has been developed for the DSP and Industrial Electronics courses, at the National Technological University of Argentina, Avellaneda Regional Faculty (UTN FRA).**

The aim of this project is to control a “Ball and Beam”-type structure, based on an object detection system, using the [OpenCV](http://www.opencv.org) library.


## Requirements
The code has been written and tested in Python 3.5.1. Dependencies are listed in the `requirements.txt` file. You will need at least:
  * Numpy @ 1.11.1
  * PyQt4 @ 4.11.4
  * OpenCV2 @ 1.0
  * PySerial @ 3.1.1 (only for communication with the controller board)


## Usage
After installing all the dependencies just run:
```
python main.py -d -t
```
  * **-d**: Debug Mode, does not try to open the serial port.
  * **-t**: Test Mode, uses de test.avi file as the input instead of the camera.

### Calibration
1. **Define detection area**: In the 'Configuracion' menu, check the 'Definir zona de deteccion' option and drag your mouse over the video to define a smaller zone where the program will try to find the ball. The smaller the zone, the faster the system will be able to react.

2. **Calibrate camera**: In the same menu, you will have the camera adjustments, such as brightness, contrast and saturation.
3. **Calibrate colors**: Once the camera is calibrated, you will have to define the ranges for the color detecion. In the 'Calibrar Objetivo' menu, you will define the ranges for the target (the ball), and in the 'Calibrar referencia 1' you will be able to define the ranges for the reference.
4. **PID control calibration**: The system was calibrated for a specific structure, so the PID control system constants will need to be adjusted to yours. Those constants are defined in the `config.json` file, they are named Kd, Kp, and Ki. If you change them, you will need to restart the system. The camera and color ranges configurations are saved after every use.


License: [GNU GPLv3](https://www.gnu.org/licenses/gpl.html)

---
## TODO
Upload the controller board schematics and an image of the structure, together with some specifications.

