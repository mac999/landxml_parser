import json
import ezdxf
from ezdxf.enums import TextEntityAlignment


def convert_json_to_dxf(json_file, dxf_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    for item in data:
        points = [
            (item['p1_x'], item['p1_y']),
            (item['p2_x'], item['p2_y']),
            (item['p3_x'], item['p3_y']),
            (item['p4_x'], item['p4_y'])
        ]
        
        msp.add_lwpolyline(points, close=True)

        sta = item.get('sta', 0.0)
        center_x = points[0][0] + (points[2][0] - points[0][0]) / 2.0
        center_y = points[0][1] + (points[2][1] - points[0][1]) / 2.0
        msp.add_text(
            f'STA: {sta:.2f}',
            height=0.04,
            dxfattribs={"style": "LiberationSerif"}
        ).set_placement((center_x, center_y), align=TextEntityAlignment.LEFT)
    
    doc.saveas(dxf_file)
    print(f"Save DXF file: {dxf_file}")
    print(f"Total {len(data)} blocks were converted.")

if __name__ == "__main__":
    input_json = "block_model_output_dxf_sta.json"
    output_dxf = "block_model_output_sta.dxf"
    
    convert_json_to_dxf(input_json, output_dxf)

