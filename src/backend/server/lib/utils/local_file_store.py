import errno
import os
from typing import Optional

from server import globalConfig
from werkzeug.datastructures import FileStorage


class LocalImageStore(object):
    """
    A local image store service
    Images will be saved on static/uploaded folder
    """

    def __init__(self, app):
        pass

    @staticmethod
    def save(image_file: FileStorage, public_id: Optional[str] = None):
        file_sep = '.'
        file_ext = image_file.filename.rsplit(file_sep, 1)[1].lower()
        if (file_sep in image_file.filename and
                file_ext in globalConfig.get('IMAGE_ALLOWED_EXTENSIONS')):
            # extension = image_file.filename.rsplit(file_sep, 1)[1].lower()
            if public_id is not None:
                filename = "{0}.{1}".format(public_id, file_ext)
            else:
                filename = image_file.filename
            file_path_all = os.path.join(globalConfig.get('UPLOAD_FOLDER'), filename)
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
            file_absolute_path = os.path.join(globalConfig.get('UPLOAD_FOLDER'),
                                              os.path.basename(path))
            os.remove(file_absolute_path)
        except OSError as e:
            # errno.ENOENT = no such file or directory
            if e.errno != errno.ENOENT:
                # re-raise exception if a different error occurred
                raise
