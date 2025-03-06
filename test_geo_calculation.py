import os, sys, re, json, random, traceback, math, pandas as pd, numpy as np, numpy as np
import civil_geo_engine as cge
from civil_geo_engine import civil_model

def main():
    tm_x = 33915.71770
    tm_y = -58031.54067

    print("Input coordinates (TM):", tm_x, tm_y)
    grs80_x, grs80_y = cge.convert_coordinates(tm_x, tm_y) # from_crs='epsg:2097', to_crs='epsg:4326'): # Central origin TM coordinate system. https://www.osgeo.kr/17
    print("Transformed coordinates (GRS80):", grs80_x, grs80_y)

if __name__ == "__main__":
    main()
