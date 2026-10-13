import math

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock


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


# ---------------------------------------------------------------------------
# Bottom Numeric Keypad
# ---------------------------------------------------------------------------

class BottomKeypad(BoxLayout):
    """A numeric keypad embedded at the bottom of the screen."""

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(260),
            padding=dp(6),
            spacing=dp(6),
            **kwargs
        )

        with self.canvas.before:
            Color(0.90, 0.92, 0.95, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)],
            )
        self.bind(pos=self.update_bg, size=self.update_bg)

        grid = GridLayout(
            cols=3,
            spacing=dp(5),
            size_hint_y=None,
        )
        grid.bind(minimum_height=grid.setter("height"))

        for i in range(1, 10):
            btn = Button(
                text=str(i),
                font_size=sp(20),
                bold=True,
                background_normal="",
                background_down="",
                background_color=(0.98, 0.99, 1, 1),
                color=(0.12, 0.15, 0.20, 1),
                size_hint_y=None,
                height=dp(48),
            )
            btn.bind(on_release=lambda instance, val=str(i): self.on_key(val))
            grid.add_widget(btn)

        self.decimal_btn = Button(
            text=".",
            font_size=sp(20),
            bold=True,
            background_normal="",
            background_down="",
            background_color=(0.98, 0.99, 1, 1),
            color=(0.12, 0.15, 0.20, 1),
            size_hint_y=None,
            height=dp(48),
        )
        self.decimal_btn.bind(on_release=lambda *_: self.on_key("."))
        grid.add_widget(self.decimal_btn)

        zero_btn = Button(
            text="0",
            font_size=sp(20),
            bold=True,
            background_normal="",
            background_down="",
            background_color=(0.98, 0.99, 1, 1),
            color=(0.12, 0.15, 0.20, 1),
            size_hint_y=None,
            height=dp(48),
        )
        zero_btn.bind(on_release=lambda *_: self.on_key("0"))
        grid.add_widget(zero_btn)

        backspace_btn = Button(
            text="⌫",
            font_size=sp(20),
            bold=True,
            background_normal="",
            background_down="",
            background_color=(0.82, 0.20, 0.20, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(48),
        )
        backspace_btn.bind(on_release=lambda *_: self.on_backspace())
        grid.add_widget(backspace_btn)

        self.add_widget(grid)

        enter_btn = Button(
            text="ENTER",
            font_size=sp(16),
            bold=True,
            background_normal="",
            background_down="",
            background_color=(0.08, 0.35, 0.72, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(46),
        )
        enter_btn.bind(on_release=lambda *_: self.on_enter())
        self.add_widget(enter_btn)

        self.active_input = None
        self.active_material = None
        self.active_field = None
        self.on_enter_callback = None

    def update_bg(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def set_target(self, material_name, field, text_input):
        self.active_input = text_input
        self.active_material = material_name
        self.active_field = field

        if field == "length":
            self.decimal_btn.disabled = False
            self.decimal_btn.background_color = (0.98, 0.99, 1, 1)
        else:
            self.decimal_btn.disabled = True
            self.decimal_btn.background_color = (0.80, 0.80, 0.80, 1)
            if "." in text_input.text:
                text_input.text = text_input.text.split(".")[0]

    def on_key(self, digit):
        if self.active_input is None:
            return

        current = self.active_input.text

        if digit == ".":
            if "." in current:
                return
            if not current:
                self.active_input.text = "0."
                return

        self.active_input.text = current + digit

    def on_backspace(self):
        if self.active_input is not None:
            self.active_input.text = self.active_input.text[:-1]

    def on_enter(self):
        if self.on_enter_callback:
            self.on_enter_callback(self.active_material, self.active_field)

    def on_done(self):
        self.active_input = None
        self.active_material = None
        self.active_field = None

    def clear_target(self):
        self.on_done()


# ---------------------------------------------------------------------------
# Material Card
# ---------------------------------------------------------------------------

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

        title = make_label(
            material_name,
            font_size=18,
            color=(0.08, 0.25, 0.48, 1),
            size_hint_y=None,
            height=dp(28),
        )
        title.bold = True
        self.add_widget(title)

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
            cursor_width=dp(2),
            padding=[dp(8), dp(12), dp(8), dp(8)],
        )
        self.length_input.bind(focus=self.on_length_focus)

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
            cursor_width=dp(2),
            padding=[dp(6), dp(12), dp(6), dp(8)],
        )
        self.quantity_input.bind(focus=self.on_quantity_focus)

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

        self.entries_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
        )
        self.entries_layout.bind(
            minimum_height=self.entries_layout.setter("height")
        )
        self.add_widget(self.entries_layout)

    def on_length_focus(self, instance, focused):
        if focused:
            instance.focus = False
            Window.release_all_keyboards()
            self.app_ref.keypad.set_target(
                self.material_name, "length", self.length_input
            )
            self.app_ref.set_active_input(self.length_input, self)
            self.app_ref._schedule_visible(self.length_input, self)

    def on_quantity_focus(self, instance, focused):
        if focused:
            instance.focus = False
            Window.release_all_keyboards()
            self.app_ref.keypad.set_target(
                self.material_name, "quantity", self.quantity_input
            )
            self.app_ref.set_active_input(self.quantity_input, self)
            self.app_ref._schedule_visible(self.quantity_input, self)

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

        entry = {"length": length, "quantity": quantity}
        self.saved_entries.append(entry)
        self.create_entry_row(entry)

        # Clear the inputs for the next entry.
        self.length_input.text = ""
        self.quantity_input.text = "1"

        # Keep the same material's length field active.
        self.app_ref.keypad.set_target(
            self.material_name, "length", self.length_input
        )
        self.app_ref.set_active_input(self.length_input, self)
        self.app_ref._schedule_visible(self.length_input, self)

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
            size=lambda instance, value: setattr(instance, "text_size", value)
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


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------

class AluminumCalculatorApp(App):
    def build(self):
        self.title = "Aluminum Calculator"

        self.active_input_widget = None
        self.active_card = None
        self.blink_event = None
        self.blink_visible = True
        self._scroll_event = None

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(10), dp(8), dp(10), dp(6)],
            spacing=dp(6),
        )

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(60),
            spacing=dp(2),
        )

        title = Label(
            text="ALUMINUM CALCULATOR",
            font_size=sp(21),
            bold=True,
            color=(0.06, 0.23, 0.44, 1),
            size_hint_y=None,
            height=dp(34),
        )
        subtitle = Label(
            text="Enter length in mm and quantity",
            font_size=sp(13),
            color=(0.35, 0.38, 0.43, 1),
            size_hint_y=None,
            height=dp(22),
        )
        header.add_widget(title)
        header.add_widget(subtitle)
        root.add_widget(header)

        self.scroll = ScrollView(
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

        self.scroll.add_widget(self.material_list)
        root.add_widget(self.scroll)

        calculate_button = make_button(
            "CALCULATE MATERIALS",
            (0.08, 0.35, 0.72, 1),
            font_size=16,
        )
        calculate_button.height = dp(46)
        calculate_button.bind(on_release=self.calculate)
        root.add_widget(calculate_button)

        self.keypad = BottomKeypad()
        self.keypad.on_enter_callback = self.advance_to_next_field
        root.add_widget(self.keypad)

        return root

    def on_start(self):
        Window.clearcolor = (0.94, 0.95, 0.97, 1)

    # ------------------------------------------------------------------
    # ENTER navigation
    # ------------------------------------------------------------------

    def advance_to_next_field(self, material_name, field):
        if material_name is None or field is None:
            return

        current_index = None
        for i, card in enumerate(self.material_cards):
            if card.material_name == material_name:
                current_index = i
                break

        if current_index is None:
            return

        current_card = self.material_cards[current_index]

        if field == "length":
            self._activate_field(current_card, "quantity")
        elif field == "quantity":
            next_index = (current_index + 1) % len(self.material_cards)
            self._activate_field(self.material_cards[next_index], "length")

    def _activate_field(self, card, field):
        target_input = (
            card.length_input if field == "length" else card.quantity_input
        )

        self.keypad.set_target(card.material_name, field, target_input)
        self.set_active_input(target_input, card)

        # Schedule scrolling after the input has become active.
        self._schedule_visible(target_input, card)

    # ------------------------------------------------------------------
    # Scrolling helper — corrected
    # ------------------------------------------------------------------

    def _schedule_visible(self, target_input, card):
        """Scroll to the active input after Kivy has updated its layout."""
        if self._scroll_event is not None:
            self._scroll_event.cancel()

        self._scroll_event = Clock.schedule_once(
            lambda dt: self._ensure_visible(card, target_input),
            0.20,
        )

    def _ensure_visible(self, card, target_input):
        """Keep the active input visible inside the materials ScrollView."""
        try:
            if target_input is None or card is None:
                return

            # Update the layouts before asking the ScrollView to reveal the input.
            # ScrollView itself does not provide a do_layout() method.
            self.material_list.do_layout()
            card.do_layout()

            # scroll_to() handles the ScrollView's coordinate system and scroll_y.
            self.scroll.scroll_to(
                target_input,
                padding=dp(20),
                animate=False,
            )
        except Exception as error:
            print("Scrolling error:", error)

    # ------------------------------------------------------------------
    # Active input highlight + blinking cursor
    # ------------------------------------------------------------------

    def set_active_input(self, text_input, card=None):
        self.clear_active_input()

        self.active_input_widget = text_input
        self.active_card = card
        text_input.background_color = (0.88, 0.94, 1, 1)
        text_input.cursor_color = (0.1, 0.3, 0.7, 1)

        with text_input.canvas.after:
            Color(0.10, 0.45, 0.85, 1)
            text_input._focus_border = Line(
                rounded_rectangle=(
                    text_input.x,
                    text_input.y,
                    text_input.width,
                    text_input.height,
                    dp(6),
                ),
                width=dp(2),
            )

        text_input.bind(
            pos=self._update_focus_border,
            size=self._update_focus_border,
        )

        self.blink_visible = True
        self.blink_event = Clock.schedule_interval(self._blink_cursor, 0.5)

    def _update_focus_border(self, instance, *_):
        border = getattr(instance, "_focus_border", None)
        if border is None:
            return

        border.rounded_rectangle = (
            instance.x,
            instance.y,
            instance.width,
            instance.height,
            dp(6),
        )

    def _blink_cursor(self, dt):
        widget = self.active_input_widget
        if widget is None:
            return False

        self.blink_visible = not self.blink_visible
        if self.blink_visible:
            widget.cursor_color = (0.1, 0.3, 0.7, 1)
        else:
            widget.cursor_color = (0.1, 0.3, 0.7, 0)
        return True

    def clear_active_input(self):
        if self.blink_event:
            self.blink_event.cancel()
            self.blink_event = None

        widget = self.active_input_widget
        if widget is not None:
            widget.background_color = (1, 1, 1, 1)
            widget.cursor_color = (0.1, 0.3, 0.7, 1)

            border = getattr(widget, "_focus_border", None)
            if border is not None:
                try:
                    widget.canvas.after.remove(border)
                except Exception:
                    pass
                widget._focus_border = None

            try:
                widget.unbind(
                    pos=self._update_focus_border,
                    size=self._update_focus_border,
                )
            except Exception:
                pass

        self.active_input_widget = None
        self.active_card = None

    # ------------------------------------------------------------------
    # Messages and calculation
    # ------------------------------------------------------------------

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
            size=lambda instance, value: setattr(instance, "text_size", value)
        )

        close_button = make_button("OK", (0.08, 0.35, 0.72, 1))
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
                pos=lambda instance, value: setattr(instance.bg_rect, "pos", value),
                size=lambda instance, value: setattr(instance.bg_rect, "size", value),
            )
            heading_row.add_widget(cell)

        content.add_widget(heading_row)

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
        result_grid.bind(minimum_height=result_grid.setter("height"))

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
                    size=lambda instance, size: setattr(instance, "text_size", size)
                )

                with cell.canvas.before:
                    Color(*background)
                    cell.bg_rect = RoundedRectangle(
                        pos=cell.pos,
                        size=cell.size,
                        radius=[dp(3)],
                    )

                cell.bind(
                    pos=lambda instance, value: setattr(instance.bg_rect, "pos", value),
                    size=lambda instance, value: setattr(instance.bg_rect, "size", value),
                )
                row.add_widget(cell)

            result_grid.add_widget(row)

        result_scroll.add_widget(result_grid)
        content.add_widget(result_scroll)

        close_button = make_button("CLOSE", (0.08, 0.35, 0.72, 1))
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
