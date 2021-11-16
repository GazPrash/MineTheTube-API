from pytrends.request import TrendReq

refer = {
    "hour": "now 1-H",
    "today": "now 1-d",
    "week": "now 7-d",
    "month": "today 1-m",
    "year": "today 12-m",
    "halfdecade": "today 5-y",
}


class Trends:
    """
    Trends Class ~ Analytical Results based on Youtube Trends,
    integrated with the PyTrends library.
    
    """
    def __init__(self, parameter) -> None:
        self.parameter_string = parameter
        self.trend_catcher = TrendReq(hl="en-US", tz=360)

    def decode_parameters(self):
        if (
            "compare=" in self.parameter_string  # trends?compare=south+park&&north+park-week
        ):  
            self.argument = "CompareTrend"
            targets, timeframe = self.parameter_string.split("-")
            target1, target2 = targets.split("=")[1].split("&&")
            self.target = (
                " ".join(target1.split("+")) + "-" + " ".join(target2.split("+"))
            )
            self.timeframe = refer[timeframe]

        elif (
            "evaltrend=" in self.parameter_string  # trends?evaltrend=rock+n+roll-halfdecade
        ): 
            self.argument = "Trend"
            target, timeframe = self.parameter_string.split("-")
            self.target = " ".join(target.split("=")[1].split("+")).lower()
            self.timeframe = refer[timeframe]

        elif "trendstoday=" in self.parameter_string:  # trends?trendstoday=None
            self.argument = "TrendsToday"

    def fetch_trends(self):
        if self.argument == "Trend":
            output_data = self.trend_data()

        elif self.argument == "CompareTrend":
            output_data = self.compare_trends()

        elif self.argument == "TrendsToday":
            output_data = self.top_trends()

        return output_data

    def trend_data(self):
        keys = [self.target]
        self.trend_catcher.build_payload(
            keys, cat="0", timeframe=self.timeframe, geo="", gprop="youtube"
        )
        fetched_data = self.trend_catcher.interest_over_time()
        fetched_data = fetched_data[self.target].to_frame()

        # fetched_data = fetched_data.astype(str)
        # fteched_json = fetched_data.to_json(date_format="iso")


        # search_freq = sorted(fetched_data[self.target].to_list())
        # low, min format : (date, relvalue)
        # peak = (search_freq[-1], fetched_data.iloc(len(search_freq) - 1))
        # low = (search_freq[0], fetched_data.iloc(0))

        fetched_data = fetched_data.to_dict()

        for key in list(fetched_data[self.target].keys()):
            new_key = str(key).split()[0]
            fetched_data[self.target][new_key] = fetched_data[self.target].pop(key)

        fetched_data["trends_data"] = fetched_data.pop(self.target)

        return fetched_data

    def compare_trends(self):
        keys = self.target.split("-")

        self.trend_catcher.build_payload(
            keys, cat="0", timeframe=self.timeframe, geo="", gprop="youtube"
        )

        fetched_data = self.trend_catcher.interest_over_time()
        print(fetched_data, keys[0], flush=True)
        target1_data = fetched_data[keys[0]].to_frame()
        target2_data = fetched_data[keys[1]].to_frame()

        target1_data = target1_data.to_dict()

        for key in list(target1_data[keys[0]].keys()):
            new_key = str(key).split()[0]
            target1_data[keys[0]][new_key] = target1_data[keys[0]].pop(key)

        target2_data = target2_data.to_dict()

        for key in list(target2_data[keys[1]].keys()):
            new_key = str(key).split()[0]
            target2_data[keys[1]][new_key] = target2_data[keys[1]].pop(key)

        target1_data["trend1"] = target1_data.pop(keys[0])
        target2_data["trend2"] = target2_data.pop(keys[1])

        final_dict = {"a": target1_data, "b": target2_data}
        
        return final_dict


    def top_trends(self):
        fetched_data = self.trend_catcher.trending_searches(pn="united_kingdom")
        final_dict = fetched_data.head(10).to_dict()

        return final_dict
