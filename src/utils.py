import json
import math
import os
import re

from PIL import Image

from src.LinkableValue import linkableValueDumpsToJSON
from src.constants import THAUM_CONTROLS_CONFIG_PATH


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def saveThaumControlsConfig(pointWritingMaterials, pointPapers, rectAspectsListingLT, rectAspectsListingRB,
                            pointAspectsScrollLeft, pointAspectsScrollRight,
                            pointAspectsMixLeft, pointAspectsMixCreate, pointAspectsMixRight, rectInventoryLT,
                            rectInventoryRB, rectHexagonsCC, hexagonSlotSizeY):
    print(re.split('[\/]', THAUM_CONTROLS_CONFIG_PATH))
    configPath = os.path.join(*(re.split('[\/]', THAUM_CONTROLS_CONFIG_PATH)[:-1]))
    if not os.path.exists(configPath):
        os.makedirs(configPath)

    with open(THAUM_CONTROLS_CONFIG_PATH, 'w') as file:
        json.dump({
            "pointWritingMaterials": {"x": pointWritingMaterials.x, "y": pointWritingMaterials.y},
            "pointPapers": {"x": pointPapers.x, "y": pointPapers.y},
            "rectAspectsListingLT": {"x": rectAspectsListingLT.x, "y": rectAspectsListingLT.y},
            "rectAspectsListingRB": {"x": rectAspectsListingRB.x, "y": rectAspectsListingRB.y},
            "pointAspectsScrollLeft": {"x": pointAspectsScrollLeft.x, "y": pointAspectsScrollLeft.y},
            "pointAspectsScrollRight": {"x": pointAspectsScrollRight.x, "y": pointAspectsScrollRight.y},
            "pointAspectsMixLeft": {"x": pointAspectsMixLeft.x, "y": pointAspectsMixLeft.y},
            "pointAspectsMixCreate": {"x": pointAspectsMixCreate.x, "y": pointAspectsMixCreate.y},
            "pointAspectsMixRight": {"x": pointAspectsMixRight.x, "y": pointAspectsMixRight.y},
            "rectInventoryLT": {"x": rectInventoryLT.x, "y": rectInventoryLT.y},
            "rectInventoryRB": {"x": rectInventoryRB.x, "y": rectInventoryRB.y},
            "rectHexagonsCC": {"x": rectHexagonsCC.x, "y": rectHexagonsCC.y},
            "hexagonSlotSizeY": hexagonSlotSizeY,
        }, file, indent=4, ensure_ascii=False, default=linkableValueDumpsToJSON)


def readJSONConfig(fullpath: str):
    if not os.path.isfile(fullpath):
        return None
    try:
        with open(fullpath, 'r') as file:
            config = json.load(file)
    except Exception as e:
        print(Warning(f"Something went wrong while opening config {fullpath}:", e))
        return None
    return config


def getImagesDiffPercent(image1: Image.Image, image2: Image.Image, *masks: tuple[Image.Image]) -> float:
    if image1.size != image2.size:
        raise ValueError("Images sizes must be the same")
    if image1.mode != image2.mode:
        raise ValueError("Image modes must be the same")

    pixels1 = list(image1.getdata())
    pixels2 = list(image2.getdata())
    pixelsCount = len(pixels1)

    masks = list(masks)
    for i in range(len(masks)):
        mask = masks[i]
        if mask.size != image1.size:
            raise ValueError("Images and all masks sizes must be the same")
        mask = mask.convert("L")  # convert to grayScale
        masks[i] = list(mask.getdata())
    totalBoolMask = [True] * pixelsCount
    for mask in masks:
        for i in range(pixelsCount):
            totalBoolMask[i] = totalBoolMask[i] and (mask[i] != 0)

    totalDiff = 0
    activePixelsCount = 0
    pixels = len(pixels1)
    directions = len(pixels1[0])
    for pixelIdx in range(pixels):
        pixel1 = pixels1[pixelIdx]
        pixel2 = pixels2[pixelIdx]
        if not totalBoolMask[pixelIdx]:
            continue
        activePixelsCount += 1
        for directionIdx in range(directions):
            totalDiff += abs(pixel1[directionIdx] - pixel2[directionIdx])
    percentDiff = totalDiff / (activePixelsCount * directions * 255)
    return percentDiff
