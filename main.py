# This File Can be used as an entry file whilst working with Command Line Interface

"""
    Developed By: Prashant Shrivastava
    Version: 0.0.2
    © 2021 - All rights reserved.
"""


from analytics import Analytics
from utility import UtilityExtras
from trends import Trends
from oauth import OauthVerfication
from versus import TuberVersus


class IndexElement:
    """
    Index Element Class ~ This is the entrypoint for obtaining all the data, 
    function datapoint takes the input, via cline or a flask wrapper and 
    responds with analyzed results accordingly.
    
    """
    def __init__(self, primary_argument, secondary_argument, target_credentials):
        self.primary_argument = primary_argument
        self.secondary_argument = secondary_argument
        self.target_credentials = target_credentials

    def data_point(self):
        if self.primary_argument == "Analytics":
            get_analytics = Analytics(self.secondary_argument, self.target_credentials)
            return get_analytics.bender()

        elif self.primary_argument == "Utility":
            if self.secondary_argument == "AdvancedSearch":
                get_utility_data = UtilityExtras(self.target_credentials, 50)
                get_utility_data.decode_parameters_for_search()
                return get_utility_data.advanced_search()
            elif self.secondary_argument == "PlaylistGenerator":
                oauth_obj = OauthVerfication()
                auth_credentials = oauth_obj.get_creds()

                get_utility_data = UtilityExtras(*(self.target_credentials))
                get_utility_data.decode_parameters_for_generator()

                return get_utility_data.playlist_generator(auth_credentials)

        elif self.primary_argument == "Trends":
            get_trends_data = Trends(self.secondary_argument)
            get_trends_data.decode_parameters()

            return get_trends_data.fetch_trends()

        elif self.primary_argument == "Versus":
            get_comparsion_data = TuberVersus(self.secondary_argument)
            get_comparsion_data.decode_parameters()

            return get_comparsion_data.fetch_stats()


if __name__ == "__main__":
    obj = IndexElement("Trends", "trends?evaltrend=markiplier-month", None)
    output = obj.data_point()

    print(output)
