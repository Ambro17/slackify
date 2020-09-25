from flask import Blueprint as BP


class Blueprint(BP):
    """Slackify `Blueprint` that allows to register slack handlers to later attach to Flask instance

    If you have an existent web server, or you want to separate slack handlers
    from all your other server endpoints you can register them with this blueprint
    and then attach them to the Flask instance using the app factory pattern.

    .. note::
        Only one blueprint is supported. All slack handlers should be handled on
        the same blueprint.
    """

    def register(self, app, options, first_registration: bool = False):
        """Overriden to allow polymorphic treatment in Slackify routing logic.

        By adding a view_functions attribute we can treat apps and blueprints routing
        indifferently. For more details see `Slackify._get_endpoint_handler`
        """
        super().register(app, options, first_registration)
        self.view_functions = app.view_functions
