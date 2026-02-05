# fichier: main.py

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import random

kivy.require('2.1.0')

DATA_FILE = "data.json"

# ----- DATA HANDLING -----
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "actions": [],
            "log": {},
            "streak": 0
        }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ----- SCREENS -----
class MainPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)
        
        self.label = Label(text="Bienvenue dans Discipline App !", font_size=24)
        self.layout.add_widget(self.label)
        
        self.points_label = Label(text="Points aujourd'hui : 0", font_size=18)
        self.layout.add_widget(self.points_label)
        
        self.streak_label = Label(text="Streak : 0 jours", font_size=18)
        self.layout.add_widget(self.streak_label)
        
        self.button_actions = Button(text="Déclarer actions", size_hint_y=None, height=50)
        self.button_actions.bind(on_press=self.go_actions)
        self.layout.add_widget(self.button_actions)
        
        self.button_stats = Button(text="Voir statistiques", size_hint_y=None, height=50)
        self.button_stats.bind(on_press=self.show_stats)
        self.layout.add_widget(self.button_stats)
        
        self.button_philo = Button(text="Phrase du jour", size_hint_y=None, height=50)
        self.button_philo.bind(on_press=self.show_philo)
        self.layout.add_widget(self.button_philo)
        
        # charger données
        self.data = load_data()
        self.update_dashboard()

    def update_dashboard(self):
        today = datetime.now().strftime("%Y-%m-%d")
        points_today = sum([a['points'] for a in self.data['log'].get(today, [])])
        self.points_label.text = f"Points aujourd'hui : {points_today}"
        self.streak_label.text = f"Streak : {self.data.get('streak',0)} jours"

    def go_actions(self, instance):
        self.manager.current = 'action'

    def show_stats(self, instance):
        StatsPage.show_plot(self.data)

    def show_philo(self, instance):
        phrases = [
            "La discipline précède la motivation.",
            "Petits efforts chaque jour, grands résultats sur le long terme.",
            "Agir est plus important que penser."
        ]
        self.label.text = random.choice(phrases)

class ActionPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = load_data()
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)

        self.label = Label(text="Choisissez votre action et entrez la quantité")
        self.layout.add_widget(self.label)

        # Spinner des actions proposées
        self.spinner = Spinner(
            text='Sélectionner une action',
            values=('Sport', 'Travail', 'Étude', 'Projet perso'),
            size_hint=(1, None),
            height=44
        )
        self.layout.add_widget(self.spinner)

        # Input quantifiable
        self.qty_input = TextInput(hint_text="Entrez la quantité (minutes/reps)", input_filter='int', multiline=False)
        self.layout.add_widget(self.qty_input)

        self.submit_btn = Button(text="Ajouter", size_hint_y=None, height=50)
        self.submit_btn.bind(on_press=self.add_action)
        self.layout.add_widget(self.submit_btn)

        self.back_btn = Button(text="Retour au dashboard", size_hint_y=None, height=50)
        self.back_btn.bind(on_press=self.go_main)
        self.layout.add_widget(self.back_btn)

    def go_main(self, instance):
        self.manager.current = 'main'

    def add_action(self, instance):
        action_name = self.spinner.text
        if action_name == 'Sélectionner une action':
            return
        qty = self.qty_input.text
        if not qty.isdigit():
            return
        qty = int(qty)
        points = qty  # simple logique : 1 point = 1 unité
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.data['log']:
            self.data['log'][today] = []
        self.data['log'][today].append({
            "name": action_name,
            "qty": qty,
            "points": points
        })
        # mise à jour streak simple : +1 si jour valide
        if len(self.data['log'][today]) > 0:
            self.data['streak'] = self.data.get('streak',0)+1
        save_data(self.data)
        self.qty_input.text = ''
        self.spinner.text = 'Sélectionner une action'
        self.manager.get_screen('main').update_dashboard()

class StatsPage(Screen):
    @staticmethod
    def show_plot(data):
        # Graphique simple des points journaliers
        dates = sorted(data['log'].keys())
        points = [sum([a['points'] for a in data['log'][d]]) for d in dates]
        if not dates:
            print("Aucune donnée à afficher")
            return
        plt.figure(figsize=(8,4))
        plt.bar(dates, points, color='skyblue')
        plt.title("Points journaliers")
        plt.xlabel("Date")
        plt.ylabel("Points")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# ----- APP -----
class DisciplineApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainPage(name='main'))
        sm.add_widget(ActionPage(name='action'))
        sm.add_widget(StatsPage(name='stats'))
        return sm

if __name__ == '__main__':
    DisciplineApp().run()
