class C:
    def __init__(self, **kw):
        for x in iter(kw):
            setattr(self, x, kw[x])
