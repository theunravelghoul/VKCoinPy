import gettext

ru = gettext.translation('base', localedir='locales', languages=['ru'])
ru.install()

_ = ru.gettext