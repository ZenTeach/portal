import errno
import os
from typing import Optional

from server.config.settings import get_settings
from werkzeug.datastructures import FileStorage


class LocalImageFileStoreService(object):
    """
    A local file store service
    Images will be saved on static/uploaded folder
    """

    @staticmethod
    def save(image_file: FileStorage, public_id: Optional[str] = None):
        file_sep = '.'
        file_ext = image_file.filename.rsplit(file_sep, 1)[1].lower()
        settings = get_settings()
        if (file_sep in image_file.filename and
                file_ext in settings.image_allowed_extensions):

            filename = image_file.filename

            if public_id is not None:
                filename = public_id

            file_path_all = os.path.join(settings.upload_folder, filename)
            image_file.save(file_path_all)
            result = {'url': "/static/uploaded/" + filename, 'abs_filepath': file_path_all}
        else:
            result = {}
        return result

    @staticmethod
    def remove(path: str, public_id: Optional[str] = None):
        """
           Remove a file from operation system and omit the error if it's not existing.
           :param public_id: public_id of the file(used for public storage service to save it's id)
           :param path: path of the file when render it in UI
           :return: None
           """
        try:
            file_absolute_path = path

            if public_id:
                file_absolute_path = os.path.join(
                    get_settings().upload_folder, os.path.basename(public_id))
            os.remove(file_absolute_path)
            return True
        except OSError as e:
            # errno.ENOENT = no such file or directory
            if e.errno != errno.ENOENT:
                # re-raise exception if a different error occurred
                raise
