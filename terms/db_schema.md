# Схема базы данных

## USER APP

### User - Пользователь
- id
- gh_username
- tg_username
- first_name 
- last_name
- group_ids - many-to-many
- is_staff
- is_active

### Group - Группа
- id
- name - [Кураторы, Обучающиеся]


## COURSE APP

### Course - Курс
- id
- name
- description

### Enrollment - Набор (Поток)
- id
- course_id
- number
- start
- finish

### Team - Группа из набора
- id
- enrollment_id
- tutor_id - (user_id) one-to-many
- students - (user_id) many-to-many

### Track - Трек
- id
- course_id
- name
- description


## LEARN APP

### Lesson - Учебный материал
- id 
- track_id
- name 
- content
- video
- slide
- repo
- url

### Challenge - Задание
- id
- track_id
- name
- content
- repo

### Homework - Домашняя работа
- id
- user_id
- challenge_id
- github_url
- status

### Week - Неделя
- id
- course_id
- number
- description
- lesson_ids - many-to-many
- challenge_ids  - many-to-many

### Program - Программа курса
- id
- name
- description
- course_id
- enrollment_ids - many-to-many
- week_ids - many-to-many
