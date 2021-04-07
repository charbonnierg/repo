class BaseError(Exception):
    """Base error used by quara-core package."""

    CODE = "GenericError"


class FileMissingError(FileNotFoundError, BaseError):

    CODE = "FileMissing"


class InvalidFormatError(BaseError):
    """An error to raise when a format is not enforced."""

    CODE = "InvalidMessage"


class ResourceNotFoundError(BaseError):
    """An error to raise when a resource is missing."""

    CODE = "ResourceNotFound"


class ResourceAlreadyExistsError(BaseError):
    """An error to raise when a resource already exists."""

    CODE = "ResourceAlreadyExists"


class ResourceUnavailableError(BaseError):

    CODE = "ResourceUnavailable"


class ResourceBusyError(BaseError):
    """An error to raise when a resource is busy."""

    CODE = "ResourceBusy"


class ClientNotConnectedError(ResourceUnavailableError):
    """An asynchronous client is not connected."""

    CODE = "ClientNotConnected"


# Plugins Errors
class PluginNotFoundError(ResourceNotFoundError):
    """The specified plugin does not exist."""

    CODE = "PluginNotFound"


class PluginImportFailedError(ResourceUnavailableError):
    """The specified plugin could not be loaded."""

    CODE = "PluginImportFailedError"

    def __init__(self, msg: str, *, error: Exception):
        self.msg = msg
        self.error = error


# S3 Errors
class S3Error(BaseError):

    CODE = "S3Error"


class NoSuchKeyError(ResourceNotFoundError):
    """The specified key does not exist."""

    CODE = "NoSuchKey"


class NoSuchBucketError(ResourceNotFoundError):
    """The specified bucket does not exist."""

    CODE = "NoSuchBucket"


class BucketAlreadyExistsError(ResourceAlreadyExistsError):
    """The bucket already exists."""

    CODE = "BucketAlreadyExists"


class BucketNotEmptyError(ResourceBusyError):
    """The bucket you tried to delete is not empty."""

    CODE = "BucketNotEmpty"


class InvalidModelFormat(InvalidFormatError):
    """Invalid model for the Inference Engine Resource."""

    CODE = "InvalidModelFormat"


# Database Errors
class DatabaseError(BaseError):

    CODE = "DatabaseError"


class DocumentNotUniqueError(ResourceAlreadyExistsError):
    """Document is not unique in respect to unique filters."""

    CODE = "DocumentAlreadyExists"


class InvalidDocumentId(InvalidFormatError):
    """Invalid document ID."""

    CODE = "InvalidDocumentId"


class EmptyDataError(InvalidFormatError):
    """File does not contain any data."""

    CODE = "EmptyData"


class InvalidMessageError(InvalidFormatError):
    """Error raised when a message cannot be parsed."""

    CODE = "InvalidMessage"


class InvalidMessageDataError(InvalidMessageError):
    """Error raised when an invalid message data is parsed."""

    CODE = "InvalidMessageData"
