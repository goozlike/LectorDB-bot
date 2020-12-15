CREATE TABLE Classes (
    id_class INT PRIMARY KEY,
    type VARCHAR(1024),
    name VARCHAR(1024),
    confirmed INT,
    link_to_folder_with_materials VARCHAR(1024),
    link_to_record VARCHAR(1024)
);

CREATE TABLE Disciplines (
    id_discipline INT PRIMARY KEY,
    name VARCHAR(1024),
    year INT
);


CREATE TABLE Groups (
    id_group INT PRIMARY KEY,
    id_discipline INT,
    FOREIGN KEY (id_discipline) REFERENCES Disciplines(id_discipline)
);


CREATE TABLE Students (
    id_student INT PRIMARY KEY,
    number_of_group INT,
    name VARCHAR(1024),
    year INT,
    chat_id VARCHAR(1024)
);

CREATE TABLE Operators (
    id_operator INT PRIMARY KEY,
    name VARCHAR(1024),
    email VARCHAR(1024),
    phone_number VARCHAR(1024),
    chat_id VARCHAR(1024)
);

CREATE TABLE Deadlines (
    id_deadline INT PRIMARY KEY,
    time_date DATETIME,
    name VARCHAR(1024),
    link_to_folder_with_tasks VARCHAR(1024),
    time_date_of_setting DATETIME,
    id_operator INT,
    FOREIGN KEY (id_operator) REFERENCES Operators(id_operator)
);

CREATE TABLE Ads (
    id_announcement INT PRIMARY KEY,
    time_date_of_setting DATETIME,
    id_operator INT, 
    FOREIGN KEY (id_operator) REFERENCES Operators(id_operator)
);



CREATE TABLE Classes_Groups (
    id_class INT,
    id_group INT, 
    format VARCHAR(1024), 
    venue VARCHAR(1024),
    start_time DATETIME,
    FOREIGN KEY (id_group) REFERENCES Groups(id_group),
    FOREIGN KEY (id_class) REFERENCES Classes(id_class),
    CONSTRAINT PK_class_group PRIMARY KEY(id_class, id_group)
);


CREATE TABLE Classes_Operators (
    id_class INT,
    id_operator INT,
    priority INT, 
    FOREIGN KEY (id_class) REFERENCES Classes(id_class),
    FOREIGN KEY (id_operator) REFERENCES Operators(id_operator),
    CONSTRAINT PK_class_op PRIMARY KEY (id_class, id_operator)
);


CREATE TABLE Groups_Students (
    id_group INT,
    id_student INT, 
    FOREIGN KEY (id_group) REFERENCES Groups(id_group),
    FOREIGN KEY (id_student) REFERENCES Students(id_student),
    CONSTRAINT PK_group_stud PRIMARY KEY (id_group, id_student)
);

CREATE TABLE Groups_Ads (
    id_group INT,
    id_announcement INT, 
    FOREIGN KEY (id_group) REFERENCES Groups(id_group),
    FOREIGN KEY (id_announcement) REFERENCES Ads(id_announcement),
    CONSTRAINT PK_group_ann PRIMARY KEY (id_group, id_announcement)
);

CREATE TABLE Groups_Deadlines (
    id_group INT,
    id_deadline INT, 
    FOREIGN KEY (id_group) REFERENCES Groups(id_group),
    FOREIGN KEY (id_deadline) REFERENCES Deadlines(id_deadline),
    CONSTRAINT PK_group_dedl PRIMARY KEY (id_group, id_deadline)
);


