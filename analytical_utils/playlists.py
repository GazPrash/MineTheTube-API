from googleapiclient.discovery import build
from other import credentials_and_secrets as creds


API = creds.api
API_VER = creds.api_version
DEV_KEY = creds.dev_key


class PlaylistFetcher:
    def __init__(self, part, target_credentials):
        self.part = part
        self.target_credentials = str(target_credentials.split("list=")[1])
        self.max_results = 50

        self.build_youtube = build(API, API_VER, developerKey=DEV_KEY)

    def fetch_playlist_argument(self):
        page_token = None

        time_total = []  # For Watchtime calculation

        title_total = []
        view_total = []
        like_total = []
        dislike_total = []
        comment_total = []

        while True:
            received_playlist = (
                self.build_youtube.playlistItems()
                .list(
                    part="contentDetails",
                    playlistId=self.target_credentials,
                    maxResults=self.max_results,
                    pageToken=page_token,
                )
                .execute()
            )

            video_stacker = []
            for element in received_playlist["items"]:
                video_stacker.append(element["contentDetails"]["videoId"])

            if self.part == "contentDetails":
                time_total.extend(self.parse_watchtime(video_stacker)[0])
                title_total.extend(self.parse_watchtime(video_stacker)[1])

            elif self.part == "statistics":
                data_stats_tuple = self.parse_stats(video_stacker)
                title_total.extend(data_stats_tuple[0])
                view_total.extend(data_stats_tuple[1])
                like_total.extend(data_stats_tuple[2])
                dislike_total.extend(data_stats_tuple[3])
                comment_total.extend(data_stats_tuple[4])

            page_token = received_playlist.get("nextPageToken")
            if not page_token:
                break

        if self.part == "contentDetails":
            return time_total, title_total

        elif self.part == "statistics":
            pl_stats = {
                "titles": title_total,
                "views": view_total,
                "likes": like_total,
                "dislikes": dislike_total,
                "comments": comment_total,
            }

            return pl_stats

    def parse_watchtime(self, video_stacker: list) -> str:
        times = []
        titles = []

        fetch_videos = (
            self.build_youtube.videos()
            .list(part="contentDetails", id=",".join(video_stacker))
            .execute()
        )

        fetch_videos_statplus = (
            self.build_youtube.videos()
            .list(part="statistics, snippet", id=",".join(video_stacker))
            .execute()
        )

        for item in fetch_videos["items"]:
            times.append(item["contentDetails"]["duration"])

        for item in fetch_videos_statplus["items"]:
            titles.append(item["snippet"]["title"])

        return (times, titles)

    def parse_stats(self, video_stacker: list) -> tuple:
        titles = []
        views = []
        likes = []
        dislikes = []
        comments = []

        fetch_videos = (
            self.build_youtube.videos()
            .list(part="statistics, snippet", id=",".join(video_stacker))
            .execute()
        )

        for element in fetch_videos["items"]:
            vid_title = element["snippet"]["title"]
            view = int(element["statistics"]["viewCount"])
            like = int(element["statistics"]["likeCount"])
            dislike = int(element["statistics"]["dislikeCount"])
            comment = int(element["statistics"]["commentCount"])

            titles.append(vid_title)
            views.append(view)
            likes.append(like)
            dislikes.append(dislike)
            comments.append(comment)

        return (titles, views, likes, dislikes, comments)
