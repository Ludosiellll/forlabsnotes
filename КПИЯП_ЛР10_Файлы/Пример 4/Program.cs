using System;
using System.Collections.Generic;
using System.Text;

namespace ConsoleApplication1
{
    class ProfessorWeb
    {
        const string ADDR = "http:\\\\professorweb.ru";
        public string level, inLevel;
        public int numberSt;
        private string inf;

        public void InfoPW()
        {
            Console.WriteLine("РЎР°Р№С‚: {0}\nР Р°Р·РґРµР»: {1}\nРџРѕРґСЂР°Р·РґРµР»: {2}\nРљРѕР»-РІРѕ СЃС‚Р°С‚РµР№:{3}", ADDR, level, inLevel, numberSt);
        }
    }

    class CSharp : ProfessorWeb
    {
        public string st;

        public CSharp(string level, string inLevel, int numberSt, string st)
        {
            this.level = level;
            this.inLevel = inLevel;
            this.numberSt = numberSt;
            this.st = st;
        }

        public void StWrite()
        {
            Console.WriteLine("РЎС‚Р°С‚СЊСЏ: " + st);
        }
    }

    class Program
    {
        static void Main()
        {
            CSharp obj = new CSharp(level: "C#", inLevel: "РџРµСЂРµРіСЂСѓР·РєР°", numberSt: 7, st: "РџРµСЂРµРіСЂСѓР·РєР° РјРµС‚РѕРґРѕРІ");
            obj.InfoPW();
            obj.StWrite();
        }
    }
}
