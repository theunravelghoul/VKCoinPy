import gettext

try:
    lang = gettext.translation('base', localedir='locales', fallback="en")
    _ = lang.gettext
except:
    _ = gettext.gettext
