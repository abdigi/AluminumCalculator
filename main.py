import math

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup


BAR_LENGTH = 5800

MATERIALS = [
    "L",
    "T",
    "Z",
    "Ferma 90°",
    "Ferma Oval",
    "External",
    "Internal",
    "Tap",
    "Zocolo",
    "Fasha",
]


def make_button(text, color, font_size=16):
    return Button(
        text=text,
        font_size=sp(font_size),
        bold=True,
        background_normal="",
        background_down="",
        background_color=color,
        color=(1, 1, 1, 1),
        size_hint_y=None,
        height=dp(44),
    )


def make_label(text, font_size=15, color=(0.12, 0.15, 0.20, 1), **kwargs):
    return Label(
        text=text,
        font_size=sp(font_size),
        color=color,
        halign="left",
        valign="middle",
        **kwargs
    )


class MaterialCard(BoxLayout):
    def __init__(self, material_name, app, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(10),
            spacing=dp(8),
            **kwargs
        )

        self.material_name = material_name
        self.app_ref = app
        self.saved_entries = []

        self.bind(minimum_height=self.setter("height"))

        with self.canvas.before:
            Color(0.96, 0.97, 0.99, 1)
            self.card_background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)],
            )

        self.bind(pos=self.update_background, size=self.update_background)

        # Material name
        title = make_label(
            material_name,
            font_size=18,
            color=(0.08, 0.25, 0.48, 1),
            size_hint_y=None,
            height=dp(28),
        )
        title.bold = True
        self.add_widget(title)

        # Input row
        input_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(46),
            spacing=dp(6),
        )

        self.length_input = TextInput(
            hint_text="Length (mm)",
            multiline=False,
            input_filter="float",
            font_size=sp(16),
            size_hint_x=0.49,
            background_normal="",
            background_active="",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            cursor_color=(0.1, 0.3, 0.7, 1),
            padding=[dp(8), dp(12), dp(8), dp(8)],
        )

        self.quantity_input = TextInput(
            hint_text="Qty",
            text="1",
            multiline=False,
            input_filter="int",
            font_size=sp(16),
            size_hint_x=0.19,
            background_normal="",
            background_active="",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            cursor_color=(0.1, 0.3, 0.7, 1),
            padding=[dp(6), dp(12), dp(6), dp(8)],
        )

        add_button = Button(
            text="+ Add",
            font_size=sp(14),
            bold=True,
            size_hint_x=0.32,
            background_normal="",
            background_down="",
            background_color=(0.12, 0.55, 0.34, 1),
            color=(1, 1, 1, 1),
        )
        add_button.bind(on_release=self.add_entry)

        input_row.add_widget(self.length_input)
        input_row.add_widget(self.quantity_input)
        input_row.add_widget(add_button)
        self.add_widget(input_row)

        # Saved entry list
        self.entries_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
        )
        self.entries_layout.bind(
            minimum_height=self.entries_layout.setter("height")
        )
        self.add_widget(self.entries_layout)

    def update_background(self, *_):
        self.card_background.pos = self.pos
        self.card_background.size = self.size

    def add_entry(self, *_):
        length_text = self.length_input.text.strip()
        quantity_text = self.quantity_input.text.strip()

        if not length_text:
            self.app_ref.show_message(
                "Missing length",
                "Please enter the material length in millimeters.",
            )
            return

        if not quantity_text:
            self.app_ref.show_message(
                "Missing quantity",
                "Please enter the quantity.",
            )
            return

        try:
            length = float(length_text)
            quantity = int(quantity_text)
        except ValueError:
            self.app_ref.show_message(
                "Invalid input",
                "Enter a valid length and whole-number quantity.",
            )
            return

        if not math.isfinite(length) or length <= 0:
            self.app_ref.show_message(
                "Invalid length",
                "Length must be a number greater than zero.",
            )
            return

        if quantity <= 0:
            self.app_ref.show_message(
                "Invalid quantity",
                "Quantity must be at least 1.",
            )
            return

        entry = {
            "length": length,
            "quantity": quantity,
        }

        self.saved_entries.append(entry)
        self.create_entry_row(entry)

        # Clear the inputs for the next entry.
        self.length_input.text = ""
        self.quantity_input.text = "1"
        self.length_input.focus = True

    def create_entry_row(self, entry):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
            spacing=dp(6),
        )

        length = entry["length"]
        quantity = entry["quantity"]
        subtotal = length * quantity

        text = f"{length:g} mm × {quantity} = {subtotal:g} mm"

        entry_label = Label(
            text=text,
            font_size=sp(13),
            color=(0.15, 0.17, 0.20, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.79,
            shorten=True,
            shorten_from="right",
        )
        entry_label.bind(
            size=lambda instance, value: setattr(
                instance, "text_size", value
            )
        )

        remove_button = Button(
            text="✕",
            font_size=sp(16),
            bold=True,
            size_hint_x=0.21,
            background_normal="",
            background_down="",
            background_color=(0.82, 0.20, 0.20, 1),
            color=(1, 1, 1, 1),
        )
        remove_button.bind(
            on_release=lambda *_: self.remove_entry(entry, row)
        )

        row.add_widget(entry_label)
        row.add_widget(remove_button)
        self.entries_layout.add_widget(row)

    def remove_entry(self, entry, row):
        if entry in self.saved_entries:
            self.saved_entries.remove(entry)

        if row.parent:
            self.entries_layout.remove_widget(row)


class AluminumCalculatorApp(App):
    def build(self):
        self.title = "Aluminum Calculator"

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(10), dp(8), dp(10), dp(10)],
            spacing=dp(8),
        )

        # Fixed header
        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(66),
            spacing=dp(2),
        )

        title = Label(
            text="ALUMINUM CALCULATOR",
            font_size=sp(21),
            bold=True,
            color=(0.06, 0.23, 0.44, 1),
            size_hint_y=None,
            height=dp(36),
        )

        subtitle = Label(
            text="Enter length in mm and quantity",
            font_size=sp(13),
            color=(0.35, 0.38, 0.43, 1),
            size_hint_y=None,
            height=dp(24),
        )

        header.add_widget(title)
        header.add_widget(subtitle)
        root.add_widget(header)

        # Scrollable material cards
        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(4),
            scroll_type=["bars", "content"],
        )

        self.material_list = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=[0, dp(2), 0, dp(10)],
            size_hint_y=None,
        )
        self.material_list.bind(
            minimum_height=self.material_list.setter("height")
        )

        self.material_cards = []

        for material in MATERIALS:
            card = MaterialCard(material, self)
            self.material_cards.append(card)
            self.material_list.add_widget(card)

        scroll.add_widget(self.material_list)
        root.add_widget(scroll)

        # Fixed bottom button
        bottom = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(56),
            padding=[0, dp(3), 0, 0],
        )

        calculate_button = make_button(
            "CALCULATE MATERIALS",
            (0.08, 0.35, 0.72, 1),
            font_size=17,
        )
        calculate_button.height = dp(50)
        calculate_button.bind(on_release=self.calculate)

        bottom.add_widget(calculate_button)
        root.add_widget(bottom)

        return root

    def on_start(self):
        # Safe on Android — set after window is created
        Window.clearcolor = (0.94, 0.95, 0.97, 1)

    def show_message(self, title, message):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12),
        )

        label = Label(
            text=message,
            font_size=sp(16),
            color=(0.15, 0.15, 0.15, 1),
            halign="center",
            valign="middle",
        )
        label.bind(
            size=lambda instance, value: setattr(
                instance, "text_size", value
            )
        )

        close_button = make_button(
            "OK",
            (0.08, 0.35, 0.72, 1),
        )

        content.add_widget(label)
        content.add_widget(close_button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.45),
            auto_dismiss=False,
        )

        close_button.bind(on_release=popup.dismiss)
        popup.open()

    @staticmethod
    def format_number(number):
        return f"{number:g}"

    def calculate(self, *_):
        results = []

        for card in self.material_cards:
            total_length = sum(
                entry["length"] * entry["quantity"]
                for entry in card.saved_entries
            )

            if total_length > 0:
                bars = math.ceil(total_length / BAR_LENGTH)

                results.append({
                    "material": card.material_name,
                    "total": total_length,
                    "bars": bars,
                })

        if not results:
            self.show_message(
                "No materials",
                "Add at least one material entry before calculating.",
            )
            return

        self.show_results(results)

    def show_results(self, results):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8),
        )

        heading = Label(
            text="MATERIAL CALCULATION RESULTS",
            font_size=sp(17),
            bold=True,
            color=(0.06, 0.23, 0.44, 1),
            size_hint_y=None,
            height=dp(35),
        )
        content.add_widget(heading)

        note = Label(
            text=f"One bar = {BAR_LENGTH:,} mm",
            font_size=sp(13),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(25),
        )
        content.add_widget(note)

        # Results column headings
        heading_row = GridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(38),
            spacing=dp(3),
        )

        for text in ["Material", "Total (mm)", "Bars"]:
            cell = Label(
                text=text,
                font_size=sp(12),
                bold=True,
                color=(1, 1, 1, 1),
                halign="center",
                valign="middle",
            )
            with cell.canvas.before:
                Color(0.12, 0.35, 0.60, 1)
                cell.bg_rect = RoundedRectangle(
                    pos=cell.pos,
                    size=cell.size,
                    radius=[dp(4)],
                )
            cell.bind(
                pos=lambda instance, value: setattr(
                    instance.bg_rect, "pos", value
                ),
                size=lambda instance, value: setattr(
                    instance.bg_rect, "size", value
                ),
            )
            heading_row.add_widget(cell)

        content.add_widget(heading_row)

        # Scrollable results
        result_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(4),
        )

        result_grid = GridLayout(
            cols=1,
            spacing=dp(4),
            size_hint_y=None,
        )
        result_grid.bind(
            minimum_height=result_grid.setter("height")
        )

        for index, result in enumerate(results):
            row = GridLayout(
                cols=3,
                size_hint_y=None,
                height=dp(42),
                spacing=dp(3),
            )

            background = (
                (0.96, 0.97, 0.99, 1)
                if index % 2 == 0
                else (1, 1, 1, 1)
            )

            values = [
                result["material"],
                self.format_number(result["total"]),
                str(result["bars"]),
            ]

            for value in values:
                cell = Label(
                    text=value,
                    font_size=sp(12),
                    color=(0.12, 0.15, 0.19, 1),
                    halign="center",
                    valign="middle",
                    shorten=True,
                    shorten_from="right",
                )
                cell.bind(
                    size=lambda instance, size: setattr(
                        instance, "text_size", size
                    )
                )
                with cell.canvas.before:
                    Color(*background)
                    cell.bg_rect = RoundedRectangle(
                        pos=cell.pos,
                        size=cell.size,
                        radius=[dp(3)],
                    )
                cell.bind(
                    pos=lambda instance, value: setattr(
                        instance.bg_rect, "pos", value
                    ),
                    size=lambda instance, value: setattr(
                        instance.bg_rect, "size", value
                    ),
                )
                row.add_widget(cell)

            result_grid.add_widget(row)

        result_scroll.add_widget(result_grid)
        content.add_widget(result_scroll)

        close_button = make_button(
            "CLOSE",
            (0.08, 0.35, 0.72, 1),
        )
        content.add_widget(close_button)

        popup = Popup(
            title="Calculation Results",
            content=content,
            size_hint=(0.96, 0.78),
            auto_dismiss=True,
        )

        close_button.bind(on_release=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    AluminumCalculatorApp().run()