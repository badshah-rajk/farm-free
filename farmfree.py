import customtkinter as ctk
import requests
import geocoder
import threading

# ---------------- CONFIG ---------------- #
API_KEY = ""

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ---------------- APP CLASS ---------------- #
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("380x680")
        self.minsize(320, 600)
        self.title("Smart Farming Assistant")

        # Responsive grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_splash()

    # -------- SPLASH SCREEN -------- #
    def show_splash(self):
        self.splash = SplashScreen(self)
        self.splash.grid(row=0, column=0, sticky="nsew")

        self.after(2500, self.load_main)

    def load_main(self):
        self.splash.destroy()
        self.main = MainUI(self)
        self.main.grid(row=0, column=0, sticky="nsew")


# ---------------- SPLASH SCREEN ---------------- #
class SplashScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.configure(fg_color="#0f2b1d")

        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Logo
        self.logo = ctk.CTkLabel(
            self,
            text="🌱",
            font=("SF Pro Display", 64)
        )
        self.logo.grid(row=0, column=0)

        # Title
        self.title = ctk.CTkLabel(
            self,
            text="Smart Farming Assistant",
            font=("SF Pro Display", 20, "bold")
        )
        self.title.grid(row=1, column=0)

        # Loading bar
        self.progress = ctk.CTkProgressBar(self, width=200)
        self.progress.grid(row=2, column=0, pady=20)
        self.progress.set(0)

        self.animate()

    def animate(self):
        # Smooth loading animation
        for i in range(100):
            self.after(i * 20, lambda v=i: self.progress.set(v / 100))


# ---------------- MAIN UI ---------------- #
class MainUI(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, fg_color="#1f6f43", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")

        self.title = ctk.CTkLabel(
            self.header,
            text="🌱 Smart Farming",
            font=("SF Pro Display", 18, "bold"),
            text_color="white"
        )
        self.title.pack(pady=15)

        # Input Section
        self.input_frame = ctk.CTkFrame(self, corner_radius=20)
        self.input_frame.grid(row=1, column=0, padx=16, pady=16, sticky="ew")

        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter village...",
            height=45,
            corner_radius=15
        )
        self.entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry.focus()

        # Buttons
        self.btn_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.btn_frame.grid(row=1, column=0, pady=10)

        self.search_btn = ctk.CTkButton(
            self.btn_frame,
            text="Check",
            command=self.get_weather,
            corner_radius=15
        )
        self.search_btn.grid(row=0, column=0, padx=5)

        self.loc_btn = ctk.CTkButton(
            self.btn_frame,
            text="📍",
            width=40,
            command=self.use_location,
            corner_radius=15
        )
        self.loc_btn.grid(row=0, column=1, padx=5)

        # Status
        self.status = ctk.CTkLabel(self, text="", font=("SF Pro Display", 12))
        self.status.grid(row=2, column=0)

        # Results
        self.results = ctk.CTkFrame(self, fg_color="transparent")
        self.results.grid(row=3, column=0, sticky="nsew", padx=16)

        self.results.grid_columnconfigure(0, weight=1)

        self.rain = self.create_card("Rain Likely", "🌧")
        self.irrigate = self.create_card("Irrigation", "💧")
        self.spray = self.create_card("Spray Safe", "🧪")

        self.details = ctk.CTkLabel(
            self.results,
            text="",
            font=("SF Pro Display", 12)
        )
        self.details.pack(pady=10)

    # -------- CARD COMPONENT -------- #
    def create_card(self, title, icon):
        card = ctk.CTkFrame(self.results, corner_radius=18)
        card.pack(fill="x", pady=8)

        label = ctk.CTkLabel(
            card,
            text=f"{icon} {title}",
            font=("SF Pro Display", 14)
        )
        label.pack(pady=(10, 0))

        value = ctk.CTkLabel(
            card,
            text="-",
            font=("SF Pro Display", 24, "bold")
        )
        value.pack(pady=(0, 10))

        return value

    # -------- UX HELPERS -------- #
    def show_status(self, msg, color="white"):
        self.status.configure(text=msg, text_color=color)

    def set_loading(self, loading=True):
        state = "disabled" if loading else "normal"
        self.search_btn.configure(state=state)
        self.loc_btn.configure(state=state)

    # -------- WEATHER LOGIC -------- #
    def get_weather(self):
        threading.Thread(target=self._get_weather).start()

    def _get_weather(self):
        self.set_loading(True)
        self.show_status("Fetching weather...", "yellow")

        village = self.entry.get().strip()

        if not village:
            self.show_status("Enter a village", "red")
            self.set_loading(False)
            return

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={village}&appid={API_KEY}&units=metric"
            data = requests.get(url).json()

            if data.get("cod") != 200:
                self.show_status("Not found", "red")
                self.set_loading(False)
                return

            self.update_results(data)

        except:
            self.show_status("Network error", "red")

        self.set_loading(False)

    def use_location(self):
        threading.Thread(target=self._use_location).start()

    def _use_location(self):
        self.set_loading(True)
        self.show_status("Getting location...", "yellow")

        try:
            g = geocoder.ip('me')
            lat, lon = g.latlng

            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
            data = requests.get(url).json()

            self.entry.delete(0, "end")
            self.entry.insert(0, data["name"])

            self.update_results(data)

        except:
            self.show_status("Location error", "red")

        self.set_loading(False)

    # -------- RESULT ANIMATION -------- #
    def animate_value(self, label, text, color):
        label.configure(text="", text_color=color)

        for i in range(len(text) + 1):
            self.after(i * 20, lambda t=text[:i]: label.configure(text=t))

    def update_results(self, data):
        self.show_status(f"{data['name']}", "green")

        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"] * 3.6
        clouds = data["clouds"]["all"]

        rain_chance = (humidity + clouds) / 2

        rain = "YES 🌧" if rain_chance > 60 else "NO ☀️"
        irrigate = "YES 💧" if (rain_chance < 40 and humidity < 70) else "NO 🌱"
        spray = "YES 🧪" if (rain_chance < 50 and wind < 15) else "NO 🌬"

        self.animate_value(self.rain, rain, "green" if "YES" in rain else "red")
        self.animate_value(self.irrigate, irrigate, "green" if "YES" in irrigate else "red")
        self.animate_value(self.spray, spray, "green" if "YES" in spray else "red")

        self.details.configure(
            text=f"Humidity: {humidity}%   Wind: {wind:.1f} km/h"
        )


# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app = App()
    app.mainloop()
