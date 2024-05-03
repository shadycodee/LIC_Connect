-- Table: Login_Sessions

CREATE TABLE Login_Sessions (
    sessionID INT PRIMARY KEY,
    studentID VARCHAR(20),
    login_time DATETIME,
    logout_time DATETIME,
    consumed_time INT,
    time_left INT DEFAULT 600,
    FOREIGN KEY (studentID) REFERENCES Student(studentID)
);

-- Table: Student
CREATE TABLE Student (
    studentID VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    course VARCHAR(255),
    password VARCHAR(255),
    time_left INT DEFAULT 600
);

-- Table: Payments
CREATE TABLE Payments (
    studentID VARCHAR(10),
    amount INT,
    time DATETIME,
    date DATETIME,
    FOREIGN KEY (studentID) REFERENCES Student(studentID)
);

-- HAHAHAHA