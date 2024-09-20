-- one to one
CREATE TABLE Person (
    id INT PRIMARY KEY,
    name VARCHAR(255)
);
  
CREATE TABLE Passport (
    id INT PRIMARY KEY,
    number VARCHAR(20),
    person_id INT UNIQUE,
    FOREIGN KEY (person_id) REFERENCES Person(id)
);

-- one to many
CREATE TABLE Department (
    id INT PRIMARY KEY,
    name VARCHAR(255)
);
  
CREATE TABLE Employee (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES Department(id)
);

-- many to many
CREATE TABLE Student (
    ID INT PRIMARY KEY,
    Name VARCHAR(255),
    Age INT
);
CREATE TABLE Course (
    CourseID INT PRIMARY KEY,
    CourseName VARCHAR(255)
);
CREATE TABLE Enrollment (
    StudentID INT,
    CourseID INT,
    Grade VARCHAR(10),
    FOREIGN KEY (StudentID) REFERENCES Student(ID),
    FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);