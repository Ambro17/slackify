from flask import Blueprint as BP


class Blueprint(BP):
    """Allow polymorhpic treatment of apps and blueprints while rerouting requests.

    See `Slackify._get_endpoint_handler` for details of why this is required.
    """

    def register(self, app, options, first_registration: bool):
        super().register(app, options, first_registration)
        self.view_functions = app.view_functions
