
countries = []
with open ("country.yml", encoding = "utf-8", mode = "r") as f:
    for line in f:
        if '-' in line and "lookup" not in line:
            countries.append(line[:len(line)-2])


with open ("test.txt", encoding="utf-8", mode = "w+") as f:
    for country in countries:
        f.write(("    - covid cases in [" +
                 " ".join(country.split()[1:])) + "]" +
                "(country)"+ "\n")
    # else:
    #     length = len(country.split())
    #     print(country.split()[1:])