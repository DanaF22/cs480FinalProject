# This file serves as the main menu where managers 
# and clients can either register or login

from db import get_connection, managerRegister
import manager_menu

def main():

    # Start menu options
    while True:
        print("\n === Hotel Managment System ===")
        print("1. Manager Register")
        print("2. Manager Login")
        print("3. Client Register")
        print("4. Client Login")
        print("5. Exit")

        choice = input("> ").strip()

        if choice == "1":
            name  = input("Enter name: ").strip()
            ssn   = input("Enter SSN: ").strip()
            email = input("Enter email: ").strip()
            managerRegister(name, ssn, email)

        # Verify Login
        elif choice == "2":
            ssn = input("Enter SSN: ").strip()
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT full_name FROM Managers WHERE ssn = %s", (ssn,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            # Succesful login goes to manager submenu
            if result:
                print(f"\nWelcome, {result[0]}!")
                manager_menu.run(ssn)
            else:
                print("No manager found with that SSN.")

        # ***Client Menu options will beign here***
        elif choice == "3":
            print("placeholder")
        
        elif choice == "4":
            print("placeholder")

        # Exit application. 
        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")

main()