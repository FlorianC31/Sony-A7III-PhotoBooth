# PhotoBooth
Wedding Photobooth control software

This aim project of this projects is to make a wedding photobooth with a Sony A7III, a 14" tactile notebook and a photo printer.
Since Sony doesn't provide any SDK for the A7III, the conventionnal solution (DSLRBooth) is not working.

Thus this Photobooth needs a control software bypassing the lack of SDK and it's the purpose of this Python program.

The camera is triggered via the USB port and the Sony application "Remote" contained in Imaging Edge Desktop.

The real time video hdmi flux is transfered to the PC via a HDMI2USB converter:
LARNMERN Carte de Capture Vidéo HDMI
https://www.amazon.fr/gp/product/B08CGVSRQV/ref=ppx_yo_dt_b_asin_title_o05_s00?ie=UTF8&psc=1

The Light and Fans are controlled by an USB relay card:
SainSmart USB 4 canal Relais automatisation
https://www.amazon.fr/gp/product/B009A524Z0/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1
