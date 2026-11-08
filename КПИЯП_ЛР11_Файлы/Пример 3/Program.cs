using System;
using System.Collections.Generic;

namespace Test_MultiLevelComposition
{
    class Teacher
    {
        public string Name { get; set; }
        public string Position { get; set; }

        public Teacher(string name, string position)
        {
            Name = name;
            Position = position;
        }
    }

    class Department
    {
        public string Name { get; set; }
        public List<Teacher> Teachers { get; set; }

        public Department(string name)
        {
            Name = name;
            Teachers = new List<Teacher>();
        }

        public void AddTeacher(Teacher teacher)
        {
            Teachers.Add(teacher);
        }
    }

    class Faculty
    {
        public string Name { get; set; }
        public List<Department> Departments { get; set; }

        public Faculty(string name)
        {
            Name = name;
            Departments = new List<Department>();
        }

        public void AddDepartment(Department department)
        {
            Departments.Add(department);
        }
    }

    class University
    {
        public string Name { get; set; }
        public List<Faculty> Faculties { get; set; }

        public University(string name)
        {
            Name = name;
            Faculties = new List<Faculty>();
        }

        public void AddFaculty(Faculty faculty)
        {
            Faculties.Add(faculty);
        }

        public void DisplayStructure()
        {
            Console.WriteLine($"Университет: {Name}");
            foreach (var faculty in Faculties)
            {
                Console.WriteLine($"  Факультет: {faculty.Name}");
                foreach (var department in faculty.Departments)
                {
                    Console.WriteLine($"    Кафедра: {department.Name}");
                    foreach (var teacher in department.Teachers)
                    {
                        Console.WriteLine($"      Преподаватель: {teacher.Name} - {teacher.Position}");
                    }
                }
            }
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            University university = new University("БГУИР");

            Faculty fcsi = new Faculty("ФКСиС");
            Faculty fit = new Faculty("ФИТ");

            Department programmingDept = new Department("Программирования");
            Department mathDept = new Department("Математики");
            Department networkDept = new Department("Сетей и систем");

            Teacher teacher1 = new Teacher("Иванов И.И.", "Профессор");
            Teacher teacher2 = new Teacher("Петров П.П.", "Доцент");
            Teacher teacher3 = new Teacher("Сидоров С.С.", "Старший преподаватель");

            programmingDept.AddTeacher(teacher1);
            programmingDept.AddTeacher(teacher2);
            mathDept.AddTeacher(teacher3);

            fcsi.AddDepartment(programmingDept);
            fcsi.AddDepartment(mathDept);
            fit.AddDepartment(networkDept);

            university.AddFaculty(fcsi);
            university.AddFaculty(fit);

            university.DisplayStructure();

            Console.Write("Press any key to continue... ");
            Console.ReadKey(true);
        }
    }
}
