import os
import sys
import re
import json
from geopy.geocoders import Nominatim

class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        self.is_registered = False

    def register(self):
        self.is_registered = True
        return f"Benutzerkonto für {self.name} wurde erstellt, Bestätigungsmail wurde gesendet an {self.email}."


class Product:
    def __init__(self, product_id, name, price):
        self.product_id = product_id
        self.name = name
        self.price = price


class ShoppingCart:
    def __init__(self):
        self.items = []
        self.total = 0

    def add_product(self, product):
        self.items.append(product)
        self.total += product.price
        return f"{product.name} wurde dem Warenkorb hinzugefügt."

    def remove_product(self, product):
        if product in self.items:
            self.items.remove(product)
            self.total -= product.price
            return f"{product.name} wurde aus dem Warenkorb entfernt."
        return "Produkt nicht im Warenkorb."

    def show_cart(self):
        if not self.items:
            return "Der Warenkorb ist leer."
        cart_content = "\n".join([f"{item.name} - {item.price}€" for item in self.items])
        return f"Im Warenkorb:\n{cart_content}\nGesamtsumme: {self.total}€"

    def apply_promo_code(self, code):
        discount = 0
        if code == "PROMO20":
            discount = self.total * 0.2
        elif code == "PROMO10":
            discount = self.total * 0.1
        self.total -= discount
        return f"Rabatt angewendet, neuer Gesamtbetrag: {self.total}€"


class Order:
    def __init__(self, user, cart, address, test_mode=False):
        self.user = user
        self.cart = cart
        self.address = self.validate_address(address, test_mode)

    def validate_address(self, address, test_mode):
        if test_mode:
            return address  # Test mode Address
        geolocator = Nominatim(user_agent="shopapp")
        location = geolocator.geocode(address)
        if location:
            return f"{location.address} (Lat: {location.latitude}, Lon: {location.longitude})"
        else:
            print("Adresse nicht gefunden. Bitte geben Sie eine gültige Adresse ein.")
            return None

    def confirm_order(self):
        if self.user.is_registered and self.cart.items and self.address:
            return f"Bestellung für {self.user.name} an Adresse {self.address} wurde verarbeitet, Bestätigungsmail gesendet."
        else:
            return "Bestellung fehlgeschlagen: Benutzer nicht registriert, Warenkorb leer oder Adresse ungültig."


class ProductReviews:
    def __init__(self, review_file="reviews.json"):
        self.review_file = review_file
        self.reviews = self.load_reviews()

    def load_reviews(self):
        if os.path.exists(self.review_file):
            with open(self.review_file, "r") as file:
                return json.load(file)
        return {}

    def save_reviews(self):
        with open(self.review_file, "w") as file:
            json.dump(self.reviews, file)

    def add_review(self, product_name, review, user_name):
        review_entry = {"user": user_name, "review": review}
        if product_name in self.reviews:
            self.reviews[product_name].append(review_entry)
        else:
            self.reviews[product_name] = [review_entry]
        self.save_reviews()
        return "Bewertung hinzugefügt."

    def get_reviews(self, product_name):
        reviews_list = self.reviews.get(product_name, [])
        if not reviews_list:
            return "Keine Bewertungen vorhanden."
        return "\n".join([f"{review['user']}: {review['review']}" for review in reviews_list])


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def is_valid_name(name):
    return name.isalpha()

def is_valid_address(address):
    return len(address) > 5


def suggest_address():
    print("Beispiel für Adressformat: Musterstraße 1, 12345 Berlin, Germany")

def auto_detect_address():
    geolocator = Nominatim(user_agent="shopapp")
    location = geolocator.geocode("Hamburg, Germany")  # Location
    if location:
        print(f"Automatisch erkannte Adresse: {location.address} (Lat: {location.latitude}, Lon: {location.longitude})")
        return location.address
    else:
        print("Adresse konnte nicht automatisch bestimmt werden.")
        return None


# Test teil
def run_tests():
    print("Test 1: Registrierung eines neuen Benutzers")
    user = User("test", "test@example.com", "geheim")
    result = user.register()
    assert "Benutzerkonto" in result, f"Test 1 fehlgeschlagen: {result}"
    print("Ergebnis: ", result)

    print("\nTest 2: Hinzufügen eines Produkts zum Warenkorb")
    product = Product(123, "Laptop", 1000)
    cart = ShoppingCart()
    result = cart.add_product(product)
    assert "wurde dem Warenkorb hinzugefügt" in result, f"Test 2 fehlgeschlagen: {result}"
    print("Ergebnis: ", result)

    print("\nTest 3: Einlösen eines gültigen Promotion-Codes")
    result = cart.apply_promo_code("PROMO20")
    assert "neuer Gesamtbetrag" in result and cart.total == 800, f"Test 3 fehlgeschlagen: {result}"
    print("Ergebnis: ", result)

    print("\nTest 4: Bestellung abschließen mit korrekten Daten")
    order = Order(user, cart, "Musterstraße 1, 12345 Berlin, Germany", test_mode=True)
    result = order.confirm_order()
    assert "Bestellung für" in result, f"Test 4 fehlgeschlagen: {result}"
    print("Ergebnis: ", result)

    print("\nTest 5: Anzeige von Produktbewertungen")
    reviews = ProductReviews()
    reviews.add_review("Laptop", "Großartiger Laptop!", "test")
    result = reviews.get_reviews("Laptop")
    assert "Großartiger Laptop!" in result, f"Test 5 fehlgeschlagen: {result}"
    print("Ergebnis: ", result)

    print("\nAlle Tests erfolgreich bestanden!")


# Manual input
def manual_mode():
    while True:
        user_name = input("Geben Sie Ihren Namen ein: ")
        if is_valid_name(user_name):
            break
        print("Ungültiger Name. Der Name darf nur Buchstaben enthalten. Bitte erneut eingeben.")

    while True:
        user_email = input("Geben Sie Ihre E-Mail-Adresse ein: ")
        if is_valid_email(user_email):
            break
        print("Ungültige E-Mail-Adresse. Bitte erneut eingeben.")

    user_password = input("Geben Sie Ihr Passwort ein: ")

    user = User(user_name, user_email, user_password)
    print(user.register())

    cart = ShoppingCart()
    
    while True:
        print("\nVerfügbare Produkte:")
        print("1. Laptop - 1000€")
        print("2. Smartphone - 500€")
        print("3. Uranium - 1000000€")
        choice = input("Wählen Sie ein Produkt zum Hinzufügen zum Warenkorb (1/2/3) oder geben Sie 'q' ein, um fortzufahren: ")
        
        if choice == "1":
            product = Product(123, "Laptop", 1000)
            print(cart.add_product(product))
        elif choice == "2":
            product = Product(124, "Smartphone", 500)
            print(cart.add_product(product))
        elif choice == "3":
            print("FIB Coming at you...")
            print("Critical Joke...")
            os.execv(sys.executable, ['python'] + sys.argv)
        elif choice.lower() == 'q':
            break
        else:
            print("Ungültige Auswahl.")
    
    while True:
        print(cart.show_cart())
        choice = input("Möchten Sie ein Produkt entfernen oder weiter einkaufen? (Entfernen: 'r', Einkaufen: 'c'): ").lower()
        if choice == 'r':
            product_name = input("Geben Sie den Namen des Produkts ein, das Sie entfernen möchten: ")
            product = next((item for item in cart.items if item.name == product_name), None)
            if product:
                print(cart.remove_product(product))
            else:
                print("Produkt nicht im Warenkorb.")
        elif choice == 'c':
            continue  # To the shopp
        else:
            break

    while True:
        choice = input("Möchten Sie die Adresse manuell eingeben (m) oder automatisch erkennen lassen (a)? (m/a): ").lower()
        if choice == 'm':
            suggest_address()  # Addres beispiel 
            user_address = input("Geben Sie Ihre Adresse für die Lieferung ein (Beispiel: Musterstraße 1, 12345 Berlin, Germany): ")
            if is_valid_address(user_address):
                break
            print("Ungültige Adresse. Bitte erneut eingeben.")
        elif choice == 'a':
            user_address = auto_detect_address()
            if user_address:
                break
        else:
            print("Ungültige Auswahl.")

    order = Order(user, cart, user_address)
    if order.address is None:
        print("Adresse konnte nicht verifiziert werden. Bestellung abgebrochen.")
    else:
        print(order.confirm_order())

    print("\nVielen Dank für Ihre Bestellung!")

    # Bewertungen
    reviews = ProductReviews()
    while True:
        print("\n1. Bewertung hinzufügen")
        print("2. Bewertungen anzeigen")
        print("3. Beenden")
        choice = input("Wählen Sie eine Option (1/2/3): ")
        
        if choice == "1":
            print("\nVerfügbare Produkte:")
            print("1. Laptop")
            print("2. Smartphone")
            product_choice = input("Wählen Sie ein Produkt (1/2): ")
            if product_choice == "1":
                product_name = "Laptop"
            elif product_choice == "2":
                product_name = "Smartphone"
            else:
                print("Ungültige Auswahl.")
                continue
            review = input("Geben Sie Ihre Bewertung ein: ")
            print(reviews.add_review(product_name, review, user_name))
        elif choice == "2":
            print("\nVerfügbare Produkte:")
            print("1. Laptop")
            print("2. Smartphone")
            product_choice = input("Wählen Sie ein Produkt (1/2): ")
            if product_choice == "1":
                product_name = "Laptop"
            elif product_choice == "2":
                product_name = "Smartphone"
            else:
                print("Ungültige Auswahl.")
                continue
            print("Bewertungen:", reviews.get_reviews(product_name))
        elif choice == "3":
            break
        else:
            print("Ungültige Auswahl.")


# main function
def main():
    print("Willkommen bei ShopApp!")
    print("1. Testmodus")
    print("2. Handbuchmodus")
    
    choice = input("Wählen Sie eine Option (1/2): ")
    
    if choice == "1":
        run_tests()
    elif choice == "2":
        manual_mode()
    else:
        print("Ungültige Auswahl. Das Programm wird beendet.")


if __name__ == "__main__":
    main()
