def importer():
    global pprint
    import pprint
    pprint.pprint('x')

importer()
pprint.pprint('y')