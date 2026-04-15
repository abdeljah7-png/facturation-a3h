from core.utils import get_societe

class ERPFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.societe = get_societe()