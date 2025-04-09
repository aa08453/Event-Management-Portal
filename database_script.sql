CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255),
    email NVARCHAR(255) UNIQUE,
    password NVARCHAR(255)
);

CREATE TABLE Students (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Admins (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Organizers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Venues (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255),
    capacity INT,
    availability BIT
);

CREATE TABLE Events (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255),
    event_type NVARCHAR(255),
    description NVARCHAR(MAX),
    datetime DATETIME,
    venue_id INT,
    organizer_id INT,
    is_paid BIT,
    FOREIGN KEY (venue_id) REFERENCES Venues(id),
    FOREIGN KEY (organizer_id) REFERENCES Organizers(id)
);

CREATE TABLE Volunteers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    event_id INT,
    student_id INT,
    role NVARCHAR(255),
    FOREIGN KEY (event_id) REFERENCES Events(id),
    FOREIGN KEY (student_id) REFERENCES Students(id)
);

CREATE TABLE Payments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    amount FLOAT,
    status NVARCHAR(255),
    method NVARCHAR(255)
);

CREATE TABLE Reports (
    id INT IDENTITY(1,1) PRIMARY KEY,
    generated_by INT,
    date_generated DATE,
    event_id INT,
    FOREIGN KEY (generated_by) REFERENCES Admins(id),
    FOREIGN KEY (event_id) REFERENCES Events(id)
);

CREATE TABLE Attendees (
    id INT IDENTITY(1,1) PRIMARY KEY,
    studentid INT,
    eventid INT,
    paymentid INT NULL,
    FOREIGN KEY (studentid) REFERENCES Students(id),
    FOREIGN KEY (eventid) REFERENCES Events(id),
    FOREIGN KEY (paymentid) REFERENCES Payments(id)
);

CREATE TABLE Event_Organizers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    organizerid INT,
    eventid INT,
    FOREIGN KEY (organizerid) REFERENCES Organizers(id),
    FOREIGN KEY (eventid) REFERENCES Events(id)
);