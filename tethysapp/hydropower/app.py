from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_apps.base import PersistentStore

class HydroPower(TethysAppBase):
    """
    Tethys app class for hydro power.
    """

    name = 'Hydro Power'
    index = 'hydropower:home'
    icon = 'hydropower/images/icon.gif'
    package = 'hydropower'
    root_url = 'hydropower'
    color = '#277554'
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='hydropower',
                           controller='hydropower.controllers.home'),
                    UrlMap(name='capacity',
                           url='hydropower/capacity',
                           controller='hydropower.controllers.calculate_capacity'),
        )

        return url_maps


    def persistent_stores(self):
        """
        Add one or more persistent persistent stores
        """

        stores = (PersistentStore(name='hydropower_db',
                                  initializer='hydropower.init_stores.init_hydropower_db',
                  ),
        )

        return stores
