# Схема базы данных

## User - Пользователь +
- id +
- gh_username +
- tg_username +
+ first_name  +
- last_name +
- group_ids - many-to-many +
- is_staff +
- is_active +

## Group - Группа +
- id +
- name - [Кураторы, Обучающиеся] +

## Course - Курс +
- id +
- name +
- description +

## Enrollment - Набор (Поток) +
- id +
- course_id +
- number +
- start +
- finish +

## Team - Группа из набора
- id
- enrollment_id
- name - [LP5_1, LPA5_2, ..., LP{t}{i}{j}]
- tutor_id - (user_id) one-to-many
- students - (user_id) many-to-many

## Track - Трек
- id
- course_id
- name
- description

## Lesson - Учебный материал
- id
- track_id
- name
- description
- content
- youtube_url
- googleslides_url
- github_url

## Challenge - Задание
- id
- course_id
- name
- description
- content
- github_url


## Homework - Домашняя работа
- id
- user_id
- сhallenge_id
- github_url
- status


## Week - Неделя
- id
- number
- description
- lesson_ids - many-to-many
- challenge_ids  - many-to-many

## Program - Программа курса
- id
- name
- description
- course_id
- enrollment_ids - many-to-many
- week_ids - many-to-many
