#Qvariant only need for gui

try:
    __IPYTHON__
except NameError:
    import sip
    sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants