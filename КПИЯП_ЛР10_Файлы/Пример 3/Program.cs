using System;

namespace ConsoleApplication1
{
    abstract class UserInfo
    {
        protected string Name;
        protected byte Age;

        public UserInfo(string Name, byte Age)
        {
            this.Name = Name;
            this.Age = Age;
        }

        public abstract string ui();
    }

    class UserFamily : UserInfo
    {
        string Family;

        public UserFamily(string Family, string Name, byte Age) : base(Name, Age)
        {
            this.Family = Family;
        }

        public override string ui()
        {
            return Family + " " + Name + " " + Age;
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            UserFamily user1 = new UserFamily("Erohin", "Alexandr", 26);
            Console.WriteLine(user1.ui());
        }
    }
}
