# Setting Up the Database:


## Run the following series of code inside the flask shell:


    ```bash
    u = User(username="Master", name="Master", phone="3737", email="master@example.com", position="Master")
    u.set_password('Master')   
    db.session.add(u)
    db.session.commit()
    ```


### This will allow you to access the app with the master and add classes, students, and staff.


    ```bash
    a1=Academy(name="Nuevos Ministerios")
    a2=Academy(name="Argüelles")
    a3=Academy(name="Alonso Martínez")
    a4=Academy(name="Ercilla")
    a5=Academy(name="Gómez Laguna")
    a6=Academy(name="San Miguel")
    a7=Academy(name="La Paz")
    a8=Academy(name="Rambla Catalunya")
    a9=Academy(name="Online")
    db.session.add(a1)   
    db.session.add(a2) 
    db.session.add(a3) 
    db.session.add(a4) 
    db.session.add(a5) 
    db.session.add(a6) 
    db.session.add(a7) 
    db.session.add(a8) 
    db.session.add(a9) 
    db.session.commit()
    academy = Academy.query.filter_by(name='Nuevos Ministerios').first() 
    u.academy_id = academy.id
    db.session.commit()
    ```


### This allows the academies that this program utilizes to be entered and ties one to the master once, more if requiring otherwise you would need to adapt.


    ```bash
    new_permission = PermissionGroups(group_name='Master')                                            
    db.session.add(new_permission)
    db.session.commit()
    permission = PermissionGroups.query.filter_by(group_name=new_permission.group_name).first() 
    u.add_access(permission)
    db.session.commit()
    new_permission = PermissionGroups(group_name='Teacher')                                            
    db.session.add(new_permission)
    db.session.commit()
    permission = PermissionGroups.query.filter_by(group_name=new_permission.group_name).first() 
    u.add_access(permission)
    db.session.commit()
    new_permission = PermissionGroups(group_name='Upper Management')                                            
    db.session.add(new_permission)
    db.session.commit()
    permission = PermissionGroups.query.filter_by(group_name=new_permission.group_name).first() 
    db.session.commit()
    new_permission = PermissionGroups(group_name='Management')                                            
    db.session.add(new_permission)
    db.session.commit()
    new_permission = PermissionGroups(group_name='Admin')                                            
    db.session.add(new_permission)
    db.session.commit()
    ```


### This will add the different permission levels required within the application and ties the master to master branch.


    ```bash
    t1=TrainedIn(name="General English") 
    t2=TrainedIn(name="Exam")            
    t3=TrainedIn(name="Children")
    t4=TrainedIn(name="Level Test")
    db.session.add(t1)
    db.session.add(t2)
    db.session.add(t3)
    db.session.add(t4)
    db.session.commit()
    t1.teacher = u.id 
    t2.teacher = u.id
    t3.teacher = u.id
    t4.teacher = u.id
    db.session.commit()
    a1=LengthOfClass(name="30 Minutes")
    a2=LengthOfClass(name="1 Hour")
    a3=LengthOfClass(name="1,5 Hours")
    a4=LengthOfClass(name="2 Hours")
    a5=LengthOfClass(name="2,5 Hours")
    a6=LengthOfClass(name="3 Hours")
    db.session.add(a1)   
    db.session.add(a2) 
    db.session.add(a3) 
    db.session.add(a4) 
    db.session.add(a5) 
    db.session.add(a6) 
    db.session.commit()
    s1=Step(name="1")
    s2=Step(name="2")
    s3=Step(name="3")
    s4=Step(name="4")
    s5=Step(name="5")
    s6=Step(name="6")
    s7=Step(name="7")
    s8=Step(name="8")
    s9=Step(name="9")
    s10=Step(name="10")
    s11=Step(name="11")
    s12=Step(name="12")
    s13=Step(name="13")
    s14=Step(name="14")
    s15=Step(name="15")
    s16=Step(name="16")
    db.session.add(s1)
    db.session.add(s2)
    db.session.add(s3)
    db.session.add(s4)
    db.session.add(s5)
    db.session.add(s6)
    db.session.add(s7)
    db.session.add(s8)
    db.session.add(s9)
    db.session.add(s10)
    db.session.add(s11)
    db.session.add(s12)
    db.session.add(s13)
    db.session.add(s14)
    db.session.add(s15)
    db.session.add(s16)
    db.session.commit()
    t1=TypeOfClass(name="121-General English")
    t2=TypeOfClass(name="121-Business English")
    t3=TypeOfClass(name="Group General English")
    t4=TypeOfClass(name="Group Business English")
    t5=TypeOfClass(name='Group Intensive')
    t6=TypeOfClass(name="Group Exam")
    t7=TypeOfClass(name="Group Children")
    t8=TypeOfClass(name="In-Company-121")
    t9=TypeOfClass(name="In-Company General English")
    t10=TypeOfClass(name="In-Company Business English")
    t11=TypeOfClass(name="121-Exam Class")
    t12=TypeOfClass(name="121-Children")
    db.session.add(t1)
    db.session.add(t2)
    db.session.add(t3)
    db.session.add(t4)
    db.session.add(t5)
    db.session.add(t6)
    db.session.add(t7)
    db.session.add(t8)
    db.session.add(t9)
    db.session.add(t10)
    db.session.add(t11)
    db.session.add(t12)
    db.session.commit()
    ```


### This snippet will add items that are required for this specific company.