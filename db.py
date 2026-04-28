import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="cs480Project",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

#1 user can register as a manager by providing name, SSN, and email.
def managerRegister(name, ssn, email):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO managers (ssn, full_name, email) VALUES (%s, %s, %s)""", (ssn, name, email))
    connection.commit()
    cursor.close()
    connection.close()
    print("Manager is registered!!!")

#1 manager can log in using their SSN
def managerLogin(ssn):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT full_name
        FROM managers
        WHERE ssn = %s
        """, (ssn,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        print(result[0], "is successfully registered!")
    else:
        print("Error. No manager exists with this SSN")

#4 top-k clients based on the number of bookings.
def topClients(k):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT c.name, c.email
        FROM Client c
        JOIN Booking b
        ON c.email = b.email
        GROUP BY c.name, c.email
        ORDER BY count(*) DESC
        LIMIT %s
        """, (k,))
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    print("\nTop clients by the number of bookings: ")

    for i in results:
        print("Client's name:", i[0])
        print(" Email:", i[1])
        print("-------------------------")

#5 generate a list of all hotel rooms + number of bookings for each room
def listOfRooms():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT r.hotel_id, r.room_number, count(b.booking_id) AS numBookings
        FROM Room r
        LEFT JOIN Booking b
        ON b.hotel_id = r.hotel_id AND b.room_number = r.room_number
        GROUP BY r.hotel_id, r.room_number
        ORDER BY numBookings DESC
        """)
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    print("\nList of all hotel rooms and number of bookings for each room:")

    for i in results:
        print("Hotel id:", i[0])
        print("Room number:", i[1])
        print("Number of bookings: ", i[2])
        print("-------------------------")

#6 : for every hotel X show name, total number of bookings, average rating
def listOfHotels():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT h.hotel_name, count(DISTINCT b.booking_id) as numBookings, round(avg(r.rating), 3) as avgRating
        FROM Hotel h
        LEFT JOIN Booking b
        ON h.hotel_id = b.hotel_id
        LEFT JOIN Review r
        ON h.hotel_id = r.hotel_id
        GROUP BY h.hotel_name
        ORDER BY avgRating DESC
        """)
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    print("\nList of hotel names, their total number of bookings and their average rating:\n")
    for i in results:
        print("Hotel's name:", i[0])
        print("Number of bookings:", i[1])
        print("Average rating: ", i[2])
        print("-------------------------")

#7 two cities C1 and C2
def twoCities(C1, C2):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
    WITH C1 AS(
        SELECT c.name, c.email
        FROM Client c
        JOIN Lives_At l
        ON c.email = l.email
        WHERE l.city = %s
    ),
    
    C2 AS(
        SELECT c.name, c.email
        FROM Client c
        JOIN Booking b
        ON c.email = b.email
        JOIN Hotel h
        ON h.hotel_id = b.hotel_id
        WHERE h.city = %s
    )
    
    SELECT C1.name, C1.email
    FROM C1
    JOIN C2 ON C2.name = C1.name AND C2.email = C1.email
    """, (C1, C2))

    results = cursor.fetchall()
    cursor.close()
    connection.close()

    print("\nList of clients that have address and booked a hotel in two cities:\n")
    for i in results:
        print("Client's name:", i[0])
        print("Client's email:", i[1])
        print("-------------------------")


#8 problematic hotels
def problematicHotels():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
    WITH rating AS(
        SELECT h.hotel_id, h.hotel_name, avg(r.rating) as avgRating
        FROM Hotel h
        LEFT JOIN Review r
        ON h.hotel_id = r.hotel_id
        WHERE h.city = 'Chicago'
        GROUP BY h.hotel_name, h.hotel_id
        HAVING avg(r.rating) < 2
        ORDER BY avgRating DESC
    ),

    clientsAddress AS(
        SELECT b.hotel_id, count(DISTINCT b.email) AS numClients
        FROM Client c
        JOIN Booking b
        ON c.email = b.email
        JOIN Lives_At l
        ON c.email = l.email
        WHERE l.city != 'Chicago' 
        GROUP BY b.hotel_id
        HAVING count(DISTINCT b.email)>= 2
    )

    SELECT r.hotel_name
    FROM rating r
    JOIN clientsAddress ca
    ON r.hotel_id = ca.hotel_id
    """)
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    print("\nList of problematic hotels:\n")
    for i in results:
        print("Hotel's name:", i[0])
        print("-------------------------")

#9 Clients and total amount spent
def totalAmountSpent():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
    WITH calcInfo as(
        SELECT c.email, c.name, hotel_id, room_number, b.price_per_day, end_date-start_date AS days
        FROM Client c
        JOIN Booking b
        ON c.email = b.email
    ),

    spent AS(
        SELECT name, SUM(days*price_per_day) AS spent
        FROM calcInfo
        GROUP BY email, name 
    )

    SELECT name, spent
    FROM spent
    ORDER BY spent DESC
    """)
    
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    print("\nList of clients and todal amount they spent on bookings:\n")
    for i in results:
        print("Client's name:", i[0])
        print("Total amount spent:", i[1])
        print("-------------------------")



# check if date format is correct
def checkDateInput(actualDate, correctFormat):
    try:
        datetime.strptime(actualDate, correctFormat)
        return True
    except ValueError:
        return False

# get input of a start and ending date to check room availability
def inputDatesBooking():
    # get date input
    inputStartDate = input("Enter Start Date (yyyy-mm-dd): ")
    inputEndDate = input("Enter End Date (yyyy-mm-dd): ")

    correctFormat = "%Y-%m-%d"
    checkStart = checkDateInput(inputStartDate, correctFormat)
    checkEnd = checkDateInput(inputEndDate, correctFormat)

    # continue to ask for input until user inputs a correct format
    while not (checkStart and checkEnd) or inputEndDate < inputStartDate:
        print("Try again. Incorrect input of date/s")
        inputStartDate = input("Enter Start Date (yyyy-mm-dd): ")
        inputEndDate = input("Enter End Date (yyyy-mm-dd): ")
       
        checkStart = checkDateInput(inputStartDate, correctFormat)
        checkEnd = checkDateInput(inputEndDate, correctFormat)

    return inputStartDate, inputEndDate

# find all available rooms based on inputted dates
def findAvailableRooms():
    inputStartDate, inputEndDate = inputDatesBooking()

    inputStartDate = datetime.strptime(inputStartDate, "%Y-%m-%d").date()
    inputEndDate = datetime.strptime(inputEndDate, "%Y-%m-%d").date()

    # get all available hotel rooms based on date range
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT r.room_number, h.hotel_name, h.hotel_id
        FROM Room r
        JOIN Hotel h ON r.hotel_id = h.hotel_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM Booking b 
            WHERE b.hotel_id = r.hotel_id
            AND b.room_number = r.room_number
            AND b.start_date <= %s
            AND b.end_date >= %s 
        )
    """, (inputEndDate, inputStartDate))
    
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return results, inputStartDate, inputEndDate

# print available rooms for specified dates
def printAvailableRooms():
    availableRooms, _, _ = findAvailableRooms()

    print("All available rooms for inputted time range: ")
    for room in availableRooms: 
        print("Room #: ", room[0], " Hotel: ", room[1])

# client books specific room based on date range
def bookSpecificRoom():
    # first get input of specific room
    chosenHotel = input("Enter Hotel Name: ")
    chosenRoom = int(input("Enter Room number: "))
    
    # then see if the room is available
    availableRooms, start, end = findAvailableRooms()

    pairingAvailableOrValid = False

    # check if room and hotel pairing are available/exists
    for room in availableRooms:
        if room[0] == chosenRoom and room[1] == chosenHotel:
            pairingAvailableOrValid = True
            break
    
    # either room pairing is available/exists or does not
    if not pairingAvailableOrValid:
        print("Room either not available or does not exist")
    else:
        print("Room available for booking!")
        
        connection = get_connection()
        cursor = connection.cursor()

        # get hotel id
        cursor.execute("""
            SELECT hotel_id
            FROM HOTEL
            WHERE hotel_name = %s
        """, (chosenHotel,))

        hotel = cursor.fetchone()

        if not hotel:
            print("Hotel not found.")
            cursor.close()
            connection.close()
            return
        
        hotelId = hotel[0]
        pricePerDay = 150
       
        # get client info
        currentClientEmail = "" #replace later with whatever clients email is

        # create booking
        cursor.execute("""
            INSERT INTO Booking (email, hotel_id, room_number, start_date, end_date, price_per_day)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (currentClientEmail,hotelId, chosenRoom, start, end, pricePerDay))

        connection.commit()

        cursor.close()
        connection.close()
        print("Room booked successfully!")

# automatic booking of room
def automaticBooking():
    # get hotel name
    chosenHotel = input("Enter Hotel Name: ")
    
    # enter date range and find all available rooms
    availableRooms, start, end = findAvailableRooms()
    
    if len(availableRooms) == 0:
        print("No room available for this date range at any hotel")
        return
    
    foundSpecifiedHotel = False
    
    availableHotels = set()
    chosenRoomNum = -1

    connection = get_connection()
    cursor = connection.cursor()

    # look for available rooms at specified hotel and date
    for room in availableRooms:
        availableHotels.add(room[1])
        if room[1] == chosenHotel:
            foundSpecifiedHotel = True
            # create a booking for a room
            pricePerDay = 150
       
            # get client info
            currentClientEmail = "" #replace later with whatever clients email is
            hotelId = room[2]
            chosenRoomNum = room[0]

            # automatically create booking
            cursor.execute("""
                INSERT INTO Booking (email, hotel_id, room_number, start_date, end_date, price_per_day)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (currentClientEmail, hotelId, chosenRoomNum, start, end, pricePerDay))
            connection.commit()

            print("Room number: ", chosenRoomNum, "at ", chosenHotel, " booked sucessfully for date range: ", start, "-", end)
            break
    cursor.close()
    connection.close()
    
    if not foundSpecifiedHotel:
        print("No room available at ", chosenHotel, " Here are other hotels that have an available room for date range ", start, "-", end, ": ")
        print(availableHotels)