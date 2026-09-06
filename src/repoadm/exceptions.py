class RepositoryNotFoundError(Exception):
    pass

class RepositoryConflictError(Exception):
    pass

class RepositoryConfigurationError(Exception):
    pass

class RepositoryTargetNotFoundError(Exception):
    pass

class RepositoryTargetConflictError(Exception):
    pass

class RepositoryBundleNotFoundError(Exception):
    pass

class RepositoryBundleConflictError(Exception):
    pass

class RepositoryBundleMemberNotFoundError(Exception):
    pass
