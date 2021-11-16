from analytical_utils.channels import ChannelFetcher
from trends import Trends


class TuberVersus:
    """
    TuberVersus Class ~ Use it to compare two youtubers
    against each other.
    
    """

    def __init__(self, parameter) -> None:
        self.parameter = parameter

    def decode_parameters(self):
        self.arg1, self.arg2 = self.parameter.split("&&")
        self.arg1 = "".join(self.arg1.split("+"))
        self.arg2 = "".join(self.arg2.split("+"))

    def fetch_stats(self):
        output_stats1 = []
        output_stats2 = []

        channel_obj1 = ChannelFetcher(self.arg1, "statistical")
        output_stats1 = channel_obj1.get_channnel_and_videos()
        channel_obj2 = ChannelFetcher(self.arg2, "statistical")
        output_stats2 = channel_obj2.get_channnel_and_videos()

        trends_obj = Trends(f"compare={self.arg1.lower()}&&{self.arg2.lower()}-year")
        trends_obj.decode_parameters()

        trend_stats = trends_obj.compare_trends()

        all_time_earnings1 = channel_obj1.view_count_all_time * (2.25 / (10 ** 3))
        all_time_earnings2 = channel_obj2.view_count_all_time * (2.25 / (10 ** 3))

        final_dict = {
            "chan1": {
                "all_time": channel_obj1.view_count_all_time,
                "sub_views_ratio": output_stats1["ratio"],
                "sub_count": channel_obj1.sub_count,
                "views_last50": output_stats1["views"],
                "avg_lifetime_earnings": all_time_earnings1,
                "last_50views": output_stats1["last_50views"],
                "titles": output_stats1["titles"],
            },
            "chan2": {
                "all_time": channel_obj2.view_count_all_time,
                "sub_views_ratio": output_stats2["ratio"],
                "sub_count": channel_obj2.sub_count,
                "views_last50": output_stats2["views"],
                "avg_lifetime_earnings": all_time_earnings2,
                "last_50views": output_stats2["last_50views"],
                "titles": output_stats2["titles"],
            },
            "trend_stats": trend_stats,
        }

        return final_dict
