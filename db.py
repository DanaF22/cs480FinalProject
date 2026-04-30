import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, date

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="cs480FinalProject",
        # database="cs480Project",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

#1 user can register as a manager by providing name, SSN, and email.
def managerRegister(name, ssn, email):
    connection = get_connection()
    cursor = connection.cursor()

    # check if ssn already exists
    cursor.execute("""SELECT * FROM managers WHERE ssn = %s""", (ssn,))
    if cursor.fetchone() is not None:
        print("Try again! A manager with this SSN already exists.")
        cursor.close()
        connection.close()
        return

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
        SELECT c.email, c.name, hotel_id, room_number, b.price_per_day, end_date - start_date AS days
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
    today = date.today()

    convertedStartDate = datetime.strptime(inputStartDate, correctFormat).date()
    convertedEndDate = datetime.strptime(inputEndDate, correctFormat).date()


    # continue to ask for input until user inputs a correct format
    while not (checkStart and checkEnd) or inputEndDate < inputStartDate or (convertedStartDate < today or convertedEndDate < today):
        print("Try again. Incorrect input of date/s")
        inputStartDate = input("Enter Start Date (yyyy-mm-dd): ")
        inputEndDate = input("Enter End Date (yyyy-mm-dd): ")
       
        checkStart = checkDateInput(inputStartDate, correctFormat)
        checkEnd = checkDateInput(inputEndDate, correctFormat)

        convertedStartDate = datetime.strptime(inputStartDate, correctFormat).date()
        convertedEndDate = datetime.strptime(inputEndDate, correctFormat).date()


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

    # if there are no avaialble rooms
    if len(availableRooms) == 0:
        print("No available rooms for requested date range")
        return
    
    print("All available rooms for inputted date range: ")
    
    for room in availableRooms: 
        print("Room #: ", room[0], " Hotel: ", room[1])

# client books specific room based on date range
def bookSpecificRoom(email):
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
       
        # create booking
        cursor.execute("""
            INSERT INTO Booking (email, hotel_id, room_number, start_date, end_date, price_per_day)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (email,hotelId, chosenRoom, start, end, pricePerDay))

        connection.commit()

        cursor.close()
        connection.close()
        print("Room booked successfully!")

# automatic booking of room
def automaticBooking(email):
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
            hotelId = room[2]
            chosenRoomNum = room[0]

            # automatically create booking
            cursor.execute("""
                INSERT INTO Booking (email, hotel_id, room_number, start_date, end_date, price_per_day)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (email, hotelId, chosenRoomNum, start, end, pricePerDay))
            connection.commit()

            print("Room number: ", chosenRoomNum, "at ", chosenHotel, " booked sucessfully for date range: ", start, "-", end)
            break
    cursor.close()
    connection.close()
    
    if not foundSpecifiedHotel:
        print("No room available at ", chosenHotel, " Here are other hotels that have an available room for date range ", start, "-", end, ": ")
        print(availableHotels)


def clientRegister(name, email, addresses, credit_cards):
    connection = get_connection()
    cursor = connection.cursor()

    #insert client info into Client table
    cursor.execute("""INSERT INTO Client (email, name) 
                   VALUES (%s, %s)""", (email, name))

    #insert the client's addresses into Address table and LivesAt table
    for address in addresses:
        cursor.execute("""INSERT INTO Address (street_name, num, city)
                       VALUES (%s, %s, %s) ON CONFLICT DO NOTHING""", (address['street_name'], address['num'], address['city']))
        
        cursor.execute ("""INSERT INTO Lives_At (email, street_name, num, city)
                        VALUES (%s, %s, %s, %s)""", (email, address['street_name'], address['num'], address['city']))
                       
    #insert the client's addresses into Address table and CreditCard table
    for card in credit_cards:
        cursor.execute("""INSERT INTO Address (street_name, num, city)
                       VALUES (%s, %s, %s) ON CONFLICT DO NOTHING""", (card['street_name'], card['num'], card['city']))

        cursor.execute("""INSERT INTO CreditCard (credit_card_number, email, street_name, num, city)
                       VALUES (%s, %s, %s, %s, %s)""", (card['credit_card_number'], email, card['street_name'], card['num'], card['city']))

    connection.commit()
    cursor.close()
    connection.close()

    print("Client is registered!")


def clientLogin(email):
    connection = get_connection()
    cursor = connection.cursor()

    #checking if the client exists
    cursor.execute("SELECT name FROM Client WHERE email = %s", (email,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result:
        print(f"\nWelcome, {result[0]}!")
        return True
    else:
        print("No client found with that email.")
        return False


def updateClientInfo(email, new_name, new_addresses, new_credit_cards):
    connection = get_connection()
    cursor = connection.cursor()

    #update the client's name
    cursor.execute("""UPDATE Client SET name = %s WHERE email = %s""", (new_name, email))

    #delete old addresses and credit cards
    cursor.execute("""DELETE FROM Lives_At WHERE email = %s""", (email,))
    cursor.execute("""DELETE FROM CreditCard WHERE email = %s""", (email,))

    #insert new addresses and credit cards
    for address in new_addresses:
        cursor.execute("""INSERT INTO Address (street_name, num, city)
                       VALUES (%s, %s, %s) ON CONFLICT DO NOTHING""", (address['street_name'], address['num'], address['city']))
        
        cursor.execute ("""INSERT INTO Lives_At (email, street_name, num, city)
                        VALUES (%s, %s, %s, %s)""", (email, address['street_name'], address['num'], address['city']))
                       
    for card in new_credit_cards:
        cursor.execute("""INSERT INTO Address (street_name, num, city)
                       VALUES (%s, %s, %s) ON CONFLICT DO NOTHING""", (card['street_name'], card['num'], card['city']))

        cursor.execute("""INSERT INTO CreditCard (credit_card_number, email, street_name, num, city)
                       VALUES (%s, %s, %s, %s, %s)""", (card['credit_card_number'], email, card['street_name'], card['num'], card['city']))

    connection.commit()
    cursor.close()
    connection.close()

    print("Client information updated!")


def viewAllBookings(email):
    connection = get_connection()
    cursor = connection.cursor()

    #fetches all the bookings for the client and calculates the total cost per booking 
    cursor.execute("""
        SELECT 
            b.hotel_id, h.hotel_name, b.room_number, b.start_date,b.end_date,
            GREATEST(b.end_date - b.start_date,1) * b.price_per_day AS total_cost
        FROM Booking b
        JOIN Hotel h ON b.hotel_id = h.hotel_id
        WHERE b.email = %s
        ORDER BY b.start_date DESC
        """, (email,)
    )

    allBookings = cursor.fetchall()

    #displays all the bookings for the client with the total cost for each booking
    if allBookings:
        print("\nYour Bookings:")
        for booking in allBookings:
            print(f"Hotel ID: {booking[0]}, Hotel Name: {booking[1]}, Room: {booking[2]}, Check-in: {booking[3]}, Check-out: {booking[4]}, Total Cost: ${booking[5]:.2f}")
    else:
        print("You have no bookings.")

    cursor.close()
    connection.close()


def submitReview(email, hotel_id):
    connection = get_connection()
    cursor = connection.cursor()

    #check if the client booking exists 
    cursor.execute("""SELECT * FROM Booking WHERE email = %s AND hotel_id = %s LIMIT 1""", (email, hotel_id))

    if cursor.fetchone() is None:
        print("You have not stayed at this hotel so you cannot submit a review.")
        cursor.close()
        connection.close()
        return

    rating = int(input("Enter rating (1-10): ").strip())
    comment = input("Enter review comment: ").strip()

    #create a review_id
    cursor.execute("""SELECT COALESCE(MAX(review_id), 0) + 1 FROM Review WHERE hotel_id = %s""", (hotel_id,))
    
    review_id = cursor.fetchone()[0]

    #insert the client's review into the Review table
    cursor.execute("""INSERT INTO Review (hotel_id, review_id, review_message, rating)
                    VALUES (%s, %s, %s, %s)""", (hotel_id, review_id, comment, rating))

    connection.commit()
    cursor.close()
    connection.close()

    print("Review submitted!")