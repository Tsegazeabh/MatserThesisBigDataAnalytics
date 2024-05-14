from typing import List
from pydantic import BaseModel, Field

def create_model_class(class_name: str, fields: List[str]):
    # Define a dictionary to hold field names and their types
    class_attrs = {}    
    # Populate the dictionary with user-defined field names
    for field_name in fields:
        class_attrs[field_name] = Field(...)    
    # Create the class dynamically using the type function
    model_class = type(class_name, (BaseModel,), class_attrs)    
    return model_class
# Example usage
class_name = "UserData"
fields = ["name", "age", "email"]
UserModel = create_model_class(class_name, fields)