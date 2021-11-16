from typing import final
from googleapiclient.discovery import build
from other import credentials_and_secrets as creds
from datetime import datetime, date
from .time_analytics import watchtime_calculator as wtc
from trends import Trends


API = creds.api
API_VER = creds.api_version
DEV_KEY = creds.dev_key


class ChannelFetcher:
    def __init__(self, argument, objective):
        self.argument = argument
        self.objective = objective
        self.build_youtube = build(API, API_VER, developerKey=DEV_KEY)

    def get_channnel_and_videos(self):
        if "channel/" not in self.argument:
            if "c/" not in self.argument:
                search_keyword = self.argument
            else:
                search_keyword = self.argument.split("c/")[1]

            print(search_keyword, flush=True)

            search_request = (
                self.build_youtube.search()
                .list(
                    part="snippet",
                    q=search_keyword,
                    maxResults=1,
                    type="channel",
                )
                .execute()
            )

            channel_info_item = search_request["items"].pop()
            self.channel_id = channel_info_item["id"]["channelId"]

        else:
            self.channel_id = self.argument.split("channel/")[1]

        channel_request = (
            self.build_youtube.channels()
            .list(
                id=self.channel_id,
                part="contentDetails, statistics",
            )
            .execute()
        )

        self.sub_count = int(
            channel_request["items"][0]["statistics"]["subscriberCount"]
        )
        self.view_count_all_time = int(
            channel_request["items"][0]["statistics"]["viewCount"]
        )

        last50_date_range = date.today().strftime("%Y-%m-%d").split("-")
        last50_before_date = (
            str(
                datetime(
                    year=int(last50_date_range[0]),
                    month=int(last50_date_range[1]),
                    day=int(last50_date_range[2]),
                ).isoformat()
            )
            + "Z"
        )

        last50_after_date = (
            str(
                datetime(
                    year=int(last50_date_range[0]) - 1,
                    month=int(last50_date_range[1]),
                    day=int(last50_date_range[2]),
                ).isoformat()
            )
            + "Z"
        )

        year_highlight_request = (
            self.build_youtube.search()
            .list(
                part="snippet",
                channelId=self.channel_id,
                publishedBefore=last50_before_date,
                publishedAfter=last50_after_date,
                maxResults=50,
                type="video",
            )
            .execute()
        )

        self.year_highlight_vids = []
        self.publish_dates = []

        for item in year_highlight_request["items"]:
            self.year_highlight_vids.append(item["id"]["videoId"])
            self.publish_dates.append(item["snippet"]["publishedAt"])

        # gives id of top_uploads playlist, arranged in date of order.
        top_uploads_id = channel_request["items"][0]["contentDetails"][
            "relatedPlaylists"
        ]["uploads"]

        self.list_videos = []

        playlist_response = (
            self.build_youtube.playlistItems()
            .list(
                part="contentDetails, id, snippet",
                playlistId=top_uploads_id,
                maxResults=50,
            )
            .execute()
        )
        for vid in playlist_response["items"]:
            self.list_videos.append(vid["contentDetails"]["videoId"])

        if self.objective == "upload_times":
            return self.time_analysis()
        elif self.objective == "statistical":
            trend_obj = Trends(f"evaltrend={self.argument.lower()}-year")
            trend_obj.decode_parameters()
            trend_obj_data = trend_obj.fetch_trends()
            final_dict = self.statistical_analysis()
            final_dict.update(trend_obj_data)
            return final_dict
        elif self.objective == "monetization":
            return self.monetization_analysis()
        elif self.objective == "content_length":
            return self.content_length_analysis()

    def time_analysis(self) -> list:
        time_data = []
        for data in self.publish_dates:
            readable_data = datetime.strptime(data, "%Y-%m-%dT%H:%M:%SZ")
            time_data.append(int(readable_data.hour))

        freq_data = []
        time_data.sort()
        for time in time_data:
            freq_data.append(time_data.count(time))
        final_dict = {"freq_data": freq_data}

        return final_dict

    def statistical_analysis(self) -> tuple:
        likes = 0
        dislikes = 0
        comments = 0
        views = 0

        stats_request = (
            self.build_youtube.videos()
            .list(part="statistics, snippet", id=",".join(self.list_videos))
            .execute()
        )

        pastyear_stats = (
            self.build_youtube.videos()
            .list(part="statistics, snippet", id=",".join(self.year_highlight_vids))
            .execute()
        )

        last_50views = []
        vid_titles = []

        for data in pastyear_stats["items"]:
            last_50views.append(data["statistics"]["viewCount"])
            vid_titles.append(data["snippet"]["title"])


        for data in stats_request["items"]:
            try:
                likes += int(data["statistics"]["likeCount"])
                dislikes += int(data["statistics"]["dislikeCount"])
                comments += int(data["statistics"]["commentCount"])
                views += int(data["statistics"]["viewCount"])

            except Exception:
                pass

        sub_views_ratio = self.sub_count / views
        all_time_views = self.view_count_all_time

        final_dict = {
            "views": views,
            "likes": likes,
            "dislikes": dislikes,
            "comments": comments,
            "ratio": sub_views_ratio,
            "all_time": all_time_views,
            "last_50views": last_50views,
            "titles": vid_titles,
        }

        return final_dict

    def monetization_analysis(self) -> tuple:
        summed_views = 0
        views = []

        stats_request = (
            self.build_youtube.videos()
            .list(part="statistics", id=",".join(self.year_highlight_vids))
            .execute()
        )

        for data in stats_request["items"]:
            count = data["statistics"]["viewCount"]
            if count.isdigit():
                summed_views += int(count)
                views.append(count)

        if summed_views == 0 or views == []:
            final_dict = {
                "min_est": "No recent records are available",
                "max_est": "No recent records are available",
                "avg_est": "No recent records are available",
                "life_est": "No recent records are available",
                "views": "No recent records are available",
            }
            
            return final_dict

        if summed_views:
            try:
                monetization_std = (0.25, 4, 2.25)  # per 1000 views
                min_estimate = round(summed_views * (monetization_std[0] / (10 ** 3)), 2)
                max_estimate = round(summed_views * (monetization_std[1] / (10 ** 3)), 2)
                avg_estimate = round(summed_views * (monetization_std[2] / (10 ** 3)), 2)
                life_estimate = round(
                    self.view_count_all_time * (monetization_std[2] / (10 ** 3)), 2
                )

                min_estimate_val = "${:,.2f}".format(min_estimate)
                max_estimate_val = "${:,.2f}".format(max_estimate)
                avg_estimate_val = "${:,.2f}".format(avg_estimate)
                life_estimate_val = "${:,.2f}".format(life_estimate)

                # based on the past year's statistics
                final_dict = {
                    "min_est": min_estimate_val,
                    "max_est": max_estimate_val,
                    "avg_est": avg_estimate_val,
                    "life_est": life_estimate_val,
                    "views": views,
                }

                return final_dict

            except Exception:
                return 'Error'

    def content_length_analysis(self) -> int:
        times = []
        upload_style = 0

        request_videos = (
            self.build_youtube.videos()
            .list(part="contentDetails", id=",".join(self.year_highlight_vids))
            .execute()
        )

        for item in request_videos["items"]:
            times.append(item["contentDetails"]["duration"])


        output_content = wtc(times)
        times_in_min = output_content[1]

        try:
            mean_upload_time = round(
                sum(times_in_min) / len(times_in_min), 2
            )  # in minutes
        except Exception:
            mean_upload_time = "Error"

        if mean_upload_time < 2:
            upload_style = "Shorts (or Memes) Creator"
        elif mean_upload_time > 2 and mean_upload_time < 5:
            upload_style = "Short - Medium Content Creator"
        elif mean_upload_time > 10 and mean_upload_time < 15:
            upload_style = "Your Average Content Creator"
        elif mean_upload_time > 15 and mean_upload_time < 30:
            upload_style = "Medium-Lengthy Content Creator"
        elif mean_upload_time > 30:
            upload_style = "Beefy Content Creator"

        final_dict = {
            "mean_time": mean_upload_time,
            "up_style": upload_style,
            "times": times_in_min,
        }
        return final_dict
