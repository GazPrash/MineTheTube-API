from googleapiclient.discovery import build
from datetime import datetime
from other import credentials_and_secrets as creds


# some constants / enviromental variables
API = creds.api
API_VER = creds.api_version
DEV_KEY = creds.dev_key


class UtilityExtras:
    """
    UtilityExtras Class ~ Usage includes, the availability
    to search for Youtube Videos with dates and generate playlists
    with keywords.
    
    """

    def __init__(self, parameter_strings, max_results):
        self.parameter_strings = parameter_strings
        self.max_results = max_results

    def decode_parameters_for_search(self):
        parameter_string, date_string = self.parameter_strings.split("&")
        self.parameter = " ".join(parameter_string.split("+"))

        before_string, after_string = date_string.split("%")
        self.before_date = before_string.split("-")
        self.after_date = after_string.split("-")

    def decode_parameters_for_generator(self):
        self.parameter = " ".join(self.parameter_strings.split("+"))

    def advanced_search(self):
        self.build_youtube = build(API, API_VER, developerKey=DEV_KEY)

        # deconstructing & converting dates to rfc 3389 ~ if self.argument == None;
        # set dates to some recent default values TODO
        self.before_date = (
            str(
                datetime(
                    year=int(self.before_date[0]),
                    month=int(self.before_date[1]),
                    day=int(self.before_date[2]),
                ).isoformat()
            )
            + "Z"
        )
        self.after_date = (
            str(
                datetime(
                    year=int(self.after_date[0]),
                    month=int(self.after_date[1]),
                    day=int(self.after_date[2]),
                ).isoformat()
            )
            + "Z"
        )

        search_request = (
            self.build_youtube.search()
            .list(
                part="snippet",
                q=self.parameter,
                maxResults=self.max_results,
                publishedBefore=self.before_date,
                publishedAfter=self.after_date,
                type="video",
            )
            .execute()
        )

        video_links = []
        video_ids = []
        thumbnail_ids = []
        titles = []
        for item in search_request["items"]:
            videoId = item["id"]["videoId"]
            thumbnail_ids.append(f"https://i1.ytimg.com/vi/{videoId}/0.jpg")
            video_links.append(f"https://www.youtube.com/watch?v={videoId}")
            video_ids.append(videoId)

        names_request = (
            self.build_youtube.videos()
            .list(part="snippet", id=",".join(video_ids))
            .execute()
        )

        for item in names_request["items"]:
            titles.append(item["snippet"]["title"])

        final_dict = {
            "links": video_links,
            "thumbnails": thumbnail_ids,
            "titles": titles,
        }

        return final_dict

    def playlist_generator(self, user_credentials):
        self.build_youtube = build(API, API_VER, credentials=user_credentials)

        search_request = (
            self.build_youtube.search()
            .list(
                part="snippet",
                q=self.parameter,
                maxResults=self.max_results,
                type="video",
            )
            .execute()
        )

        video_ids = []
        for item in search_request["items"]:
            video_ids.append(item["id"]["videoId"])

        create_playlist = (
            self.build_youtube.playlists()
            .insert(
                part="snippet, status",
                body={
                    "snippet": {
                        "title": self.parameter,
                        "description": "",
                        "defaultLanguage": "en",
                    },
                    "status": {"privacyStatus": "public"},
                },
            )
            .execute()
        )

        for id in video_ids:
            self.build_youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": create_playlist["id"],
                        "resourceId": {"kind": "youtube#video", "videoId": id},
                    }
                },
            ).execute()

        return {
            "Link": f"https://www.youtube.com/playlist?list={create_playlist['id']}"
        }
