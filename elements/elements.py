import json
import os
from datetime import datetime
from PIL import ImageGrab, Image

from pywinauto.application import Application
from pywinauto import Desktop
from .support import get_element_colors


class Elements(object):
    
    
    def __init__(self, partial_name) -> None:
        self.elements_description_current = {}
        self.elements_description_full = {}
        self.state = 1
        self.partial_name = partial_name
        self.window = None
        self.current_session_folder_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S%f')[:-3]}_{partial_name.lower()}"
        self.current_session_folder_path = os.path.join(os.getcwd(), "output", self.current_session_folder_name)
        os.mkdir(self.current_session_folder_path)
    
    
    def active_window_handle(self):

        # app = Application(backend="uia").start(r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE")
        # time.sleep(3)
        # window = app.window(title_re='* - Excel')

        if self.window is None:

            print(f"The window object not defined yet")
        
            windows = Desktop(backend="uia").windows()  # -- to get all the windows
        
            if self.partial_name:
                for window in windows:
                    if self.partial_name in window.element_info.name:
                        print(f"The window '{window.element_info.name}' matched to parial window name and will be parsed")
                        self.window = window
                        break
            
            if not self.partial_name or self.window is None:
                for window in windows:
                    if window.has_keyboard_focus():
                        print(f"Partial window name is not defined or window is not detected. The window '{window.element_info.name}' is foreground and will be parsed")
                        self.window = window
                        break
            
            self.window.set_focus()
        
        print(f"The window '{self.window.element_info.name}', state #{self.state}")

        main_screenshot = os.path.join(
            self.current_session_folder_path, 
            f"_{self.window.element_info.name.replace(' ', '_')}_window_state_{self.state}.png".lower()
            )

        img = ImageGrab.grab(None)
        img.save(main_screenshot)
        img.close()

        self.main_screenshot = main_screenshot


    def parse_elements(self):

        elements = self.window.descendants()
        self.elements_description_current = {}
        nesting_levels = {}

        for index, element in enumerate(elements, start=1):
            
            info = element.element_info
            parent = info.parent
            element_id = abs(hash(f"{info.name}{info.rectangle}{info.control_type}{info.class_name}"))
            if parent is not None:
                parent_id = abs(hash(f"{parent.name}{parent.rectangle}{parent.control_type}{parent.class_name}"))
            else:
                parent_id = None

            if not element_id in self.elements_description_full:

                # getting element image
                main_img = Image.open(self.main_screenshot)
                element_img = main_img.crop(
                    (
                    info.rectangle.left,
                    info.rectangle.top,
                    info.rectangle.right,
                    info.rectangle.bottom
                    )
                    )

                if parent_id not in nesting_levels:
                    nesting_levels[element_id] = 1
                else:
                    nesting_levels[element_id] = nesting_levels[parent_id] + 1
                
                print(f"new element #{index} '{info.name}' is detected and parsed")
                self.elements_description_current[element_id] = {
                        "element_id": element_id,
                        "name": info.name,
                        "class_name": info.class_name,
                        "class_name_frendly": element.friendlyclassname,
                        "control_type": info.control_type,
                        "automation_id": info.automation_id,
                        "rich_text": info.rich_text,
                        "rectangle": {
                            "left": info.rectangle.left,
                            "top": info.rectangle.top,
                            "bottom": info.rectangle.right,
                            "right": info.rectangle.bottom
                        },
                        "size": {
                            "height": info.rectangle.height(), 
                            "width": info.rectangle.width()
                            },
                        "colors": get_element_colors(element_img), 
                        "enabled": info.enabled,
                        "visible": info.visible,
                        "parent": parent_id,
                        "level": nesting_levels[element_id],
                        "main_screenshot": os.path.basename(self.main_screenshot),
                        "window_state": self.state
                    }
                
                area_filename = f"{element_id}.png"
                try:
                    element_img.save(os.path.join(self.current_session_folder_path, area_filename))
                except Exception as ex:
                    print(f" --- an error ocured: {ex.args[0]}, failed to make a screenshot")
                finally:
                    element_img.close()

            # else:

            #     print(f"element #{index} '{info.name}' was not changed")  
            
        if self.elements_description_current:
            self.elements_description_full.update(self.elements_description_current)
            print(f'{len(self.elements_description_current)} element(s) was updated or added')
        else:
            print('Seems nothing changed in this state...')

    
    def save_data(self):

        with open(os.path.join(self.current_session_folder_path, f'output_state.json'), 'w', encoding='utf-8') as file:
            json.dump(list(self.elements_description_current.values()), file, ensure_ascii=False, indent=4)
        
