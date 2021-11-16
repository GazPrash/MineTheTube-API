from datetime import timedelta

def watchtime_calculator(watchtimes: list) -> int:
    total_seconds = 0
    minutelist = []

    hours = ""
    minutes = ""
    seconds = ""
    wordtime = ""
    useless = ""
    for watchtime in watchtimes:
        if "H" in watchtime:
            try:
                useless, wordtime = watchtime.split("PT")
                hours, wordtime = wordtime.split("H")
                minutes, seconds = wordtime.split("M")

            except Exception as e:
                new_wordtime = watchtime.split("PT")[1]
                # print(new_wordtime)
                if "M" in new_wordtime:
                    hours, minutes = new_wordtime.split("H")
                    minutes = minutes[:-1]
                    seconds = 0
                else:
                    hours, seconds = new_wordtime.split("H")
                    minutes = 0

            if hours:
                hours = int(hours)
            else:
                hours = 0
            if minutes:
                minutes = int(minutes)
            else:
                minutes = 0
            if seconds:
                seconds = int(seconds[:-1])
            else:
                seconds = 0

            var_seconds = timedelta(
                hours=hours, minutes=minutes, seconds=seconds
            ).total_seconds()

            total_seconds += var_seconds

        elif "H" not in watchtime:
            try:
                useless, wordtime = watchtime.split("PT")
                minutes, seconds = wordtime.split("M")
                # print(minutes, seconds)

            except Exception as e:
                new_wordtime = watchtime.split("PT")[1]
                if "M" in new_wordtime:
                    minutes = new_wordtime.split("M")
                    seconds = 0
                else:
                    minutes = 0
                    seconds = new_wordtime

            if minutes:
                minutes = int(minutes)
            else:
                minutes = 0
            if seconds:
                seconds = int(seconds[:-1])
            else:
                seconds = 0

            var_seconds = timedelta(minutes=minutes, seconds=seconds).total_seconds()
            total_seconds += var_seconds

        minutelist.append(round((var_seconds / 60), 2))
    return (total_seconds, minutelist)