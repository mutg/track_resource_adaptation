import SimEngine

def logPrint(*message):
    return
    engine = SimEngine.SimEngine.SimEngine()
    asn = engine.asn
    print "A ", asn, " ", ' '.join(map(str, message))