from win10toast import ToastNotifier
from datetime import datetime, timezone, timedelta
from time import sleep
from typing import List

class Birthday(object):

	def __init__(self, name: str, date: str, tz: str, observes_ds: bool=False, location: str="") -> None:
		"""
		Passed in from load_birthdays() - parsing needed
		name: the person's name
		date: [M]M/[D]D
		tz: in the format ±HH:MM
		"""
		self.name = name

		# Zero pad date and tz strings
		date = "/".join(item.zfill(2) for item in date.split("/"))
		tz = tz.replace(":", "")

		global current_tz
		global now
		global observing_ds

		# Set datetime object, with DST in mind
		self.date = datetime.strptime(date + f"/{now.year} " + tz, "%m/%d/%Y %z")
		if observing_ds and observes_ds:
			offset = str(self.date.tzinfo)
			if offset == "UTC":
				offset = "UTC+00:00"
			hours = int(offset[4:6])
			minutes = int(offset[7:9])
			offset_td = timedelta(hours=hours, minutes=minutes)
			if offset[3] == "-":
				offset_td = -offset_td
			self.date = self.date.replace(tzinfo=timezone(offset_td + timedelta(hours=1)))

		# Edit year of date: set to next year if birthday passed this year already
		# A birthday count as passed if the entire day has passed
		# (If birthday is today, it hasn't passed)
		if now.month > self.date.month or now.month == self.date.month and now.day > self.date.day:
			self.date = self.date.replace(year=now.year+1)

		self.location = location

	def __repr__(self) -> str:
		date = datetime.strftime(self.date, "%m/%d/%Y")
		tz = datetime.strftime(self.date, "%z")
		tz = tz[:3] + ":" + tz[3:] # Insert colon
		return f"Birthday('{self.name}', '{date}', '{tz}', '{self.location}')"

	def date_string(self) -> str:
		date = datetime.strftime(self.date, "%m/%d")
		tz = datetime.strftime(self.date, "%z")
		tz = tz[:3] + ":" + tz[3:] # Insert colon
		return date + " UTC" + tz

def load_birthdays(print_load_text=True) -> List[Birthday]:

	birthdays = []

	# Used to determine if world is currently observing daylight savings; initialized in loop
	# Stored as datetime objects
	ds_start = None
	ds_end = None

	global current_tz
	global now
	global observing_ds

	with open("birthdays.txt", "r") as file:
		for line in file:

			# Blank lines or comments
			if line.isspace() or line[0] == "#":
				continue

			# Initialize current_tz, ds_start, ds_end
			if line[0] == "~":

				# current_tz
				if "Current" in line:

					offset = line[line.index(":")+1:].strip()
					hours = int(offset[1:offset.index(":")])
					minutes = int(offset[offset.index(":")+1:])

					offset_td = timedelta(hours=hours, minutes=minutes)
					# Sign (behind/ahead of UTC)
					if offset[0] == "-":
						offset_td = -offset_td

					current_tz = timezone(offset_td)

					print("Initialized current time zone STANDARD offset:", current_tz)

					# Initialize now
					now = datetime.now(current_tz)

					print("Initialized current time based on STANDARD offset:", now)

				# ds_start
				elif "Start" in line:
					
					start_string = line[line.index(":")+1:].strip()
					start_string = start_string[:start_string.index(" ")] + f"/{now.year} " + start_string[start_string.index(" ")+1:]
					ds_start = datetime.strptime(start_string, "%m/%d/%Y %H:%M").replace(tzinfo=current_tz) # Convert naive to aware
					print("Daylight savings recorded to start at:", ds_start)

				elif "End" in line:
					
					end_string = line[line.index(":")+1:].strip()
					end_string = end_string[:end_string.index(" ")] + f"/{now.year} " + end_string[end_string.index(" ")+1:]
					ds_end = datetime.strptime(end_string, "%m/%d/%Y %H:%M").replace(tzinfo=current_tz) # Convert naive to aware
					print("Daylight savings recorded to end at:", ds_end)

					# Determine if world is currently observing daylight savings
					if ds_start < now < ds_end:
						print("[DS Detection] World OBSERVING daylight savings at time of now")
						# Roll clocks ahead 1 hour
						current_tz = timezone(offset_td + timedelta(hours=1))
						now = now.replace(tzinfo=current_tz)
						now += timedelta(hours=1)
						observing_ds = True
						print("Current time zone offset changed to:", current_tz)
						print("Current time changed to:", now)

					else:
						print("[DS Detection] World NOT observing daylight savings at time of now")
						observing_ds = False

				continue

			name = line.strip()[:line.index(":")] # Omit colon
			components = line[line.index(":")+1:].strip().split()
			date = components[0]
			tz = components[1]
			observes_ds = components[2]
			try:
				location = " ".join(components[3:])
			except IndexError: # location not filled
				location = ""

			if print_load_text:
				print("Loading birthday from file:", name, date, tz, observes_ds, location)
			birthdays.append(Birthday(name, date, tz, observes_ds == "y", location))

	print("\nSuccessfully loaded birthdays:")
	print("[" + "\n ".join(str(birthday) for birthday in birthdays) + "]\n")

	return birthdays

def await_birthday(birthdays: List[Birthday]) -> None:
	
	global now

	# Store birthdays for which notifications have already been sent in current session
	# In order to not send repeated notifications when program refreshes
	cleared_birthdays = []

	while True:

		for birthday in birthdays:
			if birthday in cleared_birthdays:
				continue
			if now.day == birthday.date.day and now > birthday.date:
				show_toast(birthday)
				print(f"Toast notification sent for {birthday}\n")
				cleared_birthdays.append(birthday)

		print("Notification already sent for birthdays:", [birthday.name for birthday in cleared_birthdays])
		print("No other birthdays detected, sleeping for 30 seconds...")

		# Refresh data every 30 seconds
		sleep(30)
		print("Reloading data:\n")
		load_birthdays(print_load_text=False)

def show_toast(birthday: Birthday) -> None:

	toaster = ToastNotifier()

	# "Foo Bar's" vs "Foo Bars'"
	if birthday.name[-1].lower() == "s":
		possessive = birthday.name + "'"
	else:
		possessive = birthday.name + "'s"

	toaster.show_toast(title=f"It's {possessive} birthday!",
					   msg=f"{birthday.date_string()} // {birthday.location}",
					   icon_path="birthday_cake.ico",
					   duration=10,
					   threaded=True)

def main() -> None:

	# To store a timedelta object; initialized in load_birthdays()
	current_tz = None
	# For consistency purpose, find current time on startup and have all calculations use that
	# Initialized in load_birthdays() as current_tz is needed
	now = None
	observing_ds = None

	birthdays = load_birthdays()

	await_birthday(birthdays)
	
if __name__ == "__main__":
	main()