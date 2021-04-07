class PyprojectNotFoundError(FileNotFoundError):
    pass


class DirectoryNotFoundError(FileNotFoundError):
    pass


class PackageNotFoundError(FileNotFoundError):
    pass
