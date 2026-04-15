import random
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk


WINDOW_TITLE = "Fortune Cookie Birthday Oracle"
YEAR_MIN = 1920
YEAR_MAX = 2050


def build_day_messages():
	themes = [
		"luck", "focus", "joy", "energy", "clarity", "courage", "timing", "curiosity",
		"calm", "ideas", "growth", "gratitude", "humor", "balance", "wisdom", "kindness",
	]
	actions = [
		"opens doors", "attracts opportunities", "wins quiet battles", "turns obstacles into shortcuts",
		"makes people notice your sparkle", "brings a surprise win", "keeps you one step ahead",
		"creates perfect timing", "pulls in helpful allies", "makes your plan click",
	]

	messages = {}
	for day in range(1, 32):
		theme = themes[(day - 1) % len(themes)]
		action = actions[(day * 3) % len(actions)]
		messages[day] = [
			f"Day {day}: Your {theme} {action}.",
			f"Day {day}: A tiny risk today unlocks a big reward tomorrow.",
			f"Day {day}: Fortune says your best decision arrives right after coffee.",
			f"Day {day}: The universe bookmarks today for a cheerful surprise.",
		]
	return messages


def build_month_messages():
	month_names = [
		"January", "February", "March", "April", "May", "June",
		"July", "August", "September", "October", "November", "December",
	]
	vibes = [
		"fresh starts", "bold moves", "quiet confidence", "creative sparks", "steady momentum", "brave choices",
		"sunny surprises", "magnetic charm", "smart pivots", "deep insights", "lucky meetings", "happy endings",
	]

	messages = {}
	for month in range(1, 13):
		name = month_names[month - 1]
		vibe = vibes[month - 1]
		messages[month] = [
			f"{name}: You carry {vibe} wherever you go.",
			f"{name}: The next meaningful 'yes' will be worth the wait.",
			f"{name}: Your calendar hides one unexpectedly perfect moment.",
			f"{name}: Good news likes your timing this season.",
		]
	return messages


def build_year_messages(start=YEAR_MIN, end=YEAR_MAX):
	traits = [
		"trailblazer", "strategist", "dreamer", "fixer", "connector", "innovator", "peacemaker", "problem-solver",
		"builder", "explorer", "optimizer", "storyteller", "visionary", "mentor", "architect", "spark",
	]
	rewards = [
		"big opportunities", "surprising support", "great timing", "strong momentum", "new confidence",
		"clever ideas", "happy coincidences", "quiet victories", "lasting impact", "fresh perspectives",
	]

	messages = {}
	for year in range(start, end + 1):
		trait = traits[(year - start) % len(traits)]
		reward = rewards[(year * 7) % len(rewards)]
		messages[year] = [
			f"Year {year}: You are a natural {trait} headed toward {reward}.",
			f"Year {year}: Your patience compounds into luck faster than expected.",
			f"Year {year}: Fortune predicts a plot twist in your favor.",
			f"Year {year}: Your story is setting up an unexpectedly satisfying win.",
		]
	return messages


DAY_MESSAGES = build_day_messages()
MONTH_MESSAGES = build_month_messages()
YEAR_MESSAGES = build_year_messages()


def funny_age_message(year):
	current_year = date.today().year
	age = current_year - year

	if age < 0:
		return f"Year {year}? Wow, time traveler alert. Please share future stock tips from {abs(age)} years ahead."
	if age <= 5:
		return f"Year {year}? At age {age}, your fortune is mostly cookies and cartoons."
	if age >= 120:
		return f"Year {year}? At age {age}, you deserve a museum wing and unlimited snacks."
	return f"Year {year}? At age {age}, your back may crackle, but your luck is still premium."


def validate_birth_date(day, month, year):
	try:
		validated_date = date(year, month, day)
	except ValueError as exc:
		raise ValueError("Please enter a real calendar date.") from exc
	return validated_date


def get_fortune_bundle(day, month, year):
	validate_birth_date(day, month, year)

	fortunes = {
		"day": random.choice(DAY_MESSAGES[day]),
		"month": random.choice(MONTH_MESSAGES[month]),
	}

	if YEAR_MIN <= year <= YEAR_MAX:
		fortunes["year"] = random.choice(YEAR_MESSAGES[year])
	else:
		fortunes["year"] = funny_age_message(year)

	return fortunes


def random_valid_birth_date():
	year = random.randint(YEAR_MIN, YEAR_MAX)
	month = random.randint(1, 12)

	while True:
		day = random.randint(1, 31)
		try:
			validate_birth_date(day, month, year)
		except ValueError:
			continue
		return day, month, year


class FortuneCookieApp:
	def __init__(self, root):
		self.root = root
		self.root.title(WINDOW_TITLE)
		self.root.geometry("820x620")
		self.root.minsize(760, 560)
		self.root.configure(bg="#1B1336")

		self.day_var = tk.StringVar()
		self.month_var = tk.StringVar()
		self.year_var = tk.StringVar()
		self.status_var = tk.StringVar(value="Enter your birthday and crack open your fortune ✨")
		self.summary_var = tk.StringVar(value="No fortune yet — your cookie is warming up.")

		self._build_style()
		self._build_layout()
		self.root.bind("<Return>", lambda event: self.show_fortune())
		self.root.bind("<Escape>", lambda event: self.clear_form())

	def _build_style(self):
		style = ttk.Style(self.root)
		style.theme_use("clam")
		style.configure("Card.TFrame", background="#24174A")
		style.configure("Panel.TFrame", background="#30205E")
		style.configure("Title.TLabel", background="#24174A", foreground="#FFF5C3", font=("Segoe UI", 24, "bold"))
		style.configure("Subtitle.TLabel", background="#24174A", foreground="#D7CEFF", font=("Segoe UI", 11))
		style.configure("Section.TLabel", background="#30205E", foreground="#FFE8A3", font=("Segoe UI", 12, "bold"))
		style.configure("Body.TLabel", background="#30205E", foreground="#F6F0FF", font=("Segoe UI", 10))
		style.configure("Status.TLabel", background="#24174A", foreground="#8EF6D2", font=("Segoe UI", 11, "italic"))
		style.configure("FortuneTitle.TLabel", background="#3A2774", foreground="#FFE8A3", font=("Segoe UI", 12, "bold"))
		style.configure("FortuneBody.TLabel", background="#3A2774", foreground="#FFFFFF", font=("Segoe UI", 11), wraplength=620)
		style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
		style.map("TButton", background=[("active", "#FFD76E")])
		style.configure("TEntry", padding=7)

	def _build_layout(self):
		outer = ttk.Frame(self.root, style="Card.TFrame", padding=20)
		outer.pack(fill="both", expand=True)

		header = ttk.Frame(outer, style="Card.TFrame")
		header.pack(fill="x", pady=(0, 18))

		ttk.Label(header, text="🥠 Fortune Cookie Birthday Oracle", style="Title.TLabel").pack(anchor="w")
		ttk.Label(
			header,
			text="A playful birthday-powered fortune app with jokes, surprises, and instant feedback.",
			style="Subtitle.TLabel",
		).pack(anchor="w", pady=(4, 0))

		content = ttk.Frame(outer, style="Card.TFrame")
		content.pack(fill="both", expand=True)
		content.columnconfigure(0, weight=2)
		content.columnconfigure(1, weight=3)

		self._build_input_panel(content)
		self._build_output_panel(content)

		footer = ttk.Label(outer, textvariable=self.status_var, style="Status.TLabel")
		footer.pack(anchor="w", pady=(14, 0))

	def _build_input_panel(self, parent):
		panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
		panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
		panel.columnconfigure(1, weight=1)

		ttk.Label(panel, text="Your birthday", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
		ttk.Label(panel, text="Pick a valid date or tap Surprise Me for a lucky random one.", style="Body.TLabel").grid(
			row=1, column=0, columnspan=2, sticky="w", pady=(6, 18)
		)

		self._add_input_row(panel, 2, "Day", self.day_var, "1-31")
		self._add_input_row(panel, 3, "Month", self.month_var, "1-12")
		self._add_input_row(panel, 4, "Year", self.year_var, "1920-2050 or beyond")

		button_bar = ttk.Frame(panel, style="Panel.TFrame")
		button_bar.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(18, 14))
		for column_index in range(3):
			button_bar.columnconfigure(column_index, weight=1)

		ttk.Button(button_bar, text="🔮 Reveal Fortune", command=self.show_fortune).grid(row=0, column=0, padx=(0, 8), sticky="ew")
		ttk.Button(button_bar, text="🎲 Surprise Me", command=self.surprise_me).grid(row=0, column=1, padx=4, sticky="ew")
		ttk.Button(button_bar, text="🧹 Clear", command=self.clear_form).grid(row=0, column=2, padx=(8, 0), sticky="ew")

		tips = (
			"Tips\n"
			"• Press Enter to reveal your fortune.\n"
			"• Press Esc to clear the form.\n"
			"• Years outside 1920-2050 unlock a funny age joke."
		)
		ttk.Label(panel, text=tips, style="Body.TLabel", justify="left").grid(row=6, column=0, columnspan=2, sticky="w")

	def _build_output_panel(self, parent):
		panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
		panel.grid(row=0, column=1, sticky="nsew")
		panel.columnconfigure(0, weight=1)

		ttk.Label(panel, text="Your cosmic cookie says...", style="Section.TLabel").grid(row=0, column=0, sticky="w")
		ttk.Label(panel, textvariable=self.summary_var, style="Body.TLabel", wraplength=460).grid(
			row=1, column=0, sticky="w", pady=(6, 18)
		)

		self.day_label = self._fortune_card(panel, 2, "📅 Day Message")
		self.month_label = self._fortune_card(panel, 3, "🌙 Month Message")
		self.year_label = self._fortune_card(panel, 4, "🎉 Year Message")

	def _fortune_card(self, parent, row_index, title):
		card = ttk.Frame(parent, style="Card.TFrame", padding=14)
		card.grid(row=row_index, column=0, sticky="ew", pady=(0, 12))
		card.columnconfigure(0, weight=1)
		card.configure(style="Card.TFrame")

		inner = tk.Frame(card, bg="#3A2774", bd=0, highlightthickness=0)
		inner.pack(fill="x", expand=True)

		ttk.Label(inner, text=title, style="FortuneTitle.TLabel").pack(anchor="w", padx=12, pady=(12, 4))
		label = ttk.Label(inner, text="Waiting for your birthday...", style="FortuneBody.TLabel", justify="left")
		label.pack(anchor="w", fill="x", padx=12, pady=(0, 12))
		return label

	def _add_input_row(self, parent, row_index, label, variable, hint):
		ttk.Label(parent, text=label, style="Body.TLabel").grid(row=row_index, column=0, sticky="w", pady=6)
		entry = ttk.Entry(parent, textvariable=variable, width=20)
		entry.grid(row=row_index, column=1, sticky="ew", pady=6)
		entry.insert(0, "")
		entry.bind("<FocusIn>", lambda event, text=hint: self.status_var.set(f"Enter {label.lower()} ({text})."))

	def _read_inputs(self):
		values = {
			"day": self.day_var.get().strip(),
			"month": self.month_var.get().strip(),
			"year": self.year_var.get().strip(),
		}

		if not all(values.values()):
			raise ValueError("Please fill in day, month, and year.")

		try:
			day = int(values["day"])
			month = int(values["month"])
			year = int(values["year"])
		except ValueError as exc:
			raise ValueError("Birth details must be numbers only.") from exc

		validate_birth_date(day, month, year)
		return day, month, year

	def show_fortune(self):
		try:
			day, month, year = self._read_inputs()
			fortunes = get_fortune_bundle(day, month, year)
		except ValueError as exc:
			self.status_var.set(str(exc))
			messagebox.showwarning("Invalid birthday", str(exc))
			return

		self.day_label.config(text=fortunes["day"])
		self.month_label.config(text=fortunes["month"])
		self.year_label.config(text=fortunes["year"])

		if YEAR_MIN <= year <= YEAR_MAX:
			summary = f"Birthday decoded for {day:02d}/{month:02d}/{year} — three fresh fortunes served."
		else:
			summary = f"Birthday decoded for {day:02d}/{month:02d}/{year} — plus a bonus age joke."

		self.summary_var.set(summary)
		self.status_var.set("Fortune served hot. Try another birthday for a new spin ✨")

	def surprise_me(self):
		day, month, year = random_valid_birth_date()
		self.day_var.set(str(day))
		self.month_var.set(str(month))
		self.year_var.set(str(year))
		self.status_var.set("Lucky date loaded. Hit Reveal Fortune or press Enter.")
		self.show_fortune()

	def clear_form(self):
		self.day_var.set("")
		self.month_var.set("")
		self.year_var.set("")
		self.day_label.config(text="Waiting for your birthday...")
		self.month_label.config(text="The month message will appear here.")
		self.year_label.config(text="The year message will appear here.")
		self.summary_var.set("No fortune yet — your cookie is warming up.")
		self.status_var.set("All clear. Enter a birthday when you are ready.")


def main():
	root = tk.Tk()
	app = FortuneCookieApp(root)
	app.clear_form()
	root.mainloop()


if __name__ == "__main__":
	main()