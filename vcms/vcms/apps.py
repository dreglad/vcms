from videos.apps import VideosConfig

class VcmsVideosConfig(VideosConfig):
    """Adds signals to videos app under the vcms project"""
    def ready(self):
        import vcms.signals
