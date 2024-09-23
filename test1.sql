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