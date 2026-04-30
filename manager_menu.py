# This file handles everything a logged in manager can do.

from db import (get_connection, topClients, listOfRooms,
                listOfHotels, twoCities, problematicHotels,
                totalAmountSpent)

def run(ssn):
    # Passing in ssn so we know which manager has logged in
    
    while True:
        print("\n=== Manager Menu ===")
        print("--- Hotel & Room Managment ---")
        print("1. Add Hotel")
        print("2. Update Hotel")
        print("3. Delete Hotel")
        print("4. Add Room")
        print("5. Update Room")
        print("6. Delete Room")
        print("7. Remove Client")
        print("--- Reports ---")
        print("8. Top-K Clients by Bookings")
        print("9. List All Rooms & Booking Count")
        print("10. Hotel Stats (Booking & Avg Rating)")
        print("11. Clients in City C1 who Booked in City C2")
        print("12. Problematic Chicago Hotels")
        print("13. Client Total Spending")
        print("--- ")
        print("14. Back to Main Menu")

        choice = input("> ").strip()

        if choice == "1":
            addHotel()
        elif choice == "2":
            updateHotel()
        elif choice == "3":
            deleteHotel()
        elif choice == "4":
            addRoom()
        elif choice == "5":
            updateRoom()
        elif choice == "6":
            deleteRoom()
        elif choice == "7":
            removeClient()
        elif choice == "8":
            k = input("Enter k: ").strip()
            topClients(int(k))
        elif choice == "9":
            listOfRooms()
        elif choice == "10":
            listOfHotels()
        elif choice == "11":
            c1 = input("Enter City 1: ").strip()
            c2 = input("Enter City 2: ").strip()
            twoCities(c1, c2)
        elif choice == "12":
            problematicHotels()
        elif choice == "13":
            totalAmountSpent()
        elif choice == "14":
            break
        else:
            print("Invalid choice, try again.")

# === Hotel Functions ===

def addHotel():
    hotel_id    = input("Enter hotel ID: ").strip()
    # check if hotel ID already exists
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""SELECT * FROM Hotel WHERE hotel_id = %s""", (hotel_id,))
    if cur.fetchone() is not None:
        print("Try again! A hotel with this ID already exists.")
        cur.close()
        conn.close()
        return
    
    hotel_name  = input("Enter hotel name: ").strip()
    street_name = input("Enter street name: ").strip()
    num         = input("Enter street number: ").strip()
    city        = input("Enter city: ").strip()

    cur.execute("""
        INSERT INTO Address (street_name, num, city)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (street_name, num, city))

    cur.execute("""
        INSERT INTO Hotel (hotel_id, hotel_name, street_name, num, city)
        VALUES (%s, %s, %s, %s, %s)         
    """, (hotel_id, hotel_name, street_name, num, city))

    conn.commit()

    cur.close()
    conn.close()
    print("Hotel added successfully!")

def updateHotel():
    hotel_id   = input("Enter hotel ID to update: ").strip()
    hotel_name = input("Enter new hotel name: ").strip()

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        UPDATE Hotel SET hotel_name = %s
        WHERE hotel_id = %s
    """, (hotel_name, hotel_id))

    if cur.rowcount == 0:
        print("No hotel found with that ID.")
    else:
        print("Hotel updated successfully!")

    conn.commit()
    cur.close()
    conn.close()

def deleteHotel():
    hotel_id = input("Enter hotel ID to delete: ").strip()

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""DELETE FROM Hotel WHERE hotel_id = %s""", (hotel_id,))

    if cur.rowcount == 0:
        print("No hotel found with that ID.")
    else:
        print("Hotel deleted succesfully!")
    
    conn.commit()
    cur.close()
    conn.close()

# === Room Functions ===

def addRoom():
    conn = get_connection()
    cur  = conn.cursor()

    hotel_id    = input("Enter hotel ID: ").strip()

    cur.execute("""SELECT * FROM Hotel WHERE hotel_id = %s""", (hotel_id,))
    if cur.fetchone() is None:
        print("Try again! A hotel with this id does not exist.")
        cur.close()
        conn.close()
        return

    room_number = input("Enter room number: ").strip()

    cur.execute("""SELECT * FROM Room WHERE hotel_id = %s AND room_number = %s""", (hotel_id,room_number))
    if cur.fetchone() is not None:
        print("Try again! This room number in this hotel already exists.")
        cur.close()
        conn.close()
        return

    windows     = input("Enter number of windows: ").strip()
    ren_year    = input("Enter renovation year: ").strip()
    access      = input("Enter access type (elevator/stairs): ").strip().lower()

    if access not in ("elevator", "stairs"):
        print("Invalid access tye. Must be 'elevator' or 'stairs'.")
        return
    
    cur.execute(""" 
        INSERT INTO Room (hotel_id, room_number, windows, renovation_year, access_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (hotel_id, room_number, windows, ren_year, access))

    conn.commit()
    cur.close()
    conn.close()
    print("Room added successfully!")

def updateRoom():
    hotel_id    = input("Enter hotel ID: ").strip()
    room_number = input("Enter room number: ").strip()

    #check if hotel_id and room_number combination exists
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT * FROM Room
        WHERE hotel_id = %s AND room_number = %s
        """, (hotel_id, room_number))
    
    if cur.fetchone() is None:
        print("No room found with that hotel ID and room number.")
        cur.close()
        conn.close()
        return

    windows     = input("Enter number of windows: ").strip()
    ren_year    = input("Enter renovation year: ").strip()
    access      = input("Enter access type (elevator/stairs): ").strip().lower()

    if access not in ("elevator", "stairs"):
        print("Invalid access tye. Must be 'elevator' or 'stairs'.")
        return

    cur.execute(""" 
        UPDATE Room
        SET windows = %s, renovation_year = %s, access_type = %s
        WHERE hotel_id = %s AND room_number = %s
    """, (windows, ren_year, access, hotel_id, room_number))

    if cur.rowcount == 0:
        print("No room found with that hotel ID and room number.")
    else:
        print("Room updated successfully!")

    conn.commit()
    cur.close()
    conn.close()

def deleteRoom():
    hotel_id    = input("Enter hotel ID: ").strip()
    room_number = input("Enter room number to delete: ").strip()

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        DELETE FROM Room
        WHERE hotel_id = %s AND room_number = %s
    """, (hotel_id, room_number))

    if cur.rowcount == 0:
        print("No room found with that hotel ID and room number.")
    else:
        print("Room deleted successfully!")

    conn.commit()
    cur.close()
    conn.close()

# === Remove Client ===
def removeClient():
    email = input("Enter client email to remove: ").strip()

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""DELETE FROM Lives_At WHERE email = %s""", (email,))
    cur.execute("""DELETE FROM CreditCard WHERE email = %s""", (email,))
    cur.execute("""DELETE FROM Booking WHERE email = %s""", (email,))

    cur.execute("""DELETE FROM Client WHERE email = %s""", (email,))

    if cur.rowcount == 0:
        print("No client found with that email.")
    else:
        print("Client removed successfully")

    conn.commit()
    cur.close()
    conn.close()