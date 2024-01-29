class InvalidOrganiztion(Exception):
    """Raised when an invalid organization is used."""

    def __init__(self, organization) -> None:
        self.organization = organization

    def __str__(self) -> str:
        return "Invalid organization: {}".format(self.organization)
