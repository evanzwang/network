class Person:
    def __init__(
        self,
        name: str,
        profile_pic: str,
        contacts: list[str],
        links: list[str],
        short_description: str,
        long_description: str,
    ) -> None:
        self.name = name
        self.profile_pic = profile_pic
        self.contacts = contacts
        self.links = links
        self.short_description = short_description
        self.long_description = long_description

    def __str__(self) -> str:
        return (
            f"Name: {self.name}\n"
            f"Profile Picture: {self.profile_pic}\n"
            f"Contacts: {', '.join(self.contacts)}\n"
            f"Links: {', '.join(self.links)}\n"
            f"Short Description: {self.short_description}\n"
        )

    def __repr__(self) -> str:
        return (
            f"Person(name='{self.name}', profile_pic='{self.profile_pic}', "
            f"contacts={self.contacts}, links={self.links}, "
            f"short_description='{self.short_description}', "
            f"long_description='{self.long_description}')"
        )
