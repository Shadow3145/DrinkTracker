# Android Drink Tracker App
# A mobile app for tracking liquid intake and calories from drinks
# Built with Python and Kivy for Android deployment

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.colorpicker import ColorPicker
import json
import os
from datetime import datetime, date
from kivy.utils import get_color_from_hex

class DrinkGlass(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.daily_intake = []
        self.daily_goal = 2000  # ml
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def update_intake(self, intake_list):
        self.daily_intake = intake_list
        self.update_graphics()
    
    def update_graphics(self, *args):
        self.canvas.clear()
        
        # Glass outline
        with self.canvas:
            Color(0.2, 0.6, 0.8, 1)  # Blue outline
            # Draw glass shape (rounded bottom, straight top)
            glass_width = min(self.width * 0.8, dp(120))
            glass_height = self.height * 0.8
            glass_x = self.center_x - glass_width / 2
            glass_y = self.center_y - glass_height / 2
            
            # Glass outline
            Line(width=3, points=[
                glass_x, glass_y + glass_height,  # top left
                glass_x + glass_width, glass_y + glass_height,  # top right
                glass_x + glass_width, glass_y + glass_height * 0.2,  # right side
                glass_x + glass_width * 0.9, glass_y,  # bottom right curve
                glass_x + glass_width * 0.1, glass_y,  # bottom left curve
                glass_x, glass_y + glass_height * 0.2,  # left side
                glass_x, glass_y + glass_height  # back to top
            ])
            
            # Fill the glass with colored segments
            total_volume = sum(intake['volume'] for intake in self.daily_intake)
            if total_volume > 0:
                current_height = glass_y
                fill_height = min(glass_height * 0.9, glass_height * (total_volume / self.daily_goal))
                
                for intake in self.daily_intake:
                    segment_height = (intake['volume'] / total_volume) * fill_height
                    color = get_color_from_hex(intake['color'])
                    Color(color[0], color[1], color[2], 0.8)
                    
                    # Create filled rectangle for this drink segment
                    Rectangle(
                        pos=(glass_x + 3, current_height),
                        size=(glass_width - 6, segment_height)
                    )
                    current_height += segment_height
            
            # Add measurement lines
            Color(0.5, 0.5, 0.5, 0.5)
            for i in range(1, 5):
                y_pos = glass_y + (glass_height * i / 5)
                Line(points=[glass_x, y_pos, glass_x + glass_width, y_pos], width=1)

class DrinkTrackerApp(App):
    def build(self):
        self.drinks = [
            {'id': 1, 'name': 'Water', 'calories_per_100ml': 0, 'color': '#3B82F6'},
            {'id': 2, 'name': 'Orange Juice', 'calories_per_100ml': 45, 'color': '#F97316'},
            {'id': 3, 'name': 'Coffee', 'calories_per_100ml': 2, 'color': '#92400E'},
            {'id': 4, 'name': 'Coca Cola', 'calories_per_100ml': 42, 'color': '#7C2D12'}
        ]
        self.daily_intake = []
        self.load_data()
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = Label(
            text='Drink Tracker',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50),
            bold=True
        )
        main_layout.add_widget(header)
        
        # Progress section with glass
        progress_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(200))
        
        # Stats column
        stats_layout = BoxLayout(orientation='vertical', size_hint_x=0.4)
        
        total_volume = sum(intake['volume'] for intake in self.daily_intake)
        total_calories = sum(intake['calories'] for intake in self.daily_intake)
        
        self.volume_label = Label(
            text=f'{total_volume}ml\nToday\'s intake',
            font_size=dp(16),
            halign='center'
        )
        self.calories_label = Label(
            text=f'{int(total_calories)}\nCalories',
            font_size=dp(16),
            halign='center'
        )
        
        stats_layout.add_widget(self.volume_label)
        stats_layout.add_widget(self.calories_label)
        
        # Glass visualization
        self.glass_widget = DrinkGlass(size_hint_x=0.3)
        self.glass_widget.update_intake(self.daily_intake)
        
        # Goal info
        goal_layout = BoxLayout(orientation='vertical', size_hint_x=0.3)
        goal_percentage = min(100, (total_volume / 2000) * 100)
        self.goal_label = Label(
            text=f'Goal: 2000ml\n{goal_percentage:.0f}%',
            font_size=dp(14),
            halign='center'
        )
        goal_layout.add_widget(self.goal_label)
        
        progress_layout.add_widget(stats_layout)
        progress_layout.add_widget(self.glass_widget)
        progress_layout.add_widget(goal_layout)
        
        main_layout.add_widget(progress_layout)
        
        # Add drink button
        add_drink_btn = Button(
            text='Add New Drink',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        add_drink_btn.bind(on_press=self.show_add_drink_popup)
        main_layout.add_widget(add_drink_btn)
        
        # Drinks scroll view
        scroll = ScrollView()
        self.drinks_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.drinks_layout.bind(minimum_height=self.drinks_layout.setter('height'))
        
        self.update_drinks_list()
        
        scroll.add_widget(self.drinks_layout)
        main_layout.add_widget(scroll)
        
        return main_layout
    
    def update_drinks_list(self):
        self.drinks_layout.clear_widgets()
        
        for drink in self.drinks:
            drink_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
            
            # Drink info
            info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            
            # Color indicator
            color_widget = Widget(size_hint_x=None, width=dp(20))
            with color_widget.canvas:
                color = get_color_from_hex(drink['color'])
                Color(color[0], color[1], color[2], 1)
                Rectangle(pos=color_widget.pos, size=color_widget.size)
            
            drink_info = Label(
                text=f"{drink['name']}\n{drink['calories_per_100ml']} cal/100ml",
                size_hint_x=0.7
            )
            
            delete_btn = Button(
                text='Delete',
                size_hint_x=0.2,
                background_color=(0.8, 0.2, 0.2, 1)
            )
            delete_btn.bind(on_press=lambda x, d_id=drink['id']: self.delete_drink(d_id))
            
            info_layout.add_widget(color_widget)
            info_layout.add_widget(drink_info)
            info_layout.add_widget(delete_btn)
            
            # Buttons layout
            buttons_layout = GridLayout(cols=3, size_hint_y=None, height=dp(60), spacing=dp(5))
            
            btn_250 = Button(text='🥃\n250ml')
            btn_250.bind(on_press=lambda x, d=drink: self.add_intake(d, 250))
            
            btn_500 = Button(text='🥤\n500ml')
            btn_500.bind(on_press=lambda x, d=drink: self.add_intake(d, 500))
            
            btn_custom = Button(text='🍺\nCustom')
            btn_custom.bind(on_press=lambda x, d=drink: self.show_custom_amount_popup(d))
            
            buttons_layout.add_widget(btn_250)
            buttons_layout.add_widget(btn_500)
            buttons_layout.add_widget(btn_custom)
            
            drink_layout.add_widget(info_layout)
            drink_layout.add_widget(buttons_layout)
            
            self.drinks_layout.add_widget(drink_layout)
    
    def add_intake(self, drink, volume):
        calories = (drink['calories_per_100ml'] * volume) / 100
        intake = {
            'id': len(self.daily_intake) + 1,
            'drink_name': drink['name'],
            'volume': volume,
            'calories': calories,
            'time': datetime.now().strftime('%H:%M'),
            'color': drink['color'],
            'date': date.today().isoformat()
        }
        
        # Only keep today's intake
        today = date.today().isoformat()
        self.daily_intake = [i for i in self.daily_intake if i.get('date', today) == today]
        self.daily_intake.append(intake)
        
        self.update_display()
        self.save_data()
    
    def update_display(self):
        total_volume = sum(intake['volume'] for intake in self.daily_intake)
        total_calories = sum(intake['calories'] for intake in self.daily_intake)
        goal_percentage = min(100, (total_volume / 2000) * 100)
        
        self.volume_label.text = f'{total_volume}ml\nToday\'s intake'
        self.calories_label.text = f'{int(total_calories)}\nCalories'
        self.goal_label.text = f'Goal: 2000ml\n{goal_percentage:.0f}%'
        self.glass_widget.update_intake(self.daily_intake)
    
    def show_add_drink_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        name_input = TextInput(hint_text='Drink name', multiline=False)
        calories_input = TextInput(hint_text='Calories per 100ml', multiline=False, input_filter='float')
        
        # Simple color selection
        color_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        color_layout.add_widget(Label(text='Color:', size_hint_x=0.3))
        
        colors = ['#3B82F6', '#F97316', '#92400E', '#7C2D12', '#10B981', '#8B5CF6', '#F59E0B']
        selected_color = {'color': colors[0]}
        
        for color in colors:
            color_btn = Button(size_hint_x=None, width=dp(40))
            color_rgba = get_color_from_hex(color)
            color_btn.background_color = color_rgba
            color_btn.bind(on_press=lambda x, c=color: selected_color.update({'color': c}))
            color_layout.add_widget(color_btn)
        
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        def add_drink(instance):
            if name_input.text and calories_input.text:
                new_drink = {
                    'id': max([d['id'] for d in self.drinks]) + 1 if self.drinks else 1,
                    'name': name_input.text,
                    'calories_per_100ml': float(calories_input.text),
                    'color': selected_color['color']
                }
                self.drinks.append(new_drink)
                self.update_drinks_list()
                self.save_data()
                popup.dismiss()
        
        add_btn = Button(text='Add')
        add_btn.bind(on_press=add_drink)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        buttons_layout.add_widget(add_btn)
        buttons_layout.add_widget(cancel_btn)
        
        content.add_widget(name_input)
        content.add_widget(calories_input)
        content.add_widget(color_layout)
        content.add_widget(buttons_layout)
        
        popup = Popup(title='Add New Drink', content=content, size_hint=(0.8, 0.6))
        popup.open()
    
    def show_custom_amount_popup(self, drink):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        content.add_widget(Label(text=f'Enter amount for {drink["name"]}'))
        
        amount_input = TextInput(hint_text='Amount in ml', multiline=False, input_filter='int')
        content.add_widget(amount_input)
        
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        def add_custom(instance):
            if amount_input.text:
                self.add_intake(drink, int(amount_input.text))
                popup.dismiss()
        
        add_btn = Button(text='Add')
        add_btn.bind(on_press=add_custom)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        buttons_layout.add_widget(add_btn)
        buttons_layout.add_widget(cancel_btn)
        
        content.add_widget(buttons_layout)
        
        popup = Popup(title='Custom Amount', content=content, size_hint=(0.6, 0.4))
        popup.open()
    
    def delete_drink(self, drink_id):
        self.drinks = [d for d in self.drinks if d['id'] != drink_id]
        self.update_drinks_list()
        self.save_data()
    
    def save_data(self):
        data = {
            'drinks': self.drinks,
            'daily_intake': self.daily_intake
        }
        try:
            with open('drink_tracker_data.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        try:
            if os.path.exists('drink_tracker_data.json'):
                with open('drink_tracker_data.json', 'r') as f:
                    data = json.load(f)
                    self.drinks = data.get('drinks', self.drinks)
                    all_intake = data.get('daily_intake', [])
                    # Only keep today's intake
                    today = date.today().isoformat()
                    self.daily_intake = [i for i in all_intake if i.get('date', today) == today]
        except Exception as e:
            print(f"Error loading data: {e}")

if __name__ == '__main__':
    DrinkTrackerApp().run()