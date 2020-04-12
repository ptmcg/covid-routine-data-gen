import itertools
import pathlib
import random
import littletable as lt
from collections import namedtuple

# quick generators for table record id's
id_iter = None

def reset_id():
    global id_iter
    id_iter = itertools.count(start=100)

def next_id():
    return next(id_iter)


StaffMember = namedtuple("StaffMember", ['staff_id', 'last_name', 'first_name', 'role'])
firsts = pathlib.Path('first_names.txt').read_text().splitlines()
lasts = pathlib.Path('last_names.txt').read_text().splitlines()
NUM_NURSES = 12
NUM_DOCTORS = 8

names = set()
reset_id()
while len(names) < NUM_NURSES:
    names.add(StaffMember(next_id(), random.choice(lasts), random.choice(firsts), "nurse"))
while len(names) < NUM_NURSES + NUM_DOCTORS:
    names.add(StaffMember(next_id(), random.choice(lasts), random.choice(firsts), "doctor"))

staff = lt.Table()
staff.insert_many(sorted(names))
staff.create_index("staff_id", unique=True)
print(len(staff))
print(staff.info())
print(staff[0])
staff.csv_export("staff.csv")

departments = lt.Table()
reset_id()
departments.insert(lt.DataObject(id=next_id(), name="ER"))
departments.insert(lt.DataObject(id=next_id(), name="ICU"))
departments.insert(lt.DataObject(id=next_id(), name="OR"))
print(departments.info())
departments.create_index("id", unique=True)
departments.csv_export("departments.csv")

skills = lt.Table()
reset_id()
skills.insert(lt.DataObject(id=next_id(), name="OR-Nurse"))
skills.insert(lt.DataObject(id=next_id(), name="Surgery-Intern"))
skills.insert(lt.DataObject(id=next_id(), name="Surgeon"))
skills.insert(lt.DataObject(id=next_id(), name="Nurse-Anesthetist"))
skills.insert(lt.DataObject(id=next_id(), name="Anesthesiologist"))
skills.insert(lt.DataObject(id=next_id(), name="ER-Nurse"))
skills.insert(lt.DataObject(id=next_id(), name="ICU-Nurse"))
skills.insert(lt.DataObject(id=next_id(), name="Resident"))
skills.insert(lt.DataObject(id=next_id(), name="Nurse-Supervisor"))
skills.create_index("id", unique=True)
skills.create_index("name", unique=True)
print(skills.info())
skills.csv_export("skills.csv")

staff_skills_link = lt.Table()
NURSE_START = 100
DOCTOR_START = NURSE_START + NUM_NURSES
links = [
    # nurses
    (NURSE_START+0, skills.by.name["OR-Nurse"].id),
    (NURSE_START+1, skills.by.name["OR-Nurse"].id),
    (NURSE_START+2, skills.by.name["OR-Nurse"].id),
    (NURSE_START+3, skills.by.name["OR-Nurse"].id),
    (NURSE_START+4, skills.by.name["OR-Nurse"].id),
    (NURSE_START+5, skills.by.name["OR-Nurse"].id),
    (NURSE_START+6, skills.by.name["OR-Nurse"].id),
    (NURSE_START+7, skills.by.name["OR-Nurse"].id),
    (NURSE_START+8, skills.by.name["OR-Nurse"].id),
    (NURSE_START+9, skills.by.name["OR-Nurse"].id),
    (NURSE_START+5, skills.by.name["Nurse-Supervisor"].id),
    (NURSE_START+9, skills.by.name["Nurse-Supervisor"].id),
    (NURSE_START+4, skills.by.name["Nurse-Anesthetist"].id),
    (NURSE_START+8, skills.by.name["Nurse-Anesthetist"].id),
    # doctors
    (DOCTOR_START+0, skills.by.name["Surgeon"].id),
    (DOCTOR_START+1, skills.by.name["Surgeon"].id),
    (DOCTOR_START+2, skills.by.name["Surgeon"].id),
    (DOCTOR_START+3, skills.by.name["Surgery-Intern"].id),
    (DOCTOR_START+4, skills.by.name["Surgery-Intern"].id),
    (DOCTOR_START+5, skills.by.name["Surgery-Intern"].id),
    (DOCTOR_START+6, skills.by.name["Anesthesiologist"].id),
    (DOCTOR_START+7, skills.by.name["Anesthesiologist"].id),
]
for (staff_id, skill_id) in links:
    staff_skills_link.insert(lt.DataObject(staff_id=staff_id, skill_id=skill_id))
staff_skills_link.create_index("skill_id")
staff_skills_link.create_index("staff_id")
staff_skills_link.csv_export("staff_skills.csv")

# list out skills by staff member
staff_skill_join = (staff.join_on("staff_id")
                    + staff_skills_link).join_on("skill_id") + skills.join_on("id")
staff_skill_list = staff_skill_join()
print(staff_skill_list.info())
staff_skill_list.sort("staff_id")
for rec in staff_skill_list:
    print(rec.first_name, rec.last_name, '-', rec.name)

"""
Possible constraints:
- shift must have X doctors and Y nurses
- shift must have at least 1 nurse supervisor
- shift may have no more than 2 surgery interns for every surgeon
- shift must have 1 anesthesioligist and 1 nurse anesthetist
"""
