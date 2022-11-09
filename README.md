# event-based-astrometry
This repository was created as part of the Honours project titled: Application of Event Cameras for Improved Star Tracking. The aim of the repository is to provide functions which can convert raw event camera data into tradiontial images of the stars. 

## Dependacnies
Pyhton version: 3.8

- [metavision_core](https://docs.prophesee.ai/stable/installation/index.html)
- cv2 (OpenCV)
- matplotlib
- glob
- numpy
- astropy
- photutils

## Intsructions

To generate normalized images run the command.
```
python3.8 main.py <event_data>.raw
```

To generate normalized images and filter hot pixels using a noise file input.
```
python3.8 main.py <event_data>.raw  <noise_data>.raw
```

To generate an amplified image.
```
python3.8 centroid.py <normalized_path>.jpg
```

## Dataset
The event dataset created from this project is avaible at the following location: https://universityofadelaide.box.com/s/hpldjumqbhc3ycqw413ed9cj0kajvlpd
