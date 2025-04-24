from werkzeug.security import generate_password_hash

while True:
    password = input("Enter password to hash (or 'exit'): ")
    if password.lower() == "exit":
        break
    print("🔐 Hashed password:")
    print(generate_password_hash(password, method="pbkdf2:sha256"))
