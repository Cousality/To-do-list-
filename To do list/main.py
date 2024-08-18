import json
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup 
class MainScreen(Screen):
    pass
#Daily Screen made
class TaskDetailScreen(Screen):
    def __init__(self, **kwargs):
        super(TaskDetailScreen, self).__init__(**kwargs)
        self.current_task = None

    def on_pre_enter(self, *args):
        if self.current_task:
            self.ids.detail_text_input.text = self.manager.get_screen('Daily_Screen').task_descriptions[self.current_task].text

    def save_task_detail(self):
        detail_text = self.ids.detail_text_input.text
        daily_screen = self.manager.get_screen('Daily_Screen')
        daily_screen.task_descriptions[self.current_task].text = detail_text
        self.manager.current = 'Daily_Screen'
class DailyScreen(Screen):
    def __init__(self, **kwargs):
        super(DailyScreen, self).__init__(**kwargs)
        self.task_descriptions = {}
        self.tasks_loaded = False

    def on_enter(self):
        if not self.tasks_loaded:
            self.load_tasks()
            self.tasks_loaded = True


    def add_task(self):
        task_text = self.ids.text_input.text
        if task_text and len(task_text) <= 30:
            row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            task_label = Label(text=task_text, size_hint_x=0.6)
            delete_button = Button(text='Delete', size_hint_x=0.2)
            delete_button.bind(on_release=lambda btn: self.delete_task(row_layout))
            info_button = Button(text='Edit', size_hint_x=0.2)
            info_button.bind(on_release=lambda btn: self.show_task_info(task_text))
            row_layout.add_widget(task_label)
            row_layout.add_widget(delete_button)
            row_layout.add_widget(info_button)

            self.ids.task_list.add_widget(row_layout)
            self.ids.text_input.text = ''
            self.task_descriptions[task_text] = task_label
            self.save_tasks()
        else:
            popup = Popup(title='Character Limit',
                          content=Label(text='Character Limit of 30 and Minimun of 1'),
                          size_hint=(None, None), size=(300, 100))
            popup.open()

    def delete_task(self, row_layout):
        task_label = row_layout.children[2].text
        if task_label in self.task_descriptions:
            del self.task_descriptions[task_label]
        self.ids.task_list.remove_widget(row_layout)
        self.save_tasks()

    def show_task_info(self, task_text):
        task_detail_screen = self.manager.get_screen('TaskDetail_Screen')
        task_detail_screen.current_task = task_text
        self.manager.current = 'TaskDetail_Screen'
    def delete_all(self):
        popup = Popup(title='Confirm Deletion',
                      content=Label(text='Are you sure you want to delete all tasks?'),
                      size_hint=(None, None), size=(300, 200), auto_dismiss=False)
        yes_button = Button(text='Yes')
        no_button = Button(text='No')
        yes_button.bind(on_release=lambda btn: self.confirm_delete_all(popup))
        no_button.bind(on_release=popup.dismiss)

        button_box = BoxLayout(orientation='horizontal')
        button_box.add_widget(yes_button)
        button_box.add_widget(no_button)
        popup.content = button_box
        popup.open()

    def confirm_delete_all(self, popup):
        self.ids.task_list.clear_widgets()
        self.task_descriptions.clear()
        self.save_tasks()
        popup.dismiss()

    def save_tasks(self):
        tasks = list(self.task_descriptions.keys())
        with open('tasks.json', 'w') as file:
            json.dump(tasks, file)

    def load_tasks(self):
        self.ids.task_list.clear_widgets()
        self.task_descriptions.clear()
        if os.path.exists('tasks.json'):
            with open('tasks.json', 'r') as file:
                tasks = json.load(file)
                for task in tasks:
                    row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                    task_label = Label(text=task, size_hint_x=0.6)
                    delete_button = Button(text='Delete', size_hint_x=0.2)
                    delete_button.bind(on_release=lambda btn, layout=row_layout: self.delete_task(layout))
                    info_button = Button(text='Info', size_hint_x=0.2)
                    info_button.bind(on_release=lambda btn, text=task: self.show_task_info(text))
                    row_layout.add_widget(task_label)
                    row_layout.add_widget(delete_button)
                    row_layout.add_widget(info_button)
                    self.ids.task_list.add_widget(row_layout)
                    self.task_descriptions[task] = task_label

class WindowManager(ScreenManager):
    pass

kv = Builder.load_file('To_Do_List.kv')

class To_Do_List(App):
    def build(self):
        if platform not in ['android', 'ios']:
            Window.size = (450, 800)
        Window.clearcolor = 0.15, 0.2, 0.2, 0.2
        return kv

    def on_start(self):
        # Load tasks when the application starts
        daily_screen = self.root.get_screen('Daily_Screen')
        daily_screen.load_tasks()

    def on_stop(self):
        # Save tasks when the application is about to close
        daily_screen = self.root.get_screen('Daily_Screen')
        daily_screen.save_tasks()

if __name__ == '__main__':
    To_Do_List().run()