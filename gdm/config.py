"""Wrappers for the dependency configuration files."""

import os
import logging

import yorm

from . import common
from .shell import ShellMixin
from .source import Sources

logging.getLogger('yorm').setLevel(logging.INFO)
log = common.logger(__name__)


@yorm.attr(location=yorm.converters.String)
@yorm.attr(sources=Sources)
@yorm.attr(sources_locked=Sources)
@yorm.sync("{self.root}/{self.filename}")
class Config(ShellMixin):

    """A dictionary of dependency configuration options."""

    FILENAMES = ('gdm.yml', 'gdm.yaml', '.gdm.yml', '.gdm.yaml')

    def __init__(self, root, filename=FILENAMES[0], location='gdm_sources'):
        super().__init__()
        self.root = root
        self.filename = filename
        self.location = location
        self.sources = []
        self.sources_locked = []

    @property
    def path(self):
        """Get the full path to the configuration file."""
        return os.path.join(self.root, self.filename)

    @property
    def location_path(self):
        """Get the full path to the sources location."""
        return os.path.join(self.root, self.location)

    def install_deps(self, force=False, clean=True, update=True, recurse=False):
        """Get all sources."""
        if not os.path.isdir(self.location_path):
            self.mkdir(self.location_path)
        self.cd(self.location_path)

        sources = self._get_sources(update)
        common.show()
        common.indent()

        count = 0
        for source in sources:
            count += 1

            source.update_files(force=force, clean=clean)
            source.create_link(self.root, force=force)
            common.show()

            config = load()
            if config:
                common.indent()
                count += config.install_deps(force, clean, update and recurse)
                common.dedent()

            self.cd(self.location_path, visible=False)

        common.dedent()

        return count

    def lock_deps(self):
        """Lock down the immediate dependency versions."""
        self.cd(self.location_path)
        common.show()
        common.indent()

        self.sources_locked = []
        for source in self.sources:
            self.sources_locked.append(source.lock())
            common.show()

            self.cd(self.location_path, visible=False)

    def uninstall_deps(self):
        """Remove the sources location."""
        self.rm(self.location_path)
        common.show()

    def get_deps(self, allow_dirty=True):
        """Yield the path, repository URL, and hash of each dependency."""
        if os.path.exists(self.location_path):
            self.cd(self.location_path)
            common.show()
            common.indent()
        else:
            return

        for source in self.sources:

            yield source.identify(allow_dirty=allow_dirty)
            common.show()

            config = load()
            if config:
                common.indent()
                yield from config.get_deps(allow_dirty=allow_dirty)
                common.dedent()

            self.cd(self.location_path, visible=False)

        common.dedent()

    def _get_sources(self, update):
        if update:
            return self.sources
        elif self.sources_locked:
            return self.sources_locked
        else:
            log.warn("no locked sources available, installing latest...")
            return self.sources


def load(root=None):
    """Load the configuration for the current project."""
    if root is None:
        root = os.getcwd()

    for filename in os.listdir(root):
        if filename.lower() in Config.FILENAMES:
            config = Config(root, filename)
            log.debug("loaded config: %s", config.path)
            return config

    log.debug("no config found in: %s", root)
    return None
