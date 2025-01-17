#main.py

import os
import cv2
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from dotenv import load_dotenv
from utils.cv import ImageManager

INITIAL_INDEX = 0  # Set the initial index for file navigation

class NumberInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        if all(char.isdigit() or char == "." for char in substring):
            super().insert_text(substring, from_undo=from_undo)

class CvApp(App):
    def build(self):
        self.set_window_size_from_env()
        return MyBoxLayout()

    def set_window_size_from_env(self):
        try:
            Window.size = tuple(map(int, os.getenv('WINDOW_SIZE').strip('[]').split(',')))
        except Exception as e:
            print(f"Error setting the window size: {e}")

class MyBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_parent=self.on_parent)

    def on_parent(self, instance, value):
        if value:
            self.bind_left_box_size()

    def bind_left_box_size(self):
        left_box = self.ids.left_box
        if left_box:
            left_box.bind(on_size=self.update_left_box_size_hint_x)

    def update_left_box_size_hint_x(self, instance, value):
        left_box = self.ids.left_box
        if left_box:
            left_box.size_hint_x = instance.width / self.width

class TopNavBar(BoxLayout):
    pass

class LeftBox(BoxLayout):
    pass

class CenterBox(BoxLayout):
    pass

class RightBox(BoxLayout):
    def update_label_text(self, button_text):
        self.ids.right_label.text = f"{button_text}"

class MyAppButton(Button):
    supported_files = []
    current_index = INITIAL_INDEX
    image_manager = ImageManager()  # Create an instance of ImageManager

    def __init__(self, **kwargs):
        super(MyAppButton, self).__init__(**kwargs)
        self.bind(on_release=self.on_button_release)
        self.filters = os.getenv('IMAGE_EXT', '').split()

    def on_button_release(self, instance):
        actions = {
            'Open': self.show_file_chooser,
            'Open Dir': self.show_directory_chooser,
            'Next': self.next_action,
            'Prev': self.prev_action,
            'Save': self.save_action,
            'Info': self.Info_action,
            'Crop': self.crop_action,
            'Resize': self.resize_action,
            'Brt': self.brightness_action,
            'Sat': self.saturation_action,
            'Rot 90°': self.rotate_90_degrees_action,
            'FV/FH': self.flip_vertically_or_horizontally_action,
        }
        action = actions.get(self.text, self.update_right_label)
        action()

    def show_file_chooser(self):
        self.file_chooser_popup(is_dir=False)

    def show_directory_chooser(self):
        self.file_chooser_popup(is_dir=True)

    def next_action(self):
        supported_list = MyAppButton.supported_files[1:]
        if MyAppButton.current_index < len(supported_list):
            file_path = supported_list[MyAppButton.current_index]
            self.load_image(file_path)
            MyAppButton.current_index += 1
        else:
            self.load_none_image()

    def prev_action(self):
        if MyAppButton.current_index > 0:
            MyAppButton.current_index -= 1
            file_path = MyAppButton.supported_files[MyAppButton.current_index]
            self.load_image(file_path)
        else:
            self.load_none_image()

    def save_action(self):
        self.image_manager.save_image(MyAppButton.supported_files, MyAppButton.current_index)

    def Info_action(self):
        pass

    def crop_action(self):
        self.show_input_ui(label_items=['Top', 'Left', 'Bottom', 'Right'], callback=self.crop_button_callback)

    def resize_action(self):
        self.show_input_ui(label_items=['Width', 'Height'], callback=self.resize_button_callback)

    def brightness_action(self):
        self.show_input_ui(label_items=['brt'], callback=self.brightness_button_callback)

    def saturation_action(self):
        self.show_input_ui(label_items=['sat'], callback=self.saturation_button_callback)

    def rotate_90_degrees_action(self):
        pass

    def flip_vertically_or_horizontally_action(self):
        pass

    def show_input_ui(self, label_items, callback):
        LABEL_WIDTH_RATIO = 0.2
        INPUT_WIDTH_RATIO = 0.6

        right_box = App.get_running_app().root.ids.right_box
        right_box.clear_widgets()

        labels = []
        text_inputs = []
        label_name = label_items
        label_width = right_box.width * LABEL_WIDTH_RATIO  
        text_input_width = right_box.width * INPUT_WIDTH_RATIO

        for i in range(len(label_name)):
            label = Label(text=f"{label_name[i]} : ", size_hint=(None, None), size=(label_width, 60), padding=(10, 10))
            text_input = TextInput(text="", size_hint=(None, None), width=text_input_width, height=60, padding=(10, 10))

            labels.append(label)
            text_inputs.append(text_input)
        button = Button(text="Submit", size_hint=(None, None), size=(label_width + text_input_width, 60))

        float_layout = FloatLayout()
        for i in range(len(label_name)):
            float_layout.add_widget(labels[i])
            float_layout.add_widget(text_inputs[i])
        float_layout.add_widget(button)
        
        input_center_y = 0.9
        for i in range(len(label_name)):
            text_inputs[i].pos_hint = {'center_x': 0.6, 'center_y': input_center_y}
            labels[i].pos_hint = {'center_x': 0.2, 'center_y': input_center_y}
            input_center_y -= 0.0525
        button.pos_hint = {'center_x': 0.5, 'center_y': input_center_y}
        
        button.background_color = (250/255, 219/255, 216/255, 1)

        button.bind(on_press=lambda instance: callback(text_inputs))

        right_box.add_widget(float_layout)

    def update_right_label(self):
        right_box = App.get_running_app().root.ids
        right_box.update_label_text(self.text)

    def file_chooser_popup(self, is_dir):
        file_chooser = FileChooserListView(on_submit=self.on_directory_chosen if is_dir else self.on_file_chosen, dirselect=is_dir)
        popup = Popup(title="Select Directory" if is_dir else "Select File", content=file_chooser, size_hint=(0.8, 0.8))
        popup.open()
    
    def dismiss_popup(self, instance):
        parent = instance.parent
        while parent and not isinstance(parent, Popup):
            parent = parent.parent
        if parent:
            parent.dismiss()

    def on_file_chosen(self, instance, value, touch):
        if value:
            MyAppButton.supported_files.clear()
            MyAppButton.current_index = INITIAL_INDEX
            base_path = value[0]
            MyAppButton.supported_files.append(base_path)
            self.load_image(MyAppButton.supported_files[0])
            self.dismiss_popup(instance)

    def on_directory_chosen(self, instance, value, touch):
        extensions = [filter_.replace('*', '') for filter_ in self.filters]
        if value:
            MyAppButton.supported_files.clear()
            MyAppButton.current_index = INITIAL_INDEX
            base_path = value[0]
            for root_directory, _, filenames in os.walk(base_path):
                for filename in filenames:
                    file_path = os.path.join(root_directory, filename)
                    if os.path.isfile(file_path) and os.path.splitext(file_path)[1].lower() in extensions:
                        MyAppButton.supported_files.append(file_path)
            if MyAppButton.supported_files:
                self.load_image(MyAppButton.supported_files[0])
            self.dismiss_popup(instance)

    def load_image(self, file_path):
        center_box = App.get_running_app().root.ids.center_box
        center_box.clear_widgets()
        try:
            center_box.add_widget(Image(source=file_path))
        except Exception as e:
            center_box.add_widget(Label(text=f"Error: {str(e)}"))

    def load_none_image(self):
        center_box = App.get_running_app().root.ids.center_box
        center_box.clear_widgets()
        center_box.add_widget(Label(text="No more images available"))

    def crop_button_callback(self, text):
        items = []
        for item in text:
            if not item.text.isdigit():
                print("Please enter numeric values.")
                return
            items.append(int(item.text))
        
        self.image_manager.set_cropped(MyAppButton.supported_files, MyAppButton.current_index, items, self.load_image)

    def resize_button_callback(self, text):
        items = []
        for item in text:
            if not item.text.isdigit():
                print("Please enter numeric values.")
                return
            items.append(int(item.text))
        
        self.image_manager.set_resize(MyAppButton.supported_files, MyAppButton.current_index, items, self.load_image)
    
    def brightness_button_callback(self, text):
        items = []
        for item in text:
            value = float(item.text)
            if value < 0 or value > 2.5:
                print("Please enter numeric value between 0 and 2.5.")
                return
            items.append(value)

            self.image_manager.set_brightness(MyAppButton.supported_files, MyAppButton.current_index, items, self.load_image)

    def saturation_button_callback(self, text):
        items = []
        for item in text:
            value = float(item.text)
            if value < 0 or value > 2.5:
                print("Please enter numeric value between 0 and 2.5.")
                return
            items.append(value)

            self.image_manager.set_saturation(MyAppButton.supported_files, MyAppButton.current_index, items, self.load_image)

    def rotate_90_degrees_action(self, text):
        pass

if __name__ == '__main__':
    try:
        load_dotenv()
    except FileNotFoundError:
        print("Could not find the `.env` file. Environment variables are not loaded.")
    
    CvApp().run()
