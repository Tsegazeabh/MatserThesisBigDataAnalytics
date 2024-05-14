from enum import Enum

class SoilTempDataSources(str, Enum):
    file = "file"
    http = "http"