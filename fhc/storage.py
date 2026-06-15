from whitenoise.storage import CompressedManifestStaticFilesStorage


class ForgivingCompressedManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """WhiteNoise manifest storage that doesn't abort collectstatic when a
    referenced asset is missing.

    Third-party packages (e.g. django-jazzmin) ship minified JS/CSS that
    reference sourcemap (.map) files which aren't included. The default strict
    storage raises MissingFileError and fails the whole collectstatic run. We
    downgrade those reference errors to a skip so deployment isn't blocked,
    while still hashing/compressing everything else for cache-busting.
    """

    manifest_strict = False

    def post_process(self, *args, **kwargs):
        for name, hashed_name, processed in super().post_process(*args, **kwargs):
            if isinstance(processed, Exception):
                processed = False
            yield name, hashed_name, processed
