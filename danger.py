import random
from datetime import date


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
		]
	return messages


def build_year_messages(start=1920, end=2050):
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


def get_int(prompt):
	while True:
		raw = input(prompt).strip()
		try:
			return int(raw)
		except ValueError:
			print("Please enter a valid number.")


def main():
	print("=== Fortune Cookie by Date of Birth ===")
	day = get_int("Enter birth day (1-31): ")
	month = get_int("Enter birth month (1-12): ")
	year = get_int("Enter birth year: ")

	try:
		date(year, month, day)
	except ValueError:
		print("That date is not valid. Please run again with a real calendar date.")
		return

	print("\nYour fortune cookie messages:")
	print(random.choice(DAY_MESSAGES[day]))
	print(random.choice(MONTH_MESSAGES[month]))

	if 1920 <= year <= 2050:
		print(random.choice(YEAR_MESSAGES[year]))
	else:
		print(funny_age_message(year))


if __name__ == "__main__":
	main()