CREATE TABLE Client (
    email VARCHAR(100),
    name VARCHAR(100) NOT NULL,
	PRIMARY KEY (email)
);

CREATE TABLE Managers (
    ssn VARCHAR(11),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
	PRIMARY KEY (ssn)
);

CREATE TABLE Address (
    street_name VARCHAR(100),
    num VARCHAR(20),
    city VARCHAR(100),
    PRIMARY KEY (street_name, num, city)
);

CREATE TABLE Hotel (
    hotel_id INT,
    hotel_name VARCHAR(100) NOT NULL,
    street_name VARCHAR(100) NOT NULL,
    num VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
	PRIMARY KEY (hotel_id),
    FOREIGN KEY (street_name, num, city) REFERENCES Address(street_name, num, city)
);

CREATE TABLE Room (
    hotel_id INT,
    room_number INT,
    windows INT NOT NULL,
    renovation_year INT,
    access_type VARCHAR(20) NOT NULL
        CHECK (access_type IN ('elevator', 'stairs')),
    PRIMARY KEY (hotel_id, room_number),
    FOREIGN KEY (hotel_id) REFERENCES Hotel(hotel_id)
);

CREATE TABLE Lives_At (
    email VARCHAR(100),
    street_name VARCHAR(100),
    num VARCHAR(20),
    city VARCHAR(100),
    PRIMARY KEY (email, street_name, num, city),
    FOREIGN KEY (email) REFERENCES Client(email),
    FOREIGN KEY (street_name, num, city) REFERENCES Address(street_name, num, city)
);

CREATE TABLE CreditCard (
    credit_card_number VARCHAR(50),
    email VARCHAR(100) NOT NULL,
    street_name VARCHAR(100) NOT NULL,
    num VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
	PRIMARY KEY (credit_card_number),
    FOREIGN KEY (email) REFERENCES Client(email),
    FOREIGN KEY (street_name, num, city) REFERENCES Address(street_name, num, city)
);

CREATE TABLE Booking (
    booking_id INT,
    email VARCHAR(100) NOT NULL,
    hotel_id INT NOT NULL,
    room_number INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    price_per_day NUMERIC NOT NULL,
	PRIMARY KEY (booking_id),
    FOREIGN KEY (email) REFERENCES Client(email),
    FOREIGN KEY (hotel_id, room_number)
        REFERENCES Room(hotel_id, room_number),

    CONSTRAINT valid_dates CHECK (end_date >= start_date)
);

CREATE TABLE Review (
    hotel_id INT,
    review_id INT,
    review_message TEXT,
    rating INT CHECK (rating >= 0 AND RATING <= 10),
    PRIMARY KEY (hotel_id, review_id),
    FOREIGN KEY (hotel_id) REFERENCES Hotel(hotel_id)
);