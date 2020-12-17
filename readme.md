

Бизнес логика наше клиентского приложения заключается в том, чтобы решать вполне определенную бизнес задачу, которая вознакла у нашего проекта уже на данном этапе. 

Этот бот будут использовать два типа нашего бота: операторы и студенты. У каждого из них свой функционал. Студенты могут просмотаривать свое расписание и ближайшие дедлайны. Операторы же могут подтверждать свое участие в лекции, могут отменять свое решение и также могут получить список предстоящих назначенных съемок и назначить дедлайн.
Все эти действия происходят с помощью SQL запросов к нашей базе. 

**РЕГИСТРАЦИЯ**:

Для регистрации клиента в приложении мы должны запросить у него данные, которые помогут идентифицировать нам данного пользователя в таблице со студентами или операторами. В данном случае используем (Имя Фамилии группа/email). И при успешном находе нужной строчки, проверяем есть ли такой chat_id где-то уже в таблице и не записан ли в нужную строчку уже какой-то chat_id. В случае успеха делаем UPDATE в базе и вставляем chat_id пользователя в базу. Чтобы в дальнейшем более удобно обрабатывать запросы данного клиента.

проверка на наличие старого значения в таблице

SELECT chat_id FROM Operators
WHERE name = ?
AND email = ?

проверка что такой чат айди уже был в таблице (повторная регистрация)

SELECT chat_id FROM Operators
WHERE chat_id = ?

обновление значения таблицы 

UPDATE Operators SET chat_id = ?
WHERE name = ? 
AND email = ?


**ПОДТВЕРЖДЕНИЯ ОПЕРАТОРОВ**
У каждого занятие есть атрибу confirmed, по умолчанию = 0. За 24ч до этого занятия его съемку можно подтвердить. При нажатии команды /confirm оператору приходит запрос о его ближайшей неподтвержденной лекции. И выбрав один из вариантов ответа оператор подтверждает свое учатие или отказ. Данная информация тоже фиксируется в базе.
Также командой /abort оператор может сбросить все свои подтверждения и проставить их заново.

получить ближайшую неподтвержденную лекцию для оператора

SELECT DISTINCT Classes.id_class, Classes.name, Classes.type, MIN(Classes_Groups.start_time) FROM Operators
JOIN Classes_Operators ON Operators.id_operator = Classes_Operators.id_operator
JOIN Classes ON Classes_Operators.id_class = Classes.id_c
JOIN Classes_Groups ON Classes.id_class = Classes_Groups.id_c
WHERE Operators.chat_id = ? 
AND Classes_Groups.start_time >= date("NOW")
AND Classes_Groups.start_time < date("NOW", "+1 day")
AND Classes.confirmed == '0'

обновить атрибут confirmed у данной лекии

UPDATE Classes SET confirmed = ?
WHERE id_class = ?




**РАСПИСАНИЕ СЪЕМОК ОПЕРАТОРА**
По данной команде оператор получает список занятий, на которые он назначен в качестве оператора.

получить все лекции, которые должен снимать данный оператор на заданное количество дней 

SELECT DISTINCT Classes.id_class, Classes.name, Classes.type, Classes_Groups.start_time, Claconfirmed FROM Operators
JOIN Classes_Operators ON Operators.id_operator = Classes_Operators.id_operator
JOIN Classes ON Classes_Operators.id_class = Classes.id_cl
JOIN Classes_Groups ON Classes.id_class = Classes_Groups.id_clas
WHERE Operators.chat_id = ?
AND Classes_Groups.start_time >= date("2020-12-20")
AND Classes_Groups.start_time < date("2020-12-20", ?)
ORDER BY Classes_Groups.start_t



**ВЫСТАВЛЕНИЕ ДЕДЛАЙНА ОПЕРАТОРА**
По данной команде оператор сначала выбирает, на какое из назначенных ему занятий он будет выставлять дедлайн. ПоСле выбора он вводит время и сам текст и отправляет его. Происходит INSERT в таблицу Deadlines.


создать новый дедлайн

INSERT INTO Deadlines VALUES
(?, ?, ?, '-', DATE("now"), ?)
   
триггер добавить записи о новом дедлайне в табличку связи дедлайнов и груп

получить все группы у которых идет данное занятие

SELECT id_group FROM Classes_Groups
WHERE id_class = ?

вставить нужные значения в Groups_Deadlines

INSERT INTO Groups_Deadlines VALUES
(?, ?)

**РАСПИСАНИЕ СТУДЕНТА**
По данной команде студент получает свое расписание будущих занятий на определенное количество дней.

SELECT Classes.name, Classes.type, Classes_Groups.start_time FROM Stud
JOIN Groups_Students ON Students.id_student = Groups_Students.id_student
JOIN Groups ON Groups_Students.id_group = Groups.id_g
JOIN Classes_Groups ON Classes_Groups.id_group = Groups.id_group
JOIN Classes ON Classes.id_class = Classes_Groups.id_c
WHERE Students.chat_id = ?
AND Classes_Groups.start_time >= date("2020-12-19")
AND Classes_Groups.start_time < date("2020-12-19", ?)
ORDER BY Classes_Groups.start_time

**ДЕДЛАЙНЫ СТУДЕНТА**
По данной команде студент получает свои дедлайны на определенное количество дней.

SELECT Deadlines.name, Deadlines.time_date, Deadlines.link_to_folder_with_tasks FROM Deadlines
JOIN Groups_Deadlines ON Groups_Deadlines.id_deadline = Deadlines.id_deadline
JOIN Groups ON Groups.id_group = Groups_Deadlines.id_g
JOIN Groups_Students ON Groups_Students.id_group = Groups.id_group
JOIN Students ON Students.id_student = Groups_Students.id_stu
WHERE Students.chat_id = ?
AND Deadlines.time_date >= date("2020-12-19")
AND Deadlines.time_date < date("2020-12-19"
ORDER BY Deadlines.time_date








