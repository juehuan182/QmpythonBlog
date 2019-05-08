from django.apps import AppConfig


class ArticleConfig(AppConfig):
    name = 'article'

    def ready(self):
        # signals are imported, so that they are defined and can be used
        import article.signals

