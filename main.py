from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.properties import ListProperty, NumericProperty
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.animation import Animation
from kivy.clock import Clock
import random
import math

OWNERS = [
    "José Silva",
    "Maria Oliveira",
    "Francisco Lima",
    "Ana Sousa",
    "Pedro Costa",
    "Carlos Santos",
    "Fernanda Rocha",
    "João Pereira",
    "Isabel Martins",
    "Roberto Alves",
    "Beatriz Nunes",
]
SOILS = [
    "Latossolo Amarelo",
    "Argissolo Vermelho",
    "Cambissolo",
    "Neossolo",
    "Gleissolo",
    "Vertissolo",
]
FLORA = [
    "Marmeleiro",
    "Aroeira",
    "Jurema-Preta",
    "Angico",
    "Jatobá",
    "Ipê",
    "Mandacaru",
    "Caatinga",
    "Umbuzeiro",
    "Cajueiro",
    "Eucalipto",
    "Girassol",
]

class ApiaryPoint:
    def __init__(self, x, y, user_loc, owner):
        self.x = x
        self.y = y
        self.distance = math.hypot(x - user_loc[0], y - user_loc[1]) * 0.01
        self.owner = owner
        self.soil = random.choice(SOILS)
        self.potential_index = random.randint(40, 95)
        self.main_flora = random.sample(FLORA, k=random.randint(2, 4))
        self.color = self.get_color_by_distance()
        self.size = self.get_size_by_potential()
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        self.hives_count = random.randint(5, 45)
        self.honey_production = random.randint(15, 85)
    def get_color_by_distance(self):
        if self.distance < 8:
            return [0.92, 0.91, 0.14, 1]
        elif self.distance < 15:
            return [0.29, 0.76, 0.38, 1]
        elif self.distance < 25:
            return [0.16, 0.5, 0.87, 1]
        elif self.distance < 40:
            return [0.9, 0.37, 0.26, 1]
        else:
            return [0.35, 0.35, 0.41, 1]
    def get_size_by_potential(self):
        base_size = 8
        bonus = (self.potential_index - 40) / 55 * 12
        return base_size + bonus

class MapScatter(Scatter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_rotation = False
        self.scale_min = 0.5
        self.scale_max = 4.0
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and abs(self.scale - 1.4) < 0.01:
            return super().on_touch_down(touch)
        return False
    def on_touch_move(self, touch):
        if abs(self.scale - 1.4) < 0.01:
            return super().on_touch_move(touch)
        return False
    def on_transform_with_touch(self, touch):
        if self.scale < self.scale_min:
            self.scale = self.scale_min
        elif self.scale > self.scale_max:
            self.scale = self.scale_max
        if self.x > 300:
            self.x = 300
        elif self.x < -1200:
            self.x = -1200
        if self.y > 300:
            self.y = 300
        elif self.y < -900:
            self.y = -900

class BeeMapWidget(BoxLayout):
    user_loc = ListProperty([600, 400])
    points = ListProperty([])
    pulse_time = NumericProperty(0)
    zoom_level = NumericProperty(1.0)

    def on_kv_post(self, base_widget):
        used_coords = set()
        self.points = []
        for owner in OWNERS:
            tries = 0
            while True:
                x = random.randint(80, 1120)
                y = random.randint(80, 720)
                if (x, y) not in used_coords:
                    used_coords.add((x, y))
                    break
                tries += 1
                if tries > 10:
                    break
            self.points.append(ApiaryPoint(x, y, self.user_loc, owner))
        self.draw_map()
        Clock.schedule_interval(self.update_pulse, 1 / 30.0)

    def update_pulse(self, dt):
        self.pulse_time += dt * 2
        self.draw_map()

    def draw_map(self):
        map_scatter = self.ids.map_scatter
        canvas_area = self.ids.canvas_area
        canvas_area.canvas.clear()
        with canvas_area.canvas:
            Color(0.03, 0.04, 0.08, 1)
            Rectangle(pos=(0, 0), size=(1200, 800))
            Color(0.2, 0.6, 1, 1)
            Line(rectangle=(0, 0, 1200, 800), width=6)
            Color(0.15, 0.23, 0.44, 0.8)
            Line(rectangle=(2, 2, 1196, 796), width=2)
            grid_spacing = int(60 / max(0.5, map_scatter.scale))
            Color(0.08, 0.1, 0.15, 0.4)
            for i in range(0, 1200, grid_spacing):
                Line(points=[i, 0, i, 800], width=0.5)
            for i in range(0, 800, grid_spacing):
                Line(points=[0, i, 1200, i], width=0.5)
            Color(0.1, 0.15, 0.25, 0.3)
            for i, point1 in enumerate(self.points):
                for point2 in self.points[i + 1 :]:
                    dist = math.hypot(point1.x - point2.x, point1.y - point2.y)
                    if dist < 80 + (50 / max(0.5, map_scatter.scale)):
                        Line(points=[point1.x, point1.y, point2.x, point2.y], width=1)
            if map_scatter.scale > 1.5:
                Color(0.15, 0.2, 0.3, 0.2)
                for point in self.points:
                    if point.potential_index > 75:
                        influence_radius = 60 + point.potential_index * 0.5
                        Line(circle=(point.x, point.y, influence_radius), width=2)
            for point in self.points:
                base_size = max(8, point.size * max(0.8, map_scatter.scale * 0.7))
                Color(0, 0, 0, 0.22)
                Ellipse(
                    pos=(point.x - base_size / 2 - 2, point.y - base_size / 2 - 2),
                    size=(base_size + 4, base_size + 4),
                )
                Color(*point.color)
                Ellipse(
                    pos=(point.x - base_size / 2, point.y - base_size / 2),
                    size=(base_size, base_size),
                )
                border_color = [min(1, c * 1.12 + 0.18) for c in point.color[:3]] + [
                    1.0
                ]
                Color(*border_color)
                Line(circle=(point.x, point.y, base_size / 2), width=3)
                if map_scatter.scale > 1.0:
                    productivity_ring_size = base_size + 6
                    productivity_alpha = (point.honey_production / 100) * 0.54
                    prod_ring_col = [0.85, 0.73, 0.24, productivity_alpha]
                    Color(*prod_ring_col)
                    Line(circle=(point.x, point.y, productivity_ring_size / 2), width=2)
                if map_scatter.scale > 0.8:
                    center_alpha = 0.7 - (point.distance / 60.0) * 0.36
                    Color(1, 1, 1, center_alpha)
                    center_size = max(3, base_size * 0.3)
                    Ellipse(
                        pos=(point.x - center_size / 2, point.y - center_size / 2),
                        size=(center_size, center_size),
                    )
            # Ponto do usuário com animação
            user_pulse = (20 + 8 * math.sin(self.pulse_time * 1.5)) * max(
                0.8, map_scatter.scale
            )
            Color(0, 0, 0, 0.26)
            Ellipse(
                pos=(
                    self.user_loc[0] - user_pulse / 2 - 2,
                    self.user_loc[1] - user_pulse / 2 - 2,
                ),
                size=(user_pulse + 4, user_pulse + 4),
            )
            Color(0.14, 1, 0.53, 0.36)
            Ellipse(
                pos=(
                    self.user_loc[0] - user_pulse / 2,
                    self.user_loc[1] - user_pulse / 2,
                ),
                size=(user_pulse, user_pulse),
            )
            Color(0.18, 1, 0.6, 0.92)
            user_size = 16 * max(0.8, map_scatter.scale)
            Line(circle=(self.user_loc[0], self.user_loc[1], user_size), width=4)
            Color(0.13, 0.8, 0.4, 1)
            center_size = 12 * max(0.8, map_scatter.scale)
            Ellipse(
                pos=(
                    self.user_loc[0] - center_size / 2,
                    self.user_loc[1] - center_size / 2,
                ),
                size=(center_size, center_size),
            )

    def on_map_transform(self, instance, value):
        self.zoom_level = self.ids.map_scatter.scale
        self.draw_map()

    def zoom_in(self):
        scatter = self.ids.map_scatter
        if scatter.scale < 4.0:
            anim = Animation(scale=min(4.0, scatter.scale * 1.4), duration=0.3)
            anim.start(scatter)
            Clock.schedule_once(lambda dt: self.draw_map(), 0.35)

    def zoom_out(self):
        scatter = self.ids.map_scatter
        if scatter.scale > 0.5:
            anim = Animation(
                scale=max(0.5, scatter.scale * 0.75), duration=0.3
            )
            anim.start(scatter)
            Clock.schedule_once(lambda dt: self.draw_map(), 0.35)

    def center_map(self):
        scatter = self.ids.map_scatter
        center_x = -self.user_loc[0] * scatter.scale + 450
        center_y = -self.user_loc[1] * scatter.scale + 300
        anim = Animation(x=center_x, y=center_y, duration=0.5)
        anim.start(scatter)

    def on_touch_down(self, touch):
        # Só deixa clicar nos pontos no canvas_area
        if self.ids.canvas_area.collide_point(*touch.pos):
            scatter = self.ids.map_scatter
            local_x = (touch.x - scatter.x) / scatter.scale
            local_y = (touch.y - scatter.y) / scatter.scale
            for point in self.points:
                dist = math.hypot(point.x - local_x, point.y - local_y)
                if dist < point.size + 10:
                    self.show_popup(point)
                    return True
        return super().on_touch_down(touch)

    def show_popup(self, point):
        popup = ModernPopup(point=point)
        popup.open()

class ModernPopup(Popup):
    def __init__(self, point, **kwargs):
        super().__init__(**kwargs)
        self.point = point
        self.title = ""
        self.size_hint = (None, None)
        self.size = (500, 650)
        self.separator_height = 0
        self.background = ""
        self.auto_dismiss = True
        content = FloatLayout()
        self.create_content(content)
        self.content = content
        self.opacity = 0
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self)
    def create_content(self, layout):
        with layout.canvas.before:
            Color(0.06, 0.08, 0.12, 0.96)
            self.bg_rect = RoundedRectangle(
                pos=layout.pos, size=layout.size, radius=[25]
            )
            Color(0.2, 0.7, 1, 0.9)
            Line(
                rounded_rectangle=(
                    layout.pos[0],
                    layout.pos[1],
                    layout.size[0],
                    layout.size[1],
                    25,
                ),
                width=3,
            )
            Color(0.4, 0.8, 1, 0.5)
            Line(
                rounded_rectangle=(
                    layout.pos[0] + 2,
                    layout.pos[1] + 2,
                    layout.size[0] - 4,
                    layout.size[1] - 4,
                    23,
                ),
                width=1,
            )
        layout.bind(pos=self.update_bg, size=self.update_bg)
        title = Label(
            text="📍 DETALHES DO APIÁRIO",
            font_size=26,
            bold=True,
            color=[0.2, 0.8, 1, 1],
            pos_hint={"center_x": 0.5, "top": 0.95},
            size_hint=(1, 0.08),
        )
        layout.add_widget(title)
        info_y = 0.82
        spacing = 0.09
        info_data = [
            ("👤 PROPRIETÁRIO", self.point.owner, [1, 1, 1, 1]),
            ("📍 DISTÂNCIA", f"{self.point.distance:.1f} km", [0.3, 0.9, 1, 1]),
            ("🌱 TIPO DE SOLO", self.point.soil, [0.6, 1, 0.4, 1]),
            (
                "🏺 COLMEIAS ATIVAS",
                f"{self.point.hives_count} unidades",
                [1, 0.8, 0.3, 1],
            ),
            (
                "🍯 PRODUÇÃO ANUAL",
                f"{self.point.honey_production} kg/ano",
                [1, 0.7, 0.2, 1],
            ),
            ("🌿 FLORA PRINCIPAL", ", ".join(self.point.main_flora), [1, 0.7, 0.9, 1]),
        ]
        for label_text, value_text, color in info_data:
            self.add_info_item(layout, label_text, value_text, color, info_y)
            info_y -= spacing
        self.add_potential_bar(layout, info_y - 0.02)
        button_layout = BoxLayout(
            orientation="horizontal",
            spacing=15,
            pos_hint={"center_x": 0.5, "y": 0.05},
            size_hint=(0.9, 0.12),
        )
        route_btn = ModernButton(
            text="🗺️ VER ROTA",
            font_size=16,
            bold=True,
            background_normal="",
            background_color=[0.2, 0.6, 0.9, 1],
            color=[1, 1, 1, 1],
        )
        close_btn = ModernButton(
            text="❌ FECHAR",
            font_size=16,
            bold=True,
            background_normal="",
            background_color=[0.6, 0.2, 0.3, 1],
            color=[1, 1, 1, 1],
        )
        close_btn.bind(on_release=self.dismiss)
        button_layout.add_widget(route_btn)
        button_layout.add_widget(close_btn)
        layout.add_widget(button_layout)
    def add_info_item(self, layout, label_text, value_text, color, y_pos):
        item_bg = Label(
            text="", pos_hint={"x": 0.05, "center_y": y_pos}, size_hint=(0.9, 0.07)
        )
        with item_bg.canvas.before:
            Color(0.1, 0.12, 0.18, 0.5)
            RoundedRectangle(pos=item_bg.pos, size=item_bg.size, radius=[10])
        layout.add_widget(item_bg)
        label = Label(
            text=label_text,
            font_size=13,
            bold=True,
            color=[0.7, 0.8, 0.9, 1],
            pos_hint={"x": 0.08, "center_y": y_pos},
            size_hint=(0.35, 0.06),
            halign="left",
        )
        label.bind(size=label.setter("text_size"))
        layout.add_widget(label)
        value = Label(
            text=value_text,
            font_size=14,
            bold=True,
            color=color,
            pos_hint={"x": 0.45, "center_y": y_pos},
            size_hint=(0.48, 0.06),
            halign="left",
        )
        value.bind(size=value.setter("text_size"))
        layout.add_widget(value)
    def add_potential_bar(self, layout, y_pos):
        pot_label = Label(
            text="⚡ POTENCIAL APÍCOLA",
            font_size=14,
            bold=True,
            color=[0.7, 0.8, 0.9, 1],
            pos_hint={"x": 0.08, "center_y": y_pos + 0.04},
            size_hint=(0.4, 0.05),
            halign="left",
        )
        pot_label.bind(size=pot_label.setter("text_size"))
        layout.add_widget(pot_label)
        pot_value = Label(
            text=f"{self.point.potential_index}%",
            font_size=18,
            bold=True,
            color=(
                [0.3, 1, 0.5, 1]
                if self.point.potential_index > 70
                else [1, 0.8, 0.3, 1]
            ),
            pos_hint={"x": 0.75, "center_y": y_pos + 0.04},
            size_hint=(0.2, 0.05),
        )
        layout.add_widget(pot_value)
        bar_bg = Label(
            text="", pos_hint={"x": 0.08, "center_y": y_pos}, size_hint=(0.84, 0.03)
        )
        with bar_bg.canvas:
            Color(0.2, 0.25, 0.3, 1)
            RoundedRectangle(pos=bar_bg.pos, size=bar_bg.size, radius=[5])
            progress_width = bar_bg.size[0] * (self.point.potential_index / 100)
            if self.point.potential_index > 80:
                Color(0.2, 1, 0.3, 1)
            elif self.point.potential_index > 60:
                Color(1, 0.8, 0.2, 1)
            else:
                Color(1, 0.4, 0.4, 1)
            RoundedRectangle(
                pos=bar_bg.pos, size=(progress_width, bar_bg.size[1]), radius=[5]
            )
        layout.add_widget(bar_bg)
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class ModernButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 0.1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self.update_bg, size=self.update_bg)
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    def on_press(self):
        anim = Animation(background_color=[0.3, 0.7, 1, 1], duration=0.1)
        anim.start(self)
    def on_release(self):
        anim = Animation(background_color=self.background_color, duration=0.2)
        anim.start(self)

class BeeMapApp(App):
    def build(self):
        Builder.load_file("design.kv")
        return BeeMapWidget()

if __name__ == "__main__":
    BeeMapApp().run()