import google.ads.googleads
import pkgutil

print(f"Package location: {google.ads.googleads.__path__}")
print("Available versions:")
for importer, modname, ispkg in pkgutil.iter_modules(google.ads.googleads.__path__):
    print(f" - {modname}")
