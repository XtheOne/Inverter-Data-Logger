# from https://gist.github.com/will-hart/5899567


class PluginMount(type):
    """
    A plugin mount point derived from:
        http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    Acts as a metaclass which creates anything inheriting from Plugin
    """

    def __init__(cls, name, bases, attrs):
        """Called when a Plugin derived class is imported"""
        super(PluginMount, cls).__init__(name)

        if not hasattr(cls, 'plugins'):
            # Called when the metaclass is first instantiated
            cls.plugins = []
        else:
            # Called when a plugin class is imported
            cls.register_plugin(cls)

    def register_plugin(cls, new_plugin):
        """Add the plugin to the plugin list and perform any registration
        logic"""

        # create a plugin instance and store it
        instance = new_plugin()

        # save the plugin reference
        cls.plugins.append(instance)


class Plugin(object):
    """A plugin which must provide a process_message() method"""
    __metaclass__ = PluginMount

    config = None
    logger = None
