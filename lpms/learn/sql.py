admin_progress_header = """
SELECT
course.id as course_id,
course."name" as course_name,
lweek.number as week_num,
track.name as track_name,
enrollment.number as enrollment_num,
team.id as team_id,
CONCAT(tutor.first_name, ' ', tutor.last_name) as tutor,
tutor.id as tutor_id,
challenge_name

FROM course_course as course

JOIN course_enrollment as enrollment
ON enrollment.course_id = course.id

JOIN course_team as team
ON enrollment.id = team.enrollment_id

JOIN user_user as tutor
ON team.tutor_id = tutor.id

JOIN course_track as track
ON course.id = track.course_id

JOIN learn_program_enrollments as lpe
ON lpe.enrollment_id = enrollment.id

JOIN learn_program as lprogram
ON lprogram.id = lpe.program_id

JOIN learn_program_weeks as lpw
ON lpw.program_id = lprogram.id

JOIN learn_week as lweek
ON lweek.id = lpw.week_id

LEFT JOIN (
SELECT
course.id as course_id,
lweek.id as week_id,
track.id as track_id,
challenge.id as challenge_id,
course.name as course_name,
lweek.number as week_num,
track.name as track_name,
challenge."name" as challenge_name

FROM learn_challenge as challenge

JOIN course_track as track
ON track.id = challenge.track_id

JOIN course_course as course
ON course.id = track.course_id

JOIN learn_week_challenges as lwc
ON lwc.challenge_id = challenge.id

JOIN learn_week as lweek
ON lweek.id = lwc.week_id

ORDER BY course.name, lweek.number, track.name, challenge."order"
) AS challenges
ON challenges.week_id = lweek.id
AND challenges.track_id = track.id
AND course.id = challenges.course_id


WHERE
enrollment.finish > CURRENT_DATE

ORDER BY course_id, enrollment_num, team_id, week_num, track.id, lweek.number
"""

admin_progress_body = """
SELECT
course.id as course_id,
course."name" as course_name,
lweek.number as week_num,
track.name as track_name,
enrollment.number as enrollment_num,
team.id as team_id,
CONCAT(tutor.first_name, ' ', tutor.last_name) as tutor,
tutor.id as tutor_id,
challenges.challenge_id,
challenges.challenge_name,
students.student,
statuses.status

FROM course_course as course

JOIN course_enrollment as enrollment
ON enrollment.course_id = course.id

JOIN course_team as team
ON enrollment.id = team.enrollment_id

JOIN course_team_students as cts
ON cts.team_id = team.id

JOIN (
SELECT
student.id as student_id,
CASE WHEN student.first_name = '' THEN student.username
  ELSE CONCAT(student.first_name, ' ', student.last_name)
END AS student
FROM user_user as student) as students
ON students.student_id = cts.user_id

JOIN user_user as tutor
ON team.tutor_id = tutor.id

JOIN course_track as track
ON course.id = track.course_id

JOIN learn_program_enrollments as lpe
ON lpe.enrollment_id = enrollment.id

JOIN learn_program as lprogram
ON lprogram.id = lpe.program_id

JOIN learn_program_weeks as lpw
ON lpw.program_id = lprogram.id

JOIN learn_week as lweek
ON lweek.id = lpw.week_id

LEFT JOIN (
SELECT
course.id as course_id,
lweek.id as week_id,
track.id as track_id,
challenge.id as challenge_id,
course.name as course_name,
lweek.number as week_num,
track.name as track_name,
challenge."name" as challenge_name

FROM learn_challenge as challenge

JOIN course_track as track
ON track.id = challenge.track_id

JOIN course_course as course
ON course.id = track.course_id

JOIN learn_week_challenges as lwc
ON lwc.challenge_id = challenge.id

JOIN learn_week as lweek
ON lweek.id = lwc.week_id

ORDER BY course.name, lweek.number, track.name, challenge."order"
) AS challenges
ON challenges.week_id = lweek.id
AND challenges.track_id = track.id
AND course.id = challenges.course_id

LEFT JOIN (
SELECT
status.id as status_id,
status.updated_at as updated_at,
status.status as status,
status.homework_id as homework_id,
status.student_id as student_id,
CASE WHEN student.first_name IS NULL THEN student.username
  ELSE CONCAT(student.first_name, ' ', student.last_name)
END AS student,
homework.team_id as team_id,
homework.challenge_id as challenge_id

FROM learn_homeworkstatus as status

JOIN user_user as student
ON student.id = status.student_id

JOIN learn_homework as homework
ON homework.id = status.homework_id

WHERE (homework_id, status.updated_at) IN (
  SELECT lhs.homework_id, MAX(lhs.updated_at)
  FROM learn_homeworkstatus as lhs
  GROUP BY homework_id
)

ORDER BY updated_at

) as statuses
ON challenges.challenge_id = statuses.challenge_id
AND team.id = statuses.team_id
AND statuses.student_id = students.student_id

WHERE
enrollment.finish > CURRENT_DATE

ORDER BY course_id, enrollment_num, team_id, week_num, track.id, lweek.number
"""
