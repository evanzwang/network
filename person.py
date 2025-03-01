class Person:
    def __init__(self, name: str, context: str, related_links: list[str], picture_file: str) -> None:
        self.name = name
        self.context = context
        self.related_links = related_links
        self.picture_file = picture_file

    def __str__(self) -> str:
        return f"Person(name='{self.name}', context='{self.context}', related_links={self.related_links}, picture_file='{self.picture_file}')"
