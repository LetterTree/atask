class AtaskError(Exception):
    pass


class ValidationError(AtaskError):
    pass


class NotFoundError(AtaskError):
    pass


class ConflictError(AtaskError):
    pass
