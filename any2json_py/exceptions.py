class Any2JsonError(Exception):
    pass

class FileTooLargeError(Any2JsonError):
    pass

class UnsupportedFormatError(Any2JsonError):
    pass

class SchemaValidationError(Any2JsonError):
    pass

class ExtractionError(Any2JsonError):
    pass
