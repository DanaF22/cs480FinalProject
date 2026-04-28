# This file serves as the main menu where managers 
# and clients can either register or login

from db import get_connection, managerRegister, clientRegister, clientLogin, updateClientInfo, viewAllBookings, submitReview,printAvailableRooms,bookSpecificRoom,automaticBooking
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

        # Verify Manager Login
        elif choice == "2":
            ssn = input("Enter SSN: ").strip()
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT full_name FROM Managers WHERE ssn = %s", (ssn,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            # Successful login goes to manager submenu
            if result:
                print(f"\nWelcome, {result[0]}!")
                manager_menu.run(ssn)
            else:
                print("No manager found with that SSN.")

        #registers a client
        elif choice == "3":
            #retrieves their name and email
            name = input("Enter name: ").strip()
            email = input("Enter email: ").strip()

            addresses = []
            #retrieves their addresses
            number_addresses = int(input("How many addresses do you want to add? "))
            for i in range(number_addresses):
                street_name = input("Enter street name: ").strip()
                number = input("Enter street number: ").strip()
                city = input("Enter city: ").strip()
                addresses.append({'street_name': street_name, 'num': number, 'city': city})
            
            cards = []
            #retrieves their credit card information
            number_cards = int(input("How many credit cards do you want to add? "))
            for i in range(number_cards):
                card_number = input("Enter card number: ").strip()
                street_name = input("Enter billing street name: ").strip()
                number = input("Enter billing street number: ").strip()
                city = input("Enter billing city: ").strip()
                cards.append({'credit_card_number': card_number, 'street_name': street_name, 'num': number, 'city': city})
            
            clientRegister(name, email, addresses, cards)

        #login for clients, if successful goes to client submenu
        elif choice == "4":
            email = input("Enter client email: ").strip()

            conn = get_connection()
            cur  = conn.cursor()
            #check if client exists
            if clientLogin(email):
                #client menu options
                while True:
                    print("\n === Client Menu ===")
                    print("1. View Bookings")
                    print("2. Update Client Information")
                    print("3. Submit a Review")
                    print("4. View available rooms for given date range")
                    print("5. Book specific room for given date range")
                    print("6. Automatic booking at Hotel for given date range")
                    print("7. Logout")

                    client_choice = input("> ").strip()
                    
                    if client_choice == "1":
                        viewAllBookings(email)
                    elif client_choice == "2":
                        new_name = input("Enter new name: ").strip()
                        
                        #retrieve new addresses and credit card information
                        addresses = []
                        number_addresses = int(input("How many addresses do you want to add? "))
                        for i in range(number_addresses):
                            street_name = input("Enter street name: ").strip()
                            number = input("Enter street number: ").strip()
                            city = input("Enter city: ").strip()
                            addresses.append({'street_name': street_name, 'num': number, 'city': city})
                        
                        cards = []
                        number_cards = int(input("How many credit cards do you want to add? "))
                        for i in range(number_cards):
                            card_number = input("Enter card number: ").strip()
                            street_name = input("Enter billing street name: ").strip()
                            number = input("Enter billing street number: ").strip()
                            city = input("Enter billing city: ").strip()
                            cards.append({'credit_card_number': card_number, 'street_name': street_name, 'num': number, 'city': city})

                        updateClientInfo(email, new_name, addresses, cards)
                        
                    elif client_choice == "3":
                        hotel_id = input("Enter hotel ID: ").strip()
                        submitReview(email, hotel_id)

                    elif client_choice == "4":
                        printAvailableRooms()
                    elif client_choice == "5":
                        bookSpecificRoom(email)
                    elif client_choice == "6":
                        automaticBooking(email)
                    elif client_choice == "7":
                        print("Logging out!")
                        break
                    else:
                        print("Invalid option, try again!")
            cur.close()
            conn.close()
                
        # Exit application. 
        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")

main()