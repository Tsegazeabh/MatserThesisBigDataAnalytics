import schemdraw as schem
import schemdraw.elements as elm
import schemdraw.segments as segment
import re
import numpy as np
import base64
from models.vue_front_end import PlotResponse, Picture


#WARBURG = {
#    'name': 'WARBURG',
#    'paths': [0.8*wpath, [[0, 0], [0.5, 0]]],
#}

# define Warburg circuit element
class WARBURG(elm.Element2Term):
    def __init__(self, *d, **kwargs):
        super().__init__(*d, **kwargs)
        self.segments.append(segment.Segment([(0, 0),(0.5, 0)]))
        self.segments.append(segment.Segment([(-0.25, 0.5), (0, -0.5), (0.25, 0.25), (0.5, -0.5), (0.75, 0.5)]))

# map circuit elements to drawing fucntions
emap = {'R': elm.Resistor, 'C': elm.Capacitor, 'L': elm.Inductor, 'W': WARBURG, 'Q': elm.Capacitor,'P': elm.Capacitor, 'O': WARBURG, 'T': WARBURG,'G': elm.Inductor,}

RE_PARALLEL = re.compile(r'(\[([RCLWQGTOP0-9,-]+)\])')
RE_ELEMENT = re.compile(r'(([RCLWQGTO])|(P))([0-9]+)')
PARALLEL_RESET = True
parallel_components =[]

def draw_parallel(draw, parallel_str, parallel_list, component):
    elms_p = parallel_str.split(",")
    h = 1.5      
    # Iterate through parallel elements
    count_series_element = 0
    parallel_lines_count = 0
    for i, parallel_elem in enumerate(elms_p):
        count_series_element = 0
        # The following loop it to search series elements below the specific parallel element in the list
        # to determine the length of the component to be drawn.
        # The number of series elements in the parallel section determines the length
        for index, item in enumerate(parallel_list):
            if (parallel_elem in item) and (not parallel_elem.startswith('P')):
                element_location = index
                print('Parallel Element Location:',parallel_list[element_location])
                for element in parallel_list[element_location].split(','):
                    # Check if the current element starts with 'P'
                    print('Element: ', element)
                    if element.startswith('P'):
                        # Check if the current element comes before the specific string
                        if element != parallel_elem:
                            parallel_lines_count += 1 # count the parallel sections before the element
                    if element == parallel_elem:
                        break
                print('Parallel Element:', parallel_elem)
                print('Item:', item)
                print("Parallel List Sub:",parallel_list[:element_location])
                count_series_element = sum(item.count('-') for item in parallel_list[:element_location])
                break
        print('Count of Series Elem: ', count_series_element)
        draw.add(elm.DOT)
        # if len(elms_p) > 1:
        draw.push()
        # Draw series components for each parallel element
        draw, _ = draw_series(draw, parallel_elem, parallel_list, True, count_series_element)
        # if i < len(elms_p) - 1:  
        draw.add(elm.LINE, d='down', l=h)
        draw.add(elm.DOT)
        # Continue plotting from the end point if the last parallel component is drawn and the initial parallel component is done
        # print('Condition: ', parallel_components, (component.startswith('P')) and (component not in (','.join(parallel_list))))
        # Keep track of the parallel sections that start with 'P' and may have other components inside
        # This is used to track the push and pop points in the drawing
        if component not in parallel_components:
            parallel_components.append(component)
        draw.pop()                
        print('Parallel Lines count:', parallel_lines_count)
        if i < len(elms_p) - 1:            
            draw.add(elm.LINE, d='down', l= h + parallel_lines_count*h)
        # PARALLEL_RESET = True
    return draw

def draw_series(draw, series_str, parallel_list, from_parallel=False, count_series_element=0):
    #Split the series elements
    length = 2 if not from_parallel else (2 + 2 * count_series_element)
    clist = series_str.split('-')
    print("CList: ", clist)
    for component in clist:
        match_cmp = RE_ELEMENT.search(component)
        print("Match Comp:", match_cmp)
        if match_cmp is None:
            return None
        if match_cmp[1] != 'P':
            draw.add(emap[match_cmp[1]], label=f'${component}$', d='right', l = length)
        else:
            draw = draw_parallel(draw, parallel_list[int(match_cmp[4])], parallel_list, component)
            if draw is None:
                return None
    return draw, len(clist)

#circuit = "R0-p(R1,C1)-p(R2,W1)"
def draw_circuit(circuit):
    """ Constructs an SchemDraw drawing of a circuit that is specified as
    a string."""
    #Remove save all parallels
    p_list = []
    circuit_formatted = circuit
    print("Circuit:", circuit)
    p_list_aux = RE_PARALLEL.findall(circuit_formatted)
    print("P List Aux:", p_list_aux)
    while len(p_list_aux) > 0:
        for p_elem in p_list_aux:
            circuit_formatted = circuit_formatted.replace(p_elem[0],f"P{len(p_list)}")
            p_list.append(p_elem[1])
        p_list_aux = RE_PARALLEL.findall(circuit_formatted)
    # initialize drawing
    print("Circuit Formated Modified:", circuit_formatted)
    print("P List:", p_list)
    dwg = schem.Drawing()
    #Initialize the series call
    dwg,_ = draw_series(dwg, circuit_formatted, p_list, False, 0)
    if dwg is None:
        return None
    dwg.draw(show=False)
    image_bytes = dwg.get_imagedata(schem.ImageFormat.SVG)
    image_base64 = b'data:image/svg+xml;base64,'+base64.b64encode(image_bytes)
    return image_base64

def draw_circuit_raw_req(circuit):
    circuit_base64 = draw_circuit(circuit)
    return {"draw": circuit_base64}

def draw_circuit_req(circuit):
    warnings = []
    try:
        circuit_base64 = draw_circuit(circuit)
        return PlotResponse.get_data_response(
            "DrawCircuit",
            Picture("Circuit Draw", circuit_base64).get_vue(),
            warnings
        )
    except Exception as e:
        lastError = f"Error creating the draw: {e}"
        PlotResponse.get_error_response("DrawCircuit", warnings, lastError)
