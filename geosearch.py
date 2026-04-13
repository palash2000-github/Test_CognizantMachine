from collections import defaultdict

# World Countries and Cities Finder
# Requires: pip install geonamescache


try:
    import geonamescache
except ImportError:
    print("Missing dependency: geonamescache")
    print("Install it with: pip install geonamescache")
    raise SystemExit(1)


def paginate(items, page_size=30):
    if not items:
        print("No data found.")
        return
    total = len(items)
    for i in range(0, total, page_size):
        chunk = items[i:i + page_size]
        for line in chunk:
            print(line)
        if i + page_size < total:
            cont = input("\nPress Enter for more (or type 'q' to stop): ").strip().lower()
            if cont == "q":
                break
    print(f"\nDisplayed {min(total, i + len(chunk))} of {total} item(s).")


def build_data():
    gc = geonamescache.GeonamesCache()
    countries_raw = gc.get_countries()  # dict by ISO code
    cities_raw = gc.get_cities()        # dict by geonameid

    country_code_to_name = {
        code: data["name"] for code, data in countries_raw.items()
    }

    countries = sorted(country_code_to_name.values())

    # Map city name to list of "City, Country"
    city_entries = []
    city_index = defaultdict(list)

    for city in cities_raw.values():
        city_name = city.get("name", "").strip()
        code = city.get("countrycode", "")
        country_name = country_code_to_name.get(code, code)

        if city_name:
            full = f"{city_name}, {country_name}"
            city_entries.append(full)
            city_index[city_name.lower()].append(full)

    city_entries.sort()
    return countries, city_entries


def search_items(items, query):
    q = query.lower().strip()
    return [x for x in items if q in x.lower()]


def main():
    countries, cities = build_data()

    menu = """
Choose an option:
1) List all countries
2) List all cities
3) Find country by input
4) Find city by input
5) Exit
"""

    while True:
        print(menu)
        choice = input("Enter option (1-5): ").strip()

        if choice == "1":
            print(f"\nTotal countries: {len(countries)}")
            paginate(countries, page_size=40)

        elif choice == "2":
            print(f"\nTotal cities: {len(cities)}")
            show_all = input("This is a large list. Continue? (y/n): ").strip().lower()
            if show_all == "y":
                paginate(cities, page_size=40)

        elif choice == "3":
            q = input("Enter country name to search: ").strip()
            result = search_items(countries, q)
            print(f"\nMatches: {len(result)}")
            paginate(result, page_size=40)

        elif choice == "4":
            q = input("Enter city name to search: ").strip()
            result = search_items(cities, q)
            print(f"\nMatches: {len(result)}")
            paginate(result, page_size=40)

        elif choice == "5":
            print("Goodbye.")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()