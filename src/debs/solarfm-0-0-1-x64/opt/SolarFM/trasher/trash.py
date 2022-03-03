# Python imports
import os

# Lib imports

# Application imports




class Trash(object):
    """Base Trash class."""

    def size_dir(self, sdir):
        """Get the size of a directory.  Based on code found online."""
        size = os.path.getsize(sdir)

        for item in os.listdir(sdir):
            item = os.path.join(sdir, item)

            if os.path.isfile(item):
                size = size + os.path.getsize(item)
            elif os.path.isdir(item):
                size = size + self.size_dir(item)

        return size

    def regenerate(self):
        """Regenerate the trash and recreate metadata."""
        pass  # Some backends don’t need regeneration.

    def empty(self, verbose):
        """Empty the trash."""
        raise NotImplementedError(_('Backend didn’t implement this functionality'))

    def list(self, human=True):
        """List the trash contents."""
        raise NotImplementedError(_('Backend didn’t implement this functionality'))

    def trash(self, filepath, verbose):
        """Move specified file to trash."""
        raise NotImplementedError(_('Backend didn’t implement this functionality'))

    def restore(self, filename, verbose):
        """Restore a file from trash."""
        raise NotImplementedError(_('Backend didn’t \ implement this functionality'))
