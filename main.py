import keyboard
from elements.elements import Elements

def main():
    elements = Elements(partial_name='Paint')
    while elements.state != 10:
        if keyboard.read_key() == "s":
            print(f"State #{elements.state} of window {elements.partial_name} capturing...")
            elements.active_window_handle()
            elements.parse_elements()
            elements.save_data()
            print(f"elements parsed, data saved") 
        elements.state += 1


if __name__ == "__main__":
    main()
