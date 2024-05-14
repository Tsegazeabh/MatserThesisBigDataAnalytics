from typing import List, Any, Dict, Type
from pydantic import BaseModel, Field

class PlotResponse(BaseModel):
    name: str = Field(..., description="Name identifying the type of response")
    success: bool = Field(..., description="States if an operation was success")
    dataGraph: Dict[str,Any] = Field(..., description="Returned data. It can contains extracted data or retrieve analysis report")
    lastError:str = Field(..., description="If success=False, then this property contains the explanation of the failure")
    warnings: List[str] = Field(..., description="List of warnings during execution")
    comparisonInfo: Dict[str,Any] = Field({}, description="Information used during the comparison of two analysis")

    @staticmethod
    def get_error_response(name:str, warnings:list, last_error:str) -> "PlotResponse":
        return PlotResponse(name=name, warnings=warnings, lastError=last_error, dataGraph={}, success=False)

    @staticmethod
    def get_data_response(name:str, data:Dict[str,Any], warnings:list) -> "PlotResponse":
        return PlotResponse(name=name, warnings=warnings, lastError="", dataGraph=data, success=True)


class Table:
    def __init__(self, name:str, category:str, data_table:List[Dict[str,Any]], headers:List[str]) -> None:
        self.name = name
        self.category = category
        self.data_table = data_table
        self.headers = headers

    def get_vue(self) -> Dict[str, Any]:
        return {
            "dataTable": self.data_table,
            "title": self.name,
            "type": "table",
            "headerOrder": self.headers
        }

class Picture:
    def __init__(self, name:str, data_base64:str, category:str="") -> None:
        self.name = name
        self.category = category
        self.data_base64 = data_base64

    def get_vue(self) -> Dict[str, Any]:
        return {
            "data": self.data_base64,
            "name": self.name,
            "type": "picture"
        }


def formatCards(name:str, tables:List[Type[Table]], warnings:List[str], pictures:List[Type[Picture]] = []):
    try:
        data = {}

        # Format the tables and add to the dictionary
        for table in tables:
            tableElement = table.get_vue()
            if table.name in data.get(table.category, {}):
                warnings.append(f"Table {table.name} overwritten, please contact your system administrator")
            data[table.category][table.name] = tableElement

        # Format the Pictures
        for picture in pictures:
            pictureElement = picture.get_vue()
            if picture.name in data.get(picture.category, {}):
                warnings.append(f"Graph {picture.name} overwritten, please contact your system administrator")
            data[picture.category][picture.name] = pictureElement

        return PlotResponse.get_data_response(name, data, warnings)
    except Exception as e:
        lastError = f"Error formatting the analysis for Vuejs. Message: {str(e)}"
        return PlotResponse.get_error_response(name, warnings, lastError)
