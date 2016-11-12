import cv2
import numpy as np
import math
import detectorGUI
import detectorClass
import errorthread
from PyQt4 import QtGui, QtCore
import sys
import json

# Importa la configuracion
with open('config.json') as archivo_configuracion:
    configuracion = json.load(archivo_configuracion)


def main():
	""" Funcion principal
	"""
	app = QtGui.QApplication(sys.argv)
	ventanaPrincipal = detectorGUI.VentanaPrincipal()

	# Inicia la GUI
	#sys.exit(app.exec_())
	app.exec_()
	
if __name__ == '__main__':
	main()
