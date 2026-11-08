using System;
using System.Collections.Generic;

namespace Test_AggregationComposition
{
    public class House
    {
        public List<Room> Rooms { get; set; }

        public House()
        {
            Rooms = new List<Room>();
            Rooms.Add(new Room("Гостиная"));
            Rooms.Add(new Room("Спальня"));
            Rooms.Add(new Room("Кухня"));
        }

        public class Room
        {
            public string Name { get; set; }

            public Room(string name)
            {
                Name = name;
            }
        }
    }

    class University
    {
        public List<Student> Students { get; set; }

        public University()
        {
            Students = new List<Student>();
        }

        public void AddStudent(Student student)
        {
            Students.Add(student);
        }
    }

    class Student
    {
        public string Name { get; set; }

        public Student(string name)
        {
            Name = name;
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            House house = new House();
            Console.WriteLine("Дом создан с комнатами:");
            foreach (var room in house.Rooms)
            {
                Console.WriteLine($"- {room.Name}");
            }

            Student student1 = new Student("Иван Иванов");
            Student student2 = new Student("Петр Петров");

            University university = new University();
            university.AddStudent(student1);
            university.AddStudent(student2);

            Console.WriteLine("\nУниверситет с студентами:");
            foreach (var student in university.Students)
            {
                Console.WriteLine($"- {student.Name}");
            }

            Console.Write("Press any key to continue... ");
            Console.ReadKey(true);
        }
    }
}
