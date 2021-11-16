import os
from analytical_utils.playlists import PlaylistFetcher
from analytical_utils.channels import ChannelFetcher
from analytical_utils.time_analytics import watchtime_calculator as wtc


class Analytics:
    """
    Analytics Class ~ Contains All the Routes for fetching and analyzing 
    data from Youtube Playlists, Channels & PyTrends.
    
    """

    def __init__(self, argument, target_credentials):
        self.argument = argument
        self.target_credentials = target_credentials

    def bender(self):
        def bended(part, target_credentials):
            fetch_object = PlaylistFetcher(part, target_credentials)

            return fetch_object.fetch_playlist_argument()

        if self.argument == "Watchtime":
            watchtime_details_fetched = bended(
                "contentDetails", self.target_credentials
            )
            actual_watchtime, time_list = self.watchtime_calculation(
                watchtime_details_fetched[0]
            )

            final_out_dict = {
                "total_seconds": actual_watchtime,
                "titles": watchtime_details_fetched[1],
                "times": time_list,
            }

            return final_out_dict

        elif self.argument == "PLStatistics":
            statistics_data = bended("statistics", self.target_credentials)
            return statistics_data

        elif "ChannelStats" in self.argument:
            secondary_argument = self.argument.split("-")[1]
            channel_stats = ChannelFetcher(self.target_credentials, secondary_argument)
            data_fetched = channel_stats.get_channnel_and_videos()
            return data_fetched

    def watchtime_calculation(self, watchtimes: list) -> dict:
        calculated_time_sec, minutelist = wtc(watchtimes)
        avg_vid_lgth = sum(minutelist) / len(minutelist)

        total_sec = round(calculated_time_sec, 2)
        return total_sec, minutelist
